import subprocess, numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad/'
BHS=S+'fonts/BlackHanSans-Regular.ttf'; JUA=S+'fonts/Jua-Regular.ttf'
W,H=960,720; FPS=30; DUR=6.5; N=int(DUR*FPS)
CX,CY=W//2,300
rng=np.random.default_rng(7)

def gold_text(txt,font,size,w,h):
    s=2; f=ImageFont.truetype(font,size*s)
    m=Image.new('L',(w*s,h*s),0); d=ImageDraw.Draw(m); tb=d.textbbox((0,0),txt,font=f)
    d.text(((w*s-(tb[2]-tb[0]))/2-tb[0],(h*s-(tb[3]-tb[1]))/2-tb[1]),txt,font=f,fill=255)
    tt=np.linspace(0,1,h*s)
    top=np.array([255,244,176.]); mid=np.array([240,190,60.]); bot=np.array([150,98,18.])
    col=np.where((tt<0.5)[:,None],top+(mid-top)*(tt/0.5)[:,None],mid+(bot-mid)*((tt-0.5)/0.5)[:,None])
    grad=np.zeros((h*s,w*s,3),np.float32); grad[:]=col[:,None,:]
    ma=np.asarray(m,np.float32)/255
    edge=np.asarray(m.filter(ImageFilter.MaxFilter(9)),np.float32)/255
    out=np.zeros((h*s,w*s,4),np.float32)
    out[...,:3]=np.where(edge[...,None]>0,[70,42,6],0); out[...,3]=edge*255
    out[...,:3]=np.where(ma[...,None]>0.5,grad,out[...,:3]); out[...,3]=np.maximum(out[...,3],ma*255)
    return Image.fromarray(out.clip(0,255).astype(np.uint8),'RGBA').resize((w,h),Image.LANCZOS)
def plain_text(txt,font,size,w,h,fill,stroke=0,stroke_fill=(0,0,0,255)):
    s=2; im=Image.new('RGBA',(w*s,h*s),(0,0,0,0)); d=ImageDraw.Draw(im); f=ImageFont.truetype(font,size*s)
    tb=d.textbbox((0,0),txt,font=f,stroke_width=stroke*s)
    d.text(((w*s-(tb[2]-tb[0]))/2-tb[0],(h*s-(tb[3]-tb[1]))/2-tb[1]),txt,font=f,fill=fill,stroke_width=stroke*s,stroke_fill=stroke_fill)
    return im.resize((w,h),Image.LANCZOS)
TITLE=gold_text('총무부',BHS,235,760,300)
GLOW_T=TITLE.filter(ImageFilter.GaussianBlur(18))
HEAD=[plain_text(c,BHS,58,70,80,(255,236,170,255)) for c in '광산장년회']
TAG=plain_text('보이지 않는 곳에서, 가장 먼저 움직이는 사람들',JUA,38,900,60,(255,255,255,255),stroke=2,stroke_fill=(10,16,40,255))
LBL=[plain_text(t,BHS,34,110,50,(255,255,255,255)) for t in ('노력','헌신','섬김')]
MAXL=plain_text('MAX',BHS,30,100,44,(255,214,90,255))
FIN=plain_text('총무부, 사랑하고 응원합니다!',BHS,66,940,110,(255,255,255,255),stroke=5,stroke_fill=(120,78,10,255))
FIN_G=FIN.filter(ImageFilter.GaussianBlur(10))

yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
R=np.hypot(xx-CX,yy-CY)/(0.75*W); ANG=np.arctan2(yy-CY,xx-CX)
def bg(t):
    g=np.clip(t/0.9,0,1)*0.55+(1.0 if t>=0.9 else 0)*0.45*(0.75+0.25*math.sin(t*2.0))
    base=np.zeros((H,W,3),np.float32); base[...]=[6,9,24]
    glow=np.exp(-R*2.2)*g
    base+=glow[...,None]*np.array([95,66,14],np.float32)
    rays=(0.5+0.5*np.sin(ANG*11+t*0.9))**4*np.exp(-R*1.4)*g
    base+=rays[...,None]*np.array([70,52,18],np.float32)
    base*= (1-0.55*np.clip(R*1.1,0,1))[...,None]
    return base
def add(a,layer): return np.clip(a+np.asarray(layer.convert('RGB'),np.float32),0,255)
# particles
NP=170; P_ang=rng.uniform(0,2*np.pi,NP); P_spd=rng.uniform(160,950,NP); P_sz=rng.uniform(1.6,4.8,NP)
P_col=np.where(rng.random((NP,1))<0.7,np.array([255,214,100]),np.array([255,255,235])).astype(np.float32)
# stars (sparkles) background
ST=[(rng.uniform(0,W),rng.uniform(0,H*0.8),rng.uniform(0.6,1.6),rng.uniform(0,6.28)) for _ in range(60)]
# confetti
NC=140; C_x=rng.uniform(0,W,NC); C_v=rng.uniform(170,380,NC); C_t0=rng.uniform(0,0.9,NC); C_w=rng.uniform(5,11,NC); C_a=rng.uniform(0,6.28,NC); C_om=rng.uniform(-6,6,NC); C_sw=rng.uniform(10,40,NC)
C_cols=[(255,214,90),(255,90,90),(60,210,120),(255,255,255),(90,170,255),(255,150,60)]
C_col=[C_cols[i] for i in rng.integers(0,len(C_cols),NC)]
def ease(x): x=min(1,max(0,x)); return 1-(1-x)**3

enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',S+'end_epic.mp4'],stdin=subprocess.PIPE)
for n in range(N):
    t=n/FPS; a=bg(t)
    # sparkle stars
    lay=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(lay)
    for (sx,sy,sz,ph) in ST:
        tw=0.5+0.5*math.sin(t*3+ph)
        if t>0.3: d.ellipse([sx-sz,sy-sz,sx+sz,sy+sz],fill=(int(220*tw),int(200*tw),int(130*tw)))
    # lens streak
    if 0.15<=t<1.15:
        k=math.sin(math.pi*(t-0.15)/1.0); wlen=int(W*0.95*k)
        d.rectangle([CX-wlen//2,CY-3,CX+wlen//2,CY+3],fill=(255,240,200))
        d.rectangle([CX-3,CY-int(120*k),CX+3,CY+int(120*k)],fill=(255,230,170))
    # shockwave + particles
    tau=t-0.9
    if tau>=0:
        rr=950*(1-math.exp(-3.6*tau)); wd=max(1,int(22*math.exp(-3*tau))); al=math.exp(-2.2*tau)
        d.ellipse([CX-rr,CY-rr,CX+rr,CY+rr],outline=(int(255*al),int(205*al),int(95*al)),width=wd)
        for i in range(NP):
            life=1.9
            if tau>life: continue
            dist=P_spd[i]*(1-math.exp(-2.2*tau))/2.2
            px=CX+math.cos(P_ang[i])*dist; py=CY+math.sin(P_ang[i])*dist+260*tau*tau
            f=max(0,1-tau/life); r=P_sz[i]*(0.6+0.6*f)
            c=tuple(int(v*f) for v in P_col[i]); d.ellipse([px-r,py-r,px+r,py+r],fill=c)
    lay=lay.filter(ImageFilter.GaussianBlur(2.2))
    a=add(a,lay)
    img=Image.fromarray(a.astype(np.uint8)).convert('RGBA')
    # title
    if tau>=0:
        sc=1+0.75*math.exp(-9*tau); sh=16*math.exp(-8*tau)
        tw_,th_=int(TITLE.width*sc),int(TITLE.height*sc)
        gl=GLOW_T.resize((tw_,th_),Image.LANCZOS); tl=TITLE.resize((tw_,th_),Image.LANCZOS)
        ox=int(sh*math.sin(tau*95)); oy=int(sh*math.cos(tau*83))
        glow_a=int(255*(0.7+0.3*math.sin(t*3)))
        gl.putalpha(gl.getchannel('A').point(lambda v:min(255,int(v*0.9))))
        img.alpha_composite(gl,(CX-tw_//2+ox,CY-th_//2+oy)); img.alpha_composite(tl,(CX-tw_//2+ox,CY-th_//2+oy))
        # light sweep across the title
        sw=((tau-0.9)/0.7)
        if 0<sw<1:
            sweep=Image.new('RGBA',img.size,(0,0,0,0)); sd=ImageDraw.Draw(sweep)
            x0=CX-380+760*sw
            sd.polygon([(x0,CY-130),(x0+60,CY-130),(x0+10,CY+130),(x0-50,CY+130)],fill=(255,255,255,120))
            msk=tl.getchannel('A'); full=Image.new('L',img.size,0); full.paste(msk,(CX-tw_//2+ox,CY-th_//2+oy))
            sweep.putalpha(ImageChops.multiply(sweep.getchannel('A'),full)); img.alpha_composite(sweep)
    # header letters
    for i,ch in enumerate(HEAD):
        t0=1.6+0.13*i
        if t>=t0:
            e=ease((t-t0)/0.35); l=ch.copy(); l.putalpha(l.getchannel('A').point(lambda v:int(v*e)))
            img.alpha_composite(l,(int(CX-5*70/2+i*70-35+ (5*70-5*70)/2),int(112+(1-e)*-30)))
    # tagline
    if t>=2.2:
        e=ease((t-2.2)/0.5); l=TAG.copy(); l.putalpha(l.getchannel('A').point(lambda v:int(v*e)))
        img.alpha_composite(l,(CX-450,int(468+(1-e)*24)))
    # stat bars
    stats_alpha=1.0 if t<4.35 else max(0,1-(t-4.35)/0.3)
    if t>=2.9 and stats_alpha>0:
        dd=ImageDraw.Draw(img,'RGBA')
        for i,(lb,t0) in enumerate(zip(LBL,(2.9,3.2,3.5))):
            y=548+i*56; e=ease((t-t0)/0.55)
            lab=lb.copy(); lab.putalpha(lab.getchannel('A').point(lambda v:int(v*stats_alpha))); img.alpha_composite(lab,(80,y-25))
            dd.rounded_rectangle([200,y-13,700,y+13],radius=13,fill=(22,24,36,int(235*stats_alpha)),outline=(255,230,150,int(190*stats_alpha)),width=2)
            fw=int(496*e)
            if fw>8:
                for xx_ in range(fw):
                    c=int(160+95*xx_/496); dd.line([(202+xx_,y-11),(202+xx_,y+11)],fill=(255,min(255,c),60,int(255*stats_alpha)))
            if e>=1:
                mx=MAXL.copy(); fl=0.65+0.35*math.sin((t-t0)*14); mx.putalpha(mx.getchannel('A').point(lambda v:int(v*stats_alpha*fl))); img.alpha_composite(mx,(716,y-22))
    # final line
    if t>=4.4:
        e=ease((t-4.4)/0.4); sc=1+0.35*(1-e)
        fw_,fh_=int(FIN.width*sc),int(FIN.height*sc)
        g2=FIN_G.resize((fw_,fh_)); f2=FIN.resize((fw_,fh_))
        for L in (g2,f2): L.putalpha(L.getchannel('A').point(lambda v:int(v*e)))
        img.alpha_composite(g2,(CX-fw_//2,598-fh_//2)); img.alpha_composite(f2,(CX-fw_//2,598-fh_//2))
    # confetti
    if t>=4.3:
        cd=ImageDraw.Draw(img,'RGBA')
        for i in range(NC):
            tt=t-4.3-C_t0[i]
            if tt<0: continue
            y=-20+C_v[i]*tt; x=C_x[i]+C_sw[i]*math.sin(tt*3+C_a[i])
            if y>H+20: continue
            ang=C_a[i]+C_om[i]*tt; wv=C_w[i]; hv=wv*1.9*abs(math.cos(tt*5+C_a[i]))+2
            ca,sa=math.cos(ang),math.sin(ang)
            pts=[(x+ca*dx-sa*dy,y+sa*dx+ca*dy) for dx,dy in ((-wv,-hv),(wv,-hv),(wv,hv),(-wv,hv))]
            cd.polygon(pts,fill=C_col[i]+(235,))
    # white flash on impact
    if tau>=0:
        fl=0.85*math.exp(-11*tau)
        if fl>0.01: img=Image.blend(img.convert('RGB'),Image.new('RGB',img.size,(255,248,230)),fl).convert('RGBA')
    enc.stdin.write(np.asarray(img.convert('RGB')).tobytes())
enc.stdin.close(); enc.wait(); print('done',N)
