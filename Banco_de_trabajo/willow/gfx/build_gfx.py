#!/usr/bin/env python3
"""Converts the text pixel-art into SMS planar tiles + .inc symbol files."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import sprites as S
import bg as B
import portrait as P

OUT = os.path.join(os.path.dirname(__file__), '..', 'build')
os.makedirs(OUT, exist_ok=True)


def tile_bytes(px):  # px: 8 rows of 8 colour indices
    out = bytearray()
    for row in px:
        for plane in range(4):
            b = 0
            for x in range(8):
                if row[x] >> plane & 1:
                    b |= 0x80 >> x
            out.append(b)
    return bytes(out)


def grid_to_idx(grid, chars):
    return [[chars[c] for c in row] for row in grid]


def cut(idx, w, h):
    """split w x h pixel image (multiples of 8) into tiles: row-major tile order"""
    tiles = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            tiles.append([idx[ty * 8 + y][tx * 8:tx * 8 + 8] for y in range(8)])
    return tiles


def mirror(grid):
    return [row[::-1] for row in grid]


def sms_col(c):
    return c[0] | c[1] << 2 | c[2] << 4


inc = []
# ---------------- sprites ----------------
spr = bytearray()
ntile = 0


def add_sprite(name, grid):
    global ntile, spr
    h = len(grid); w = len(grid[0])
    idx = grid_to_idx(grid, S.SPAL_CHARS)
    tiles = cut(idx, w, h)
    inc.append('SPR_%s equ %d' % (name, ntile))
    for t in tiles:
        spr += tile_bytes(t)
    ntile += len(tiles)


WILLOW = ['W_STAND', 'W_WALK1', 'W_WALK2', 'W_JUMP', 'W_FART', 'W_DEAD']
for n in WILLOW:
    add_sprite(n + '_R', getattr(S, n))
for n in WILLOW:
    add_sprite(n + '_L', mirror(getattr(S, n)))
for n in ['BOLA1', 'BOLA2', 'ESC1', 'ESC2', 'ESCB1', 'ESCB2', 'BALL1', 'BALL2']:
    add_sprite(n, getattr(S, n))
for n in ['CLOUD_LOW1', 'CLOUD_LOW2']:
    add_sprite(n, getattr(S, n))
for n in ['PUFF1', 'PUFF2', 'PUFFBIG1', 'PUFFBIG2', 'STAR1', 'STAR2']:
    add_sprite(n, getattr(S, n))
def sit_on_ground(grid):
    # move the drawing down so its lowest row touches the bottom of the sprite
    g = list(grid)
    while g[-1].strip('.') == '':
        g = [g[-1]] + g[:-1]
    return g


for n in ['ATUN', 'PIENSO', 'GALLETA', 'SUSHI', 'SARDINA', 'LECHE']:
    add_sprite(n, sit_on_ground(getattr(S, n)))
add_sprite('ASP1_R', S.ASP1)
add_sprite('ASP2_R', S.ASP2)
add_sprite('ASP1_L', mirror(S.ASP1))
add_sprite('ASP2_L', mirror(S.ASP2))
for n in ['LAV1', 'LAV2', 'LAV_HIT']:
    add_sprite(n, getattr(S, n))
assert ntile <= 192, ntile
inc.append('SPR_NTILES equ %d' % ntile)
open(os.path.join(OUT, 'spr.bin'), 'wb').write(spr)

# sprite palette
spal = bytes(sms_col(c) for c in S.SPAL)
open(os.path.join(OUT, 'spal.bin'), 'wb').write(spal)

# ---------------- common BG: font + HUD ----------------
bgc = bytearray()
bt = 0
for ch in B.FONT_ORDER:
    g = B.FONT[ch]
    assert len(g) == 8 and all(len(r) == 8 for r in g), ch
    bgc += tile_bytes(grid_to_idx(g, B.BG_CHARS))
    bt += 1
inc.append('FONT_BASE equ 0')
inc.append('FONT_COUNT equ %d' % bt)
for name, g in B.HUD_TILES.items():
    inc.append('T_%s equ %d' % (name, bt))
    bgc += tile_bytes(grid_to_idx(g, B.BG_CHARS))
    bt += 1
inc.append('BG_COMMON_TILES equ %d' % bt)
open(os.path.join(OUT, 'bgcommon.bin'), 'wb').write(bgc)
# font char map for the assembler: we emit a translation table 0..255 -> tile
ftab = bytearray([0] * 256)
for i, ch in enumerate(B.FONT_ORDER):
    code = ch.encode('latin1')[0]
    ftab[code] = i
    if 'A' <= ch <= 'Z':
        ftab[ord(ch.lower())] = i
# Spanish extras map to closest
open(os.path.join(OUT, 'fontmap.bin'), 'wb').write(ftab)

# ---------------- rooms ----------------
ROOM_TILE_BASE = 96
inc.append('ROOM_TILE_BASE equ %d' % ROOM_TILE_BASE)
for i, n in enumerate(B.ROOM_TILE_NAMES):
    inc.append('RT_%s equ %d' % (n, ROOM_TILE_BASE + i))
inc.append('ROOM_TILE_COUNT equ %d' % len(B.ROOM_TILE_NAMES))
assert bt <= ROOM_TILE_BASE
for r, room in enumerate(B.ROOMS):
    data = bytearray()
    for n in B.ROOM_TILE_NAMES:
        g = room[n]
        assert len(g) == 8 and all(len(x) == 8 for x in g), (room['name'], n)
        base = room['WALLA'][0][0]
        g = [row.replace('.', base) for row in g]
        data += tile_bytes(grid_to_idx(g, B.BG_CHARS))
    open(os.path.join(OUT, 'room%d.bin' % r), 'wb').write(data)
    pal = list(B.BG_FIXED) + list(room['colors'])
    assert len(pal) == 16
    open(os.path.join(OUT, 'room%d.pal' % r), 'wb').write(bytes(sms_col(c) for c in pal))

# ---------------- title portrait ----------------
size = 96
idx, ppal = P.build(os.path.join(os.path.dirname(__file__), 'willow_foto.png'), (640, 330, 2040, 1730), size, 16,
                    [(0, 0, 0), (3, 3, 3), (3, 3, 0)], None)
while len(ppal) < 16:
    ppal.append((0, 0, 0))
# title palette must keep font colours at 0..2 -> already fixed
tiles = cut(idx.tolist(), size, size)
uniq, tmap = [], []
PORTRAIT_BASE = ROOM_TILE_BASE  # title uses room slot area (rooms not loaded on title)
for t in tiles:
    b = tile_bytes(t)
    if b not in uniq:
        uniq.append(b)
    tmap.append(PORTRAIT_BASE + uniq.index(b))
assert PORTRAIT_BASE + len(uniq) <= 256, len(uniq)
open(os.path.join(OUT, 'portrait.bin'), 'wb').write(b''.join(uniq))
open(os.path.join(OUT, 'portrait.map'), 'wb').write(bytes(tmap))
open(os.path.join(OUT, 'portrait.pal'), 'wb').write(bytes(sms_col(c) for c in ppal[:16]))
inc.append('PORTRAIT_TILES equ %d' % len(uniq))
inc.append('PORTRAIT_W equ %d' % (size // 8))

open(os.path.join(OUT, 'gfx.inc'), 'w').write('\n'.join(inc) + '\n')
print('sprite tiles', ntile, 'bg common', bt, 'portrait', len(uniq))
