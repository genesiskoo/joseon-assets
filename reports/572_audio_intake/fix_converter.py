import pathlib
p=pathlib.Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon/tools/audio_intake.py')
s=p.read_text(encoding='utf-8')
s=s.replace('["-i", src, "-af", af, "-ar", "44100"]','["-i", src, "-map", "0:a:0", "-vn", "-af", af, "-ar", "44100"]')
needle='    finally:\n        shutil.rmtree(tmp, ignore_errors=True)'
test='''        # #572: Suno MP3 album art must never become a Theora track in game OGG.
        cover = os.path.join(tmp, "cover.ppm")
        open(cover, "wb").write(b"P6\\n2 2\\n255\\n" + b"\\x80\\x40\\x20" * 4)
        covered = os.path.join(tmp, "covered.mp3")
        fixture = run(["ffmpeg", "-hide_banner", "-y", "-i", src2, "-i", cover,
                       "-map", "0:a:0", "-map", "1:v:0", "-c:a", "libmp3lame", "-c:v", "mjpeg",
                       "-disposition:v:0", "attached_pic", covered])
        if fixture.returncode:
            fails.append("covered MP3 fixture: " + fixture.stderr)
        else:
            cover_out = intake(covered, "probe_cover", "bgm", out_root)[0]
            streams = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", cover_out]).stdout)["streams"]
            if len(streams) != 1 or streams[0]["codec_type"] != "audio":
                fails.append("album art leaked into OGG: %s" % streams)
            os.remove(cover_out)
'''
assert needle in s
s=s.replace(needle,test+needle)
p.write_text(s,encoding='utf-8')
