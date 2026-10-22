import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad/'
BHS=S+'fonts/BlackHanSans-Regular.ttf'; SM=S+'fonts/SongMyung-Regular.ttf'
W,H=960,656
def gold_text(txt,font,size,w,h,anchor_y=None):
    """gold lettering with bevel and dark drop shadow on a transparent canvas"""
    s=2; f=ImageFont.truetype(font,size*s)
    m=Image.new('L',(w*s,h*s),0); d=ImageDraw.Draw(m); tb=d.textbbox((0,0),txt,font=f)
    x=(w*s-(tb[2]-tb[0]))/2-tb[0]; y=(h*s-(tb[3]-tb[1]))/2-tb[1]
    d.text((x,y),txt,font=f,fill=255)
    grad=np.zeros((h*s,w*s,3),np.float32)
    tt=np.linspace(0,1,h*s)
    top=np.array([255,240,160.]); mid=np.array([225,175,50.]); bot=np.array([150,100,20.])
    col=np.where((tt<0.5)[:,None],top+(mid-top)*(tt/0.5)[:,None],mid+(bot-mid)*((tt-0.5)/0.5)[:,None])
    grad[:]=col[:,None,:]
    ma=np.asarray(m,np.float32)/255
    # shadow
    sh=m.filter(ImageFilter.GaussianBlur(6*s/2)); sha=np.asarray(sh,np.float32)/255*0.8
    out=np.zeros((h*s,w*s,4),np.float32)
    off=3*s
    sh_sh=np.roll(np.roll(sha,off,0),off,1)
    out[...,:3]=0; out[...,3]=sh_sh*255
    edge=np.asarray(m.filter(ImageFilter.MaxFilter(5)),np.float32)/255   # dark outline
    out[...,:3]=np.where(edge[...,None]>0,[60,40,5],out[...,:3]); out[...,3]=np.maximum(out[...,3],edge*255)
    out[...,:3]=np.where(ma[...,None]>0.5,grad,out[...,:3]); out[...,3]=np.maximum(out[...,3],ma*255)
    return Image.fromarray(out.clip(0,255).astype(np.uint8),'RGBA').resize((w,h),Image.LANCZOS)

# ---- gold orb on a dark, olive-hazed background
bg=np.zeros((H,W,3),np.float32)
yy,xx=np.mgrid[0:H,0:W]
for cy,amp in ((190,34),(255,22)):
    bg[...,0]+=amp*np.exp(-((yy-cy)/22.0)**2)*0.9; bg[...,1]+=amp*np.exp(-((yy-cy)/22.0)**2)*1.05; bg[...,2]+=amp*np.exp(-((yy-cy)/22.0)**2)*0.2
cx,cy,R=480,250,112
r=np.hypot(xx-cx,yy-cy)
glow=np.exp(-np.clip(r-R,0,None)/38.0)*(r>R*0.4)
orb=np.clip(1-r/R,0,1)
hl=np.exp(-((xx-(cx-38))**2+(yy-(cy-42))**2)/(2*32.0**2))
for c,(a,b) in enumerate(((235,120),(205,105),(60,10))):
    bg[...,c]+= glow*a*0.45
    bg[...,c]=np.where(r<=R,b+(a-b)*(orb**0.6)+hl*(255-a)*0.7,bg[...,c])
Image.fromarray(bg.clip(0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)).save(S+'t7/orb.png')

# ---- gold name that sits under the orb
gold_text('광산장년구역장',BHS,86,880,130).save(S+'t7/gold_name.png')

# ---- closing logo card
lg=np.zeros((H,W,3),np.float32)
t=np.linspace(0,1,H)[:,None]
lg[...,0]=(18+40*t); lg[...,1]=(26+60*t); lg[...,2]=(8+14*t)
lg=lg*(1-0.35*np.clip((np.hypot(xx-W/2,yy-H/2)/520),0,1)[...,None])
im=Image.fromarray(lg.clip(0,255).astype(np.uint8)).convert('RGBA')
im.alpha_composite(gold_text('광산장년',BHS,120,720,170),(120,110))
pl=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(pl)
d.rectangle([225,320,735,460],fill=(40,30,8,255)); d.rectangle([232,327,728,453],outline=(235,190,70,255),width=6)
im.alpha_composite(pl)
im.alpha_composite(gold_text('구역장',BHS,96,500,130),(230,332))
im.convert('RGB').save(S+'t7/logo.png')
print('ok')
