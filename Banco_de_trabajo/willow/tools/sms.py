"""sms.py - Sega Master System test machine (Z80 + VDP mode 4 + PSG + pads).

Usage as module:
    m = SMS(open('game.sms','rb').read())
    m.run_frames(60, pad=lambda frame: 0)   # pad bits: 1=up 2=down 4=left 8=right 16=b1 32=b2
    m.screenshot('a.png')
"""
import numpy as np
from z80 import Z80

UP, DOWN, LEFT, RIGHT, B1, B2 = 1, 2, 4, 8, 16, 32
CYCLES_PER_LINE = 228
LINES = 262


class VDP:
    def __init__(self):
        self.vram = bytearray(0x4000)
        self.cram = bytearray(32)
        self.reg = [0x36, 0x80, 0xFF, 0xFF, 0xFF, 0xFF, 0xFB, 0x00, 0, 0, 0xFF] + [0] * 5
        self.addr = 0
        self.code = 0
        self.latch = None
        self.buf = 0
        self.status = 0
        self.line = 0
        self.linecnt = 0xFF
        self.line_irq = False
        self.tiles = np.zeros((512, 8, 8), np.uint8)
        self.dirty = set()
        self.vram_writes = 0

    def ctrl_w(self, v):
        if self.latch is None:
            self.latch = v
            self.addr = (self.addr & 0x3F00) | v
            return
        lo = self.latch
        self.latch = None
        self.code = v >> 6
        self.addr = (v & 0x3F) << 8 | lo
        if self.code == 0:
            self.buf = self.vram[self.addr]
            self.addr = (self.addr + 1) & 0x3FFF
        elif self.code == 2:
            r = v & 15
            if r < 11:
                self.reg[r] = lo

    def ctrl_r(self):
        s = self.status
        self.status = 0
        self.latch = None
        self.line_irq = False
        return s | 0x1F

    def data_w(self, v):
        self.latch = None
        if self.code == 3:
            self.cram[self.addr & 31] = v
        else:
            self.vram[self.addr] = v
            self.dirty.add(self.addr >> 5)
            self.vram_writes += 1
        self.buf = v
        self.addr = (self.addr + 1) & 0x3FFF

    def data_r(self):
        self.latch = None
        v = self.buf
        self.buf = self.vram[self.addr]
        self.addr = (self.addr + 1) & 0x3FFF
        return v

    def irq(self):
        return bool((self.status & 0x80) and (self.reg[1] & 0x20)) or bool(self.line_irq and (self.reg[0] & 0x10))

    def update_tiles(self):
        for t in self.dirty:
            b = self.vram[t * 32:t * 32 + 32]
            arr = np.frombuffer(bytes(b), np.uint8).reshape(8, 4)
            bits = np.unpackbits(arr, axis=1).reshape(8, 4, 8)
            self.tiles[t] = bits[:, 0] | bits[:, 1] << 1 | bits[:, 2] << 2 | bits[:, 3] << 3
        self.dirty.clear()

    def palette_rgb(self):
        out = np.zeros((32, 3), np.uint8)
        for i, c in enumerate(self.cram):
            out[i] = [(c & 3) * 85, ((c >> 2) & 3) * 85, ((c >> 4) & 3) * 85]
        return out

    def render(self):
        """Render full frame to index buffer (0..31)."""
        self.update_tiles()
        R = self.reg
        img = np.zeros((192, 256), np.uint8)
        prio = np.zeros((192, 256), bool)
        bg = 16 + (R[7] & 15)
        if not R[1] & 0x40:
            img[:] = bg
            return img, []
        nt = (R[2] & 0x0E) << 10
        names = np.frombuffer(bytes(self.vram[nt:nt + 32 * 28 * 2]), '<u2').reshape(28, 32)
        sx = R[8]
        sy = R[9]
        # build full 256x224 bg
        full = np.zeros((224, 256), np.uint8)
        pfull = np.zeros((224, 256), bool)
        for ty in range(28):
            for tx in range(32):
                e = int(names[ty, tx])
                t = self.tiles[e & 511]
                if e & 0x200: t = t[:, ::-1]
                if e & 0x400: t = t[::-1, :]
                pal = 16 if e & 0x800 else 0
                blk = t + pal
                full[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8] = blk
                if e & 0x1000:
                    pfull[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8] = t != 0
        trans = np.zeros((192, 256), bool)
        for y in range(192):
            yy = y if (R[0] & 0x40 and y < 16) else y
            ry = (y + sy) % 224
            xs = 0 if (R[0] & 0x40 and y < 16) else sx
            row = np.roll(full[ry], xs)
            prow = np.roll(pfull[ry], xs)
            img[y] = row
            prio[y] = prow
        # sprites
        sat = (R[5] & 0x7E) << 7
        tall = bool(R[1] & 2)
        h = 16 if tall else 8
        base = 256 if R[6] & 4 else 0
        shift = 8 if R[0] & 8 else 0
        count = np.zeros(192, int)
        overflow = []
        spr = np.full((192, 256), 255, np.uint8)
        for n in range(64):
            y = self.vram[sat + n]
            if y == 0xD0:
                break
            y = y + 1
            if y > 240: y -= 256
            x = self.vram[sat + 128 + n * 2] - shift
            t = self.vram[sat + 128 + n * 2 + 1] + base
            if tall: t &= ~1
            for row in range(h):
                ly = y + row
                if 0 <= ly < 192:
                    if count[ly] >= 8:
                        overflow.append(ly); continue
                    count[ly] += 1
                    pix = self.tiles[(t + (row >> 3)) & 511][row & 7]
                    for px in range(8):
                        lx = x + px
                        if 0 <= lx < 256 and pix[px] and spr[ly, lx] == 255:
                            spr[ly, lx] = pix[px] + 16
        m = (spr != 255) & ~prio
        img[m] = spr[m]
        if R[0] & 0x20:
            img[:, :8] = bg
        return img, overflow


class PSG:
    def __init__(self):
        self.log = []  # (cycle, value)
        self.latch = 0
        self.regs = [0, 15, 0, 15, 0, 15, 0, 15]

    def write(self, v, cyc):
        self.log.append((cyc, v))
        if v & 0x80:
            self.latch = (v >> 4) & 7
            if self.latch & 1 or self.latch == 6:
                self.regs[self.latch] = v & 15
            else:
                self.regs[self.latch] = (self.regs[self.latch] & 0x3F0) | (v & 15)
        else:
            if self.latch & 1 or self.latch == 6:
                self.regs[self.latch] = v & 15
            else:
                self.regs[self.latch] = (self.regs[self.latch] & 15) | ((v & 0x3F) << 4)


class SMS:
    def __init__(self, rom):
        self.rom = bytes(rom)
        if len(self.rom) < 0x8000:
            self.rom += b'\xff' * (0x8000 - len(self.rom))
        self.nbanks = max(1, len(self.rom) // 0x4000)
        self.ram = bytearray(0x2000)
        self.bank = [0, 1, 2 % self.nbanks]
        self.vdp = VDP()
        self.psg = PSG()
        self.cpu = Z80(self)
        self.pad = 0
        self.pause = False
        self.frame = 0
        self.total_cycles = 0
        self.frame_busy = []  # cycles before program waited (approx)
        self.watch = {}
        self.render_flag = False

    # bus
    def read(self, a):
        if a < 0x400:
            return self.rom[a]
        if a < 0xC000:
            b = self.bank[a >> 14] % self.nbanks
            return self.rom[b * 0x4000 + (a & 0x3FFF)]
        return self.ram[a & 0x1FFF]

    def write(self, a, v):
        if a >= 0xC000:
            self.ram[a & 0x1FFF] = v
            if a >= 0xFFFC:
                if a == 0xFFFD: self.bank[0] = v
                elif a == 0xFFFE: self.bank[1] = v
                elif a == 0xFFFF: self.bank[2] = v
        # writes to ROM ignored

    def inp(self, p):
        p &= 0xFF
        if p < 0x40:
            return 0xFF
        if p < 0x80:
            if p & 1:
                return 0  # H counter
            l = self.vdp.line
            return l if l <= 0xDA else l - 6
        if p < 0xC0:
            return self.vdp.ctrl_r() if p & 1 else self.vdp.data_r()
        if p & 1:
            return 0xFF
        return (~self.pad) & 0xFF

    def out(self, p, v):
        p &= 0xFF
        if p < 0x40:
            return
        if p < 0x80:
            self.psg.write(v, self.total_cycles)
            return
        if p < 0xC0:
            if p & 1: self.vdp.ctrl_w(v)
            else: self.vdp.data_w(v)

    def run_frame(self):
        cpu, vdp = self.cpu, self.vdp
        for line in range(LINES):
            vdp.line = line
            budget = CYCLES_PER_LINE
            while budget > 0:
                if vdp.irq():
                    c = cpu.interrupt()
                    budget -= c
                c = cpu.step()
                budget -= c
                self.total_cycles += c
            if line <= 192:
                if line == 0:
                    vdp.linecnt = vdp.reg[10]
                else:
                    vdp.linecnt -= 1
                    if vdp.linecnt < 0:
                        vdp.linecnt = vdp.reg[10]
                        vdp.line_irq = True
            else:
                vdp.linecnt = vdp.reg[10]
            if line == 192:
                vdp.status |= 0x80
                if self.render_flag:
                    self.render_now()
        self.frame += 1

    def render_now(self):
        img, ovf = self.vdp.render()
        self.last_index = img
        self.last_overflow = ovf
        self.last_pal = self.vdp.palette_rgb()

    def run_frames(self, n, pad=None, every=None):
        for i in range(n):
            if pad is None:
                self.pad = 0
            else:
                p = pad(self.frame)
                if p == 'PAUSE':
                    self.cpu.nmi()
                    p = 0
                self.pad = p
            self.render_flag = bool(every) or i == n - 1
            self.run_frame()
            if every:
                every(self)

    def rgb(self):
        return self.last_pal[self.last_index]

    def screenshot(self, fn, scale=2):
        from PIL import Image
        im = Image.fromarray(self.rgb())
        if scale != 1:
            im = im.resize((256 * scale, 192 * scale), Image.NEAREST)
        im.save(fn)
