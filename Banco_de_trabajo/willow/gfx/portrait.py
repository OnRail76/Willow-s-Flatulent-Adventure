import sys
from PIL import Image
import numpy as np
SMS = [(r,g,b) for r in range(4) for g in range(4) for b in range(4)]
def build(src, box, size, ncol, fixed, out_preview=None, dither=True):
    im = Image.open(src).convert('RGB').crop(box).resize((size,size), Image.LANCZOS)
    # boost contrast a bit
    from PIL import ImageEnhance
    im = ImageEnhance.Contrast(im).enhance(1.25)
    im = ImageEnhance.Color(im).enhance(1.1)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    # oval vignette: outside -> black
    m = Image.new('L',(size,size),0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).ellipse((1,1,size-2,size-2),fill=255)
    im = Image.composite(im, Image.new('RGB',(size,size),(0,0,0)), m)
    a = np.asarray(im, float).reshape(-1,3)
    SP = np.array(SMS, float)*85
    near = ((a[:,None,:]-SP[None])**2).sum(2).argmin(1)
    counts = np.bincount(near, minlength=64)
    order = [SMS[i] for i in np.argsort(-counts) if counts[i]>0]
    cols = [c for c in order if c not in fixed][:ncol-len(fixed)]
    palette = list(fixed) + cols
    # remap with FS dither against sms palette
    arr = np.asarray(im, float)
    P = np.array([[c[0]*85,c[1]*85,c[2]*85] for c in palette], float)
    idx = np.zeros((size,size), np.uint8)
    for y in range(size):
        for x in range(size):
            old = arr[y,x].copy()
            d = ((P-old)**2).sum(1)
            d[0]+=0 
            i = int(d.argmin()); idx[y,x]=i
            if dither:
                err = (old-P[i])*0.35
                if x+1<size: arr[y,x+1]+=err*7/16
                if y+1<size:
                    if x>0: arr[y+1,x-1]+=err*3/16
                    arr[y+1,x]+=err*5/16
                    if x+1<size: arr[y+1,x+1]+=err*1/16
    if out_preview:
        rgb = P[idx].astype(np.uint8)
        Image.fromarray(rgb).resize((size*4,size*4),Image.NEAREST).save(out_preview)
    return idx, palette
if __name__=='__main__':
    idx,pal=build(__import__('os').path.join(__import__('os').path.dirname(__file__),'willow_foto.png'),(640,330,2040,1730),96,16,[(0,0,0),(3,3,3),(3,3,0)],'/tmp/portrait.png')
    print(len(pal),pal)
