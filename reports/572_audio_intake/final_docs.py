import pathlib,json,shutil,re
root=pathlib.Path('C:/workspace/joseon');work=pathlib.Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon');p=root/'tmp/audio572'
manifest=work/'data/audio/production_572.json';dest=work/'docs/design/audio_572_manifest.json'
if manifest.exists():manifest.rename(dest)
# Empty new directory is never a tracked deletion.
sfx=json.loads((p/'sfx_intake.json').read_text(encoding='utf-8'));voice=json.loads((p/'voice_intake.json').read_text(encoding='utf-8'))
assert len(sfx)==111 and len(voice)==155
for r in sfx+voice:
 assert r['loudness'][1]<=-1.5,r['target']
 assert r['previous_sha256']!=r['sha256'],r['target']
vm=json.loads((p/'voice_manifest.json').read_text(encoding='utf-8'))
for file,want in vm['source_sha256'].items():
 import hashlib
 assert hashlib.sha256((work/file).read_bytes()).hexdigest()==want,file
log='''# 승인 오디오 반입 #572 (2026-10-03)

## PD 지시와 반입

“효과음은 새로 생성된 걸로 교체해라 / 대사는 elevenlabs v4 맥락 넣어서 만들걸로 넣고 / 판소리 오프닝에 넣고”를 게임 반입 승인으로 적용했다.

- 기존 SFX 60큐·109변주 전체 교체, 마을·동굴 환경음 2개 교체. 기존 파일 이름과 랜덤 큐 계약을 유지하여 이전 변주가 섞이지 않는다.
- #559·#566·#567 후보 중 기술적으로 깨끗한 것을 재사용하고, 부족한 43큐는 새로 생성했다. 재시도를 포함한 #572 SFX 원본은 136클립이며, 채택 소스는 모두 원본 클리핑 표본 0이다.
- 최신 대본 발화155줄·4,399글자를 eleven_v4로 생성했다. 총 음성691.76초. 도호=Taemin, 촌장/김영감=Sung-ho, 무당=JungA, 주모=Yuna. 안정도0.5, 유사도0.75, 한국어.
- 대본의 레이블·조건·선택지 분기를 추적해 같은 실행 분기의 이전/다음 발화를 요청에 넣었다. 98줄은 이웃 문맥이 있고, 독립 인사·무작위 소문 등 57줄은 타 분기 대사를 섞지 않는다. 선택지·무화자 서술은 낭독하지 않는다.
- Suno 판소리 A1(248c97f7-52c9-4a2f-b969-7bd5eddea7f0)을 opening.ogg로 반입했다. 168.8초, 오프닝 전용 1회 재생. 닫으면 대기 중이던 BGM/환경음이 이어진다.

## 음량과 구조

SFX/대사는 44.1kHz 16-bit mono WAV, SFX 목표−16LUFS·대사−18LUFS, 실제 TP≤−1.5dBTP. 환경음은 stereo OGG−24LUFS, 판소리는 stereo OGG−18LUFS. 선형 게인으로 어택을 보존하며 변환 후 실제 피크를 재측정해 여유를 맞췄다.

대사는 정적 ID와 전용 단일 플레이어로 연결한다. 같은 ID가 대본의 위치를 옮겨도 같은 파일을 찾으며 줄 변경·닫기·건너뛰기는 즉시 중단한다. 자동 진행은 음성 종료를 기다린다. 효과음 랜덤 풀을 공유하면 피치·겹침·자리 교체로 말이 끊기므로 전용 플레이어를 사용했다. 오프닝도 독립 플레이어가 원래 BGM의 재생 위치를 보존하므로 음악을 처음부터 재시작하는 방식보다 기존 음악 흐름을 지킨다.

Suno MP3 커버 이미지가 기본 FFmpeg 변환에서 Theora로 따라오는 문제를 발견했다. audio_intake는 첫 오디오 트랙만 매핑하고 영상은 제외한다. 커버가 붙은 MP3 합성 회귀 테스트를 추가했다. 브라우저의 OGG 길이 표시 차이는 동일 오디오 WAV 프리뷰로 해결했으며 게임용 OGG는 음성 트랙 하나·168.8초를 검증했다.

## 근거·청취

- 파일별 소스·SHA·이전SHA·실제음량: audio_572_manifest.json.
- 생성 요청·분기·대본SHA·캐스팅·모든 원본·기각 후보·실행 로그: joseon-assets/reports/572_audio_intake/.
- 최종267개: http://127.0.0.1:8767/release572/ . 기존 비교페이지에도 “게임 반입 #572” 267항목을 추가했다(총663항목).
- 집중 게임 E2E: audio_cues121, dialogue_band73, story_cutin32 검사 PASS. 대사 실제재생/종료, 판소리 단발/자연종료/못골복귀/새층음악대기/타이틀정리를 검증한다.
- 브라우저 대사1.28초·판소리168.8초 readyState4/error없음, 267개 파일 경로 및 각 종류HTTP200 PASS.
'''
(work/'docs/design/audio_572_log.md').write_text(log,encoding='utf-8')
(work/'docs/art/572_audio_intake/README.md').write_text('# #572 음원 청취 검수\n\n572_release_page.jpg = 최종 반입267개 페이지에서 실제 v4 대사 재생을 확인한 화면. 게임 변화는 음원·재생 연결이며 UI 화풍/레이아웃 변경은 없다. 원본 화면과 오디오/요청 원문은 joseon-assets reports/572_audio_intake에 보존한다.\n',encoding='utf-8')
print('FINAL_AUDIT 267 files; all replaced audio TP <= -1.5; latest dialogue source SHA matches')
