#!/usr/bin/env python3
"""Original music + SFX for Willow's Flatulent Adventure -> build/sound.inc
Music stream bytes:
  n (1..63)  note index, followed by duration (in 16ths)
  0          rest, followed by duration
  $F0 v      volume (attenuation 0..15)
  $F1 e      envelope (0 hold, 1 slow decay, 2 staccato)
  $F2        next note is a "miau" (pitch bend up then down)
  $FF        loop to start
  $FE        end of stream (stop)
Drum stream bytes: drum (0 rest,1 kick,2 snare,3 hat,4 crash) + duration
"""
import os
CLOCK = 3579545
BASE_MIDI = 44   # note index 1 = MIDI 45 (A2, lowest the PSG can do)
NAMES = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def midi(n):
    o = int(n[-1]); p = n[:-1]
    return 12 * (o + 1) + NAMES[p]


def note_idx(n):
    i = midi(n) - BASE_MIDI
    assert 1 <= i <= 63, n
    return i


def period_table():
    out = []
    for i in range(64):
        if i == 0:
            out.append(0); continue
        f = 440 * 2 ** ((i + BASE_MIDI - 69) / 12)
        p = round(CLOCK / (32 * f))
        assert p <= 1023, (i, p)
        out.append(p)
    return out


def seq(text, vol=None, env=None):
    """text: 'G4:2 B4:2 r:4 ~D5:6 | ...'  ~ = miau"""
    b = []
    if vol is not None: b += [0xF0, vol]
    if env is not None: b += [0xF1, env]
    for tok in text.replace('|', ' ').split():
        if tok.startswith('v'):
            b += [0xF0, int(tok[1:])]; continue
        if tok.startswith('e'):
            b += [0xF1, int(tok[1:])]; continue
        n, d = tok.split(':')
        d = int(d)
        if n == 'r':
            b += [0, d]; continue
        if n.startswith('~'):
            b.append(0xF2); n = n[1:]
        b += [note_idx(n), d]
    return b


def bar_len(text):
    return sum(int(t.split(':')[1]) for t in text.replace('|', ' ').split() if ':' in t)


def bass_bar(root, pat=(0, 7, 12, 7, 0, 7, 12, 7)):
    r = midi(root)
    toks = []
    for k in pat:
        m = r + k
        name = [k for k, v in NAMES.items() if v == m % 12][0]
        toks.append('%s%d:2' % (name, m // 12 - 1))
    return ' '.join(toks)


def skank_bar(n1, n2):
    return 'r:2 %s:2 r:2 %s:2 r:2 %s:2 r:2 %s:2' % (n1, n2, n1, n2)


DRUM = {'r': 0, 'K': 1, 'S': 2, 'H': 3, 'C': 4}


def drums(text):
    b = []
    for tok in text.split():
        d, n = tok[0], int(tok[1:])
        b += [DRUM[d], n]
    return b


BEAT = 'K2 H2 S2 H2 K2 H2 S2 H2'
FILL = 'K2 H2 S2 H2 K2 S1 S1 S2 S2'
INTRO_D = 'C2 H2 S2 H2 K2 H2 S2 S2'

# ---------------- MAIN THEME "Gata con marcha" (A major, 180 bpm, low & bouncy) ----------------
# Hook: sneaky chromatic run (cat stalking) + bounce + "miau" bends at phrase ends.
melA = [
    'E4:1 F4:1 F#4:1 G#4:1 A4:2 C#5:2 r:1 B4:1 A4:2 ~E4:4',      # A
    'F#4:2 A4:2 r:1 F#4:1 C#5:2 B4:2 A4:2 F#4:4',                # F#m
    'D4:1 D#4:1 E4:2 F#4:2 A4:2 D5:3 C#5:1 B4:2 A4:2',           # D
    'G#4:2 B4:2 E5:2 r:2 ~E5:6 r:2',                             # E
    'E4:1 F4:1 F#4:1 G#4:1 A4:2 C#5:2 r:1 B4:1 A4:2 ~E4:4',      # A
    'F#4:2 A4:2 r:1 F#4:1 C#5:2 E5:2 D5:2 C#5:2 B4:2',           # F#m
    'A4:2 F#4:2 D4:2 F#4:2 G#4:2 B4:2 E4:2 G#4:2',               # D | E
    'A4:3 C#5:1 r:2 A4:2 ~A4:6 r:2',                             # A
]
melB = [
    'r:2 A3:2 D4:2 F#4:2 A4:3 G#4:1 A4:2 B4:2',                  # D
    'C#5:3 B4:1 G#4:2 E4:2 ~B4:6 r:2',                           # E
    'r:2 G#3:2 C#4:2 E4:2 G#4:3 F#4:1 G#4:2 A4:2',               # C#m
    'B4:3 A4:1 F#4:2 C#4:2 ~A4:6 r:2',                           # F#m
    'D5:2 C#5:2 B4:2 A4:2 F#4:2 A4:2 B4:2 D5:2',                 # D
    'E5:3 D5:1 C#5:2 B4:2 G#4:2 E4:2 F#4:2 G#4:2',               # E
    'A4:2 B4:2 C#5:2 D5:2 D#5:1 E5:3 r:2 E4:2',                  # Bm | E
    '~A4:10 r:6',                                                # A
]
melody = melA + melB
for b in melody:
    assert bar_len(b) == 16, b


def obass(root, walk=None):
    """driving octave bass in eighths; optional chromatic walk-up in last beat"""
    r = midi(root)
    seqn = [0, 12, 0, 12, 0, 12, 0, 12]
    if walk is not None:
        seqn[6:] = [walk - 2 - r, walk - 1 - r]
    toks = []
    for k in seqn:
        m = r + k
        name = [n for n, v in NAMES.items() if v == m % 12][0]
        toks.append('%s%d:2' % (name, m // 12 - 1))
    return ' '.join(toks)


def split_bass(r1, r2):
    a = obass(r1).split()[:4]
    b = obass(r2).split()[:4]
    return ' '.join(a + b)


bass = [
    obass('A2'), obass('F#3'), obass('D3'), obass('E3', midi('A2') + 12),
    obass('A2'), obass('F#3'), split_bass('D3', 'E3'), obass('A2', midi('D3')),
    obass('D3'), obass('E3'), obass('C#3'), obass('F#3', midi('D3') + 12),
    obass('D3'), obass('E3'), split_bass('B2', 'E3'), obass('A2', midi('A2') + 12),
]
# off-beat stabs, kept in the low-middle register
STAB = {'A': ('C#4', 'E4'), 'F#m': ('A3', 'C#4'), 'D': ('D4', 'F#4'), 'E': ('G#3', 'B3'),
        'C#m': ('G#3', 'E4'), 'Bm': ('B3', 'D4')}


def stab(c1, c2=None):
    if c2 is None:
        return skank_bar(*STAB[c1])
    a, b = STAB[c1], STAB[c2]
    return 'r:2 %s:2 r:2 %s:2 r:2 %s:2 r:2 %s:2' % (a[0], a[1], b[0], b[1])


harm = [stab('A'), stab('F#m'), stab('D'), stab('E'), stab('A'), stab('F#m'), stab('D', 'E'), stab('A'),
        stab('D'), stab('E'), stab('C#m'), stab('F#m'), stab('D'), stab('E'), stab('Bm', 'E'), stab('A')]
GROOVE = 'K2 H1 H1 S2 H2 K1 K1 H2 S2 H2'
GFILL = 'K2 H1 H1 S2 H2 K1 K1 S1 S1 S1 S1 S2'
drum_bars = []
for i in range(16):
    drum_bars.append(GFILL if i % 4 == 3 else GROOVE)
drum_bars[0] = 'C2 H1 H1 S2 H2 K1 K1 H2 S2 H2'
drum_bars[8] = 'C2 H1 H1 S2 H2 K1 K1 H2 S2 H2'

MAIN = {
    'ch0': seq(' '.join(melody), vol=1, env=1) + [0xFF],
    'ch1': seq(' '.join(harm), vol=6, env=2) + [0xFF],
    'ch2': seq(' '.join(bass), vol=2, env=2) + [0xFF],
    'drum': drums(' '.join(drum_bars)) + [0xFF],
}

skank_notes = {'G': ('B4', 'D5'), 'E': ('G4', 'B4'), 'C': ('E4', 'G4'), 'D': ('F#4', 'A4'), 'A': ('C5', 'E4')}

STAB.update({'Am': ('A3', 'C4'), 'F': ('A3', 'C4'), 'G': ('B3', 'D4'), 'Dm': ('D4', 'F4')})

# ---------------- BOSS THEME "La Lavadora" (A minor, 180 bpm, low & menacing) ----------------
bm = [
    'A3:2 A3:1 A3:1 C4:2 A3:2 D#4:1 E4:3 C4:2 A3:2',      # Am
    'F4:2 E4:2 D#4:1 E4:1 C4:2 A3:4 r:4',                 # F
    'G3:2 B3:2 D4:2 G4:2 F#4:1 G4:1 F4:2 D4:4',           # G
    'G#3:2 B3:2 E4:2 G#4:2 ~B4:6 r:2',                    # E
    'A3:2 A3:1 A3:1 C4:2 A3:2 D#4:1 E4:3 C4:2 A3:2',      # Am
    'F4:2 A4:2 C5:2 A4:2 G#4:1 A4:1 F4:2 C4:4',           # F
    'D4:2 F4:2 A4:2 D4:2 E4:2 G#4:2 B4:2 D5:2',           # Dm | E
    'C5:2 B4:1 A#4:1 A4:2 E4:2 ~A4:6 r:2',                # Am
]
for x in bm:
    assert bar_len(x) == 16, x
bbass = [obass('A2'), obass('F3'), obass('G3'), obass('E3', midi('A2') + 12),
         obass('A2'), obass('F3'), split_bass('D3', 'E3'), obass('A2', midi('A2') + 12)]
bharm = [stab('Am'), stab('F'), stab('G'), stab('E'), stab('Am'), stab('F'), stab('Dm', 'E'), stab('Am')]
BGROOVE = 'K1 K1 H2 S2 H2 K1 K1 H1 H1 S2 S2'
BOSS = {
    'ch0': seq(' '.join(bm), vol=1, env=1) + [0xFF],
    'ch1': seq(' '.join(bharm), vol=7, env=2) + [0xFF],
    'ch2': seq(' '.join(bbass), vol=2, env=2) + [0xFF],
    'drum': drums(' '.join([BGROOVE] * 7 + [GFILL])) + [0xFF],
}

# ---------------- TITLE "Gata al sol" (A major, 150 bpm, laid-back version of the hook) ----------------
tm = [
    'E4:1 F4:1 F#4:1 G#4:1 A4:4 C#5:2 B4:2 ~A4:4',        # A
    'r:2 F#4:2 A4:2 C#5:2 B4:4 A4:4',                     # F#m
    'D4:1 D#4:1 E4:2 F#4:4 A4:2 B4:2 D5:4',               # D
    'C#5:2 B4:2 G#4:2 E4:2 ~B4:8',                        # E
    'E4:1 F4:1 F#4:1 G#4:1 A4:4 C#5:2 B4:2 ~A4:4',        # A
    'r:2 F#4:2 A4:2 C#5:2 E5:4 D5:2 C#5:2',               # F#m
    'B4:4 A4:2 F#4:2 G#4:4 B4:2 D5:2',                    # D | E
    '~A4:12 r:4',                                         # A
]
for x in tm:
    assert bar_len(x) == 16, x
BOUNCE = (0, 12, 7, 12, 0, 12, 7, 12)
tbass = [bass_bar(r, BOUNCE) for r in ['A2', 'F#3', 'D3', 'E3', 'A2', 'F#3']] + \
        [split_bass('D3', 'E3'), bass_bar('A2', BOUNCE)]
TITLE = {
    'ch0': seq(' '.join(tm), vol=1, env=1) + [0xFF],
    'ch1': seq(' '.join([stab('A'), stab('F#m'), stab('D'), stab('E'), stab('A'), stab('F#m'),
                         stab('D', 'E'), stab('A')]), vol=7, env=2) + [0xFF],
    'ch2': seq(' '.join(tbass), vol=2, env=2) + [0xFF],
    'drum': drums(' '.join(['K2 H2 S2 H1 H1 K2 H2 S2 H2'] * 7 + ['K2 H2 S2 H2 K2 S1 S1 S2 S2'])) + [0xFF],
}

# ---------------- JINGLES (same sneaky-run + miau language) ----------------
READY = {   # "¡Preparada!"
    'ch0': seq('E4:1 F4:1 F#4:1 G#4:1 A4:2 C#5:2 E5:2 r:2 ~A4:8', vol=1, env=1) + [0xFE],
    'ch1': seq('r:4 C#4:2 E4:2 A4:2 r:2 E4:8', vol=5, env=1) + [0xFE],
    'ch2': seq('A2:2 r:2 A3:2 r:2 A2:2 A3:2 E3:2 r:2 A2:8', vol=2, env=1) + [0xFE],
    'drum': drums('K1 K1 K1 K1 S2 S2 K2 r2 C8') + [0xFE],
}
CLEAR = {
    'ch0': seq('A4:2 C#5:2 E5:2 C#5:1 B4:1 A4:2 r:2 D4:1 D#4:1 E4:2 G#4:2 ~A4:8', vol=1, env=1) + [0xFE],
    'ch1': seq('C#4:2 E4:2 A4:2 E4:1 D4:1 C#4:2 r:2 B3:1 B3:1 B3:2 D4:2 C#4:8', vol=5, env=1) + [0xFE],
    'ch2': seq('A2:2 A3:2 A2:2 A3:2 A2:2 r:2 E3:2 E3:2 E3:2 A2:8', vol=2, env=1) + [0xFE],
    'drum': drums('K2 H2 S2 H2 K2 r2 S1 S1 S1 S1 S2 C8') + [0xFE],
}
DEATH = {   # sad sliding meows going down
    'ch0': seq('~E4:4 D#4:2 ~D4:4 C#4:2 ~C4:6 ~A3:10', vol=1, env=1) + [0xFE],
    'ch1': seq('C4:4 B3:2 A#3:4 A3:2 G#3:6 E3:10', vol=6, env=1) + [0xFE],
    'ch2': seq('A2:6 r:6 F3:6 E3:4 A2:6', vol=3, env=1) + [0xFE],
    'drum': [0, 28, 0xFE],
}
OVER = {
    'ch0': seq('A4:4 G#4:4 G4:4 ~F#4:12 r:4 F4:2 E4:2 D#4:2 ~E4:12', vol=1, env=1) + [0xFE],
    'ch1': seq('C#4:4 C4:4 B3:4 A3:12 r:4 D4:2 C4:2 B3:2 G#3:12', vol=6, env=1) + [0xFE],
    'ch2': seq('A2:12 D3:12 r:4 E3:6 A2:12', vol=3, env=1) + [0xFE],
    'drum': drums('r12 K12 r4 S2 S2 S2 C12') + [0xFE],
}
ENDING = {
    'ch0': seq(' '.join(melA[:7] + ['A4:3 C#5:1 E5:2 A4:2 ~A4:8']), vol=1, env=1) + [0xFE],
    'ch1': seq(' '.join(harm[:8]), vol=6, env=2) + [0xFE],
    'ch2': seq(' '.join(bass[:7] + [obass('A2')]), vol=2, env=2) + [0xFE],
    'drum': drums(' '.join([GROOVE] * 3 + [GFILL] + [GROOVE] * 3 + ['C16'])) + [0xFE],
}

TEMPO = {'MUS_MAIN': 5, 'MUS_BOSS': 5, 'MUS_TITLE': 6, 'MUS_READY': 5, 'MUS_CLEAR': 5,
         'MUS_DEATH': 6, 'MUS_OVER': 7, 'MUS_ENDING': 6}
SONGS = [('MUS_MAIN', MAIN), ('MUS_BOSS', BOSS), ('MUS_TITLE', TITLE), ('MUS_READY', READY),
         ('MUS_CLEAR', CLEAR), ('MUS_DEATH', DEATH), ('MUS_OVER', OVER), ('MUS_ENDING', ENDING)]

# ---------------- SFX (per frame: dw period, db vol2, db noisectl, db noisevol) ----------------
import random
random.seed(7)


def sfx_fart(n=30, base=640, spread=380, loud=0):
    """loud, rasping 'prrrrt': square buzz (tone 2) + white noise clocked by tone 2.
    Even/odd frame flutter gives the rippling; pitch drops (period rises) towards the end."""
    f = []
    for i in range(n):
        p = base + int(spread * (i / n) ** 1.5) + random.randint(-70, 70)
        fade = max(0, i - (n - 7)) * 2
        if i < 2:                     # 'pff' attack: noise only
            f.append((min(1023, p), 15, 7, 0))
            continue
        v2 = min(15, (0 if i % 2 == 0 else 3) + loud + fade)
        nv = min(15, (0 if i % 2 == 0 else 2) + loud + fade)
        f.append((min(1023, p), v2, 7, nv))
    return f


def sfx_sweep(p0, p1, n, v0=2, v1=12, nctl=None, nv=15):
    f = []
    for i in range(n):
        p = int(p0 + (p1 - p0) * i / max(1, n - 1))
        v = int(v0 + (v1 - v0) * i / max(1, n - 1))
        f.append((p, v, nctl if nctl is not None else 0xFF, nv))
    return f


def sfx_noise(n, ctl, v0, v1):
    return [(0, 15, ctl, int(v0 + (v1 - v0) * i / max(1, n - 1))) for i in range(n)]


SFX = [
    ('SFX_FART', sfx_fart()),
    ('SFX_BIGFART', sfx_fart(44, 760, 260, 0)),
    ('SFX_JUMP', sfx_sweep(380, 170, 10, 4, 12)),
    ('SFX_GAS', sfx_sweep(300, 450, 6, 6, 13) + sfx_noise(6, 4, 6, 14)),
    ('SFX_KICK', sfx_noise(3, 4, 2, 6) + sfx_sweep(500, 120, 10, 3, 12)),
    ('SFX_POP', sfx_sweep(140, 60, 8, 2, 9) + sfx_sweep(90, 40, 8, 4, 13)),
    ('SFX_FOOD', sfx_sweep(254, 254, 3, 3, 4) + sfx_sweep(190, 190, 3, 3, 4) + sfx_sweep(127, 127, 6, 3, 12)),
    ('SFX_POWER', sum([sfx_sweep(300 - 40 * k, 200 - 30 * k, 4, 3, 7) for k in range(5)], [])),
    ('SFX_BOUNCE', sfx_sweep(700, 900, 4, 4, 12)),
    ('SFX_BOSSHIT', sfx_noise(4, 4, 0, 4) + sfx_sweep(900, 1000, 14, 2, 14, 7, 6)),
    ('SFX_EXTEND', sum([sfx_sweep(p, p, 4, 2, 6) for p in (254, 213, 190, 160, 127, 107, 95)], [])),
    ('SFX_HURRY', sum([sfx_sweep(150, 150, 6, 2, 4) + sfx_sweep(200, 200, 6, 2, 4) for k in range(3)], [])),
    ('SFX_CLANG', sfx_sweep(60, 64, 12, 3, 15, 4, 8)),
    ('SFX_SELECT', sfx_sweep(150, 150, 5, 3, 12)),
]

per = period_table()
out = ['; generated by music.py - do not edit', 'note_periods:']
out.append(' dw ' + ','.join(str(p) for p in per))
for name, song in SONGS:
    out.append('%s_data:' % name.lower())
    out.append(' dw %s_c0, %s_c1, %s_c2, %s_d' % ((name.lower(),) * 4))
    for key, lab in (('ch0', 'c0'), ('ch1', 'c1'), ('ch2', 'c2'), ('drum', 'd')):
        out.append('%s_%s:' % (name.lower(), lab))
        data = song[key]
        for i in range(0, len(data), 24):
            out.append(' db ' + ','.join(str(x) for x in data[i:i + 24]))
for i, (name, _) in enumerate(SONGS):
    out.append('%s equ %d' % (name, i))
out.append('song_tempo:')
out.append(' db ' + ','.join(str(TEMPO[n]) for n, _ in SONGS))
out.append('song_table:')
out.append(' dw ' + ','.join('%s_data' % n.lower() for n, _ in SONGS))
for i, (name, frames) in enumerate(SFX):
    out.append('%s equ %d' % (name, i + 1))
out.append('sfx_table:')
out.append(' dw ' + ','.join('%s_data' % n.lower() for n, _ in SFX))
for name, frames in SFX:
    out.append('%s_data:' % name.lower())
    for (p, v2, nc, nv) in frames:
        out.append(' dw %d\n db %d,%d,%d' % (p, v2, nc, nv))
    out.append(' dw $FFFF')
open(os.path.join(os.path.dirname(__file__), '..', 'build', 'sound.inc'), 'w').write('\n'.join(out) + '\n')
tot = sum(len(s[k]) for _, s in SONGS for k in s) + sum(len(f) * 5 + 2 for _, f in SFX)
print('sound data bytes ~', tot)
