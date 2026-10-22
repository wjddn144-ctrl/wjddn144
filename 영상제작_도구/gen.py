import os
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
JUA=FD+'Jua-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'; DH=FD+'DoHyeon-Regular.ttf'
GG=FD+'Gaegu-Bold.ttf'; GUGI=FD+'Gugi-Regular.ttf'; SM=FD+'SongMyung-Regular.ttf'
PEN='/usr/share/fonts/truetype/nanum/NanumPen.ttf'; BRUSH='/usr/share/fonts/truetype/nanum/NanumBrush.ttf'
NSQ='/usr/share/fonts/truetype/nanum/NanumSquareB.ttf'; NGX='/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf'

texts={}
def tf(name,s):
    p=f'{S}/t/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p

# ---- camera segments (start,end,kind,params)
D=lambda a,b:b-a
segs=[
 (0,5.233,'zoom',dict(z0=1.0,z1=1.22,fx=.5,fy=.5)),
 (5.233,7.233,'pan',dict(z=1.2,fx0=0,fx1=1,fy0=.5,fy1=.5)),
 (7.233,8.733,'zoom',dict(z0=1.0,z1=1.35,fx=.55,fy=.45)),
 (8.733,11.866,'pan',dict(z=1.18,fx0=1,fx1=0,fy0=.6,fy1=.4)),
 (11.866,13.866,'zoom',dict(z0=1.35,z1=1.0,fx=.5,fy=.5)),
 (13.866,15.333,'shake',dict(z=1.14,amp=10)),
 (15.333,16.333,'zoom',dict(z0=1.0,z1=1.3,fx=.5,fy=.3)),
 (16.333,17.366,'pan',dict(z=1.2,fx0=.2,fx1=.8,fy0=.8,fy1=.2)),
 (17.366,20.266,'zoom',dict(z0=1.0,z1=1.25,fx=.45,fy=.4)),
 (20.266,21.5,'punch',dict(z=1.12,k=.3,amp=26)),
 (21.5,26.866,'whip',dict(z=1.02,k=.3)),
]
IW,IH=1920,1440
parts=[]
n=len(segs)
parts.append(f"[0:v]scale={IW}:{IH}:flags=lanczos,split={n}"+''.join(f'[v{i}]' for i in range(n)))
for i,(a,b,k,p) in enumerate(segs):
    d=b-a
    if k=='zoom':
        z=f"{p['z0']}+({p['z1']}-{p['z0']})*in_time/{d:.3f}"
        x=f"(iw-iw/zoom)*{p['fx']}"; y=f"(ih-ih/zoom)*{p['fy']}"
    elif k=='pan':
        z=f"{p['z']}"
        x=f"(iw-iw/zoom)*({p['fx0']}+({p['fx1']}-{p['fx0']})*in_time/{d:.3f})"
        y=f"(ih-ih/zoom)*({p['fy0']}+({p['fy1']}-{p['fy0']})*in_time/{d:.3f})"
    elif k=='shake':
        z=f"{p['z']}"
        x=f"(iw-iw/zoom)/2+{p['amp']*2}*sin(in_time*47)+{p['amp']}*sin(in_time*83)"
        y=f"(ih-ih/zoom)/2+{p['amp']*2}*cos(in_time*61)+{p['amp']}*sin(in_time*97)"
    elif k=='punch':
        z=f"{p['z']}+{p['k']}*exp(-9*in_time)"
        x=f"(iw-iw/zoom)/2+{p['amp']*2}*exp(-3*in_time)*sin(in_time*70)"
        y=f"(ih-ih/zoom)/2+{p['amp']*2}*exp(-3*in_time)*cos(in_time*63)"
    elif k=='whip':
        z=f"{p['z']}+{p['k']}*exp(-2.5*in_time)"
        x=f"(iw-iw/zoom)*(0.5+0.0*in_time)"; y=f"(ih-ih/zoom)*0.5"
    extra=''
    pre=f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS"
    if a==7.233:
        jb=tf('jb','광산장년회')
        kp=[(7.2,233,215),(7.47,240,212),(7.73,252,222),(8.0,273,229),(8.13,276,223),(8.27,271,215),(8.4,263,208),(8.53,256,204),(8.74,255,200)]
        kp=[(t-7.233,x*4,y*4) for t,x,y in kp]
        def lerp(idx):
            e=str(kp[-1][idx])
            for (t0,*v0),(t1,*v1) in reversed(list(zip(kp[:-1],kp[1:]))):
                e=f"if(lt(t,{t1:.3f}),{v0[idx-1]}+({v1[idx-1]}-{v0[idx-1]})*(t-{t0:.3f})/{t1-t0:.3f},{e})"
            return e
        parts.append(f"color=c=0xF5C518:s=340x230:r=30:d=1.6,drawbox=x=12:y=12:w=316:h=206:color=0xC8102E:t=fill,drawtext=fontfile={BHS}:textfile={jb}:fontsize=54:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2[bd]")
        parts.append(pre+"[j]")
        parts.append(f"[j][bd]overlay=x='{lerp(1)}-170':y='{lerp(2)}-115':eof_action=pass:eval=frame[jb]")
        pre="[jb]null"
        src=pre
    else:
        src=pre
    parts.append(f"{src},zoompan=z='{z}':x='{x}':y='{y}':d=1:s=960x720:fps=30[s{i}]")

# ---- animated end card (local time t)
c=[]
c.append("drawbox=x=0:y=0:w=960:h=720:color=0x1F7A3F:t=fill")
c.append("drawbox=x=30:y=30:w=900:h=660:color=0xF5C518:t=6")
star=tf('star','★')
for j,(sx,off,sp,col,sz) in enumerate([(90,0,90,'0xFFE066',34),(230,300,70,'white',26),(380,520,110,'0xFFE066',30),(560,120,80,'white',34),(700,420,100,'0xFFE066',28),(840,640,75,'white',30),(150,200,60,'0xFFF3B0',22),(780,80,65,'0xFFF3B0',24)]):
    c.append(f"drawtext=fontfile={NGX}:textfile={star}:fontsize={sz}:fontcolor={col}:x={sx}:y='mod(t*{sp}+{off},780)-50'")
big=tf('big','광산장년회'); l2=tf('l2','구역장님들, 따봉!'); l3=tf('l3','사랑하고 응원합니다')
# pop-in big title with overshoot
c.append(f"drawtext=fontfile={BHS}:textfile={big}:fontsize='130*min(1,max(0.01,(t-0.1)/0.35))+14*sin(max(0,t-0.45)*10)*exp(-3*max(0,t-0.45))*gte(t,0.45)':fontcolor=0xFFE066:borderw=5:bordercolor=0x0B3D1E:x='(w-text_w)/2':y='230-text_h/2'")
c.append(f"drawtext=fontfile={JUA}:textfile={l2}:fontsize=76:fontcolor=white:borderw=3:bordercolor=0x0B3D1E:x='(w-text_w)/2+700*pow(max(0,1-(t-0.8)/0.5),2)':y=345:alpha='min(1,max(0,(t-0.8)/0.3))'")
parts.append("[1:v]"+','.join(c)+"[card]")

labels=''.join(f'[s{i}]' for i in range(n))+'[card]'
parts.append(f"{labels}concat=n={n+1}:v=1:a=0,setpts=PTS-STARTPTS[cat]")
# grading + flashes + vignette + intro fade
parts.append("[cat]eq=saturation=1.2:contrast=1.06:brightness='0.45*exp(-10*(t-20.266))*gte(t,20.266)+0.5*exp(-8*(t-26.866))*gte(t,26.866)':eval=frame,vignette=angle=PI/5,fade=t=in:st=0:d=0.5[g]")
# frosted caption bar
parts.append("[g]split[a][b]")
parts.append("[b]crop=960:160:0:550,boxblur=30:3,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.5:t=fill[bl]")
parts.append("[a][bl]overlay=0:550:enable='0'[o]")

def cap(name,s,font,size,col,bcol,t0,t1,y=618,bw=3,anim='up'):
    p=tf(name,s)
    if anim=='up':
        ya=f"{y}+36*pow(max(0,1-(t-{t0})/0.35),2)"; xa="(w-text_w)/2"
    elif anim=='left':
        ya=str(y); xa=f"(w-text_w)/2-600*pow(max(0,1-(t-{t0})/0.4),2)"
    elif anim=='zoom':
        ya=str(y); xa="(w-text_w)/2"
    return (f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor={col}:borderw={bw}:bordercolor={bcol}:"
            f"x='{xa}':y='{ya}':alpha='min(1,max(0,(t-{t0})/0.25))':enable='between(t,{t0},{t1})'")
fx=[]
fx.append(cap('v1','세계적인 오렌지의 명산지, 브라질',JUA,50,'white','black',5.9,9.2,y=560,anim='up'))
fx.append(cap('v2','브라질에서도 정말 좋은 오렌지를 찾았을 때',JUA,46,'white','black',11.6,15.9,y=560,anim='up'))
fx.append(cap('v3','광산장년회는 이렇게 말합니다',JUA,50,'white','black',15.9,18.2,y=110,anim='up'))
# big TTABONG burst
tb=tf('tb','따봉!')
fx.append(f"drawtext=fontfile={BHS}:textfile={tb}:fontsize='60+170*min(1,(t-20.3)/0.2)+12*sin((t-20.5)*12)*exp(-4*(t-20.5))*gte(t,20.5)':fontcolor=0xFFE066:borderw=8:bordercolor=0xD7263D:x='(w-text_w)/2':y=40:enable='between(t,20.3,21.9)':alpha='min(1,(t-20.3)/0.1)'")
# logo badge
b1=tf('b1','광산장년회')
fx.append("drawbox=x=60:y=290:w=240:h=170:color=0xF5C518:t=fill:enable='between(t,23.5,24.5)'")
fx.append("drawbox=x=70:y=300:w=220:h=150:color=0xC8102E:t=fill:enable='between(t,23.5,24.5)'")
fx.append(f"drawtext=fontfile={BHS}:textfile={b1}:fontsize=42:fontcolor=white:x=180-text_w/2:y=358:enable='between(t,23.5,24.5)'")
# slogan card
c2=tf('c2','정말 좋은 구역장님들로 만듭니다.')
fx.append("drawbox=x=40:y=280:w=880:h=200:color=0xF5C518:t=fill:enable='between(t,24.5,26.87)'")
fx.append("drawbox=x=48:y=288:w=864:h=184:color=0x1F7A3F:t=fill:enable='between(t,24.5,26.87)'")
fx.append(f"drawtext=fontfile={BHS}:textfile={b1}:fontsize=70:fontcolor=0xFFE066:x='(w-text_w)/2':y='302+30*pow(max(0,1-(t-24.5)/0.3),2)':alpha='min(1,(t-24.5)/0.25)':enable='between(t,24.5,26.87)'")
fx.append(f"drawtext=fontfile={DH}:textfile={c2}:fontsize=44:fontcolor=white:x='(w-text_w)/2':y=402:alpha='min(1,max(0,(t-24.8)/0.3))':enable='between(t,24.5,26.87)'")
parts.append("[o]"+','.join(fx)+"[v]")
open(S+'/f2.txt','w',encoding='utf-8').write(';\n'.join(parts))
