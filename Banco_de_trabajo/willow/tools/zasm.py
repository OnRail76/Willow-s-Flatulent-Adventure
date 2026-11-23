#!/usr/bin/env python3
"""zasm.py - small two-pass Z80 assembler (Tony's SMS projects).

Syntax:
  label:            global label      .loop:   local label (scoped to last global)
  NAME equ expr / NAME = expr
  org expr          db/defb, dw/defw, ds/defs n[,fill], incbin "file", include "file"
  align n           rsset expr / NAME rb n / NAME rw n   (RAM variable layout)
  macro NAME / endm   (args \\1..\\9, \\@ unique counter)
  if expr / else / endif
  assert expr[, "msg"]
Numbers: 123, $FF, 0xFF, 0FFh, %1010, 0b1010, 'A'.  $ = current address.
Functions: lo(x) hi(x).
"""
import re, sys, os

R8 = {'b': 0, 'c': 1, 'd': 2, 'e': 3, 'h': 4, 'l': 5, '(hl)': 6, 'a': 7}
RP = {'bc': 0, 'de': 1, 'hl': 2, 'sp': 3}
RP2 = {'bc': 0, 'de': 1, 'hl': 2, 'af': 3}
CC = {'nz': 0, 'z': 1, 'nc': 2, 'c': 3, 'po': 4, 'pe': 5, 'p': 6, 'm': 7}
ALU = {'add': 0, 'adc': 1, 'sub': 2, 'sbc': 3, 'and': 4, 'xor': 5, 'or': 6, 'cp': 7}
ROT = {'rlc': 0, 'rrc': 1, 'rl': 2, 'rr': 3, 'sla': 4, 'sra': 5, 'sll': 6, 'srl': 7}
SIMPLE = {'nop': [0x00], 'rlca': [0x07], 'rrca': [0x0F], 'rla': [0x17], 'rra': [0x1F], 'daa': [0x27],
          'cpl': [0x2F], 'scf': [0x37], 'ccf': [0x3F], 'halt': [0x76], 'di': [0xF3], 'ei': [0xFB],
          'exx': [0xD9], 'neg': [0xED, 0x44], 'retn': [0xED, 0x45], 'reti': [0xED, 0x4D],
          'rrd': [0xED, 0x67], 'rld': [0xED, 0x6F],
          'ldi': [0xED, 0xA0], 'cpi': [0xED, 0xA1], 'ini': [0xED, 0xA2], 'outi': [0xED, 0xA3],
          'ldd': [0xED, 0xA8], 'cpd': [0xED, 0xA9], 'ind': [0xED, 0xAA], 'outd': [0xED, 0xAB],
          'ldir': [0xED, 0xB0], 'cpir': [0xED, 0xB1], 'inir': [0xED, 0xB2], 'otir': [0xED, 0xB3],
          'lddr': [0xED, 0xB8], 'cpdr': [0xED, 0xB9], 'indr': [0xED, 0xBA], 'otdr': [0xED, 0xBB]}


class AsmError(Exception):
    pass


def split_args(s):
    out, depth, cur, q = [], 0, '', None
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = None
            continue
        if ch in '"\'':
            # char literal 'x' or string
            q = ch; cur += ch; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def strip_comment(line):
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q:
                q = None
            continue
        if ch == '"':
            q = ch
        elif ch == "'":
            # af' handling: ex af,af'
            if line[max(0, i-2):i].lower() == 'af':
                continue
            q = ch
        elif ch == ';':
            return line[:i]
    return line


class Assembler:
    def __init__(self):
        self.syms = {}
        self.macros = {}
        self.listing = []

    # ---------- expressions ----------
    def ev(self, expr, need=True):
        e = expr.strip()
        if not e:
            raise AsmError('empty expression')

        def num(m):
            t = m.group(0)
            tl = t.lower()
            if t.startswith('$') and len(t) > 1:
                return str(int(t[1:], 16))
            if tl.startswith('0x'):
                return str(int(t[2:], 16))
            if tl.startswith('0b') and re.fullmatch(r'0b[01]+', tl):
                return str(int(t[2:], 2))
            if t.startswith('%'):
                return str(int(t[1:], 2))
            if tl.endswith('h') and re.fullmatch(r'[0-9][0-9a-f]*h', tl):
                return str(int(t[:-1], 16))
            return t
        # char literals
        e = re.sub(r"'(\\?.)'", lambda m: str(ord(m.group(1)[-1])), e)
        e = re.sub(r'\$[0-9A-Fa-f]+|0[xX][0-9A-Fa-f]+|0[bB][01]+\b|%[01]+|\b[0-9][0-9A-Fa-f]*[hH]\b', num, e)
        # $ alone = pc
        e = re.sub(r'(?<![\w$])\$(?![\w])', str(self.pc), e)
        e = e.replace('!=', ' != ').replace('<>', ' != ')
        e = re.sub(r'(?<![<>=!])=(?!=)', '==', e)
        # local labels
        e = re.sub(r'(?<![\w.])\.([A-Za-z_]\w*)', lambda m: self.scope + '.' + m.group(1), e)

        def sym(m):
            name = m.group(0)
            low = name.lower()
            if low in ('lo', 'hi', 'and', 'or', 'not'):
                return name
            if name in self.syms:
                return '(%d)' % self.syms[name]
            if need and self.final:
                raise AsmError('undefined symbol ' + name)
            self.unresolved = True
            return '(0)'
        e = re.sub(r'[A-Za-z_][\w.]*', sym, e)
        e = e.replace('/', '//')
        try:
            v = eval(e, {'__builtins__': {}}, {'lo': lambda x: x & 255, 'hi': lambda x: (x >> 8) & 255})
        except Exception as ex:
            raise AsmError('bad expression %r (%s)' % (expr, ex))
        return int(v)

    # ---------- operand classification ----------
    def is_mem(self, o):
        return o.startswith('(') and o.endswith(')') and self.balanced(o[1:-1])

    @staticmethod
    def balanced(s):
        d = 0
        for ch in s:
            if ch == '(':
                d += 1
            elif ch == ')':
                d -= 1
                if d < 0:
                    return False
        return d == 0

    def idx(self, o):
        """(ix+d) -> (prefix, d) or None"""
        m = re.fullmatch(r'\(\s*(ix|iy)\s*(?:([+-])(.*))?\)', o, re.I)
        if not m:
            return None
        pre = 0xDD if m.group(1).lower() == 'ix' else 0xFD
        d = 0
        if m.group(2):
            d = self.ev(m.group(3))
            if m.group(2) == '-':
                d = -d
        if not -128 <= d <= 127:
            raise AsmError('index offset out of range')
        return pre, d & 255

    def r8(self, o):
        """returns (code, prefix_bytes, disp_bytes) or None"""
        ol = o.lower().replace(' ', '')
        if ol in R8:
            return R8[ol], [], []
        ix = self.idx(o)
        if ix:
            return 6, [ix[0]], [ix[1]]
        return None

    # ---------- encoding ----------
    def encode(self, mn, ops):
        L = [o.lower().replace(' ', '') for o in ops]
        n = len(ops)
        if mn in SIMPLE and n == 0:
            return list(SIMPLE[mn])
        if mn == 'ex':
            if L == ['af', "af'"] or L == ['af', 'af']:
                return [0x08]
            if L == ['de', 'hl']:
                return [0xEB]
            if L == ['(sp)', 'hl']:
                return [0xE3]
            if L == ['(sp)', 'ix']:
                return [0xDD, 0xE3]
            if L == ['(sp)', 'iy']:
                return [0xFD, 0xE3]
        if mn == 'im':
            v = self.ev(ops[0])
            return [0xED, {0: 0x46, 1: 0x56, 2: 0x5E}[v]]
        if mn == 'rst':
            v = self.ev(ops[0])
            if v & ~0x38:
                raise AsmError('bad rst')
            return [0xC7 | v]
        if mn in ('push', 'pop'):
            base = 0xC5 if mn == 'push' else 0xC1
            if L[0] in ('ix', 'iy'):
                return [0xDD if L[0] == 'ix' else 0xFD, base | 0x20]
            return [base | RP2[L[0]] << 4]
        if mn in ('jp', 'call', 'jr', 'djnz', 'ret'):
            return self.enc_flow(mn, ops, L)
        if mn in ('inc', 'dec'):
            o = L[0]
            if o in RP:
                return [(0x03 if mn == 'inc' else 0x0B) | RP[o] << 4]
            if o in ('ix', 'iy'):
                return [0xDD if o == 'ix' else 0xFD, 0x23 if mn == 'inc' else 0x2B]
            r = self.r8(ops[0])
            if r:
                return r[1] + [(0x04 if mn == 'inc' else 0x05) | r[0] << 3] + r[2]
        if mn in ALU:
            a = ALU[mn]
            if n == 2 and L[0] in ('hl', 'ix', 'iy') and mn in ('add', 'adc', 'sbc'):
                rp = L[1]
                if L[0] in ('ix', 'iy'):
                    pre = 0xDD if L[0] == 'ix' else 0xFD
                    if mn != 'add':
                        raise AsmError('bad op')
                    m = {'bc': 0, 'de': 1, L[0]: 2, 'sp': 3}[rp]
                    return [pre, 0x09 | m << 4]
                if mn == 'add':
                    return [0x09 | RP[rp] << 4]
                if mn == 'adc':
                    return [0xED, 0x4A | RP[rp] << 4]
                return [0xED, 0x42 | RP[rp] << 4]
            if n == 2:
                if L[0] != 'a':
                    raise AsmError('alu needs A')
                src = ops[1]
            else:
                src = ops[0]
            r = self.r8(src)
            if r:
                return r[1] + [0x80 | a << 3 | r[0]] + r[2]
            v = self.ev(src)
            return [0xC6 | a << 3, self.byte(v)]
        if mn in ROT:
            r = self.r8(ops[0])
            if r[1]:
                return [r[1][0], 0xCB, r[2][0], ROT[mn] << 3 | 6]
            return [0xCB, ROT[mn] << 3 | r[0]]
        if mn in ('bit', 'res', 'set'):
            b = self.ev(ops[0])
            if not 0 <= b <= 7:
                raise AsmError('bad bit')
            base = {'bit': 0x40, 'res': 0x80, 'set': 0xC0}[mn]
            r = self.r8(ops[1])
            if r[1]:
                return [r[1][0], 0xCB, r[2][0], base | b << 3 | 6]
            return [0xCB, base | b << 3 | r[0]]
        if mn == 'in':
            if L[1] == '(c)':
                r = R8[L[0]]
                return [0xED, 0x40 | r << 3]
            if L[0] != 'a':
                raise AsmError('in needs A')
            return [0xDB, self.byte(self.ev(ops[1][1:-1]))]
        if mn == 'out':
            if L[0] == '(c)':
                if L[1] == '0':
                    return [0xED, 0x71]
                return [0xED, 0x41 | R8[L[1]] << 3]
            if L[1] != 'a':
                raise AsmError('out needs A')
            return [0xD3, self.byte(self.ev(ops[0][1:-1]))]
        if mn == 'ld':
            return self.enc_ld(ops, L)
        raise AsmError('unknown instruction %s %s' % (mn, ','.join(ops)))

    def byte(self, v):
        if not -128 <= v <= 255:
            if self.final:
                raise AsmError('byte out of range: %d' % v)
        return v & 255

    def word(self, v):
        if not -32768 <= v <= 65535 and self.final:
            raise AsmError('word out of range: %d' % v)
        return [v & 255, (v >> 8) & 255]

    def enc_flow(self, mn, ops, L):
        if mn == 'ret':
            if not ops:
                return [0xC9]
            return [0xC0 | CC[L[0]] << 3]
        if mn == 'jp':
            if len(ops) == 1:
                if L[0] in ('(hl)', 'hl'):
                    return [0xE9]
                if L[0] in ('(ix)', 'ix'):
                    return [0xDD, 0xE9]
                if L[0] in ('(iy)', 'iy'):
                    return [0xFD, 0xE9]
                return [0xC3] + self.word(self.ev(ops[0]))
            return [0xC2 | CC[L[0]] << 3] + self.word(self.ev(ops[1]))
        if mn == 'call':
            if len(ops) == 1:
                return [0xCD] + self.word(self.ev(ops[0]))
            return [0xC4 | CC[L[0]] << 3] + self.word(self.ev(ops[1]))
        if mn in ('jr', 'djnz'):
            tgt = ops[-1]
            if mn == 'djnz':
                op = 0x10
            elif len(ops) == 1:
                op = 0x18
            else:
                c = CC[L[0]]
                if c > 3:
                    raise AsmError('bad jr condition')
                op = 0x20 | c << 3
            t = self.ev(tgt)
            d = t - (self.pc + 2)
            if self.final and not -128 <= d <= 127:
                raise AsmError('jr out of range (%d)' % d)
            return [op, d & 255]

    def enc_ld(self, ops, L):
        d, s = L
        D, S = ops
        # special regs
        sp = {('i', 'a'): [0xED, 0x47], ('r', 'a'): [0xED, 0x4F], ('a', 'i'): [0xED, 0x57], ('a', 'r'): [0xED, 0x5F],
              ('sp', 'hl'): [0xF9], ('sp', 'ix'): [0xDD, 0xF9], ('sp', 'iy'): [0xFD, 0xF9],
              ('a', '(bc)'): [0x0A], ('a', '(de)'): [0x1A], ('(bc)', 'a'): [0x02], ('(de)', 'a'): [0x12]}
        if (d, s) in sp:
            return list(sp[(d, s)])
        rd, rs = self.r8(D), self.r8(S)
        if rd and rs:
            if rd[0] == 6 and rs[0] == 6:
                raise AsmError('ld (hl),(hl)')
            return (rd[1] or rs[1]) + [0x40 | rd[0] << 3 | rs[0]] + (rd[2] or rs[2])
        # 16 bit
        if d in RP or d in ('ix', 'iy'):
            pre = [0xDD] if d == 'ix' else [0xFD] if d == 'iy' else []
            if self.is_mem(S):
                addr = self.word(self.ev(S[1:-1]))
                if d in ('hl', 'ix', 'iy'):
                    return pre + [0x2A] + addr
                return [0xED, 0x4B | RP[d] << 4] + addr
            v = self.word(self.ev(S))
            if pre:
                return pre + [0x21] + v
            return [0x01 | RP[d] << 4] + v
        if self.is_mem(D) and not rd:
            addr = self.word(self.ev(D[1:-1]))
            if s == 'a':
                return [0x32] + addr
            if s == 'hl':
                return [0x22] + addr
            if s in ('ix', 'iy'):
                return [0xDD if s == 'ix' else 0xFD, 0x22] + addr
            if s in RP:
                return [0xED, 0x43 | RP[s] << 4] + addr
            raise AsmError('bad ld')
        if d == 'a' and self.is_mem(S) and not rs:
            return [0x3A] + self.word(self.ev(S[1:-1]))
        if rd:
            v = self.byte(self.ev(S))
            return rd[1] + [0x06 | rd[0] << 3] + rd[2] + [v]
        raise AsmError('bad ld %s,%s' % (D, S))

    # ---------- driver ----------
    def load(self, fn):
        lines = []
        base = os.path.dirname(fn)
        for i, l in enumerate(open(fn, encoding='utf-8').read().split('\n')):
            m = re.match(r'\s*include\s+"([^"]+)"', l, re.I)
            if m:
                lines += self.load(os.path.join(base, m.group(1)))
            else:
                lines.append((fn, i + 1, l))
        return lines

    def expand(self, lines):
        out, i, cnt = [], 0, [0]
        while i < len(lines):
            f, n, l = lines[i]
            t = strip_comment(l).strip()
            m = re.match(r'macro\s+(\w+)', t, re.I)
            if m:
                body = []
                i += 1
                while not re.match(r'\s*endm\b', strip_comment(lines[i][2]), re.I):
                    body.append(lines[i]); i += 1
                self.macros[m.group(1).lower()] = body
                i += 1
                continue
            w = t.split(None, 1)
            if w and w[0].lower() in self.macros and not t.endswith(':'):
                args = split_args(w[1]) if len(w) > 1 else []
                cnt[0] += 1
                body = []
                for bf, bn, bl in self.macros[w[0].lower()]:
                    for k in range(9, 0, -1):
                        bl = bl.replace('\\%d' % k, args[k - 1] if k <= len(args) else '')
                    bl = bl.replace('\\@', '_m%d' % cnt[0])
                    body.append((bf, bn, bl))
                out += self.expand(body)
                i += 1
                continue
            out.append(lines[i]); i += 1
        return out

    def assemble(self, fn):
        lines = self.expand(self.load(fn))
        prev = None
        for p in range(12):
            self.final = False
            self.unresolved = False
            out = self.run(lines)
            snap = dict(self.syms)
            if snap == prev:
                break
            prev = snap
        self.final = True
        return self.run(lines)

    def run(self, lines):
        self.pc = 0
        self.defined_now = set()
        self.scope = '_g'
        self.rs = 0
        mem = {}
        self.listing = []
        cond = [True]
        for fn, ln, raw in lines:
            line = strip_comment(raw).rstrip()
            try:
                t = line.strip()
                tl = t.lower()
                # conditionals
                if re.match(r'if\b', tl):
                    cond.append(cond[-1] and bool(self.ev(t[2:], need=False)) if cond[-1] else False)
                    continue
                if tl == 'else':
                    parent = all(cond[:-1])
                    cond[-1] = parent and not cond[-1]
                    continue
                if tl == 'endif':
                    cond.pop(); continue
                if not all(cond):
                    continue
                if not t:
                    continue
                # label
                m = re.match(r'(\.?[A-Za-z_][\w.]*):\s*(.*)$', t)
                if m:
                    name = m.group(1)
                    if name.startswith('.'):
                        name = self.scope + name
                    else:
                        self.scope = name
                    self.define(name, self.pc)
                    t = m.group(2).strip()
                    if not t:
                        continue
                # equ / = / rb / rw
                m = re.match(r'([A-Za-z_][\w.]*)\s+(equ|=|rb|rw)\s+(.*)$', t, re.I) or \
                    re.match(r'([A-Za-z_][\w.]*)\s*(=)\s*(.*)$', t)
                if m and m.group(1).lower() not in ('ld', 'db', 'dw', 'ds'):
                    kind = m.group(2).lower()
                    if kind in ('equ', '='):
                        self.define(m.group(1), self.ev(m.group(3), need=False))
                    else:
                        self.define(m.group(1), self.rs)
                        self.rs += self.ev(m.group(3)) * (2 if kind == 'rw' else 1)
                    continue
                w = t.split(None, 1)
                mn = w[0].lower()
                arg = w[1] if len(w) > 1 else ''
                data = None
                if mn == 'org':
                    self.pc = self.ev(arg); continue
                if mn == 'rsset':
                    self.rs = self.ev(arg); continue
                if mn == 'align':
                    a = self.ev(arg)
                    self.pc = (self.pc + a - 1) // a * a
                    continue
                if mn == 'assert':
                    a = split_args(arg)
                    if self.final and not self.ev(a[0]):
                        raise AsmError('assert failed: ' + (a[1] if len(a) > 1 else a[0]))
                    continue
                if mn in ('db', 'defb', 'byte', 'dm'):
                    data = []
                    for a in split_args(arg):
                        if a.startswith('"'):
                            data += list(a[1:-1].encode('latin1'))
                        else:
                            data.append(self.byte(self.ev(a)))
                elif mn in ('dw', 'defw', 'word'):
                    data = []
                    for a in split_args(arg):
                        data += self.word(self.ev(a))
                elif mn in ('ds', 'defs'):
                    a = split_args(arg)
                    data = [self.ev(a[1]) & 255 if len(a) > 1 else 0] * self.ev(a[0])
                elif mn == 'incbin':
                    p = os.path.join(os.path.dirname(fn), arg.strip().strip('"'))
                    data = list(open(p, 'rb').read())
                else:
                    ops = split_args(arg)
                    data = self.encode(mn, ops)
                for i, b in enumerate(data):
                    a = self.pc + i
                    if self.final and a in mem:
                        raise AsmError('overlap at $%04X' % a)
                    mem[a] = b
                if self.final:
                    self.listing.append('%04X  %-12s %s' % (self.pc, ' '.join('%02X' % b for b in data[:4]), raw.strip()))
                self.pc += len(data)
            except AsmError as e:
                if self.final:
                    raise AsmError('%s:%d: %s\n    %s' % (fn, ln, e, raw.strip()))
            except (KeyError, IndexError, TypeError, ValueError) as e:
                raise AsmError('%s:%d: syntax error (%s)\n    %s' % (fn, ln, e, raw.strip()))
        return mem

    def define(self, name, val):
        if self.final:
            if name in self.defined_now:
                raise AsmError('duplicate symbol ' + name)
            self.defined_now.add(name)
        self.syms[name] = val


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--size', type=lambda x: int(x, 0), default=0x8000)
    ap.add_argument('--sym')
    ap.add_argument('--lst')
    ap.add_argument('--sms', action='store_true', help='fix SMS header checksum')
    a = ap.parse_args()
    asm = Assembler()
    try:
        mem = asm.assemble(a.src)
    except AsmError as e:
        print('ERROR', e)
        sys.exit(1)
    rom = bytearray([0xFF] * a.size)
    for k, v in mem.items():
        if k >= a.size:
            print('ERROR: code beyond ROM size at $%X' % k); sys.exit(1)
        rom[k] = v
    if a.sms:
        # header at $7FF0: "TMR SEGA", reserved(2), checksum(2), product(2.5), version, region/size
        rom[0x7FF0:0x7FF8] = b'TMR SEGA'
        rom[0x7FF8:0x7FFA] = b'\x00\x00'
        rom[0x7FFC:0x7FFF] = b'\x26\x70\x00'  # product code / version
        rom[0x7FFF] = 0x4C  # SMS export, 32KB
        cs = sum(rom[0:0x7FF0]) & 0xFFFF
        rom[0x7FFA] = cs & 255
        rom[0x7FFB] = cs >> 8
    open(a.out, 'wb').write(rom)
    used = len(mem)
    print('OK %s: %d bytes used of %d' % (a.out, used, a.size))
    if a.sym:
        with open(a.sym, 'w') as f:
            for k, v in sorted(asm.syms.items(), key=lambda x: x[1]):
                f.write('%04X %s\n' % (v & 0xFFFF, k))
    if a.lst:
        open(a.lst, 'w').write('\n'.join(asm.listing))


if __name__ == '__main__':
    main()
