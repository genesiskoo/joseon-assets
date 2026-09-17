from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path('workbench/reviews/yeokbyeong_v1_attack_bite_2026-06-08')
dirs = ['south', 'east', 'north']
# checkerboard background for visual alpha review
cell = 176
pad = 22
label_h = 24
cols = 9
rows = len(dirs)

def checker(size, tile=8):
    w, h = size
    bg = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    c1 = (42, 42, 42, 255)
    c2 = (66, 66, 66, 255)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            d.rectangle([x, y, x + tile - 1, y + tile - 1], fill=c1 if ((x // tile + y // tile) % 2 == 0) else c2)
    return bg

# GIFs per direction
for direction in dirs:
    frames = [Image.open(root / direction / f'frame_{i:03d}.png').convert('RGBA') for i in range(9)]
    gif_frames = []
    for fr in frames:
        bg = checker(fr.size)
        bg.alpha_composite(fr)
        gif_frames.append(bg.convert('P', palette=Image.Palette.ADAPTIVE))
    gif_frames[0].save(root / f'attack_bite_{direction}.gif', save_all=True, append_images=gif_frames[1:], duration=110, loop=0, disposal=2)

# Contact sheet
sheet_w = pad + cols * cell
sheet_h = pad + rows * (cell + label_h)
sheet = checker((sheet_w, sheet_h), tile=8)
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('arial.ttf', 14)
except Exception:
    font = ImageFont.load_default()
for r, direction in enumerate(dirs):
    y0 = pad + r * (cell + label_h)
    draw.text((4, y0 + 4), direction, fill=(255, 255, 255, 255), font=font)
    for i in range(cols):
        fr = Image.open(root / direction / f'frame_{i:03d}.png').convert('RGBA')
        x = pad + i * cell
        sheet.alpha_composite(fr, (x, y0 + label_h))
        draw.text((x + 4, y0 + label_h + 4), f'{i}', fill=(255, 255, 0, 255), font=font)
sheet.save(root / 'attack_bite_contact_sheet.png')

# East flipped preview for west reuse
frames = [Image.open(root / 'east' / f'frame_{i:03d}.png').convert('RGBA').transpose(Image.Transpose.FLIP_LEFT_RIGHT) for i in range(9)]
for i, fr in enumerate(frames):
    out_dir = root / 'west_from_east_flip'
    out_dir.mkdir(exist_ok=True)
    fr.save(out_dir / f'frame_{i:03d}.png')
gif_frames = []
for fr in frames:
    bg = checker(fr.size)
    bg.alpha_composite(fr)
    gif_frames.append(bg.convert('P', palette=Image.Palette.ADAPTIVE))
gif_frames[0].save(root / 'attack_bite_west_from_east_flip.gif', save_all=True, append_images=gif_frames[1:], duration=110, loop=0, disposal=2)

print('created', root / 'attack_bite_contact_sheet.png')
print('created gifs', ', '.join(str(root / f'attack_bite_{d}.gif') for d in dirs))
print('created', root / 'attack_bite_west_from_east_flip.gif')
