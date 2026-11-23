# Background art: font, HUD icons, room tilesets.
# BG palette: 0 black,1 white,2 yellow,3 grey,4 green,5 red, 6..15 room colours (a..j)
BG_CHARS = {'k': 0, 'w': 1, 'y': 2, 'l': 3, 'g': 4, 'r': 5,
            'a': 6, 'b': 7, 'c': 8, 'd': 9, 'e': 10, 'f': 11, 'h': 12, 'i': 13, 'j': 14, 'm': 15,
            '.': 0, '#': 1}
BG_FIXED = [(0, 0, 0), (3, 3, 3), (3, 3, 0), (2, 2, 2), (1, 3, 0), (3, 0, 0)]

FONT_ORDER = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!?.,:-'/()¡©+=%Ñ"
FONT = {
' ': ["........"] * 8,
'0': ["..####..", ".##..##.", ".##.###.", ".###.##.", ".##..##.", ".##..##.", "..####..", "........"],
'1': ["...##...", "..###...", "...##...", "...##...", "...##...", "...##...", ".######.", "........"],
'2': ["..####..", ".##..##.", ".....##.", "....##..", "...##...", "..##....", ".######.", "........"],
'3': ["..####..", ".##..##.", ".....##.", "...###..", ".....##.", ".##..##.", "..####..", "........"],
'4': ["....##..", "...###..", "..####..", ".##.##..", ".######.", "....##..", "....##..", "........"],
'5': [".######.", ".##.....", ".#####..", ".....##.", ".....##.", ".##..##.", "..####..", "........"],
'6': ["..####..", ".##.....", ".#####..", ".##..##.", ".##..##.", ".##..##.", "..####..", "........"],
'7': [".######.", ".....##.", "....##..", "...##...", "..##....", "..##....", "..##....", "........"],
'8': ["..####..", ".##..##.", ".##..##.", "..####..", ".##..##.", ".##..##.", "..####..", "........"],
'9': ["..####..", ".##..##.", ".##..##.", "..#####.", ".....##.", "....##..", "..###...", "........"],
'A': ["...##...", "..####..", ".##..##.", ".##..##.", ".######.", ".##..##.", ".##..##.", "........"],
'B': [".#####..", ".##..##.", ".##..##.", ".#####..", ".##..##.", ".##..##.", ".#####..", "........"],
'C': ["..####..", ".##..##.", ".##.....", ".##.....", ".##.....", ".##..##.", "..####..", "........"],
'D': [".####...", ".##.##..", ".##..##.", ".##..##.", ".##..##.", ".##.##..", ".####...", "........"],
'E': [".######.", ".##.....", ".##.....", ".#####..", ".##.....", ".##.....", ".######.", "........"],
'F': [".######.", ".##.....", ".##.....", ".#####..", ".##.....", ".##.....", ".##.....", "........"],
'G': ["..####..", ".##..##.", ".##.....", ".##.###.", ".##..##.", ".##..##.", "..#####.", "........"],
'H': [".##..##.", ".##..##.", ".##..##.", ".######.", ".##..##.", ".##..##.", ".##..##.", "........"],
'I': [".######.", "...##...", "...##...", "...##...", "...##...", "...##...", ".######.", "........"],
'J': ["....###.", ".....##.", ".....##.", ".....##.", ".##..##.", ".##..##.", "..####..", "........"],
'K': [".##..##.", ".##.##..", ".####...", ".###....", ".####...", ".##.##..", ".##..##.", "........"],
'L': [".##.....", ".##.....", ".##.....", ".##.....", ".##.....", ".##.....", ".######.", "........"],
'M': [".##...##", ".###.###", ".#######", ".##.#.##", ".##...##", ".##...##", ".##...##", "........"],
'N': [".##..##.", ".###.##.", ".######.", ".######.", ".##.###.", ".##..##.", ".##..##.", "........"],
'O': ["..####..", ".##..##.", ".##..##.", ".##..##.", ".##..##.", ".##..##.", "..####..", "........"],
'P': [".#####..", ".##..##.", ".##..##.", ".#####..", ".##.....", ".##.....", ".##.....", "........"],
'Q': ["..####..", ".##..##.", ".##..##.", ".##..##.", ".##.###.", ".##.##..", "..##.##.", "........"],
'R': [".#####..", ".##..##.", ".##..##.", ".#####..", ".####...", ".##.##..", ".##..##.", "........"],
'S': ["..####..", ".##..##.", ".##.....", "..####..", ".....##.", ".##..##.", "..####..", "........"],
'T': [".######.", "...##...", "...##...", "...##...", "...##...", "...##...", "...##...", "........"],
'U': [".##..##.", ".##..##.", ".##..##.", ".##..##.", ".##..##.", ".##..##.", "..####..", "........"],
'V': [".##..##.", ".##..##.", ".##..##.", ".##..##.", ".##..##.", "..####..", "...##...", "........"],
'W': [".##...##", ".##...##", ".##...##", ".##.#.##", ".#######", ".###.###", ".##...##", "........"],
'X': [".##..##.", ".##..##.", "..####..", "...##...", "..####..", ".##..##.", ".##..##.", "........"],
'Y': [".##..##.", ".##..##.", ".##..##.", "..####..", "...##...", "...##...", "...##...", "........"],
'Z': [".######.", ".....##.", "....##..", "...##...", "..##....", ".##.....", ".######.", "........"],
'!': ["...##...", "...##...", "...##...", "...##...", "...##...", "........", "...##...", "........"],
'?': ["..####..", ".##..##.", ".....##.", "....##..", "...##...", "........", "...##...", "........"],
'.': ["........", "........", "........", "........", "........", "...##...", "...##...", "........"],
',': ["........", "........", "........", "........", "........", "...##...", "...##...", "..##...."],
':': ["........", "...##...", "...##...", "........", "...##...", "...##...", "........", "........"],
'-': ["........", "........", "........", ".######.", "........", "........", "........", "........"],
"'": ["...##...", "...##...", "..##....", "........", "........", "........", "........", "........"],
'/': [".....##.", "....##..", "....##..", "...##...", "..##....", "..##....", ".##.....", "........"],
'(': ["....##..", "...##...", "..##....", "..##....", "..##....", "...##...", "....##..", "........"],
')': ["..##....", "...##...", "....##..", "....##..", "....##..", "...##...", "..##....", "........"],
'¡': ["...##...", "........", "...##...", "...##...", "...##...", "...##...", "...##...", "........"],
'©': ["..####..", ".#....#.", "#..##..#", "#.#....#", "#.#....#", "#..##..#", ".#....#.", "..####.."],
'+': ["........", "...##...", "...##...", ".######.", "...##...", "...##...", "........", "........"],
'=': ["........", "........", ".######.", "........", ".######.", "........", "........", "........"],
'Ñ': ["..##.#..", ".#.##...", ".##..##.", ".###.##.", ".######.", ".##.###.", ".##..##.", "........"],
'%': [".##...#.", ".##..#..", "....#...", "...#....", "..#..##.", ".#...##.", "........", "........"],
}

# HUD / misc BG tiles (fixed palette 0-5)
HUD_TILES = {
    'LIFE': ["........", ".w...w..", ".ww.ww..", ".lllll..", ".lylyl..", ".lllll..", "..www...", "........"],
    'HEART': ["........", ".rr.rr..", "rrrrrrr.", "rrrrrrr.", ".rrrrr..", "..rrr...", "...r....", "........"],
    'I_ATUN': ["........", ".llllll.", ".wwwwww.", ".llwlll.", ".lllwll.", ".wwwwww.", ".llllll.", "........"],
    'I_PIENSO': ["........", ".rrrrrr.", ".ryyyyr.", ".ryllyr.", ".ryllyr.", ".ryyyyr.", ".rrrrrr.", "........"],
    'I_GALLETA': ["........", "........", "..yyyy.y", ".yykyyyy", ".yyyyyyy", "..yyyy.y", "........", "........"],
    'BAR_E': ["........", "llllllll", "k.k.k.k.", "........", "........", "k.k.k.k.", "llllllll", "........"],
    'BAR_F': ["........", "llllllll", "rrrrrrrr", "rrrrrrrr", "rrrrrrrr", "rrrrrrrr", "llllllll", "........"],
    'BAR_G': ["........", "llllllll", "gggggggg", "gggggggg", "gggggggg", "gggggggg", "llllllll", "........"],
    'SOLID_K': ["kkkkkkkk"] * 8,
}

# ---------------- room tilesets ----------------
# each room: colours a..j (10 entries, rgb 0..3) and tiles
ROOMS = []

# 1. EL DORMITORIO - night blue wallpaper, wooden shelves/bed
ROOMS.append({
    'name': 'DORMITORIO',
    'colors': [(0, 0, 1), (0, 1, 2), (1, 2, 3), (2, 1, 0), (1, 0, 0), (3, 2, 1), (3, 3, 2), (0, 0, 2), (2, 0, 1), (3, 1, 2)],
    #          a dkblue   b blue     c ltblue   d brown    e dkbrown  f tan      h cream    i navy     j plum     m pink
    'WALLA': ["aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaabaa", "aaaaaaaa", "aaaaaaaa"],
    'WALLB': ["aaaaaaaa", "aaaaaaaa", "aabaaaaa", "abcbaaaa", "aabaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa"],
    'FLOOR': ["ffffffff", "dddddddd", "dddedddd", "dddedddd", "eeeeeeee", "ddddddde", "ddddddde", "eeeeeeee"],
    'SIDE':  ["deeeeeed", "dffffffd", "dfddddfd", "dfddddfd", "dfddddfd", "dfddddfd", "dffffffd", "deeeeeed"],
    'PL':    [".fffffff", "fddddddd", "fddddddd", "eeeeeeee", ".e......", ".e......", "........", "........"],
    'PM':    ["ffffffff", "dddddddd", "dddddddd", "eeeeeeee", "........", "........", "........", "........"],
    'PR':    ["fffffff.", "ddddddde", "ddddddde", "eeeeeeee", "......e.", "......e.", "........", "........"],
    # deco: window with moon (2x2)
    'D0': ["eeeeeeee", "eiiiiiii", "eiiiiiii", "eiiihhii", "eiihhiii", "eiihhiii", "eiiihhii", "eiiiiiii"],
    'D1': ["eeeeeeee", "iiiiiiie", "iiiiiiie", "iiiiiiie", "iiiiwiie", "iiiiiiie", "iiiiiiie", "iiiiiiie"],
    'D2': ["eeeeeeee", "eiiiiiii", "eiiiiiii", "eiiiwiii", "eiiiiiii", "eiiiiiii", "eiiiiiii", "eeeeeeee"],
    'D3': ["eeeeeeee", "iiiiiiie", "iiiiiiie", "iiiiiiie", "iiiiiiie", "iwiiiiie", "iiiiiiie", "eeeeeeee"],
    # deco: framed fish picture (2x2)
    'D4': ["ffffffff", "fhhhhhhh", "fhhhhhhh", "fhhhcccc", "fhhcccbc", "fhhhcccc", "fhhhhhhh", "fhhhhhhh"],
    'D5': ["ffffffff", "hhhhhhhf", "hhhhhhhf", "hhchhhhf", "cccchhhf", "hhchhhhf", "hhhhhhhf", "hhhhhhhf"],
    'D6': ["fhhhhhhh", "fhhhhhhh", "fhhhhhhh", "fhhhhhhh", "fhhhhhhh", "fhhhhhhh", "fhhhhhhh", "ffffffff"],
    'D7': ["hhhhhhhf", "hhhhhhhf", "hhhhhhhf", "hhhhhhhf", "hhhhhhhf", "hhhhhhhf", "hhhhhhhf", "ffffffff"],
})

# 2. EL COMEDOR - brown & gold striped wallpaper, table-top platforms
ROOMS.append({
    'name': 'COMEDOR',
    'colors': [(1, 0, 0), (2, 1, 0), (3, 2, 0), (2, 1, 1), (1, 1, 0), (3, 3, 1), (3, 2, 1), (0, 0, 0), (1, 1, 1), (2, 2, 2)],
    #          a dkbrown  b brown    c gold     d wine     e olive    f ltyel    h tan      i black    j dgrey    m grey
    'WALLA': ["abaaabaa", "abaaabaa", "abaacbaa", "abaaabaa", "abaaabaa", "abaaabaa", "abaaabaa", "abaaabaa"],
    'WALLB': ["abaaabaa", "abaaabaa", "abaaabaa", "abaaabaa", "abaaabaa", "abacabaa", "abaaabaa", "abaaabaa"],
    'FLOOR': ["hhhhhhhh", "bbcbbbbc", "bcbbbbcb", "cbbbbcbb", "bbbbcbbb", "bbbcbbbb", "bbcbbbbb", "aaaaaaaa"],
    'SIDE':  ["cbbbbbba", "cbbbbbba", "cbbbbbba", "cccccccc", "bbbabbbb", "bbbabbbb", "bbbabbbb", "aaaaaaaa"],
    'PL':    [".ccccccc", "cfffffff", "cbbbbbbb", "aaaaaaaa", ".a......", ".a......", "........", "........"],
    'PM':    ["cccccccc", "ffffffff", "bbbbbbbb", "aaaaaaaa", "........", "........", "........", "........"],
    'PR':    ["ccccccc.", "fffffffc", "bbbbbbba", "aaaaaaaa", "......a.", "......a.", "........", "........"],
    # clock (2x2)
    'D0': ["....cccc", "..ccffff", ".cffffff", ".cfffiff", "cffffiff", "cffffiff", "cffffiii", "cfffffff"],
    'D1': ["cccc....", "ffffcc..", "ffffffc.", "ffffffc.", "fffffffc", "fffffffc", "fffffffc", "fffffffc"],
    'D2': ["cfffffff", "cfffffff", ".cffffff", ".cffffff", "..ccffff", "....cccc", "......aa", "......aa"],
    'D3': ["fffffffc", "fffffffc", "ffffffc.", "ffffffc.", "ffffcc..", "cccc....", "aa......", "aa......"],
    # painting of a fish bowl (2x2)
    'D4': ["cccccccc", "cjjjjjjj", "cjjjjjjj", "cjjjmmmm", "cjjmhhhh", "cjmhhhhh", "cjmhhyhh", "cjmhhhhh"],
    'D5': ["cccccccc", "jjjjjjjc", "jjjjjjjc", "mmmmjjjc", "hhhhmjjc", "hhhhhmjc", "hhhhhmjc", "hhhhhmjc"],
    'D6': ["cjjmhhhh", "cjjjmmmm", "cjjjjjjj", "cjjjjjjj", "cjjjjjjj", "cjjjjjjj", "cjjjjjjj", "cccccccc"],
    'D7': ["hhhhmjjc", "mmmmjjjc", "jjjjjjjc", "jjjjjjjc", "jjjjjjjc", "jjjjjjjc", "jjjjjjjc", "cccccccc"],
})

# 3. LA COCINA - pale tiles, checkered floor, worktop platforms
ROOMS.append({
    'name': 'COCINA',
    'colors': [(3, 3, 2), (2, 2, 1), (0, 0, 0), (3, 3, 3), (1, 1, 1), (2, 2, 2), (0, 1, 2), (3, 1, 0), (2, 0, 0), (1, 2, 3)],
    #          a cream    b khaki    c black    d white    e dgrey    f grey     h steel    i orange   j dred     m skyblue
    'WALLA': ["aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "bbbbbbbb"],
    'WALLB': ["aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "bbbbbbbb"],
    'FLOOR': ["ddddcccc", "ddddcccc", "ddddcccc", "ddddcccc", "ccccdddd", "ccccdddd", "ccccdddd", "ccccdddd"],
    'SIDE':  ["ffffffff", "fddddddf", "fdhhhhdf", "fdhhhhdf", "fdhhhhdf", "fdhhhhdf", "fddddddf", "eeeeeeee"],
    'PL':    [".fffffff", "fddddddd", "ffffffff", "eeeeeeee", ".e......", ".e......", "........", "........"],
    'PM':    ["ffffffff", "dddddddd", "ffffffff", "eeeeeeee", "........", "........", "........", "........"],
    'PR':    ["fffffff.", "dddddddf", "ffffffff", "eeeeeeee", "......e.", "......e.", "........", "........"],
    # window with sky (2x2)
    'D0': ["ffffffff", "fmmmmmmm", "fmmmmmmm", "fmmmdmmm", "fmmddddm", "fmmmmmmm", "fmmmmmmm", "ffffffff"],
    'D1': ["ffffffff", "mmmmmmmf", "mmmmmmmf", "mmmmmmmf", "mmmmmmmf", "mmmmmmmf", "mmmmmmmf", "ffffffff"],
    'D2': ["fmmmmmmm", "fmmmmmmm", "fmmmmmmm", "fmmmmmmm", "fmmmmmmm", "ffffffff", "dddddddd", "eeeeeeee"],
    'D3': ["mmmmmmmf", "mmmmdmmf", "mmmddddf", "mmmmmmmf", "mmmmmmmf", "ffffffff", "dddddddd", "eeeeeeee"],
    # hanging pans (2x2)
    'D4': ["eeeeeeee", "...e....", "...e....", "..eee...", ".eiiie..", "eiiiiie.", "eiiiiie.", "eiiiiie."],
    'D5': ["eeeeeeee", "....e...", "....e...", "....e...", "...eee..", "..ehhhe.", ".ehhhhhe", ".ehhhhhe"],
    'D6': [".eiiie..", "..eee...", "........", "........", "........", "........", "........", "........"],
    'D7': [".ehhhhhe", "..ehhhe.", "...eee..", "........", "........", "........", "........", "........"],
})

# 4. EL BANO - aqua tiles, white shelves
ROOMS.append({
    'name': 'BANO',
    'colors': [(1, 3, 3), (0, 2, 2), (3, 3, 3), (0, 1, 1), (2, 3, 3), (1, 2, 2), (3, 3, 0), (3, 1, 0), (0, 1, 3), (2, 2, 2)],
    #          a aqua     b teal     c white    d dkteal   e paleaq   f midteal  h duck yel i beak     j blue     m grey
    'WALLA': ["aaaaaaab", "aeaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "bbbbbbbb"],
    'WALLB': ["aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaaab", "aaaaaeab", "aaaaaaab", "aaaaaaab", "bbbbbbbb"],
    'FLOOR': ["cccccccc", "cmcccccm", "cccccccc", "cccmcccc", "mmmmmmmm", "cccccccc", "cmccccmc", "mmmmmmmm"],
    'SIDE':  ["ffffffff", "fbbbbbbd", "fbbbbbbd", "fbbbbbbd", "fbbbbbbd", "fbbbbbbd", "fbbbbbbd", "dddddddd"],
    'PL':    [".ccccccc", "cccccccc", "mmmmmmmm", "dddddddd", ".d......", ".d......", "........", "........"],
    'PM':    ["cccccccc", "cccccccc", "mmmmmmmm", "dddddddd", "........", "........", "........", "........"],
    'PR':    ["ccccccc.", "cccccccc", "mmmmmmmm", "dddddddd", "......d.", "......d.", "........", "........"],
    # mirror (2x2)
    'D0': ["mmmmmmmm", "meeeeeee", "meceeeee", "meeceeee", "meeeceee", "meeeeeee", "meeeeeee", "meeeeeee"],
    'D1': ["mmmmmmmm", "eeeeeeem", "eeeeeeem", "eeeeeeem", "eeeeeeem", "eeeeeeem", "eeeceeem", "eeeeceem"],
    'D2': ["meeeeeee", "meeeeeee", "meeeeeee", "meeeeeee", "meeeeeee", "meeeeeee", "mmmmmmmm", "...mm..."],
    'D3': ["eeeeeeem", "eeeeeeem", "eeeeeeem", "eeeeeeem", "eeeeeeem", "eeeeeeem", "mmmmmmmm", "...mm..."],
    # rubber duck (2x2)
    'D4': ["aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaahh", "aaaaahhh", "aaaaahkh", "aaaaahhh", "aaaaaahh"],
    'D5': ["aaaaaaab", "aaaaaaab", "aaaaaaab", "haaaaaab", "hhaaaaab", "hiiaaaab", "hiiiaaab", "haaaaaab"],
    'D6': ["aahhaahh", "ahhhhhhh", "ahhhhhhh", "ahhhhhhh", "aahhhhhh", "aaahhhhh", "aaaaaaaa", "bbbbbbbb"],
    'D7': ["hhaaaaab", "hhhaaaab", "hhhhaaab", "hhhhaaab", "hhhaaaab", "hhaaaaab", "aaaaaaab", "bbbbbbbb"],
})
ROOM_TILE_NAMES = ['WALLA', 'WALLB', 'FLOOR', 'SIDE', 'PL', 'PM', 'PR', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
