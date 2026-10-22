import subprocess, numpy as np, cv2, sys
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad/'
V=open(S+'v10path.txt').read().strip()
W,H=1280,720; FPS=30; T0=13.0; DUR=32.88
BHS=S+'fonts/BlackHanSans-Regular.ttf'; GG=S+'fonts/Gaegu-Bold.ttf'; JUA=S+'fonts/Jua-Regular.ttf'
def F(p,s): return ImageFont.truetype(p,s)
GREEN=(31,122,63); GOLD=(245,197,24)

def pil_to_bgr(im): return cv2.cvtColor(np.asarray(im.convert('RGB')),cv2.COLOR_RGB2BGR)
def make_banner(w,h):
    s=2; im=Image.new('RGB',(w*s,h*s),(246,246,240)); d=ImageDraw.Draw(im)
    r=int(h*0.36*s); cx=int(h*0.55*s); cy=h*s//2
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=GOLD); d.ellipse([cx-r+7,cy-r+7,cx+r-7,cy+r-7],fill=GREEN)
    f=F(BHS,int(r*0.62)); tb=d.textbbox((0,0),'구역장',font=f); d.text((cx-(tb[2]-tb[0])/2-tb[0],cy-(tb[3]-tb[1])/2-tb[1]),'구역장',font=f,fill=(255,255,255))
    x0=cx+r+int(h*0.12*s)
    for txt,yy,sz in (('구역장님이랑',0.30,0.26),('잘했군 잘했어',0.68,0.26)):
        f=F(GG,int(h*sz*s)*1)
        while d.textlength(txt,font=f)>(w*s-x0-int(h*0.1*s)) and f.size>20: f=F(GG,f.size-2)
        tb=d.textbbox((0,0),txt,font=f); d.text((x0,int(h*yy*s)-(tb[3]-tb[1])/2-tb[1]),txt,font=f,fill=(30,30,30))
    return pil_to_bgr(im.resize((w,h),Image.LANCZOS))
def badge_img(w,h,lines,sizes,r=10):
    sc=2; im=Image.new('RGBA',(w*sc,h*sc),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,w*sc-1,h*sc-1],radius=r*sc,fill=GOLD+(255,)); d.rounded_rectangle([4*sc,4*sc,w*sc-5*sc,h*sc-5*sc],radius=(r-2)*sc,fill=GREEN+(255,))
    tot=sum(sizes)*1.1; y=(h-tot)/2
    for ln,sz in zip(lines,sizes):
        f=F(BHS,sz*sc)
        while d.textlength(ln,font=f)>(w-14)*sc and sz>10: sz-=2; f=F(BHS,sz*sc)
        tb=d.textbbox((0,0),ln,font=f); d.text(((w*sc-(tb[2]-tb[0]))/2-tb[0],y*sc-tb[1]),ln,font=f,fill=(255,255,255,255)); y+=sz*1.1
    return im.resize((w,h),Image.LANCZOS)
def dot_img(sz):
    sc=3; im=Image.new('RGBA',(sz*sc,sz*sc),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,sz*sc-1,sz*sc-1],fill=GOLD+(255,)); d.ellipse([3*sc,3*sc,sz*sc-4*sc,sz*sc-4*sc],fill=GREEN+(255,))
    f=F(BHS,int(sz*0.52)*sc); tb=d.textbbox((0,0),'구',font=f); d.text(((sz*sc-(tb[2]-tb[0]))/2-tb[0],(sz*sc-(tb[3]-tb[1]))/2-tb[1]),'구',font=f,fill=(255,255,255,255))
    return im.resize((sz,sz),Image.LANCZOS)
def paste_rgba(a,layer,cx,cy):
    h,w=layer.height,layer.width; x0=int(round(cx-w/2)); y0=int(round(cy-h/2))
    xs0,ys0=max(0,x0),max(0,y0); xs1,ys1=min(W,x0+w),min(H,y0+h)
    if xs1<=xs0 or ys1<=ys0: return
    L=np.asarray(layer)[ys0-y0:ys1-y0,xs0-x0:xs1-x0].astype(np.float32); al=L[...,3:4]/255.0
    rgb=L[...,:3][...,::-1]
    a[ys0:ys1,xs0:xs1]=np.clip(a[ys0:ys1,xs0:xs1]*(1-al)+rgb*al,0,255).astype(np.uint8)

def hsv(a): return cv2.cvtColor(a,cv2.COLOR_BGR2HSV)
state={}
def smooth(key,val,k=0.6):
    p=state.get(key)
    if p is None: state[key]=val; return val
    new=tuple(k*pv+(1-k)*nv for pv,nv in zip(p,val)); state[key]=new; return new

def patch_banner(a,t):
    x0,y0,x1,y1=300,70,1240,430
    roi=a[y0:y1,x0:x1]; b,g,r=[roi[...,i].astype(int) for i in range(3)]
    mn=np.minimum(np.minimum(r,g),b); mx=np.maximum(np.maximum(r,g),b)
    m=((mx-mn<40)&(((r+g+b)//3)>105)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((31,31),np.uint8))
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not cnts: return a
    c=max(cnts,key=cv2.contourArea)
    if cv2.contourArea(c)<60000: return a
    rect=cv2.minAreaRect(c)
    box=cv2.boxPoints(rect).astype(np.float32)
    box=box[np.argsort(box[:,1])]; top=box[:2][np.argsort(box[:2,0])]; bot=box[2:][np.argsort(box[2:,0])]
    quad=np.array([top[0],top[1],bot[1],bot[0]],np.float32)
    quad=np.array([smooth(f'q{i}',tuple(quad[i]),0.5) for i in range(4)],np.float32)
    w=int(np.linalg.norm(quad[1]-quad[0])); h=int(np.linalg.norm(quad[3]-quad[0]))
    if w<300 or h<120: return a
    ban=make_banner(w,h)
    src=np.array([[0,0],[w,0],[w,h],[0,h]],np.float32)
    off=np.array([x0,y0],np.float32)
    Mx=cv2.getPerspectiveTransform(src,quad+off)
    warped=cv2.warpPerspective(ban,Mx,(W,H),flags=cv2.INTER_LINEAR)
    # exact banner shape = filled contour (so nothing outside the real banner is touched)
    mask=np.zeros((H,W),np.uint8); cv2.drawContours(mask,[c+np.array([[x0,y0]],np.int32)],-1,255,-1)
    mask=cv2.dilate(mask,np.ones((5,5),np.uint8)); mask=cv2.GaussianBlur(mask,(0,0),1.5).astype(np.float32)[...,None]/255.0
    shade=np.clip(a.astype(np.float32).mean()/150.0,0.6,1.0)
    a[:]=np.clip(a*(1-mask)+warped*mask*0.62,0,255).astype(np.uint8)
    return a

def patch_truck(a,t):
    x0,y0,x1,y1=430,185,665,335; roi=a[y0:y1,x0:x1]; h=hsv(roi)
    H_,S_,V_=h[...,0],h[...,1],h[...,2]
    ye=((H_>=14)&(H_<=30)&(S_>150)&(V_>170))
    re=(((H_<=8)|(H_>=172))&(S_>150)&(V_>110))
    m=(ye|re).astype(np.uint8)
    m[:, :0]=0
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    keep=[i for i in range(1,n) if st[i,4]>260 and st[i,2]>28]
    if not keep: return a
    X0=min(st[i,0] for i in keep); Y0=min(st[i,1] for i in keep); X1=max(st[i,0]+st[i,2] for i in keep); Y1=max(st[i,1]+st[i,3] for i in keep)
    cx,cy,w,h2=smooth('truck',((X0+X1)/2+x0,(Y0+Y1)/2+y0,(X1-X0),(Y1-Y0)),0.5)
    b=badge_img(int(w*1.28),int(h2*1.22),['광산장년','구역장'],[int(h2*0.34)]*2)
    paste_rgba(a,b,cx,cy)
    # tiny logo on the cab door
    rx0,ry0,rx1,ry1=290,185,360,240; rr=hsv(a[ry0:ry1,rx0:rx1]); mm=(((rr[...,0]<=8)|(rr[...,0]>=172))&(rr[...,1]>150)&(rr[...,2]>110)).astype(np.uint8)
    ys,xs=np.nonzero(mm)
    if len(xs)>20:
        paste_rgba(a,dot_img(max(18,int(max(xs.max()-xs.min(),ys.max()-ys.min())*1.5))),rx0+xs.mean(),ry0+ys.mean())
    return a

FR=[(44.41,496,524),(44.45,496,524),(44.7,506,510),(44.95,526,516),(45.2,510,514),(45.45,496,486),(45.75,468,472),(45.9,460,468)]
FRD=None
def patch_fries(a,t):
    global FRD
    if FRD is None: FRD=dot_img(80)
    ts=[k[0] for k in FR]; cx=float(np.interp(t,ts,[k[1] for k in FR])); cy=float(np.interp(t,ts,[k[2] for k in FR]))
    paste_rgba(a,FRD,cx,cy)
    return a

def band(a):
    x0,y0,x1,y1=230,648,1050,712
    reg=a[y0:y1,x0:x1]; bl=cv2.GaussianBlur(reg,(0,0),16); bl=cv2.GaussianBlur(bl,(0,0),10)
    a[y0:y1,x0:x1]=(bl*0.45).astype(np.uint8)
    return a

dec=subprocess.Popen(['ffmpeg','-v','error','-ss',str(T0),'-t',str(DUR),'-i',V,'-vf',f'fps=30,scale={W}:{H}:flags=lanczos','-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',S+'mc_patched.mp4'],stdin=subprocess.PIPE)
n=0; sz=W*H*3
while True:
    buf=dec.stdout.read(sz)
    if len(buf)<sz: break
    a=np.frombuffer(buf,dtype=np.uint8).reshape(H,W,3).copy(); t=T0+n/FPS
    if 19.15<=t<20.6: a=patch_banner(a,t)
    if 21.9<=t<23.72: a=patch_truck(a,t)
    if 44.41<=t<45.88: a=patch_fries(a,t)
    a=band(a)
    enc.stdin.write(a.tobytes()); n+=1
enc.stdin.close(); enc.wait(); print('frames',n)
