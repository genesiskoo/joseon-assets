# 872 야차 동작 점검 장부 (/motion-pass)
- 카드: https://github.com/genesiskoo/joseon-hunters/issues/872 · 서비스·크레딧: 없음(GLB 가중치만 — `tools/joint_band.py`)
- 원본 `yacha_before.glb` = 게임 main `assets/models/yacha/yacha.glb`(#872 전) · 채택 `yacha_knee_band010.glb` (sha256 c35a73d6…) = `joint_band.py --band 0.10`(무릎 둘)
- 문제: 무릎 경계가 한 변에서 허벅지 0.97 | 종아리 0.96 · 무릎 앞면이 축에서 21cm 앞 → 달리기 33 · 죽기 35cm
- 되풀이: 띠 0.06(22·21) → **0.10(12.7·13.9)** → 0.15(11.8·13.9) → + 어깨·팔꿈치(공격 16.5→22.6 ✗ 기각)
- Blender 자(motion_pass): 죽기 35.0→12.26 · 달리기 32.88→13.1 · 걷기 17.34→8.62 · 대기 18.62→12.8 · 공격·맞기 그대로
- 보고서: `reports/motion_pass/yacha/{before,iter2}` · 사진: `reports/872/`
