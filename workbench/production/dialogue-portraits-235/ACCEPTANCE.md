# #243 PD 채택 기록 (2026-09-28)

PD의 '승인 다음작업'에 따라 직전 검토판의 후보 전부를 채택했다. 이 기록은 원화 채택이며 게임 파일 연결은 별도 카드에서 진행한다.

- 채택 원화: 5 PNG
- 원본 후보 커밋: 7ffe5687859da97252e324572bc790d3b525d751
- 원본·프롬프트·해시: manifest.json, generation_sources.json, PROMPTS.md
- 검수: 각 카드의 reports 폴더와 게임 docs/art 갤러리

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
| doho/neutral | `workbench/production/dialogue-portraits-235/game/doho/neutral.png` | `522b0357e833bb2aa3ac4974013fd809401f7356bb56bb9ec1bccd6527d4ddd1` |
| doho/smug | `workbench/production/dialogue-portraits-235/game/doho/smug.png` | `e3dde31273a6ca964928e729e3d2268eaca9e4b7237ce254dbebadce6ab6ad57` |
| doho/serious | `workbench/production/dialogue-portraits-235/game/doho/serious.png` | `24dfb5acbc0321f42277820dbee4f81e5334ac2aff8ece1b4f59ca87dc3daee7` |
| merchant/neutral | `workbench/production/dialogue-portraits-235/game/merchant/neutral.png` | `df61a1b15d7d18c9b5adc1ab1e434d6d47e8b8863386040a790e40cf092d9f79` |
| merchant/smile | `workbench/production/dialogue-portraits-235/game/merchant/smile.png` | `549a5f20f88e9c07612c87ec5dd85a05a4c1f8ae608ba37c723378714271970a` |

대화 초상 파일럿을 채택했다. 현재 초상 정지화상용 앵커·그늘과 intake_portrait 도구가 없으므로, 별도 게임 반입 카드에서 실제 교체 전후·회귀 검수를 마친다. 이후 같은 기준으로 남은 인물 표정을 제작한다.
