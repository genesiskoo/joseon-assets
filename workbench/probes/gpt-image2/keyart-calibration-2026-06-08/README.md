# Key Art Calibration â€” 2026-06-08

ì´ í´ë”ëŠ” `art-direction/work-orders/2026-06-08-keyart-calibration-v1.md` ê²°ê³¼ë¬¼ì„ ë³´ê´€í•œë‹¤.

## Reference Set

- `joseon_active_working_v1`

## Output Rule

- ì›ë³¸ ìƒì„± PNGëŠ” ê·¸ëŒ€ë¡œ ë³´ì¡´í•œë‹¤.
- ì‚¬ëŒì´ ê³ ë¥¸ í›„ë³´ëŠ” íŒŒì¼ëª…ì— `_selected`ë¥¼ ë¶™ì´ì§€ ë§ê³  `art-direction/manifests/generations.csv`ì˜ `review_status`ë¡œ ê´€ë¦¬í•œë‹¤.
- ê³µì‹ í‚¤ì•„íŠ¸ë¡œ ìŠ¹ê²©í•˜ê¸° ì „ê¹Œì§€ `concept/` ë˜ëŠ” `landing/`ìœ¼ë¡œ ë³µì‚¬í•˜ì§€ ì•ŠëŠ”ë‹¤.

## Candidates

- `joseon_keyart_calibration_v1_a.png`
  - ìƒì„± ì‹œê°: `2026-06-08T11:44:03+09:00`
  - ë„êµ¬: built-in `image_gen`
  - ìƒíƒœ: `pending`
  - 1ì°¨ ë¦¬ë·°: ì „ì²´ ë¬´ë“œì™€ ì¡°ì„  ë§ˆì„ ë¬¸ì€ ì¢‹ë‹¤. upper-left íƒ€ì´í‹€ ì—¬ë°±ì´ ë‹¬ê³¼ ì¥ìŠ¹ìœ¼ë¡œ ì¢ê³ , ê·€ìƒˆ ì‹¤ë£¨ì—£ì´ ì•½ê°„ ì¼ë°˜ ì•”ì‚´ì ìª½ìœ¼ë¡œ ê¸°ìš´ë‹¤.
- `joseon_keyart_calibration_v1_b.png`
  - ìƒì„± ì‹œê°: `2026-06-08T11:50:43+09:00`
  - ë„êµ¬: built-in `image_gen`
  - ìƒíƒœ: `review`
  - 1ì°¨ ë¦¬ë·°: upper-left title-safe ì—¬ë°±ê³¼ ë¶‰ì€ ê°€ë©´ ë¬´í¬ ì‹¤ë£¨ì—£ì´ Aë³´ë‹¤ ë‚«ë‹¤. ë‹¤ë§Œ ìºë¦­í„° ì •ì²´ì„±ì€ ì§ì ‘ reference-image ì…ë ¥ì´ ì•„ë‹ˆë¼ í”„ë¡¬í”„íŠ¸ ê¸°ë°˜ì´ë¼ ë‹¤ìŒ API/CLI íŒ¨ìŠ¤ì—ì„œ ë³´ê°•í•´ì•¼ í•œë‹¤.

## i2v Motion Previews (2026-06-09)

The i2v videos use the keyart images as source frames to preview cinematic animation potential. Prompts emphasize slow camera push-in for drama, subtle wind on fabrics/talismans, atmospheric mist and minimal monster movement to keep complex compositions readable. Designed as reference for further keyart refinement or PixelLab-style animation planning. All 6s @ 720p, static composition with living subtle motion.

### v1_a
- File: joseon_keyart_calibration_v1_a_i2v_6s_720p.mp4
- Source: joseon_keyart_calibration_v1_a.png

**Prompt used:**
"Cinematic key art at night in front of a grand Joseon village gate with a massive dark monster spirit emerging from the shadows. Three heroes stand ready: central male swordsman in black gat and robe holding a sword, shamaness in flowing white hanbok with fan and bells on the left, masked red-clad blade dancer with curved sword on the right. Very slow smooth camera push-in from medium wide establishing shot toward the central group, subtle night wind gently moving robes, hair, and hanging talismans, faint mist and blue spirit lights flicker, the monster's form shifts slightly with glowing eyes. Dramatic restrained lighting, tense mysterious atmosphere, clear readable silhouettes. Present tense, minimal but living motion."

### v1_b
- File: joseon_keyart_calibration_v1_b_i2v_6s_720p.mp4
- Source: joseon_keyart_calibration_v1_b.png

**Prompt used:**
"Cinematic key art at night in front of a grand Joseon village gate with a massive dark monster spirit looming overhead. Three heroes in dynamic stance: central male swordsman in black gat and robe with sword, shamaness in white hanbok with fan on the left, red masked dancer with blades on the right. Very slow smooth camera push-in from wide shot tightening on the trio, subtle wind blowing fabrics, ribbons and talismans, atmospheric mist and blue energy wisps, monster's smoky form drifts slightly with intense glowing eyes. Restrained dramatic lighting, strong title-safe upper left space, mysterious tense mood. Present tense, clear silhouettes, minimal but atmospheric motion."

These can be reviewed alongside the statics for calibration decisions (e.g., which composition supports better motion without losing impact). Next steps could include using these as loose reference for further GPT Image refinements or direct PixelLab animation tests if moving to production sprites.

## Sprite Test i2v (2026-06-10)
Downsized composite sheet (joseon_keyart_calibration_sprite_test_source.png)ÀÇ 3°³ ½ºÄÉÀÏ Ä³¸¯ÅÍ¸¦ image_edit·Î ºĞ¸®(cuts/)ÇÏ°í front view walk/run (large+medium), walk (tiny) i2v 480p 6s »ı¼º.

Àü¿ë Æú´õ: workbench/probes/inbox/joseon_keyart_calibration_sprite_test_source/
- cuts/: large/medium/tiny isolated jpg
- videos/: 5°³ seamless ¸ğ¼Ç mp4 (large_walk, large_run, medium_walk, medium_run, tiny_walk)
- 256/384 ´Ù¿î½ºÄÉÀÏ ½ÃÆ® º¹»çº» Æ÷ÇÔ
- README.md¿¡ ÀüÃ¼ ÇÁ·ÒÇÁÆ®¿Í ffmpeg 256px ¿öÅ©¾î¶ó¿îµå ±â·Ï

»ó¼¼: ÇØ´ç Æú´õ README.md ÂüÁ¶. PixelLab ½ºÇÁ¶óÀÌÆ® Á¦ÀÛ Àü ¸ğ¼Ç Âü°í¿ë.
