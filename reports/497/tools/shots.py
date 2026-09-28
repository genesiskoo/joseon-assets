from PIL import Image
import shutil
pick = {"ss1.jpg": "cand/05_512.jpg", "ss2.jpg": "cand/06_590.jpg", "ss3.jpg": "cand/02_200.jpg"}
for out, src in pick.items():
    im = Image.open(src).convert("RGB")
    assert im.size == (1920, 1080), im.size
    im.save("../drive/" + out, quality=92, subsampling=0)
    print(out, src, im.size)
