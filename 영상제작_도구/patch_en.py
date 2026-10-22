import subprocess, numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad/'
V=open(S+'v6path.txt').read().strip()
W,H=960,720; FPS=30
BHS=S+'fonts/BlackHanSans-Regular.ttf'; JUA=S+'fonts/Jua-Regular.ttf'; GG=S+'fonts/Gaegu-Bold.ttf'
def F(p,sz): return ImageFont.truetype(p,sz)

# ---------- helpers ----------
def blur_sum(a,r):
    k=np.ones(2*r+1,dtype=np.float32)
    a=np.apply_along_axis(lambda m:np.convolve(m,k,'same'),0,a)
    a=np.apply_along_axis(lambda m:np.convolve(m,k,'same'),1,a)
    return a
def inpaint(region,mask,iters=3,r=6):
    """fill masked pixels with the average of nearby unmasked pixels"""
    reg=region.astype(np.float32).copy(); m=(~mask).astype(np.float32)
    for _ in range(iters):
        num=np.stack([blur_sum(reg[...,c]*m,r) for c in range(3)],-1); den=blur_sum(m,r)[...,None]+1e-3
        fill=num/den; reg=np.where(mask[...,None],fill,reg); m=np.maximum(m,mask.astype(np.float32)*(den[...,0]>1))
    return reg.clip(0,255).astype(np.uint8)
def dilate(mask,r):
    return blur_sum(mask.astype(np.float32),r)>0
def luma(a): return (a[...,0]*0.299+a[...,1]*0.587+a[...,2]*0.114)
def paste_rot(base,layer,cx,cy,ang):
    l=layer.rotate(ang,expand=True,resample=Image.BICUBIC)
    base.paste(l,(int(cx-l.width/2),int(cy-l.height/2)),l)

# ---------- cached graphics ----------
def sticker(w,h,txt,size):
    s=3; im=Image.new('RGBA',(w*s,h*s),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,w*s-1,h*s-1],radius=10*s,fill=(245,197,24,255))
    d.rounded_rectangle([5*s,5*s,w*s-6*s,h*s-6*s],radius=8*s,fill=(31,122,63,255))
    sz=size*s
    while True:                                   # shrink the text until it fits inside the badge
        f=F(BHS,sz); tb=d.textbbox((0,0),txt,font=f)
        if tb[2]-tb[0]<=(w-22)*s or sz<20: break
        sz-=2
    d.text(((w*s-(tb[2]-tb[0]))/2-tb[0],(h*s-(tb[3]-tb[1]))/2-tb[1]),txt,font=f,fill=(255,255,255,255))
    return im.resize((w,h),Image.LANCZOS)
def text_layer(txt,font,size,fill,w,h,shadow=None,stroke=0,stroke_fill=None):
    s=3; im=Image.new('RGBA',(w*s,h*s),(0,0,0,0)); d=ImageDraw.Draw(im)
    f=F(font,size*s); tb=d.textbbox((0,0),txt,font=f,stroke_width=stroke*s)
    x=(w*s-(tb[2]-tb[0]))/2-tb[0]; y=(h*s-(tb[3]-tb[1]))/2-tb[1]
    if shadow: d.text((x+shadow[0]*s,y+shadow[1]*s),txt,font=f,fill=shadow[2],stroke_width=stroke*s,stroke_fill=shadow[2])
    d.text((x,y),txt,font=f,fill=fill,stroke_width=stroke*s,stroke_fill=stroke_fill)
    return im.resize((w,h),Image.LANCZOS)
BUB=text_layer('구역장님',JUA,60,(255,255,255,255),250,70,shadow=(2,2,(120,80,40,160)))
CHALK=text_layer('구역장님',GG,100,(240,240,240,255),265,125).filter(ImageFilter.GaussianBlur(0.6))
SIGN_TXT=text_layer('광산장년회',BHS,100,(255,255,255,255),470,110)
SIGN_TXT=SIGN_TXT.transform(SIGN_TXT.size,Image.AFFINE,(1,0.22,-12,0,1,0),resample=Image.BICUBIC)   # italic look
BOX_TXT=text_layer('구역장님 응원',BHS,24,(200,30,30,255),170,32)

# ---------- measured keyframes for the Energizer label: (frame, cx, cy, angle[deg, CCW], w, h) ----------
GROUPS=[
 [(0,471,401,17,185,78),(4,471,341,24,185,78),(8,479,330,23,185,78),(12,479,324,22,185,78),(15,471,324,24,185,78),(19,471,324,24,185,78),
  (22,479,351,21,185,78),(26,471,334,24,185,78),(30,479,372,25,215,105),(34,465,510,8,185,78),(38,471,396,15,185,78),(42,479,324,25,185,78),
  (45,492,337,24,185,78),(49,483,329,24,185,78),(53,545,300,-35,230,105),(57,575,300,-51,200,80),(60,567,300,-50,200,80),(64,567,296,-52,210,90),
  (68,565,360,-52,200,80),(72,571,357,-52,210,90),(75,562,280,-42,200,80),(79,562,263,-45,205,85),(83,564,265,-45,200,80),(86,564,265,-45,200,80)],
 [(99,410,40,-40,210,80),(101,412,58,-40,210,80),(104,446,92,-45,220,80),(106,460,105,-45,220,80)],
 [(316,870,575,-43,270,90),(334,870,575,-43,270,90),(337,764,566,-37,300,90),(339,682,412,-60,160,64)],
 [(344,478,410,95,115,46),(348,415,442,95,115,46)],
 [(387,693,503,115,145,52),(388,693,503,115,145,52),(392,693,477,106,145,52),(398,693,468,103,145,52),(404,701,453,100,145,52),(412,703,473,98,145,52),(424,697,477,100,145,52),(440,701,481,100,145,52),(450,701,481,100,145,52)],
]
def label_at(n):
    for g in GROUPS:
        if g[0][0]<=n<=g[-1][0]:
            ns=[k[0] for k in g]
            return [float(np.interp(n,ns,[k[i] for k in g])) for i in range(1,6)]
    return None
_stk={}
def stk(w,h):
    key=(int(round(w/5)*5),int(round(h/5)*5))
    if key not in _stk: _stk[key]=sticker(key[0],key[1],'광산장년구역장',int(key[1]*0.5))
    return _stk[key]

PL=np.median(np.stack([np.asarray(Image.open(S+f'e6/{i+1:04d}.png').convert('RGB')) for i in range(342,352)]),axis=0)[335:472,338:548].astype(np.float32)
dec=subprocess.Popen(['ffmpeg','-v','error','-i',V,'-vf','crop=960:720:160:0,fps=30','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',S+'en_patched.mp4'],stdin=subprocess.PIPE)
LAB_STICK=sticker(190,66,'광산장년회',34)
n=0; sz=W*H*3
while True:
    buf=dec.stdout.read(sz)
    if len(buf)<sz: break
    a=np.frombuffer(buf,dtype=np.uint8).reshape(H,W,3).copy()
    t=n/FPS; img=None
    def ensure():
        global img
        if img is None: img=Image.fromarray(a)
        return img
    # 1) bubble line 1  "에너자이저" -> "구역장님"
    if n<=210:
        x0,y0,x1,y1=88,62,352,134
        reg=a[y0:y1,x0:x1]; m=dilate(luma(reg.astype(np.float32))>228,3)
        a[y0:y1,x0:x1]=inpaint(reg,m,iters=4,r=7)
        im=ensure(); im=Image.fromarray(a); img=im
        im.paste(BUB,(x0+int((x1-x0-250)/2)+2,y0-2),BUB)
        a=np.asarray(im).copy(); img=None
    # 2) Energizer label on the character
    k=label_at(n)
    if k:
        im=Image.fromarray(a); paste_rot(im,stk(k[3],k[4]),k[0],k[1],k[2]); a=np.asarray(im).copy()
    # 3) wall scene: sign
    if n>=316:
        R,G,B=a[...,0].astype(int),a[...,1].astype(int),a[...,2].astype(int)
        if n>=350:
            a[0:205,225:765]=(22,22,22)
            a[0:205,225:765]=(22,22,22)
        else:
            a[0:143,235:745]=(22,22,22)
            sub=a[143:200,570:765]; r,g,b=sub[...,0].astype(int),sub[...,1].astype(int),sub[...,2].astype(int)
            mk=dilate(((r-b>18)|(r-g>35)),2); sub[mk]=(22,22,22); a[143:200,570:765]=sub
        im=Image.fromarray(a)
        im.paste(SIGN_TXT,(240,22),SIGN_TXT)
        if n>=350:
            d=ImageDraw.Draw(im,'RGBA')
            if n>=384:   # pink swoosh (same look as the original sign)
                for i in range(0,540,3):
                    x=225+i; y=196-int(i*0.085); al=int(255*min(1,i/200))
                    d.line([(x,y),(x+3,y)],fill=(255,70,170,al),width=int(4+10*(1-i/540)))
                d.line([(450,150),(740,138)],fill=(255,235,200,230),width=3)
            d.rectangle([585,158,740,190],fill=(250,235,205,255),outline=(250,235,205,255))
            im.paste(BOX_TXT,(580,158),BOX_TXT)
        a=np.asarray(im).copy()
    # 4) wall handwriting 건전지 -> 구역장님
    if n>=372:
        x1_=480 if n<384 else (522 if n<396 else 548)
        x0,y0,x1,y1=338,335,x1_,472
        cx0,cy0,cx1,cy1=x0-30,y0-30,min(x1+30,960),min(y1+30,720)     # wider context for the fill
        ctx=a[cy0:cy1,cx0:cx1].astype(np.float32); Y=luma(ctx)
        loc=blur_sum(Y,8)/((17)**2)
        m=np.zeros(Y.shape,bool); inside=(slice(y0-cy0,y1-cy0),slice(x0-cx0,x1-cx0))
        m[inside]=dilate((Y>190)&((Y-loc)>25),6)[inside]
        fill=inpaint(ctx.astype(np.uint8),m,iters=6,r=12).astype(np.float32)
        rng=np.random.default_rng(n); fill+=rng.normal(0,8,size=fill.shape[:2])[...,None]
        alpha=np.clip(blur_sum(m.astype(np.float32),3)/49.0*1.5,0,1)[...,None]
        out=np.clip(ctx*(1-alpha)+fill*alpha,0,255).astype(np.uint8)
        a[y0:y1,x0:x1]=out[inside]
        im=Image.fromarray(a); al=min(1.0,(n-372)/10)
        lay=CHALK.copy(); lay.putalpha(lay.getchannel('A').point(lambda v:int(v*al)))
        l=lay.rotate(-8,expand=True,resample=Image.BICUBIC)
        im.paste(l,(int(436-l.width/2),int(404-l.height/2)),l)
        a=np.asarray(im).copy()
    enc.stdin.write(a.tobytes()); n+=1
enc.stdin.close(); enc.wait(); print('frames',n)
