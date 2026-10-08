from pathlib import Path
import shutil
src=Path('C:/workspace/joseon/tmp/audio572')
w=Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon')
dst=Path('C:/workspace/joseon-assets/reports/572_audio_intake')
shutil.copytree(src,dst,dirs_exist_ok=True)
shutil.copytree(w/'tmp/e2e_raw',dst/'game_e2e_raw',dirs_exist_ok=True)
for name in ('audio_572_manifest.json','audio_572_log.md'):
    shutil.copy2(w/'docs/design'/name,dst/name)
(dst/'README.md').write_text('# #572 승인 오디오 반입\n\n신규 효과음109·환경음2, ElevenLabs eleven_v4 한국어 문맥 대사155, Suno 판소리 A1. 요청과 분기·대본 원문 및 SHA는 voice_manifest.json, 선택 후보는 sfx_selection.json, 실제 반입 파일별 SHA/음량은 audio_572_manifest.json. game_e2e_raw는 전체118/118 PASS의 원문. 생성 키는 보관하지 않는다. 게임 반입267개 청취: http://127.0.0.1:8767/release572/ .\n',encoding='utf-8')
print('ARCHIVED',dst)
