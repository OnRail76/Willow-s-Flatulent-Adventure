import sys, random
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import *
S = syms()
P = S['player']; EN = S['enemies']
def ent(m, base):
    r = m.ram; o = base - 0xC000
    return dict(type=r[o], state=r[o+1], x=r[o+3], y=r[o+5], tufo=r[o+13], dir=r[o+10], w=r[o+22])
def rd(m, name, n=1):
    o = S[name]-0xC000
    return m.ram[o] if n == 1 else bytes(m.ram[o:o+n])
class Bot:
    def __init__(s): s.t = 0; s.rnd = random.Random(1)
    def __call__(s, m):
        s.t += 1
        p = ent(m, P)
        es = [ent(m, EN + 32*i) for i in range(8)]
        es = [e for e in es if e['type'] and e['state'] != 3]
        pad = 0
        if not es: return RIGHT if (s.t//60)%2 else LEFT
        # target: closest
        def dist(e): return abs(e['x']-p['x']) + 2*abs(e['y']-p['y'])
        e = min(es, key=dist)
        dx = e['x'] - p['x']; dy = e['y'] - p['y']
        if abs(dy) < 14 and e['type'] in (1,2) and e['state'] in (0,1):
            # face AWAY from enemy (gas comes out of the rear) and fart
            want_dir = 1 if dx > 0 else 0
            if abs(dx) < 20:
                pad |= LEFT if dx > 0 else RIGHT    # back off
            elif p['dir'] != want_dir:
                pad |= LEFT if want_dir else RIGHT
            if s.t % 6 == 0: pad |= B1
        else:
            pad |= RIGHT if dx > 0 else LEFT
            if dy < -10 and s.t % 20 < 3: pad |= B2
        return pad
