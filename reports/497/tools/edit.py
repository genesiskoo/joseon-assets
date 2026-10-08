"""#497 ILE 제출 영상 — 1080p 재촬영(capture_1080.avi)에서 컷을 잘라 15초·풀 트레일러를 만든다.

- 컷 위치 = 장면 표식(CAPTURE <clip> BEGIN <frame>) + 장면 안 프레임. #456 30초 편집의 컷 그대로가 기본.
- 규격(폼): 1920×1080 · mp4 · H.264 약 24Mbps(권장 20 이상) · 30fps · AAC 48kHz 스테레오 · -15 LKFS ±1.
- 사용: python edit.py plan.json out.mp4
"""
import json, re, subprocess, sys, os, tempfile

WORK = os.path.dirname(os.path.abspath(__file__))
AVI = os.path.join(WORK, "capture_1080.avi")
LOG = os.path.join(WORK, "capture_1080_out.log")
FPS = 30


def markers():
    out = {}
    for line in open(LOG, encoding="utf-8", errors="replace"):
        m = re.match(r"CAPTURE (\S+) (BEGIN|END) (\d+)", line.strip())
        if m:
            out.setdefault(m.group(1), {})[m.group(2)] = int(m.group(3))
    return out


def run(cmd):
    print(" ".join(f'"{c}"' if " " in c else c for c in cmd)[:600], flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit(r.returncode)
    return r


def main():
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    mk = markers()
    inputs, vparts, aparts = [], [], []
    total = 0
    for i, c in enumerate(plan["cuts"]):
        b = mk[c["clip"]]["BEGIN"]
        start = b + c["from"]
        n = c["frames"]
        end_limit = mk[c["clip"]].get("END", 10**9)
        if start + n > end_limit:
            print(f"경고: {c['clip']} 컷이 장면 끝({end_limit})을 넘음 {start}+{n}")
        inputs += ["-ss", f"{start / FPS:.6f}", "-t", f"{n / FPS:.6f}", "-i", AVI]
        d = n / FPS
        vparts.append(f"[{i}:v]trim=end_frame={n},setpts=PTS-STARTPTS,fps={FPS},scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p[v{i}]")
        aparts.append(f"[{i}:a]atrim=end={d:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:st=0:d=0.025,afade=t=out:st={d - 0.025:.6f}:d=0.025[a{i}]")
        total += n
    k = len(plan["cuts"])
    fg = vparts + aparts
    fg.append("".join(f"[v{i}][a{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=1[vc][ac]")
    vlast, alast = "[vc]", "[ac]"
    card = plan.get("end_card")
    if card:
        cn = int(card["seconds"] * FPS)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{cn / FPS:.6f}", "-i", card["image"]]
        inputs += ["-f", "lavfi", "-t", f"{cn / FPS:.6f}", "-i", "anullsrc=r=48000:cl=stereo"]
        ci, ai = k, k + 1
        fg.append(f"[{ci}:v]scale=1920:1080,setsar=1,format=yuv420p,trim=end_frame={cn},setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.6[vcard]")
        # 게임 소리는 카드 들어가기 0.6초 전부터 줄인다
        gs = total / FPS
        fg.append(f"{alast}afade=t=out:st={gs - 0.6:.6f}:d=0.6[acf]")
        fg.append(f"{vlast}fade=t=out:st={gs - 0.4:.6f}:d=0.4[vcf]")
        fg.append(f"[vcf][acf][vcard][{ai}:a]concat=n=2:v=1:a=1[vc2][ac2]")
        vlast, alast = "[vc2]", "[ac2]"
        total += cn
    else:
        # 끝 0.4초 페이드
        gs = total / FPS
        fg.append(f"{alast}afade=t=out:st={gs - 0.5:.6f}:d=0.5[acf]")
        alast = "[acf]"
    fgs = ";\n".join(fg)
    graph = os.path.join(WORK, os.path.basename(out) + ".filter.txt")
    open(graph, "w", encoding="utf-8").write(fgs)

    # 1) 무손실 중간본(영상 x264 crf 0 대신 고화질 crf 10 + pcm) — 라우드니스 측정용
    mid = os.path.join(WORK, os.path.basename(out) + ".mid.mkv")
    run(["ffmpeg", "-hide_banner", "-y", *inputs, "-filter_complex_script", graph, "-map", vlast, "-map", alast,
         "-frames:v", str(total), "-c:v", "libx264", "-preset", "fast", "-crf", "8", "-pix_fmt", "yuv420p",
         "-c:a", "pcm_s16le", "-ar", "48000", mid])

    # 2) 라우드니스 1차 측정
    r = run(["ffmpeg", "-hide_banner", "-i", mid, "-map", "0:a", "-af", "loudnorm=I=-15:TP=-1.5:LRA=20:print_format=json", "-f", "null", "-"])
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-15:TP=-1.5:LRA=20:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,aresample=48000")
    print("1차 측정", js["input_i"], js["input_tp"], js["input_lra"])

    # 3) 최종 인코드 (2-pass 24Mbps)
    passlog = os.path.join(WORK, os.path.basename(out) + ".x264")
    venc = ["-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-level:v", "4.2", "-pix_fmt", "yuv420p",
            "-b:v", "24M", "-maxrate", "32M", "-bufsize", "48M", "-g", "30", "-r", str(FPS), "-passlogfile", passlog]
    run(["ffmpeg", "-hide_banner", "-y", "-i", mid, *venc, "-pass", "1", "-an", "-f", "mp4", "NUL"])
    run(["ffmpeg", "-hide_banner", "-y", "-i", mid, *venc, "-pass", "2", "-af", ln,
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", out])

    # 4) 검증
    r = run(["ffmpeg", "-hide_banner", "-i", out, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rindex("Summary:"):]
    print(tail)
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration,bit_rate:stream=codec_name,width,height,r_frame_rate,bit_rate,sample_rate,channels", "-of", "compact", out])
    print(r.stdout)
    os.remove(mid)
    for f in os.listdir(WORK):
        if f.startswith(os.path.basename(out) + ".x264"):
            os.remove(os.path.join(WORK, f))


if __name__ == "__main__":
    main()
