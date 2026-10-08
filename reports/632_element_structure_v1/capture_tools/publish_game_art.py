"""Publish only authorized #632 art README and six exact-frame JPGs."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
DEST=ROOT/'docs/art/632_element_structure_v1'
ASSETS='C:/workspace/joseon-assets/reports/632_element_structure_v1'
ap=argparse.ArgumentParser()
ap.add_argument('--game-commit')
a=ap.parse_args()
m=json.loads((BASE/'deliverables/video_manifest.json').read_text(encoding='utf-8'))
photos=json.loads((BASE/'deliverables/photos/photos_manifest.json').read_text(encoding='utf-8'))
assert len(photos['photos'])==6
DEST.mkdir(parents=True,exist_ok=True)
for row in photos['photos']:
    source=BASE/'deliverables/photos'/row['jpg']
    assert source.stat().st_size==row['bytes']<=300_000 and hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    shutil.copy2(source,DEST/row['jpg'])
lines=[ '# #632 속성 구조 v1 — 실제 전후 영상', '', '불·한기·벼락 부적의 실제 투사/명중과 적 살 구슬을 같은 배우·장비·카메라·구도·시드로 녹화했다. 낮음/강함 8구간 각 180프레임(3초), 편집본 합계 24초다. 정상 1×이며 Godot MovieMaker 기록 60fps는 실시간 성능 수치가 아니다.', '', f'기준 소스: `{m["source_before"]}`. 변경 후 최종 촬영: `{m["phase_after"]}`. 신규 `core/vfx_elements.gd` 및 `actors/enemy.gd`를 포함한 144개 runtime/data 원본 SHA256은 `video_manifest.json`에 있다. 촬영 대본 SHA256 `{m["capture_script_sha256"]}`는 BEFORE부터 최종 AFTER까지 같으며 전후 각 **47/47 PASS**다.', '', '전체 전투 메타를 exact 비교했다. 피해·명중·AoE·MP·부적 소모·HP·상태 timer·독립 투사체 RNG·배우/목표/카메라 위치·시전 cooldown·프레임별 time_scale까지 일치한다. 불/한기는 현재 반경 1.5의 3명 AoE, 벼락은 기존 단일 명중 그대로다. 살은 나찰녀의 실제 적 투사체이며 플레이어 독 주문을 추가하지 않았다. 세부 상태 루프는 #634에서 별도 검수한다.', '', '강도는 기존 정상 계산을 사용했다: 부적 정기20/150 → mult1.2/2.5, 살 지역Lv1/16 → 피해 배수1/2.5. 부적 belt5→4, MP 소모 없음. 기존 저강도와 고강도의 전투 수치도 각각 전후 동일하다.', '', '| 영상 | 길이 / 프레임 | 크기 |', '|---|---:|---:|' ]
for row in m['files']:
    stream=next(s for s in row['probe']['streams'] if s['codec_name']=='h264')
    lines.append(f'| [{row["file"]}]({ASSETS}/{row["file"]}) | {row["probe"]["format"]["duration"]}초 / {stream["nb_frames"]} | {row["bytes"]:,}B |')
lines += ['', '비교 영상은 좌우 같은 (280,80,720,540) crop을 640×480으로 보여준다. 실제 영상과 전체 엔진 전후 영상은 원래 카메라의 1280×720 화면이다. 4편 모두 전체 decode 오류0, 60/1fps, 프레임 수 검사를 통과했다. 최종 편집 경계는 정확한 `[BEGIN, END)`이며 AVI zero-based N은 Engine process counter N과 같다. 1프레임당 48kHz 원음800samples를 같은 경계로 잘랐다.', '', '**원음 표기:** baseline부터 Audio의 독립 변주/pitch RNG가 randomize되어 전후 원음은 byte동일하지 않다. A/B 비교와 실제 편집본에는 변경 후 실제 원음을 공유하며, 전체 엔진 전후 영상에는 각 촬영의 원음을 그대로 보존했다. 오디오 SHA 비교 및 차이 사유를 manifest에 기록했다.', '', '**원본 보존:** 최초 fixture/manager/E2E 실패와 모든 성공 로그를 제거 없이 reports에 보존한다. 유효 캡처에는 실행 중 shader/runtime error가 없고, PASS/녹화 종료 이후 기존 teardown의 ObjectDB11 / resource6 메시지는 원문 그대로 별도 분류한다. AVI 중간본은 파일당10MB 이상이라 로컬 ignored 폴더에 두고 위치·바이트·SHA256을 `local_originals.json`에 기록한다. 공유 가능한 전체 엔진 MP4 전후2편을 reports에 보존한다.', '', '원본·영상·촬영/편집 도구·메타·phase 원문: [`reports/632_element_structure_v1`]('+ASSETS+'/README.md). 각 파일10MB 미만, 카드50MB 미만이며 archive manifest로 바이트/SHA를 검증한다.', '', '| 같은 프레임 사진 | 변경 전 | 변경 후 |', '|---|---|---|' ]
for label,name in [('fire_strong','불 강함'),('cold_strong','한기 강함'),('sal_strong','적 살 강함')]:
    frame=next(row['source_frame_zero_based'] for row in photos['photos'] if row['label']==label)
    lines.append(f'| {name} · frame{frame} · 피해 최초 관측+8 | ![변경 전](before_{label}.jpg) | ![변경 후](after_{label}.jpg) |')
lines += ['', '사진6장은 원래 1280폭 화면으로 동일 엔진 프레임을 추출했고 각각300KB 이하이다. 현재 카메라·안개·알파 설정을 유지했다. 붓결 body 면과 지면 trace는 서로 다른 실제 접촉 높이를 사용한다.', '']
if a.game_commit:
    lines += [f'최종 게임 코드 커밋: `{a.game_commit}`.', '']
else:
    lines += ['최종 게임 커밋 및 전체 회귀시험 실측은 root의 시험 종료·커밋 후 이 기록과 reports에 추가한다.', '']
(DEST/'README.md').write_text('\n'.join(lines),encoding='utf-8')
total=sum(p.stat().st_size for p in DEST.iterdir() if p.is_file())
assert total<2_000_000
print(json.dumps({'game_art':str(DEST),'jpgs':6,'bytes':total},ensure_ascii=False))
