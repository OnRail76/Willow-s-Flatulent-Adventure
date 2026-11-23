# Sprite pixel art for Willow's Flatulent Adventure (SMS).
# All drawn facing RIGHT; left versions are mirrored by build_gfx.py.
# Palette chars (sprite palette):
SPAL_CHARS = {
    '.': 0, 'K': 1, 'D': 2, 'L': 3, 'W': 4, 'P': 5, 'G': 6, 'g': 7,
    'R': 8, 'r': 9, 'B': 10, 'S': 11, 'O': 12, 'U': 13, 'u': 14, 'Y': 15,
}
# SMS colours as (r,g,b) 0..3
SPAL = [
    (0, 0, 0),   # 0 transparent
    (0, 0, 0),   # K black
    (1, 1, 1),   # D dark grey
    (2, 2, 2),   # L light grey
    (3, 3, 3),   # W white
    (3, 2, 2),   # P pink
    (1, 3, 0),   # G gas green
    (0, 2, 0),   # g dark green
    (3, 0, 0),   # R red
    (2, 0, 0),   # r dark red
    (2, 1, 0),   # B brown
    (3, 3, 1),   # S straw
    (3, 2, 0),   # O orange
    (0, 1, 3),   # U blue
    (2, 3, 3),   # u light blue
    (3, 3, 0),   # Y yellow
]

# ---------------- WILLOW (16x16) ----------------
BODY = [
    "..LLDLLDLWLPLWL.",
    "..LLDLLDLDWWWL..",
    "..LLDLLDLDWWL...",
    "..LLDLLDLLWW....",
    "..LLLLLLLLWW....",
    "...WWWWWWWW.....",
]
HEAD = [
    ".........D...D..",
    "........DPD.DPD.",
    "........DLLDLLD.",
    "........LDLDLDL.",
    "........LYKLYKL.",
]
W_STAND = [
    "................",
    ".D" + HEAD[0][2:],
    ".L" + HEAD[1][2:],
    ".D" + HEAD[2][2:],
    "..L" + HEAD[3][3:],
    "..D" + HEAD[4][3:],
] + BODY + [
    "...LD.LD.LD.LD..",
    "...DL.DL.DL.DL..",
    "...LD.LD.LD.LD..",
    "...WW.WW.WW.WW..",
]
W_WALK1 = W_STAND[:12] + [
    "..LD..LD.LD..LD.",
    "..DL...DLDL..DL.",
    ".LD.....LD..LD..",
    ".WW.....WW..WW..",
]
W_WALK2 = W_STAND[:12] + [
    "....LDLD...LDLD.",
    "....DL.DL..DL.D.",
    "...LD...LD.LD...",
    "...WW...WW.WW...",
]
W_JUMP = [
    ".........D...D..",
    "........DPD.DPD.",
    "D.......DLLDLLD.",
    "L.......LDLDLDL.",
    ".D......LYKLYKL.",
    ".LLLDLLDLWLPLWL.",
    "..LLDLLDLDWWWL..",
    "..LLDLLDLDWWLD..",
    "..LLDLLDLLWWLDL.",
    ".LLLLLLLLLWW.WWL",
    "LDWWWWWWWWW.....",
    "DL..........LD..",
    "WL...........WW.",
    "W...............",
    "................",
    "................",
]
W_FART = [
    "D...............",
    "L........D...D..",
    ".D......DPD.DPD.",
    ".L......DLLDLLD.",
    "..D.....LDLDLDL.",
    "..LD....LKKLKKL.",
] + BODY + [
    "...LD.LD.LD.LD..",
    "...DL.DL.DL.DL..",
    "...LD.LD.LD.LD..",
    "...WW.WW.WW.WW..",
]
W_DEAD = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    ".........D...D..",
    "........DPD.DPD.",
    "........DLLDLLD.",
    ".D......LKLDLKL.",
    "..D.....KLKLKLK.",
    "..LLDLLDLWLPLWL.",
    "..LLDLLDLLWWWL..",
    "..WLLLLLLLLLWW..",
    ".WW.WWWWWWWW.WW.",
]

# ---------------- BOLA DE GOMA (16x16) ----------------
BOLA1 = [
    "................",
    ".....rrrrrr.....",
    "...rrRRRRRRrr...",
    "..rRRWWRRRRRRr..",
    "..rRWWRRRRRRRr..",
    ".rRRWRRRRRRRRRr.",
    ".rRKKKRRRRKKKRr.",
    ".rRRWKRRRRWKRRr.",
    ".rRRKKRRRRKKRRr.",
    ".rRRRRRRRRRRRRr.",
    ".rRRRKKKKKKRRRr.",
    "..rRRRRRRRRRRr..",
    "..rRRRRRRRRRRr..",
    "...rrRRRRRRrr...",
    ".....rrrrrr.....",
    "................",
]
BOLA2 = [
    "................",
    "................",
    "................",
    "....rrrrrrrr....",
    "..rrRRRRRRRRrr..",
    ".rRRWWRRRRRRRRr.",
    "rRRWWRRRRRRRRRRr",
    "rRKKKRRRRRRKKKRr",
    "rRRWKRRRRRRWKRRr",
    "rRRKKRRRRRRKKRRr",
    "rRRRRRKKKKRRRRRr",
    "rRRRRRRRRRRRRRRr",
    ".rRRRRRRRRRRRRr.",
    "..rrRRRRRRRRrr..",
    "....rrrrrrrr....",
    "................",
]
# ---------------- ESCOBA (16x16), symmetric hopping broom ----------------
ESC1 = [
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".....rrrrrr.....",
    "....SSSSSSSS....",
    "....SWKSSWKS....",
    "...SSKKSSKKSS...",
    "...SSSSSSSSSS...",
    "..SSSOSSSSOSSS..",
    "..SSOSSOSSOSOS..",
    ".SSOSSOSSOSSOSS.",
    ".SOSSOSSSSOSSOS.",
    "SOS.SOS..SOS.SOS",
    "S...S......S...S",
]
ESC2 = [
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".....rrrrrr.....",
    "....SSSSSSSS....",
    "....SWKSSWKS....",
    "...SSKKSSKKSS...",
    "...SSSKKKKSSS...",
    "...SSOSSOSSOS...",
    "...SOSSOSSOSS...",
    "..SOSSOSSOSSOS..",
    "..SOSSOSSOSSOS..",
    "..S.S.S..S.S.S..",
]
ESCB1 = [  # bald broom (lost half its bristles)
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".....rrrrrr.....",
    "....SSSSSSSS....",
    "....SWKSSWKS....",
    "....SKKSSKKS....",
    "....SSKKKKSS....",
    "....S.S..S.S....",
    "....S.S..S.S....",
    ".....S....S.....",
    ".....S....S.....",
    "................",
]
ESCB2 = [
    "................",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".......BB.......",
    ".....rrrrrr.....",
    "....SSSSSSSS....",
    "....SKWSSKWS....",
    "....SKKSSKKS....",
    "....SSKKKKSS....",
    "....S.S..S.S....",
    "...S..S..S..S...",
    "...S..S..S..S...",
    "................",
]
# ---------------- GAS ----------------
CLOUD_LOW1 = [  # 16x8 bottom-half cloud overlay
    "..GG....GGG.....",
    ".GGGG.GGGGGG.GG.",
    "GGGgGGGGgGGGGGGG",
    "GgGGGGgGGGGgGGgG",
    "GGGGgGGGGgGGGGGG",
    "GGgGGGGgGGGGgGGG",
    ".GGGGgGGGGGgGGG.",
    "..GG..GGGG..GG..",
]
CLOUD_LOW2 = [
    "...GG...GGG..G..",
    ".GGGGGGGGGGGGGG.",
    "GGgGGGGgGGGGGgGG",
    "GGGGgGGGGGgGGGGG",
    "GgGGGGGgGGGGGGgG",
    "GGGGgGGGGgGGgGGG",
    ".GGgGGGGGGGGGGG.",
    "...GGG..GG.GGG..",
]
BALL1 = [  # fully gassed enemy: stinky cloud ball with dizzy eyes
    ".....GGGGG......",
    "...GGGGGGGGG....",
    "..GGGgGGGGGGGG..",
    ".GGGGGGGGGgGGGG.",
    ".GGgGGGGGGGGGGG.",
    "GGGGWWGGGGWWGGGG",
    "GGGWKWGGGWKWGgGG",
    "GgGGWWGGGGWWGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGGGKKKKGGGGgG",
    "GGgGGGGGGGGGGGGG",
    ".GGGGGGgGGGGGGG.",
    ".GGGGGGGGGGGgGG.",
    "..GGgGGGGGGGGG..",
    "...GGGGGGGGGG...",
    ".....GGGGGG.....",
]
BALL2 = [
    "......GGGGG.....",
    "....GGGGGGGGG...",
    "..GGGGGGGGgGGG..",
    ".GGGGgGGGGGGGGG.",
    ".GGGGGGGGGGGGgG.",
    "GGGGWWGGGGWWGGGG",
    "GgGGWKWGGGWKWGGG",
    "GGGGWWGGGGWWGGGG",
    "GGGGGGGGGGGGGGGG",
    "GgGGGGKKKKGGGGGG",
    "GGGGGGGGGGGGGgGG",
    ".GGGgGGGGGGGGGG.",
    ".GGGGGGGGgGGGGG.",
    "..GGGGGGGGGGgG..",
    "...GGGGGGGGGG...",
    ".....GGGGGG.....",
]
PUFF1 = [  # 8x8 gas puff
    "..GG....",
    ".GGGG.G.",
    "GGgGGGGG",
    "GGGGGgGG",
    ".GgGGGG.",
    "GGGGGGGG",
    ".GGgGG..",
    "...GG...",
]
PUFF2 = [
    "...G.G..",
    ".GGGGGG.",
    "GGGGgGGG",
    "GgGGGGGG",
    "GGGGGGgG",
    ".GGgGGG.",
    "..GGGG..",
    "........",
]
PUFFBIG1 = [  # tuna-powered puff (yellowish core)
    ".GG.GG..",
    "GGYYGGG.",
    "GYYYYGGG",
    "GYYGYYGG",
    "GGYYYYGG",
    "GGGYYGG.",
    ".GGGGGG.",
    "..G.GG..",
]
PUFFBIG2 = [
    "..GGG.G.",
    ".GGYYGGG",
    "GGYYYYGG",
    "GYYYGYYG",
    "GGYYYYGG",
    ".GYYYGGG",
    "GGGGGGG.",
    ".G.GG...",
]
STAR1 = [
    "...Y....",
    "...Y....",
    ".YYWYY..",
    "..YWY...",
    ".Y...Y..",
    "........",
    "........",
    "........",
]
STAR2 = [
    "........",
    ".Y...Y..",
    "..Y.Y...",
    "...W....",
    "..Y.Y...",
    ".Y...Y..",
    "........",
    "........",
]
# ---------------- ITEMS (16x16) ----------------
ATUN = [
    "................",
    "................",
    "...LLLLLLLLLL...",
    "..LWWWWWWWWWWL..",
    "..LLLLLLLLLLLL..",
    "..UUUUUUUUUUUU..",
    "..UuuuuuuuuuuU..",
    "..UuLLLuuuuLuU..",
    "..ULLKLLLLLLLU..",
    "..UuLLLuuuuLuU..",
    "..UuuuuuuuuuuU..",
    "..UUUUUUUUUUUU..",
    "..LLLLLLLLLLLL..",
    "...LLLLLLLLLL...",
    "................",
    "................",
]
PIENSO = [
    "................",
    "...BBBBBBBBBB...",
    "..BOOOOOOOOOOB..",
    "..BBBBBBBBBBBB..",
    "..ROOOOOOOOOOR..",
    "..RODOOODOOOOR..",
    "..ROLLLLLOOOOR..",
    "..ROLYLYLOOOOR..",
    "..ROLLPLLOOOOR..",
    "..ROOLLLOOOBOR..",
    "..ROOOOOOOBBBR..",
    "..ROOOOOOOOBOR..",
    "..RRRRRRRRRRRR..",
    "..rrrrrrrrrrrr..",
    "................",
    "................",
]
GALLETA = [
    "................",
    "................",
    "................",
    "..........BB....",
    "......OOOOBBB...",
    "....OOSOOOOBB...",
    "...OOOOOOSOO.B..",
    "..OKOOSOOOOOOBB.",
    "..OOOOOOOSOOBBB.",
    "...OOSOOOOOO.B..",
    "....OOOOSOOBB...",
    "......OOOOBBB...",
    "..........BB....",
    "................",
    "................",
    "................",
]
SUSHI = [
    "................",
    "................",
    "................",
    "................",
    "....OOOOOOOO....",
    "..OOWOOWOOWOOO..",
    ".OOOOOOOOOOOOOO.",
    ".rOOOOOOOOOOOOr.",
    ".WWWWWWWWWWWWWW.",
    ".WWLWWWWLWWWWLW.",
    ".WWWWWWWWWWWWWW.",
    ".LWWWLWWWWWLWWL.",
    "..LLLLLLLLLLLL..",
    "................",
    "................",
    "................",
]
SARDINA = [
    "................",
    "................",
    "................",
    "................",
    "..........U.....",
    ".U....UUUUUUU...",
    ".UU.UULLLLLLLUU.",
    "..UULLLLLLLWKLU.",
    "..UULWWWWWWWWLU.",
    ".UU.UUWWWWWWUU..",
    ".U.....UUUUU....",
    "................",
    "................",
    "................",
    "................",
    "................",
]
LECHE = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "..UUUUUUUUUUUU..",
    ".UWWWWWWWWWWWWU.",
    ".UWWWWWWWWWWWWU.",
    ".UUWWWWWWWWWWUU.",
    "..UUUUUUUUUUUU..",
    "...UuuuuuuuuU...",
    "....UUUUUUUU....",
    "................",
    "................",
    "................",
]
# ---------------- ASPIRADORA (16x16), facing right ----------------
ASP1 = [
    "................",
    "....KKK.........",
    "...K...K........",
    "...K....K.......",
    "...K.....KRRRR..",
    "..KKK...RROOOORR",
    "..KDK..RROOOOOOR",
    "...K..RRWKOOWKOR",
    "...K..ROOKOOOKOR",
    "...KKKROOOOOOOOR",
    "......ROKKKKKKOR",
    "......RRRRRRRRRR",
    "......rrrrrrrrrr",
    ".......KK....KK.",
    "......KDDK..KDDK",
    ".......KK....KK.",
]
ASP2 = [
    "................",
    "...KKK..........",
    "..K...K.........",
    "..K....K........",
    "..K.....KRRRR...",
    ".KKK...KRROOOORR",
    ".KDK..RROOOOOOOR",
    "..K..RRWKOOOWKOR",
    "..K..ROOKOOOOKOR",
    "..KKKROOOOOOOOOR",
    ".....ROOKKKKKOOR",
    ".....RRRRRRRRRRR",
    ".....rrrrrrrrrrr",
    "......KK.....KK.",
    ".....KDDK...KDDK",
    "......KK.....KK.",
]
# ---------------- LAVADORA (32x32 boss) ----------------
LAV1 = [
    "................................",
    "..LLLLLLLLLLLLLLLLLLLLLLLLLLLL..",
    ".LWWWWWWWWWWWWWWWWWWWWWWWWWWWWL.",
    ".LWWRWWWYWWWKKKKKKKKKKKWWUUWWWL.",
    ".LWWWWWWWWWWKuuuuuuuuuKWWUUWWWL.",
    ".LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL.",
    ".LWWWWWWWWWWWWWWWWWWWWWWWWWWWWL.",
    ".LWWWWWWWWWLLLLLLLLLLWWWWWWWWWL.",
    ".LWWWWWWWLLDDDDDDDDDDLLWWWWWWWL.",
    ".LWWWWWWLDDUUUUUUUUUUDDLWWWWWWL.",
    ".LWWWWWLDDUUuuuuuuuuUUDDLWWWWWL.",
    ".LWWWWWLDUUuuuuuuuuuuUUDLWWWWWL.",
    ".LWWWWLDUUWWWuuuuuuWWWUUDLWWWWL.",
    ".LWWWWLDUWWKWWuuuuWWKWWUDLWWWWL.",
    ".LWWWWLDUWKKKWuuuuWKKKWUDLWWWWL.",
    ".LWWWWLDUUWWWuuuuuuWWWUUDLWWWWL.",
    ".LWWWWLDUUuuuuuuuuuuuuUUDLWWWWL.",
    ".LWWWWLDUUuuKKKKKKKKuuUUDLWWWWL.",
    ".LWWWWLDUUuKRRRRRRRRKuUUDLWWWWL.",
    ".LWWWWLDUUuKWRWRWRWRKuUUDLWWWWL.",
    ".LWWWWWLDUUuKKKKKKKKuUUDLWWWWWL.",
    ".LWWWWWLDDUUuuuuuuuuUUDDLWWWWWL.",
    ".LWWWWWWLDDUUUUUUUUUUDDLWWWWWWL.",
    ".LWWWWWWWLLDDDDDDDDDDLLWWWWWWWL.",
    ".LWWWWWWWWWLLLLLLLLLLWWWWWWWWWL.",
    ".LWWWWWWWWWWWWWWWWWWWWWWWWWWWWL.",
    ".LWWWWWWWWWWWWWWWWWWWWWWWWWWWWL.",
    ".LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL.",
    ".DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD.",
    "..KKKK....................KKKK..",
    "..KDDK....................KDDK..",
    "..KKKK....................KKKK..",
]

def _lav2():
    # frame 2: angry eyes + mouth open wider, body bobbed
    rows = list(LAV1)
    rows[13] = ".LWWWWLDUWKKWWuuuuWWKKWUDLWWWWL."
    rows[14] = ".LWWWWLDUWKKKWuuuuWKKKWUDLWWWWL."
    rows[17] = ".LWWWWLDUUuKKKKKKKKKKuUUDLWWWWL."
    rows[18] = ".LWWWWLDUUuKRRRRRRRRKuUUDLWWWWL."
    rows[19] = ".LWWWWLDUUuKRRRRRRRRKuUUDLWWWWL."
    rows[20] = ".LWWWWWLDUUuKWRWRWRWKuUDLWWWWWL."
    rows[3] = ".LWWYWWWRWWWKKKKKKKKKKKWWUUWWWL."
    return rows
LAV2 = _lav2()
LAV_HIT = [r.replace('W', 'P').replace('u', 'R') for r in LAV1]

# heart / willow face small icons (8x8) for HUD come from BG tiles.
