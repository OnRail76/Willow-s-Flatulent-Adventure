"""z80.py - Z80 CPU core for testing (documented instructions + flags)."""

SF, ZF, YF, HF, XF, PF, NF, CF = 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01

SZ = [0] * 256
SZP = [0] * 256
for i in range(256):
    s = (i & 0x80) | (ZF if i == 0 else 0) | (i & (YF | XF))
    SZ[i] = s
    p = bin(i).count('1') % 2 == 0
    SZP[i] = s | (PF if p else 0)

# base cycle counts (unprefixed)
CYC = [
    4, 10, 7, 6, 4, 4, 7, 4, 4, 11, 7, 6, 4, 4, 7, 4,
    8, 10, 7, 6, 4, 4, 7, 4, 12, 11, 7, 6, 4, 4, 7, 4,
    7, 10, 16, 6, 4, 4, 7, 4, 7, 11, 16, 6, 4, 4, 7, 4,
    7, 10, 13, 6, 11, 11, 10, 4, 7, 11, 13, 6, 4, 4, 7, 4,
] + [4] * 64 + [4] * 64 + [
    5, 10, 10, 10, 10, 11, 7, 11, 5, 10, 10, 0, 10, 17, 7, 11,
    5, 10, 10, 11, 10, 11, 7, 11, 5, 4, 10, 11, 10, 0, 7, 11,
    5, 10, 10, 19, 10, 11, 7, 11, 5, 4, 10, 4, 10, 0, 7, 11,
    5, 10, 10, 4, 10, 11, 7, 11, 5, 6, 10, 4, 10, 0, 7, 11,
]
for i in range(0x40, 0xC0):
    CYC[i] = 4
    if (i & 7) == 6 or ((i >> 3) & 7) == 6 and i < 0x80:
        CYC[i] = 7
CYC[0x76] = 4


class Z80:
    def __init__(self, bus):
        self.bus = bus
        self.rd = bus.read
        self.wr = bus.write
        self.a = self.f = self.b = self.c = self.d = self.e = self.h = self.l = 0
        self.a_ = self.f_ = self.b_ = self.c_ = self.d_ = self.e_ = self.h_ = self.l_ = 0
        self.ix = self.iy = 0xFFFF
        self.sp = 0xDFF0
        self.pc = 0
        self.i = self.r = 0
        self.iff1 = self.iff2 = 0
        self.im = 0
        self.halted = False
        self.ei_delay = False
        self.cycles = 0
        self.irq_line = False

    # --- helpers ---
    def fetch(self):
        v = self.rd(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return v

    def fetch16(self):
        lo = self.rd(self.pc)
        hi = self.rd((self.pc + 1) & 0xFFFF)
        self.pc = (self.pc + 2) & 0xFFFF
        return lo | hi << 8

    def rd16(self, a):
        return self.rd(a) | self.rd((a + 1) & 0xFFFF) << 8

    def wr16(self, a, v):
        self.wr(a, v & 255)
        self.wr((a + 1) & 0xFFFF, v >> 8)

    def push(self, v):
        self.sp = (self.sp - 2) & 0xFFFF
        self.wr16(self.sp, v)

    def pop(self):
        v = self.rd16(self.sp)
        self.sp = (self.sp + 2) & 0xFFFF
        return v

    def getr(self, i):
        if i == 0: return self.b
        if i == 1: return self.c
        if i == 2: return self.d
        if i == 3: return self.e
        if i == 4: return self.h
        if i == 5: return self.l
        if i == 6: return self.rd(self.h << 8 | self.l)
        return self.a

    def setr(self, i, v):
        if i == 0: self.b = v
        elif i == 1: self.c = v
        elif i == 2: self.d = v
        elif i == 3: self.e = v
        elif i == 4: self.h = v
        elif i == 5: self.l = v
        elif i == 6: self.wr(self.h << 8 | self.l, v)
        else: self.a = v

    def getrp(self, p):
        if p == 0: return self.b << 8 | self.c
        if p == 1: return self.d << 8 | self.e
        if p == 2: return self.h << 8 | self.l
        return self.sp

    def setrp(self, p, v):
        if p == 0: self.b, self.c = v >> 8, v & 255
        elif p == 1: self.d, self.e = v >> 8, v & 255
        elif p == 2: self.h, self.l = v >> 8, v & 255
        else: self.sp = v

    def cond(self, y):
        f = self.f
        if y == 0: return not f & ZF
        if y == 1: return bool(f & ZF)
        if y == 2: return not f & CF
        if y == 3: return bool(f & CF)
        if y == 4: return not f & PF
        if y == 5: return bool(f & PF)
        if y == 6: return not f & SF
        return bool(f & SF)

    # --- ALU ---
    def alu(self, op, v):
        a = self.a
        if op == 0 or op == 1:  # add / adc
            c = (self.f & CF) if op == 1 else 0
            r = a + v + c
            res = r & 255
            self.f = SZ[res] | (r >> 8) | ((a ^ v ^ res) & HF) | (PF if ((a ^ ~v) & (a ^ res) & 0x80) else 0)
            self.a = res
        elif op == 2 or op == 3 or op == 7:  # sub sbc cp
            c = (self.f & CF) if op == 3 else 0
            r = a - v - c
            res = r & 255
            f = (SZ[res] & ~(YF | XF)) | NF | (CF if r < 0 else 0) | ((a ^ v ^ res) & HF) | (PF if ((a ^ v) & (a ^ res) & 0x80) else 0)
            if op == 7:
                self.f = f | (v & (YF | XF))
            else:
                self.f = f | (res & (YF | XF))
                self.a = res
        elif op == 4:
            self.a = a & v
            self.f = SZP[self.a] | HF
        elif op == 5:
            self.a = a ^ v
            self.f = SZP[self.a]
        else:
            self.a = a | v
            self.f = SZP[self.a]

    def inc8(self, v):
        r = (v + 1) & 255
        self.f = (self.f & CF) | SZ[r] | (HF if (r & 15) == 0 else 0) | (PF if r == 0x80 else 0)
        return r

    def dec8(self, v):
        r = (v - 1) & 255
        self.f = (self.f & CF) | SZ[r] | NF | (HF if (r & 15) == 15 else 0) | (PF if r == 0x7F else 0)
        return r

    def add16(self, x, y):
        r = x + y
        self.f = (self.f & (SF | ZF | PF)) | ((r >> 16) & CF) | (((x ^ y ^ r) >> 8) & HF) | ((r >> 8) & (YF | XF))
        return r & 0xFFFF

    def adc16(self, x, y):
        c = self.f & CF
        r = x + y + c
        res = r & 0xFFFF
        self.f = ((res >> 8) & (SF | YF | XF)) | (ZF if res == 0 else 0) | ((r >> 16) & CF) | (((x ^ y ^ r) >> 8) & HF) | \
            (PF if ((x ^ ~y) & (x ^ res) & 0x8000) else 0)
        return res

    def sbc16(self, x, y):
        c = self.f & CF
        r = x - y - c
        res = r & 0xFFFF
        self.f = ((res >> 8) & (SF | YF | XF)) | (ZF if res == 0 else 0) | (CF if r < 0 else 0) | NF | \
            (((x ^ y ^ res) >> 8) & HF) | (PF if ((x ^ y) & (x ^ res) & 0x8000) else 0)
        return res

    def rot(self, op, v):
        c = self.f & CF
        if op == 0: co = v >> 7; v = ((v << 1) | co) & 255
        elif op == 1: co = v & 1; v = (v >> 1) | (co << 7)
        elif op == 2: co = v >> 7; v = ((v << 1) | c) & 255
        elif op == 3: co = v & 1; v = (v >> 1) | (c << 7)
        elif op == 4: co = v >> 7; v = (v << 1) & 255
        elif op == 5: co = v & 1; v = (v >> 1) | (v & 0x80)
        elif op == 6: co = v >> 7; v = ((v << 1) | 1) & 255
        else: co = v & 1; v = v >> 1
        self.f = SZP[v] | co
        return v

    def daa(self):
        a = self.a
        f = self.f
        cor = 0
        c = f & CF
        if (f & HF) or (a & 15) > 9:
            cor |= 6
        if c or a > 0x99:
            cor |= 0x60
            c = CF
        if f & NF:
            h = HF if (f & HF) and (a & 15) < 6 else 0
            a = (a - cor) & 255
        else:
            h = HF if (a & 15) > 9 else 0
            a = (a + cor) & 255
        self.a = a
        self.f = SZP[a] | h | (f & NF) | c

    # --- interrupts ---
    def interrupt(self):
        if self.iff1 and not self.ei_delay:
            if self.halted:
                self.halted = False
                self.pc = (self.pc + 1) & 0xFFFF
            self.iff1 = self.iff2 = 0
            self.push(self.pc)
            if self.im == 2:
                self.pc = self.rd16(self.i << 8 | 0xFF)
            else:
                self.pc = 0x38
            return 13
        return 0

    def nmi(self):
        if self.halted:
            self.halted = False
            self.pc = (self.pc + 1) & 0xFFFF
        self.iff2 = self.iff1
        self.iff1 = 0
        self.push(self.pc)
        self.pc = 0x66
        return 11

    # --- execution ---
    def step(self):
        self.ei_delay = False
        if self.halted:
            return 4
        self.r = (self.r & 0x80) | ((self.r + 1) & 0x7F)
        op = self.fetch()
        if op == 0xCB:
            return self.exec_cb()
        if op == 0xED:
            return self.exec_ed()
        if op == 0xDD or op == 0xFD:
            return self.exec_idx(op)
        return self.exec_main(op)

    def exec_main(self, op):
        cyc = CYC[op]
        x = op >> 6
        y = (op >> 3) & 7
        z = op & 7
        if x == 1:
            if op == 0x76:
                self.halted = True
                self.pc = (self.pc - 1) & 0xFFFF
                return 4
            self.setr(y, self.getr(z))
            return cyc
        if x == 2:
            self.alu(y, self.getr(z))
            return cyc
        if x == 0:
            if z == 0:
                if y == 0: return 4
                if y == 1:
                    self.a, self.a_ = self.a_, self.a
                    self.f, self.f_ = self.f_, self.f
                    return 4
                if y == 2:
                    d = self.fetch()
                    self.b = (self.b - 1) & 255
                    if self.b:
                        self.pc = (self.pc + (d - 256 if d > 127 else d)) & 0xFFFF
                        return 13
                    return 8
                d = self.fetch()
                if y == 3 or self.cond(y - 4):
                    self.pc = (self.pc + (d - 256 if d > 127 else d)) & 0xFFFF
                    return 12
                return 7
            if z == 1:
                p = y >> 1
                if y & 1:
                    self.setrp(2, self.add16(self.getrp(2), self.getrp(p)))
                else:
                    self.setrp(p, self.fetch16())
                return cyc
            if z == 2:
                if y == 0: self.wr(self.b << 8 | self.c, self.a)
                elif y == 1: self.a = self.rd(self.b << 8 | self.c)
                elif y == 2: self.wr(self.d << 8 | self.e, self.a)
                elif y == 3: self.a = self.rd(self.d << 8 | self.e)
                elif y == 4: self.wr16(self.fetch16(), self.h << 8 | self.l)
                elif y == 5:
                    v = self.rd16(self.fetch16()); self.h, self.l = v >> 8, v & 255
                elif y == 6: self.wr(self.fetch16(), self.a)
                else: self.a = self.rd(self.fetch16())
                return cyc
            if z == 3:
                p = y >> 1
                v = self.getrp(p)
                self.setrp(p, (v + (-1 if y & 1 else 1)) & 0xFFFF)
                return cyc
            if z == 4:
                self.setr(y, self.inc8(self.getr(y)))
                return 11 if y == 6 else 4
            if z == 5:
                self.setr(y, self.dec8(self.getr(y)))
                return 11 if y == 6 else 4
            if z == 6:
                self.setr(y, self.fetch())
                return 10 if y == 6 else 7
            # z == 7
            a = self.a
            if y == 0:
                c = a >> 7; self.a = ((a << 1) | c) & 255
                self.f = (self.f & (SF | ZF | PF)) | c | (self.a & (YF | XF))
            elif y == 1:
                c = a & 1; self.a = (a >> 1) | (c << 7)
                self.f = (self.f & (SF | ZF | PF)) | c | (self.a & (YF | XF))
            elif y == 2:
                c = a >> 7; self.a = ((a << 1) | (self.f & CF)) & 255
                self.f = (self.f & (SF | ZF | PF)) | c | (self.a & (YF | XF))
            elif y == 3:
                c = a & 1; self.a = (a >> 1) | ((self.f & CF) << 7)
                self.f = (self.f & (SF | ZF | PF)) | c | (self.a & (YF | XF))
            elif y == 4:
                self.daa()
            elif y == 5:
                self.a = a ^ 255
                self.f = (self.f & (SF | ZF | PF | CF)) | HF | NF | (self.a & (YF | XF))
            elif y == 6:
                self.f = (self.f & (SF | ZF | PF)) | CF | (a & (YF | XF))
            else:
                c = self.f & CF
                self.f = ((self.f & (SF | ZF | PF)) | (HF if c else 0) | (c ^ CF)) | (a & (YF | XF))
            return 4
        # x == 3
        if z == 0:
            if self.cond(y):
                self.pc = self.pop(); return 11
            return 5
        if z == 1:
            if y & 1 == 0:
                v = self.pop()
                p = y >> 1
                if p == 3:
                    self.a, self.f = v >> 8, v & 255
                else:
                    self.setrp(p, v)
                return 10
            if y == 1: self.pc = self.pop(); return 10
            if y == 3:
                self.b, self.c, self.b_, self.c_ = self.b_, self.c_, self.b, self.c
                self.d, self.e, self.d_, self.e_ = self.d_, self.e_, self.d, self.e
                self.h, self.l, self.h_, self.l_ = self.h_, self.l_, self.h, self.l
                return 4
            if y == 5: self.pc = self.h << 8 | self.l; return 4
            self.sp = self.h << 8 | self.l; return 6
        if z == 2:
            t = self.fetch16()
            if self.cond(y): self.pc = t
            return 10
        if z == 3:
            if y == 0: self.pc = self.fetch16(); return 10
            if y == 2: self.bus.out(self.fetch(), self.a); return 11
            if y == 3: self.a = self.bus.inp(self.fetch()); return 11
            if y == 4:
                v = self.rd16(self.sp); self.wr16(self.sp, self.h << 8 | self.l)
                self.h, self.l = v >> 8, v & 255; return 19
            if y == 5:
                self.d, self.e, self.h, self.l = self.h, self.l, self.d, self.e; return 4
            if y == 6: self.iff1 = self.iff2 = 0; return 4
            if y == 7: self.iff1 = self.iff2 = 1; self.ei_delay = True; return 4
            raise RuntimeError('bad op %02X at %04X' % (op, self.pc - 1))
        if z == 4:
            t = self.fetch16()
            if self.cond(y):
                self.push(self.pc); self.pc = t; return 17
            return 10
        if z == 5:
            if y & 1 == 0:
                p = y >> 1
                self.push((self.a << 8 | self.f) if p == 3 else self.getrp(p))
                return 11
            if y == 1:
                t = self.fetch16(); self.push(self.pc); self.pc = t; return 17
            raise RuntimeError('bad op %02X' % op)
        if z == 6:
            self.alu(y, self.fetch()); return 7
        self.push(self.pc); self.pc = y * 8; return 11

    def exec_cb(self):
        op = self.fetch()
        x, y, z = op >> 6, (op >> 3) & 7, op & 7
        v = self.getr(z)
        if x == 0:
            self.setr(z, self.rot(y, v))
        elif x == 1:
            r = v & (1 << y)
            self.f = (self.f & CF) | HF | (ZF | PF if not r else 0) | (SF if y == 7 and r else 0) | (v & (YF | XF))
            return 12 if z == 6 else 8
        elif x == 2:
            self.setr(z, v & ~(1 << y))
        else:
            self.setr(z, v | (1 << y))
        return 15 if z == 6 else 8

    def exec_ed(self):
        op = self.fetch()
        x, y, z = op >> 6, (op >> 3) & 7, op & 7
        if x == 1:
            p, q = y >> 1, y & 1
            if z == 0:
                v = self.bus.inp(self.c)
                if y != 6: self.setr(y, v)
                self.f = (self.f & CF) | SZP[v]
                return 12
            if z == 1:
                self.bus.out(self.c, 0 if y == 6 else self.getr(y)); return 12
            if z == 2:
                hl = self.h << 8 | self.l
                r = self.adc16(hl, self.getrp(p)) if q else self.sbc16(hl, self.getrp(p))
                self.h, self.l = r >> 8, r & 255
                return 15
            if z == 3:
                a = self.fetch16()
                if q: self.setrp(p, self.rd16(a))
                else: self.wr16(a, self.getrp(p))
                return 20
            if z == 4:
                v = self.a; self.a = 0; self.alu(2, v); return 8
            if z == 5:
                self.pc = self.pop(); self.iff1 = self.iff2; return 14
            if z == 6:
                self.im = [0, 0, 1, 2][y & 3]; return 8
            if y == 0: self.i = self.a; return 9
            if y == 1: self.r = self.a; return 9
            if y == 2 or y == 3:
                self.a = self.i if y == 2 else self.r
                self.f = (self.f & CF) | SZ[self.a] | (PF if self.iff2 else 0)
                return 9
            if y == 4 or y == 5:  # rrd / rld
                hl = self.h << 8 | self.l
                m = self.rd(hl)
                if y == 4:
                    self.wr(hl, ((self.a << 4) | (m >> 4)) & 255)
                    self.a = (self.a & 0xF0) | (m & 15)
                else:
                    self.wr(hl, ((m << 4) | (self.a & 15)) & 255)
                    self.a = (self.a & 0xF0) | (m >> 4)
                self.f = (self.f & CF) | SZP[self.a]
                return 18
            return 8
        if x == 2 and z <= 3 and y >= 4:
            return self.block(y, z)
        raise RuntimeError('bad ED op %02X at %04X' % (op, self.pc - 2))

    def block(self, y, z):
        inc = 1 if y in (4, 6) else -1
        rep = y >= 6
        hl = self.h << 8 | self.l
        bc = self.b << 8 | self.c
        if z == 0:  # ld
            de = self.d << 8 | self.e
            v = self.rd(hl)
            self.wr(de, v)
            hl = (hl + inc) & 0xFFFF; de = (de + inc) & 0xFFFF; bc = (bc - 1) & 0xFFFF
            self.d, self.e = de >> 8, de & 255
            self.f = (self.f & (SF | ZF | CF)) | (PF if bc else 0)
        elif z == 1:  # cp
            v = self.rd(hl)
            r = (self.a - v) & 255
            hl = (hl + inc) & 0xFFFF; bc = (bc - 1) & 0xFFFF
            self.f = (self.f & CF) | (SZ[r] & ~(YF | XF)) | NF | ((self.a ^ v ^ r) & HF) | (PF if bc else 0)
        elif z == 2:  # in
            v = self.bus.inp(self.c)
            self.wr(hl, v)
            hl = (hl + inc) & 0xFFFF
            self.b = (self.b - 1) & 255
            bc = self.b << 8 | self.c
            self.f = (SZ[self.b]) | NF
        else:  # out
            v = self.rd(hl)
            self.b = (self.b - 1) & 255
            self.bus.out(self.c, v)
            hl = (hl + inc) & 0xFFFF
            bc = self.b << 8 | self.c
            self.f = SZ[self.b] | NF
        self.h, self.l = hl >> 8, hl & 255
        self.b, self.c = bc >> 8, bc & 255
        if rep:
            if z >= 2:
                again = self.b != 0
            elif z == 1:
                again = bc != 0 and not (self.f & ZF)
            else:
                again = bc != 0
            if again:
                self.pc = (self.pc - 2) & 0xFFFF
                return 21
        return 16

    def exec_idx(self, pre):
        isx = pre == 0xDD
        xr = self.ix if isx else self.iy
        op = self.fetch()

        def setx(v):
            if isx: self.ix = v
            else: self.iy = v

        def disp():
            d = self.fetch()
            return (xr + (d - 256 if d > 127 else d)) & 0xFFFF
        if op == 0x21: setx(self.fetch16()); return 14
        if op == 0x22: self.wr16(self.fetch16(), xr); return 20
        if op == 0x2A: setx(self.rd16(self.fetch16())); return 20
        if op == 0x23: setx((xr + 1) & 0xFFFF); return 10
        if op == 0x2B: setx((xr - 1) & 0xFFFF); return 10
        if op in (0x09, 0x19, 0x29, 0x39):
            p = op >> 4
            v = xr if p == 2 else self.getrp(p)
            setx(self.add16(xr, v)); return 15
        if op == 0x34 or op == 0x35:
            a = disp()
            self.wr(a, self.inc8(self.rd(a)) if op == 0x34 else self.dec8(self.rd(a)))
            return 23
        if op == 0x36:
            a = disp(); self.wr(a, self.fetch()); return 19
        if op == 0xE1: setx(self.pop()); return 14
        if op == 0xE5: self.push(xr); return 15
        if op == 0xE9: self.pc = xr; return 8
        if op == 0xF9: self.sp = xr; return 10
        if op == 0xE3:
            v = self.rd16(self.sp); self.wr16(self.sp, xr); setx(v); return 23
        if 0x40 <= op < 0x80 and op != 0x76:
            y, z = (op >> 3) & 7, op & 7
            if z == 6:
                a = disp(); self.setr(y, self.rd(a)); return 19
            if y == 6:
                a = disp(); self.wr(a, self.getr(z)); return 19
        if 0x80 <= op < 0xC0 and (op & 7) == 6:
            a = disp(); self.alu((op >> 3) & 7, self.rd(a)); return 19
        if op == 0xCB:
            a = disp()
            op2 = self.fetch()
            x, y, z = op2 >> 6, (op2 >> 3) & 7, op2 & 7
            v = self.rd(a)
            if x == 0:
                self.wr(a, self.rot(y, v))
            elif x == 1:
                r = v & (1 << y)
                self.f = (self.f & CF) | HF | (ZF | PF if not r else 0) | (SF if y == 7 and r else 0)
                return 20
            elif x == 2:
                self.wr(a, v & ~(1 << y))
            else:
                self.wr(a, v | (1 << y))
            return 23
        raise RuntimeError('unsupported %02X %02X at %04X' % (pre, op, self.pc - 2))
