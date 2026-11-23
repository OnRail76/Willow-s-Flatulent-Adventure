#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 gfx/build_gfx.py
python3 src/levels.py
python3 src/music.py
python3 tools/zasm.py src/main.asm -o build/willow.sms --size 0x8000 --sms --sym build/willow.sym --lst build/willow.lst
