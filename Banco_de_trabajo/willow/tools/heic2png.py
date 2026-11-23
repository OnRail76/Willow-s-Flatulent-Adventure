#!/usr/bin/env python3
"""Minimal HEIC -> PNG: parses ISOBMFF, decodes HEVC tiles with ffmpeg, composes grid."""
import struct, sys, subprocess, os, tempfile
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
data = open(src, 'rb').read()

def boxes(buf, off, end):
    while off < end:
        size, typ = struct.unpack('>I4s', buf[off:off+8])
        hdr = 8
        if size == 1:
            size = struct.unpack('>Q', buf[off+8:off+16])[0]; hdr = 16
        elif size == 0:
            size = end - off
        yield typ.decode('latin1'), off, off+hdr, off+size
        off += size

def find(buf, off, end, typ):
    for t, o, b, e in boxes(buf, off, end):
        if t == typ: return o, b, e
    return None

meta = find(data, 0, len(data), 'meta')
mb = meta[1] + 4  # full box
mend = meta[2]
items = {}
# pitm
p = find(data, mb, mend, 'pitm'); ver = data[p[1]]
primary = struct.unpack('>H', data[p[1]+4:p[1]+6])[0] if ver == 0 else struct.unpack('>I', data[p[1]+4:p[1]+8])[0]
# iinf
ii = find(data, mb, mend, 'iinf'); ver = data[ii[1]]
o = ii[1] + 4 + (2 if ver == 0 else 4)
for t, bo, b, e in boxes(data, o, ii[2]):
    v = data[b]
    if v >= 2:
        if v == 2:
            iid = struct.unpack('>H', data[b+4:b+6])[0]; q = b+8
        else:
            iid = struct.unpack('>I', data[b+4:b+8])[0]; q = b+10
        items[iid] = {'type': data[q:q+4].decode('latin1')}
# iloc
il = find(data, mb, mend, 'iloc'); b = il[1]; ver = data[b]; q = b+4
a, c = data[q], data[q+1]; q += 2
offs, lens, bases, idxs = a >> 4, a & 15, c >> 4, (c & 15 if ver in (1, 2) else 0)
def rd(n):
    global q
    v = int.from_bytes(data[q:q+n], 'big') if n else 0; q += n; return v
cnt = rd(2) if ver < 2 else rd(4)
for _ in range(cnt):
    iid = rd(2) if ver < 2 else rd(4)
    cm = (rd(2) & 15) if ver in (1, 2) else 0
    rd(2); base = rd(bases); ec = rd(2); ext = []
    for _ in range(ec):
        if idxs: rd(idxs)
        eo = rd(offs); el = rd(lens); ext.append((base+eo, el))
    items.setdefault(iid, {})['ext'] = ext; items[iid]['cm'] = cm
# iref
ir = find(data, mb, mend, 'iref')
if ir:
    ver = data[ir[1]]
    for t, bo, b, e in boxes(data, ir[1]+4, ir[2]):
        w = 2 if ver == 0 else 4
        fid = int.from_bytes(data[b:b+w], 'big'); n = int.from_bytes(data[b+w:b+w+2], 'big')
        refs = [int.from_bytes(data[b+w+2+i*w:b+w+2+(i+1)*w], 'big') for i in range(n)]
        items[fid].setdefault('ref', {})[t] = refs
# iprp
ip = find(data, mb, mend, 'iprp')
pc = find(data, ip[1], ip[2], 'ipco')
props = [(t, b, e) for t, o2, b, e in boxes(data, pc[1], pc[2])]
pm = find(data, ip[1], ip[2], 'ipma'); b = pm[1]; ver, fl = data[b], int.from_bytes(data[b+1:b+4], 'big'); q = b+4
n = rd(4)
for _ in range(n):
    iid = rd(2) if ver < 1 else rd(4); k = rd(1)
    for _ in range(k):
        if fl & 1: v = rd(2); idx = v & 0x7fff
        else: v = rd(1); idx = v & 0x7f
        if idx: items.setdefault(iid, {}).setdefault('props', []).append(props[idx-1])

def item_bytes(iid):
    if items[iid].get('cm') == 1:
        idat = find(data, mb, mend, 'idat')
        return b''.join(data[idat[1]+o:idat[1]+o+l] for o, l in items[iid]['ext'])
    return b''.join(data[o:o+l] for o, l in items[iid]['ext'])

def hvcc_annexb(b, e):
    q = b + 22; nar = data[q]; q += 1; out = b''
    for _ in range(nar):
        q += 1; nn = struct.unpack('>H', data[q:q+2])[0]; q += 2
        for _ in range(nn):
            l = struct.unpack('>H', data[q:q+2])[0]; q += 2
            out += b'\0\0\0\1' + data[q:q+l]; q += l
    return out

def decode(iid, tmp):
    hv = [p for p in items[iid]['props'] if p[0] == 'hvcC'][0]
    s = hvcc_annexb(hv[1], hv[2]); raw = item_bytes(iid); q = 0
    while q < len(raw):
        l = struct.unpack('>I', raw[q:q+4])[0]; s += b'\0\0\0\1' + raw[q+4:q+4+l]; q += 4 + l
    fn = os.path.join(tmp, f'{iid}.hevc'); open(fn, 'wb').write(s)
    png = fn + '.png'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'hevc', '-i', fn, '-frames:v', '1', png], check=True)
    return Image.open(png).convert('RGB')

tmp = tempfile.mkdtemp()
it = items[primary]
if it['type'] == 'grid':
    g = item_bytes(primary); fl = g[1]
    rows, cols = g[2]+1, g[3]+1
    if fl & 1: W, H = struct.unpack('>II', g[4:12])
    else: W, H = struct.unpack('>HH', g[4:8])
    tiles = [decode(t, tmp) for t in it['ref']['dimg']]
    tw, th = tiles[0].size
    img = Image.new('RGB', (cols*tw, rows*th))
    for i, t in enumerate(tiles): img.paste(t, ((i % cols)*tw, (i//cols)*th))
    print("grid", g[:12].hex(), rows, cols, W, H, tiles[0].size, len(tiles)); img = img.crop((0, 0, min(W,img.width), min(H,img.height)))
else:
    img = decode(primary, tmp)
for p in it.get('props', []):
    if p[0] == 'irot':
        ang = (data[p[1]] & 3) * 90
        if ang: img = img.rotate(ang, expand=True)
img.save(dst)
print(primary, it['type'], img.size)
