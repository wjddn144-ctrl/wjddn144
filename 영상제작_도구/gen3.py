S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
JUA=FD+'Jua-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'; DH=FD+'DoHyeon-Regular.ttf'; GG=FD+'Gaegu-Bold.ttf'
NSQ='/usr/share/fonts/truetype/nanum/NanumSquareB.ttf'
def tf(name,s):
    p=f'{S}/t3/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p

# kiss scene (24.233-25.233) removed: laughing shot (25.233-26.4) is slowed to fill 24.233-26.4 so the audio stays in sync
cuts=[0,3.366,4.699,6.033,7.366,8.366,9.533,10.533,13.366,15.366,16.8,19.9,21.9,24.233,26.4,27.4]
kinds=[
 ('zoom',dict(z0=1.0,z1=1.12,fx=.5,fy=.4),'start'),
 ('zoom',dict(z0=1.0,z1=1.2,fx=.5,fy=.5),''),
 ('pan',dict(z=1.15,fx0=0,fx1=1,fy0=.5,fy1=.5),''),
 ('zoom',dict(z0=1.25,z1=1.0,fx=.5,fy=.5),''),
 ('pan',dict(z=1.18,fx0=1,fx1=0,fy0=.4,fy1=.6),''),
 ('zoom',dict(z0=1.0,z1=1.22,fx=.4,fy=.4),''),
 ('zoom',dict(z0=1.0,z1=1.15,fx=.6,fy=.45),''),
 ('zoom',dict(z0=1.0,z1=1.2,fx=.5,fy=.4),''),
 ('zoom',dict(z0=1.0,z1=1.25,fx=.6,fy=.5),''),
 ('pan',dict(z=1.15,fx0=.1,fx1=.9,fy0=.8,fy1=.2),''),
 ('zoom',dict(z0=1.0,z1=1.2,fx=.5,fy=.35),''),
 ('pan',dict(z=1.18,fx0=.9,fx1=.1,fy0=.5,fy1=.5),''),
 ('zoom',dict(z0=1.28,z1=1.0,fx=.5,fy=.5),''),
 ('zoom',dict(z0=1.0,z1=1.18,fx=.5,fy=.4),'slow'),   # 24.233-26.4 slowed laugh
 ('whip',dict(z=1.02,k=.28),''),                      # skyline 26.4-27.4
]
n=len(kinds); IW,IH=1920,1440
parts=["[0:v]split[ya][yb]",
       f"[ya]fps=30,scale={IW}:{IH}:flags=lanczos,split={n-1}"+''.join(f'[v{i}]' for i in range(n) if kinds[i][2]!='slow'),
       f"[yb]trim=start=25.233:end=26.4,setpts=(PTS-STARTPTS)*{(26.4-24.233)/(26.4-25.233):.4f},fps=30,scale={IW}:{IH}:flags=lanczos[v13]"]
for i,(k,p,tag) in enumerate(kinds):
    a,b=cuts[i],cuts[i+1]; d=b-a
    if k=='zoom':
        z=f"{p['z0']}+({p['z1']}-{p['z0']})*in_time/{d:.3f}"; x=f"(iw-iw/zoom)*{p['fx']}"; y=f"(ih-ih/zoom)*{p['fy']}"
    elif k=='pan':
        z=f"{p['z']}"; x=f"(iw-iw/zoom)*({p['fx0']}+({p['fx1']}-{p['fx0']})*in_time/{d:.3f})"; y=f"(ih-ih/zoom)*({p['fy0']}+({p['fy1']}-{p['fy0']})*in_time/{d:.3f})"
    else:
        z=f"{p['z']}+{p['k']}*exp(-2.5*in_time)"; x="(iw-iw/zoom)*0.5"; y="(ih-ih/zoom)*0.5"
    # road rumble on every shot; engine-start jolt on the opening shot
    x+=f"+4*sin(in_time*35)"; y+=f"+3*sin(in_time*29)"
    if tag=='start':
        x+="+30*exp(-3*in_time)*sin(in_time*80)"; y+="+22*exp(-3*in_time)*cos(in_time*71)"
    if tag=='slow':
        src=f"[v{i}]null"
    else:
        src=f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS"
    parts.append(f"{src},zoompan=z='{z}':x='{x}':y='{y}':d=1:s=960x720:fps=30[s{i}]")

# ---- end card: road + sky + licence plate
c=["drawbox=x=0:y=0:w=960:h=430:color=0x5BB5F0:t=fill","drawbox=x=0:y=430:w=960:h=290:color=0x3B3F46:t=fill",
   "drawbox=x=0:y=430:w=960:h=8:color=white:t=fill","drawbox=x=0:y=700:w=960:h=20:color=0xF5C518:t=fill"]
dash=tf('dash','━━')
for j,off in enumerate(range(0,1200,300)):
    c.append(f"drawtext=fontfile={NSQ}:textfile={dash}:fontsize=90:fontcolor=white:x='mod({off}-t*420,1200)-150':y=640")
# signs / text
def sign(name,s,font,size,col,x,y,t0,fill='0x0E7A47',extra=''):
    p=tf(name,s)
    al=f"alpha='min(1,max(0,(t-{t0})/0.3))'"
    ya=f"{y}-60*pow(max(0,1-(t-{t0})/0.4),2)"
    return [f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor=white:box=1:boxcolor=white:boxborderw=22:x={x}:y='{ya}':{al}",
            f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor=white:box=1:boxcolor={fill}:boxborderw=14:x={x}:y='{ya}':{al}"]
c+=sign('k1','광산장년회',BHS,92,'white','(w-text_w)/2',70,0.1)
l2=tf('k2','구역장님과 함께 시작하세요')
c.append(f"drawtext=fontfile={JUA}:textfile={l2}:fontsize=64:fontcolor=white:borderw=4:bordercolor=0x0B3D6E:x='(w-text_w)/2+800*pow(max(0,1-(t-0.7)/0.5),2)':y=265:alpha='min(1,max(0,(t-0.7)/0.3))'")
plate=tf('k3','광산장년 1004')
c.append("drawbox=x=250:y=470:w=460:h=140:color=white:t=fill")
c.append("drawbox=x=260:y=480:w=440:h=120:color=0x14703F:t=fill")
c.append(f"drawtext=fontfile={BHS}:textfile={plate}:fontsize=62:fontcolor=white:x='(w-text_w)/2':y='(540-text_h/2)+80*pow(max(0,1-(t-1.2)/0.5),2)':alpha='min(1,max(0,(t-1.2)/0.3))'")
parts.append("color=c=black:s=960x720:r=30:d=2.95,"+','.join(c)+"[card]")

labels=''.join(f'[s{i}]' for i in range(n))+'[card]'
parts.append(f"{labels}concat=n={n+1}:v=1:a=0,setpts=PTS-STARTPTS[cat]")
parts.append("[cat]eq=saturation=1.12:contrast=1.04:brightness='0.3*exp(-10*(t-24.233))*gte(t,24.233)':eval=frame,vignette=angle=PI/6,fade=t=in:st=0:d=0.3[g]")
parts.append("[g]split[a][b]")
parts.append("[b]crop=700:150:130:475,boxblur=30:3,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.55:t=fill[bl]")
parts.append("[a][bl]overlay=130:475:enable='between(t,0,3.366)'[o]")

fx=[]
# --- opening: typed caption in original style + traffic light
txt='구역장님과 함께 시작하세요'
fx.append("drawbox=x=150:y=500:w=660:h=3:color=0xD7263D:t=fill:enable='between(t,0,3.366)'")
fx.append("drawbox=x=150:y=597:w=660:h=3:color=0xD7263D:t=fill:enable='between(t,0,3.366)'")
L=len(txt)
for k in range(1,L+1):
    t0=0.12*k; t1=0.12*(k+1) if k<L else 3.366
    p=tf(f'ty{k}',txt[:k])
    fx.append(f"drawtext=fontfile={NSQ}:textfile={p}:fontsize=50:fontcolor=white:borderw=2:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3:x=165:y=528:enable='between(t,{t0:.2f},{t1:.3f})'")
go=tf('go','출발! 출발!')
fx.append(f"drawtext=fontfile={BHS}:textfile={go}:fontsize=64:fontcolor=0x30D158:borderw=5:bordercolor=black:x=40:y=40:enable='between(t,0,0.95)'")

# --- road-sign captions
def rsign(name,s,font,size,t0,t1,fill,y=590):
    p=tf(name,s)
    al=f"alpha='min(1,max(0,(t-{t0})/0.25))'"
    ya=f"{y}+40*pow(max(0,1-(t-{t0})/0.35),2)"; en=f"enable='between(t,{t0},{t1})'"
    return [f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor=white:box=1:boxcolor=white:boxborderw=20:x='(w-text_w)/2':y='{ya}':{al}:{en}",
            f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor=white:box=1:boxcolor={fill}:boxborderw=12:x='(w-text_w)/2':y='{ya}':{al}:{en}"]
G,B,BR='0x0E7A47','0x0B5FA8','0x7A4A21'
for args in [
 ('a1','도시는 좁아도 구역장님의 길은 넓다',NSQ,46,4.5,8.2,G),
 ('a2','여유 있는 아침, 여유 있는 구역장님',NSQ,46,10.5,13.6,B),
 ('a3','수고, 정성 다 들여도',NSQ,50,13.6,17.3,G),
 ('a4','사랑하니까 하는 거지 뭐',NSQ,50,17.5,19.8,BR),
 ('a5','구역 식구들, 챙겨주셔야죠',NSQ,52,21.9,24.0,G),
 ('a6','새로운 믿음, 새로운 열매',NSQ,56,24.2,27.3,B),
]:
    fx+=rsign(*args)
parts.append("[o]"+','.join(fx)+"[v]")
open(S+'/f4.txt','w',encoding='utf-8').write(';\n'.join(parts))
