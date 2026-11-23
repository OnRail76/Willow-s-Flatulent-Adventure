import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bot import *
def start(m):
    m.run_frames(60); m.run_frames(6, pad=lambda f: B1); m.run_frames(200)
def goto(m, room, scr):
    c = m.cpu
    for _ in range(200000):
        if c.halted and c.pc == S['wait_vblank.w'] and c.iff1: break
        c.step()
    assert c.halted and c.pc == S['wait_vblank.w'], hex(c.pc)
    c.halted = False
    c.sp = (c.sp + 2) & 0xFFFF          # drop wait_vblank return
    m.ram[S['room_num'] - 0xC000] = room
    m.ram[S['screen_num'] - 0xC000] = scr
    c.pc = S['new_screen']
