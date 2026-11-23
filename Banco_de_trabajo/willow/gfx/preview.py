import sys
from PIL import Image
sys.path.insert(0, '.')
import sprites as S

def to_img(grid, pal, chars, scale=6):
    h = len(grid); w = len(grid[0])
    for r in grid:
        assert len(r) == w, (len(r), r)
    im = Image.new('RGB', (w, h), (255, 0, 255))
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            i = chars[ch]
            if i:
                c = pal[i]
                im.putpixel((x, y), (c[0] * 85, c[1] * 85, c[2] * 85))
            else:
                im.putpixel((x, y), (60, 90, 120))
    return im.resize((w * scale, h * scale), Image.NEAREST)

names = sys.argv[2:]
imgs = [to_img(getattr(S, n), S.SPAL, S.SPAL_CHARS) for n in names]
W = sum(i.width for i in imgs) + 8 * len(imgs)
H = max(i.height for i in imgs)
sheet = Image.new('RGB', (W, H), (30, 30, 30))
x = 0
for i in imgs:
    sheet.paste(i, (x, 0)); x += i.width + 8
sheet.save(sys.argv[1])
