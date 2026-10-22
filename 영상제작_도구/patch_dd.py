import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad/'
V=open(S+'v8path.txt').read().strip()
W,H=960,656; FPS=30
BHS=S+'fonts/BlackHanSans-Regular.ttf'; SM=S+'fonts/SongMyung-Regular.ttf'
def F(p,s): return ImageFont.truetype(p,s)

# ---- graphics ----
def badge(w,h,lines,sizes,bg=(31,122,63),fg=(255,255,255),border=(245,197,24),rot=0,r=12):
    sc=3; im=Image.new('RGBA',(w*sc,h*sc),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,w*sc-1,h*sc-1],radius=r*sc,fill=border+(255,))
    d.rounded_rectangle([5*sc,5*sc,w*sc-6*sc,h*sc-6*sc],radius=(r-2)*sc,fill=bg+(255,))
    tot=sum(sizes)*1.1; y=(h-tot)/2
    for ln,sz in zip(lines,sizes):
        f=F(BHS,sz*sc)
        while d.textlength(ln,font=f)>(w-24)*sc and sz>14: sz-=2; f=F(BHS,sz*sc)
        tb=d.textbbox((0,0),ln,font=f)
        d.text(((w*sc-(tb[2]-tb[0]))/2-tb[0],y*sc-tb[1]),ln,font=f,fill=fg)
        y+=sz*1.1
    im=im.resize((w,h),Image.LANCZOS)
    return im.rotate(rot,expand=True,resample=Image.BICUBIC) if rot else im
def dot_badge(sz):
    sc=3; im=Image.new('RGBA',(sz*sc,sz*sc),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,sz*sc-1,sz*sc-1],fill=(245,197,24,255)); d.ellipse([4*sc,4*sc,sz*sc-5*sc,sz*sc-5*sc],fill=(31,122,63,255))
    f=F(BHS,int(sz*0.55)*sc); tb=d.textbbox((0,0),'구',font=f)
    d.text(((sz*sc-(tb[2]-tb[0]))/2-tb[0],(sz*sc-(tb[3]-tb[1]))/2-tb[1]),'구',font=f,fill=(255,255,255,255))
    return im.resize((sz,sz),Image.LANCZOS)
EMB=dot_badge(58)
def vtext(chars,x,y0,step,size):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); f=F(SM,size)
    for i,c in enumerate(chars):
        tb=d.textbbox((0,0),c,font=f)
        d.text((x-(tb[2]-tb[0])/2-tb[0],y0+i*step),c,font=f,fill=(255,255,255,255),stroke_width=3,stroke_fill=(0,0,0,255))
    return lay
TITLE=Image.alpha_composite(vtext('구역장님의',790,100,56,48),vtext('가을',790,420,56,48))
PACK=badge(640,390,['광산장년','구역장'],[125,125],rot=0)
BOX=badge(390,453,['광산장년','구역장','응원합니다'],[88,110,44],bg=(24,96,52))
LOGOBAR=badge(420,66,['광산장년회'],[46],bg=(20,60,40),r=8)

EM=[(9.95,715,446),(10.2,655,424),(10.4,611,424),(10.6,594,370),(10.8,556,276),(11.0,534,279),(11.2,512,285),(11.4,507,312),(11.65,496,312)]
TIP=[(18.085,288),(19.1,433)]
def interp(kf,t,i=1):
    ts=[k[0] for k in kf]
    return float(np.interp(t,ts,[k[i] for k in kf]))

dec=subprocess.Popen(['ffmpeg','-v','error','-i',V,'-vf','crop=1054:720:108:0,scale=960:656:flags=lanczos,fps=30','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',S+'dd_patched.mp4'],stdin=subprocess.PIPE)
n=0; sz=W*H*3
while True:
    buf=dec.stdout.read(sz)
    if len(buf)<sz: break
    a=np.frombuffer(buf,dtype=np.uint8).reshape(H,W,3).copy(); t=n/FPS
    im=None
    if 0.3<=t<4.72:
        x0,x1,y0,y1=735,845,85,555
        L=a[y0:y1,x0-8:x0-4].astype(np.float32).mean(1); R=a[y0:y1,x1+4:x1+8].astype(np.float32).mean(1)
        w=np.linspace(0,1,x1-x0)[None,:,None]
        fill=L[:,None,:]*(1-w)+R[:,None,:]*w
        fill+=np.random.default_rng(n).normal(0,3,fill.shape)
        a[y0:y1,x0:x1]=np.clip(fill,0,255).astype(np.uint8)
        im=Image.fromarray(a); im.alpha_composite if False else None
        base=im.convert('RGBA'); base.alpha_composite(TITLE); im=base.convert('RGB')
    if 9.95<=t<11.68:
        if im is None: im=Image.fromarray(a)
        ex,ey=interp(EM,t,1),interp(EM,t,2)
        im.paste(EMB,(int(ex-29),int(ey-29)),EMB)
    if 18.085<=t<19.097:
        if im is None: im=Image.fromarray(a)
        tx=interp(TIP,t); im.paste(PACK,(int(tx-20-320),int(165-195)),PACK)
    if t>=27.634:
        if im is None: im=Image.fromarray(a)
        k=min(1.0,(t-27.634)/0.25); k=max(k,0.01)
        b=BOX.resize((max(2,int(BOX.width*k)),max(2,int(BOX.height*k))),Image.LANCZOS)
        im.paste(b,(int(222+(390-b.width)/2),int(72+(453-b.height)/2)),b)
        if t>=28.4:
            k2=min(1.0,(t-28.4)/0.2); lb=LOGOBAR.resize((max(2,int(LOGOBAR.width*k2)),LOGOBAR.height),Image.LANCZOS)
            im.paste(lb,(int(285+(420-lb.width)/2),545),lb)
    if im is not None: a=np.asarray(im)
    enc.stdin.write(a.tobytes()); n+=1
enc.stdin.close(); enc.wait(); print('frames',n)
