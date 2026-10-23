#!/usr/bin/env python3
"""Compose the requested phrase from glyphs read back out of a PSF2 file."""
import argparse, struct, unicodedata
from pathlib import Path
from PIL import Image
from join import join_word

def load(path):
    raw=Path(path).read_bytes(); magic,version,hs,flags,n,bpg,h,w=struct.unpack_from("<4s7I",raw,0)
    bpr=(w+7)//8; pos=hs+n*bpg; m={}
    for i in range(n):
        while True:
            cp,=struct.unpack_from("<H",raw,pos);pos+=2
            if cp==0xffff: break
            m[cp]=i
    cells={}
    for cp,i in m.items():
        start=hs+i*bpg; cells[cp]=[[bool(raw[start+y*bpr+x//8]&(0x80>>(x%8))) for x in range(w)] for y in range(h)]
    return w,h,cells

def forms():
    m={}
    for cp in range(0xfe70,0xfefd):
        d=unicodedata.decomposition(chr(cp)).split()
        if len(d)==2 and d[0].startswith("<"):
            pos={"isolated":"isol","final":"fina","initial":"init","medial":"medi"}.get(d[0][1:-1])
            if pos: m[(int(d[1],16),pos)]=cp
    return m

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--psf",default="out/unifont-8x24.psfu"); ap.add_argument("--out",default="out/preview-unifont.png"); ap.add_argument("--scale",type=int,default=12); a=ap.parse_args()
    w,h,cells=load(a.psf); fm=forms(); phrase="بسم الله الرحمن الرحيم"; logical=[]; missing=[]
    tokens = phrase.split()
    for token_i, token in enumerate(reversed(tokens)):
        for name,pos in reversed(join_word(token)):
            if name=="lam-alef": missing.append(f"{name}-{pos}"); logical.append(None); continue
            base=ord({v:k for k,v in {"ا":"alef","ب":"beh","ت":"teh","ث":"theh","ج":"jeem","ح":"hah","خ":"khah","د":"dal","ذ":"thal","ر":"reh","ز":"zain","س":"seen","ش":"sheen","ص":"sad","ض":"dad","ط":"tah","ظ":"zah","ع":"ain","غ":"ghain","ف":"feh","ق":"qaf","ك":"kaf","ل":"lam","م":"meem","ن":"noon","ه":"heh","و":"waw","ي":"yeh"}.items()}[name])
            cp=fm.get((base,pos));
            if cp is None or cp not in cells: missing.append(f"{name}-{pos}"); logical.append(None)
            else: logical.append(cells[cp])
        if token_i != len(tokens) - 1: logical.append(None) # word gap
    canvas=[[False]*(len(logical)*w) for _ in range(h)]
    for i,cell in enumerate(logical):
        if cell:
            for y in range(h):
                for x in range(w): canvas[y][i*w+x]=cell[y][x]
    im=Image.new("1",(len(visual)*w,h),0)
    for y in range(h):
        for x in range(len(canvas[0])):
            if canvas[y][x]: im.putpixel((x,y),1)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); im.resize((im.width*a.scale,im.height*a.scale),Image.Resampling.NEAREST).save(out)
    print(f"phrase={phrase!r} source={a.psf}"); print(f"PNG: {out} size={im.size} scale={a.scale} nearest")
    print("unplaced=" + (", ".join(sorted(set(missing))) if missing else "none"))

if __name__=="__main__": main()
