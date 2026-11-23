import sys, time
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import load, syms
from psg2wav import render
song, frames, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
m = load(); S = syms()
m.run_frames(40)
cpu = m.cpu
cpu.halted = False; cpu.push((cpu.pc + 1) & 0xFFFF); cpu.a = S[song]; cpu.pc = S['snd_play_music']
m.psg.log.clear(); t0 = m.total_cycles
t=time.time(); m.run_frames(frames); print('emu s', round(time.time()-t,1))
log = [(c - t0, v) for c, v in m.psg.log]
render(log, m.total_cycles - t0, out)
