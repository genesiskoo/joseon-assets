from pathlib import Path
import re
w=Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon')
m=Path('C:/workspace/joseon')
nums=[]
for root in (w,m):
    for f in ('docs/DECISIONS.md','docs/DECISIONS_HISTORY.md'):
        nums += [int(n) for n in re.findall(r'D-(\d{3})',(root/f).read_text(encoding='utf-8'))]
d=f'D-{max(nums)+1:03d}'
def edit(f,old,new):
    p=w/f;s=p.read_text(encoding='utf-8');assert old in s,f;p.write_text(s.replace(old,new),encoding='utf-8')
edit('docs/DECISIONS.md','사설 텍스트(음성 0)','사설 텍스트·판소리 음원')
edit('docs/DECISIONS.md','**D-017** EA 음성 0 — 대사·가창·나레이션만 음성, 기합·신음·사망 소리는 효과음(D-076)',f'**D-017** EA 음성 0은 {d}로 갱신 — 정적 대사·판소리 오프닝 허용, 기합·신음·사망 소리는 효과음(D-076)')
with (w/'docs/DECISIONS.md').open('a',encoding='utf-8') as f:f.write(f'\n- **{d}** 승인 오디오 반입(#572, 2026-10-03): 신규 SFX 109·환경음 2 교체, ElevenLabs v4 분기 문맥 대사 155줄, Suno 판소리 오프닝 A1 단발 재생. D-017·D-049의 음성 0 갱신.\n')
with (w/'docs/DECISIONS_HISTORY.md').open('a',encoding='utf-8') as f:f.write(f'\n## {d} — 승인 오디오 실반입 (2026-10-03, #572)\n\nPD 지시: 「효과음은 새로 생성된 걸로 교체해라 / 대사는 elevanlab v4 맥락 넣어서 만들걸로 넣고 / 판소리 오프닝에 넣고」. D-017의 EA 음성 0과 D-049의 사설 텍스트 음성 0을 이 승인 범위에서 갱신한다. 신규 효과음 109개·환경음 2개, 현재 정적 대사 155줄의 ElevenLabs eleven_v4 한국어 음성, Suno 판소리 A1을 반입한다. 대사 문맥은 같은 분기의 인접 발화만 사용하고, 오프닝은 한 번 재생한 뒤 기존 BGM으로 돌아간다. 소스·검증은 `design/audio_572_log.md`·`audio_572_manifest.json`.\n')
edit('AGENTS.md','- ❌ EA 음성 = 대사·가창·나레이션 (D-017, 1.0 카드). **기합·신음·사망 소리는 효과음이라 EA 반입 O** (D-076)',f'- **음성 승인 범위({d}, #572)**: 정적 대사 = ElevenLabs v4 문맥 음성, 판소리 오프닝 반입. 기합·신음·사망 소리는 효과음(D-076). D-017의 EA 음성 0은 이 범위에서 갱신.')
edit('docs/design/dialogue_v2.md','D-017(음성 0 — 자막만)',f'{d}(정적 대사 v4 음성 승인 · D-017 갱신)')
edit('docs/design/dialogue_v2.md','## 7. 소리\n','## 7. 소리\n\n'+f'- {d}·#572: 정적 발화 ID와 같은 이름의 `assets/audio/voice/<ID>.wav`를 재생한다. 같은 분기의 앞뒤 대사를 v4 문맥에 넣는다. 다음 줄·건너뛰기·대화 종료 때 이전 음성을 중단하고, 자동 진행은 발화 종료 뒤 대기 시간을 센다.\n')
with (w/'docs/TASK_CURRENT.md').open('a',encoding='utf-8') as f:f.write('\n- 2026-10-03 #572 ← `C:/workspace/joseon-assets/reports/572_audio_intake/` 신규 SFX109·환경음2·문맥형v4 대사155·Suno 판소리A1 → `assets/audio/` (267개, 44.1kHz·음량/피크 검수·전용 대사/오프닝 재생 연결).\n')
with (w/'docs/STATE.md').open('a',encoding='utf-8') as f:f.write('\n- 2026-10-03 #572: 신규 SFX109·환경음2 교체, ElevenLabs v4 문맥형 정적 대사155 연결, Suno 판소리A1 오프닝 단발 재생. 최종267개 청취 `http://127.0.0.1:8767/release572/`, 소스·기각 후보는 assets reports/572_audio_intake.\n')
print(d)
