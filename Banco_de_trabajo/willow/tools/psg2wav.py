import numpy as np, wave
CLOCK = 3579545
SR = 44100
VOL = [10 ** (-i * 2 / 20) for i in range(15)] + [0.0]

def lfsr_seq(white):
    if not white:
        s = np.zeros(16); s[0] = 1; return s
    r = 0x8000; out = []
    for _ in range(65535):
        out.append(r & 1)
        fb = ((r & 1) ^ ((r >> 3) & 1))
        r = (r >> 1) | (fb << 15)
    return np.array(out, float)
WHITE = lfsr_seq(True); PER = lfsr_seq(False)

def render(log, total_cycles, fn):
    regs = [0, 15, 0, 15, 0, 15, 0, 15]
    latch = 0
    nsamp = int(total_cycles / CLOCK * SR)
    out = np.zeros(nsamp)
    phase = [0.0, 0.0, 0.0, 0.0]
    events = sorted(log)
    pos = 0; t0 = events[0][0] if events else 0
    i = 0
    seg_start = 0
    def seg(a, b):
        if b <= a: return
        n = b - a; idx = np.arange(n)
        mix = np.zeros(n)
        for c in range(3):
            per = regs[c * 2] or 1
            f = CLOCK / (32 * per)
            v = VOL[regs[c * 2 + 1]]
            if f > SR / 2 or v == 0:
                phase[c] += f * n / SR; continue
            ph = phase[c] + idx * f / SR
            mix += v * np.where((ph % 1.0) < 0.5, 1.0, -1.0)
            phase[c] = (phase[c] + n * f / SR) % 1.0
        nctl = regs[6]; v = VOL[regs[7]]
        rate = nctl & 3
        per = (0x10, 0x20, 0x40)[rate] if rate < 3 else (regs[4] or 1)
        shift_f = CLOCK / (16 * per * 2)
        seqn = WHITE if nctl & 4 else PER
        ph = phase[3] + idx * shift_f / SR
        if v:
            mix += v * (seqn[(ph.astype(np.int64)) % len(seqn)] * 2 - 1)
        phase[3] = (phase[3] + n * shift_f / SR) % len(seqn)
        out[a:b] = mix
    for cyc, val in events:
        s = int((cyc - t0) / CLOCK * SR)
        s = min(s, nsamp)
        seg(pos, s); pos = s
        if val & 0x80:
            latch = (val >> 4) & 7
            if latch & 1 or latch == 6:
                regs[latch] = val & 15
            else:
                regs[latch] = (regs[latch] & 0x3F0) | (val & 15)
        else:
            if latch & 1 or latch == 6:
                regs[latch] = val & 15
            else:
                regs[latch] = (regs[latch] & 15) | ((val & 0x3F) << 4)
    seg(pos, nsamp)
    out = out / 4 * 0.9
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    w = wave.open(fn, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes()); w.close()
