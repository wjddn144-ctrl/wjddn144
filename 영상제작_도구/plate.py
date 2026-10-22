import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
V="/root/.claude/uploads/abc8043e-b14c-5ac4-9a25-e067a14aebca/cad1edbb-Daewoo_Tico_1992_start_commercial_korea.mp4"; W,H=960,720; FPS=60
FONT='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad/fonts/BlackHanSans-Regular.ttf'
# manual keyframes (t, x0,y0,x1,y1) per window, from gridded crops
K={
 'A':[(3.366,405,442,456,467),(3.8,400,424,458,448),(4.2,402,422,455,448),(4.7,398,430,453,456)],
 'B':[(6.033,250,260,304,284),(6.1,250,262,303,285),(6.5,248,273,310,298),(6.9,245,284,318,312),(7.37,245,296,332,328)],
 'C':[(13.366,232,396,302,419),(13.9,237,399,305,421),(14.5,243,404,316,432),(15.366,238,411,322,445)],
}
def bbox(t,kf):
    ts=[k[0] for k in kf]
    if t<ts[0] or t>ts[-1]: return None
    return [float(np.interp(t,ts,[k[i] for k in kf])) for i in range(1,5)]
cache={}
def plate(w,h):
    key=(w,h)
    if key in cache: return cache[key]
    s=4; im=Image.new('RGB',(w*s,h*s),(205,215,205)); d=ImageDraw.Draw(im)
    b=max(1,int(h*0.1))*s
    d.rectangle([b,b,w*s-b-1,h*s-b-1],fill=(38,88,66))
    f=ImageFont.truetype(FONT,int(h*s*0.62))
    tb=d.textbbox((0,0),'1004',font=f)
    d.text(((w*s-(tb[2]-tb[0]))/2-tb[0],(h*s-(tb[3]-tb[1]))/2-tb[1]),'1004',font=f,fill=(235,240,235))
    im=im.resize((w,h),Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.7))
    cache[key]=im; return im
dec=subprocess.Popen(['ffmpeg','-v','error','-i',V,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','10','-pix_fmt','yuv420p','patched.mp4'],stdin=subprocess.PIPE)
n=0; sz=W*H*3
while True:
    buf=dec.stdout.read(sz)
    if len(buf)<sz: break
    t=n/FPS
    box=None
    for kf in K.values():
        box=bbox(t,kf) or box
    if box:
        x0,y0,x1,y1=[int(round(v)) for v in box]
        x0-=2;y0-=2;x1+=2;y1+=2
        fr=Image.frombuffer('RGB',(W,H),buf,'raw','RGB',0,1)
        fr.paste(plate(x1-x0,y1-y0),(x0,y0))
        buf=fr.tobytes()
    enc.stdin.write(buf); n+=1
enc.stdin.close(); enc.wait(); print('frames',n)
