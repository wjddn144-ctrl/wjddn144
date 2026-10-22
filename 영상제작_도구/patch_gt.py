import subprocess, numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad/'
V=open(S+'v9path.txt').read().strip()
W,H=960,720; FPS=30
BHS=S+'fonts/BlackHanSans-Regular.ttf'; DH=S+'fonts/DoHyeon-Regular.ttf'
def F(p,s): return ImageFont.truetype(p,s)

def badge(w,h,lines,sizes,bg=(31,122,63),fg=(255,255,255),border=(245,197,24),r=12):
    sc=2; im=Image.new('RGBA',(w*sc,h*sc),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,w*sc-1,h*sc-1],radius=r*sc,fill=border+(255,))
    d.rounded_rectangle([5*sc,5*sc,w*sc-6*sc,h*sc-6*sc],radius=(r-2)*sc,fill=bg+(255,))
    tot=sum(sizes)*1.1; y=(h-tot)/2
    for ln,sz in zip(lines,sizes):
        f=F(BHS,sz*sc)
        while d.textlength(ln,font=f)>(w-24)*sc and sz>12: sz-=2; f=F(BHS,sz*sc)
        tb=d.textbbox((0,0),ln,font=f)
        d.text(((w*sc-(tb[2]-tb[0]))/2-tb[0],y*sc-tb[1]),ln,font=f,fill=fg); y+=sz*1.1
    return im.resize((w,h),Image.LANCZOS)
def dot(sz):
    sc=3; im=Image.new('RGBA',(sz*sc,sz*sc),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,sz*sc-1,sz*sc-1],fill=(245,197,24,255)); d.ellipse([4*sc,4*sc,sz*sc-5*sc,sz*sc-5*sc],fill=(31,122,63,255))
    f=F(BHS,int(sz*0.5)*sc); tb=d.textbbox((0,0),'구',font=f)
    d.text(((sz*sc-(tb[2]-tb[0]))/2-tb[0],(sz*sc-(tb[3]-tb[1]))/2-tb[1]),'구',font=f,fill=(255,255,255,255))
    return im.resize((sz,sz),Image.LANCZOS)
CARD_BADGE=badge(620,200,['광산장년구역장'],[84])
yy,xx=np.mgrid[0:H,0:W]
def card_bg(t,seed=0):
    r=np.hypot(xx-W/2,yy-H/2)/600.0
    base=np.stack([20+40*(1-r),120+70*(1-r),60+40*(1-r)],-1).clip(0,255)
    ang=(xx-W/2)*math.cos(0.5+seed)+(yy-H/2)*math.sin(0.5+seed)
    rays=(np.sin(ang/38.0+t*2.5)>0.55)*22.0
    base+=rays[...,None]*np.array([0.6,1.0,0.5])
    return Image.fromarray(base.clip(0,255).astype(np.uint8))
def card_frame(t,t0,seed):
    im=card_bg(t,seed).convert('RGBA'); k=1+0.06*math.sin((t-t0)*7)
    b=CARD_BADGE.resize((int(CARD_BADGE.width*k),int(CARD_BADGE.height*k)),Image.LANCZOS).rotate(-14+8*math.sin((t-t0)*4),expand=True,resample=Image.BICUBIC)
    im.alpha_composite(b,(int(W/2-b.width/2),int(H/2-b.height/2)))
    return im.convert('RGB')
CARDS=[(5.333,6.366,0.0),(8.133,9.833,1.2),(16.4997,17.733,2.1)]

CAPS=[(6.366,7.433,'영혼의 갈증을 풀어 주는 사랑'),(18.9663,20.1997,'꾸미지 않아야 한다'),(22.033,23.0663,'말보다 마음이 먼저여야 한다')]
def caption_frame(a,text,t,t0):
    a=a.copy(); y0,y1=0,720
    L=a[y0:y1,0:30].astype(np.float32).mean(1); R=a[y0:y1,930:960].astype(np.float32).mean(1)
    w=np.linspace(0,1,W)[None,:,None]; fill=L[:,None,:]*(1-w)+R[:,None,:]*w
    a[y0:y1]=np.clip(fill,0,255).astype(np.uint8)
    im=Image.fromarray(a).convert('RGBA'); lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    sz=96
    while True:
        f=F(DH,sz)
        if d.textlength(text,font=f)<=860 or sz<40: break
        sz-=2
    k=min(1.0,(t-t0)/0.12); k=max(k,0.01)
    tb=d.textbbox((0,0),text,font=f)
    tx=(W-(tb[2]-tb[0]))/2-tb[0]; ty=360-(tb[3]-tb[1])/2-tb[1]
    d.text((tx+4,ty+4),text,font=f,fill=(0,60,20,200)); d.text((tx,ty),text,font=f,fill=(255,255,255,255))
    if k<1.0:
        lay=lay.resize((max(2,int(W*(0.8+0.2*k))),max(2,int(H*(0.8+0.2*k)))),Image.LANCZOS)
        full=Image.new('RGBA',(W,H),(0,0,0,0)); full.paste(lay,((W-lay.width)//2,(H-lay.height)//2)); lay=full
    im.alpha_composite(lay); return np.asarray(im.convert('RGB'))

# ---- end card (replaces bottle, cans, 제일제당 logo, billboard) ----
BOTTLE=badge(430,640,['광산장년','구역장','응원합니다'],[88,108,46],bg=(24,96,52))
LOGOB=badge(390,84,['광산장년회'],[54],bg=(20,60,40),r=8)
BOARD=badge(290,255,['영혼의 갈증은','역시','구역장님'],[40,52,52],bg=(240,248,240),fg=(31,122,63),border=(31,122,63))

KF_W=[(15.77,471,436,80,80),(16.5,490,440,80,80)]
KF_D=[(17.73,390,410,230,150),(17.8,390,410,230,150),(18.0,415,380,240,150),(18.2,435,300,270,190),(18.4,450,245,300,170),(18.6,465,232,330,140),(18.8,485,222,310,180),(18.97,485,222,310,180)]
KF_G=[(24.77,205,385,56,76),(25.3,322,412,56,70),(25.7,312,450,56,72),(26.1,282,450,60,80),(26.5,280,425,62,140),(26.9,280,420,62,135),(28.95,283,435,62,138),(29.0,283,435,62,138)]
KF_L=[(24.77,735,297,56,60),(25.3,735,330,56,70),(25.7,745,400,56,80),(26.1,750,430,56,80),(26.5,752,440,56,86),(28.95,734,446,52,86),(29.0,734,446,52,86)]
def kf(k,t):
    ts=[q[0] for q in k]
    return [float(np.interp(t,ts,[q[i] for q in k])) for i in (1,2,3,4)]
_bc={}
def get_badge(w,h):
    key=(int(round(w/6)*6),int(round(h/6)*6))
    if key not in _bc:
        w2,h2=key
        _bc[key]=dot(min(w2,h2)) if max(w2,h2)<=90 and abs(w2-h2)<=30 else badge(w2,h2,['광산장년구역장'] if w2>=h2*1.6 else ['광산장년','구역장'],[int(min(h2*0.42,w2*0.2))] if w2>=h2*1.6 else [int(min(h2*0.22,w2*0.34))]*2,r=10)
    return _bc[key]
def paste_kf(im,k,t):
    cx,cy,w,h=kf(k,t); b=get_badge(w,h); im.paste(b,(int(cx-b.width/2),int(cy-b.height/2)),b)

dec=subprocess.Popen(['ffmpeg','-v','error','-i',V,'-vf','scale=960:720:flags=lanczos,fps=30','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',S+'gt_patched.mp4'],stdin=subprocess.PIPE)
n=0; sz=W*H*3
while True:
    buf=dec.stdout.read(sz)
    if len(buf)<sz: break
    a=np.frombuffer(buf,dtype=np.uint8).reshape(H,W,3).copy(); t=n/FPS
    done=False
    for (c0,c1,seed) in CARDS:
        if c0<=t<c1: a=np.asarray(card_frame(t,c0,seed)); done=True
    for (c0,c1,txt) in CAPS:
        if c0<=t<c1: a=caption_frame(a,txt,t,c0); done=True
    if not done:
        im=None
        if 15.77<=t<16.4997:
            im=Image.fromarray(a); paste_kf(im,KF_W,t)
        elif 17.733<=t<18.9663:
            im=Image.fromarray(a); paste_kf(im,KF_D,t)
        elif 24.77<=t<29.0:
            im=Image.fromarray(a); paste_kf(im,KF_G,t); paste_kf(im,KF_L,t)
        elif t>=29.0:
            im=Image.fromarray(a)
            k=min(1.0,(t-29.0)/0.3); k=max(k,0.02)
            bo=BOTTLE.resize((max(2,int(BOTTLE.width*k)),max(2,int(BOTTLE.height*k))),Image.LANCZOS)
            im.paste(bo,(int(55+(430-bo.width)/2),int(85+(640-bo.height)/2)),bo)
            im.paste(LOGOB,(500,590),LOGOB)
            im.paste(BOARD,(572,8),BOARD)
        if im is not None: a=np.asarray(im)
    enc.stdin.write(np.ascontiguousarray(a).tobytes()); n+=1
enc.stdin.close(); enc.wait(); print('frames',n)
