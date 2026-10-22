S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
JUA=FD+'Jua-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'; DH=FD+'DoHyeon-Regular.ttf'; GG=FD+'Gaegu-Bold.ttf'
BRUSH='/usr/share/fonts/truetype/nanum/NanumBrush.ttf'; NSQ='/usr/share/fonts/truetype/nanum/NanumSquareB.ttf'; NGX='/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf'
def tf(name,s):
    p=f'{S}/t2/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p

cuts=[0,3.366,4.699,6.033,7.366,8.366,9.533,10.533,13.366,15.366,16.8,19.9,21.9,24.233,25.233,26.4,27.4]
kinds=[
 ('zoom',dict(z0=1.0,z1=1.12,fx=.5,fy=.4)),
 ('zoom',dict(z0=1.0,z1=1.2,fx=.5,fy=.5)),
 ('pan',dict(z=1.15,fx0=0,fx1=1,fy0=.5,fy1=.5)),
 ('zoom',dict(z0=1.25,z1=1.0,fx=.5,fy=.5)),
 ('pan',dict(z=1.18,fx0=1,fx1=0,fy0=.4,fy1=.6)),
 ('zoom',dict(z0=1.0,z1=1.22,fx=.4,fy=.4)),
 ('shake',dict(z=1.1,amp=5)),
 ('zoom',dict(z0=1.0,z1=1.2,fx=.5,fy=.4)),
 ('zoom',dict(z0=1.0,z1=1.25,fx=.6,fy=.5)),
 ('pan',dict(z=1.15,fx0=.1,fx1=.9,fy0=.8,fy1=.2)),
 ('zoom',dict(z0=1.0,z1=1.2,fx=.5,fy=.35)),
 ('pan',dict(z=1.18,fx0=.9,fx1=.1,fy0=.5,fy1=.5)),
 ('zoom',dict(z0=1.28,z1=1.0,fx=.5,fy=.5)),
 ('punch',dict(z=1.1,k=.25,amp=10)),
 ('whip',dict(z=1.02,k=.28)),
 ('zoom',dict(z0=1.0,z1=1.15,fx=.4,fy=.5)),
]
n=len(kinds); IW,IH=1920,1440
parts=[f"[0:v]fps=30,scale={IW}:{IH}:flags=lanczos,split={n}"+''.join(f'[v{i}]' for i in range(n))]
for i,(k,p) in enumerate(kinds):
    a,b=cuts[i],cuts[i+1]; d=b-a
    if k=='zoom':
        z=f"{p['z0']}+({p['z1']}-{p['z0']})*in_time/{d:.3f}"; x=f"(iw-iw/zoom)*{p['fx']}"; y=f"(ih-ih/zoom)*{p['fy']}"
    elif k=='pan':
        z=f"{p['z']}"; x=f"(iw-iw/zoom)*({p['fx0']}+({p['fx1']}-{p['fx0']})*in_time/{d:.3f})"; y=f"(ih-ih/zoom)*({p['fy0']}+({p['fy1']}-{p['fy0']})*in_time/{d:.3f})"
    elif k=='shake':
        z=f"{p['z']}"; x=f"(iw-iw/zoom)/2+{p['amp']*2}*sin(in_time*47)+{p['amp']}*sin(in_time*83)"; y=f"(ih-ih/zoom)/2+{p['amp']*2}*cos(in_time*61)+{p['amp']}*sin(in_time*97)"
    elif k=='punch':
        z=f"{p['z']}+{p['k']}*exp(-9*in_time)"; x=f"(iw-iw/zoom)/2+{p['amp']*2}*exp(-3*in_time)*sin(in_time*70)"; y=f"(ih-ih/zoom)/2+{p['amp']*2}*exp(-3*in_time)*cos(in_time*63)"
    else:
        z=f"{p['z']}+{p['k']}*exp(-2.5*in_time)"; x="(iw-iw/zoom)*0.5"; y="(ih-ih/zoom)*0.5"
    parts.append(f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=960x720:fps=30[s{i}]")

# end card
c=["drawbox=x=0:y=0:w=960:h=720:color=0x1F7A3F:t=fill","drawbox=x=30:y=30:w=900:h=660:color=0xF5C518:t=6"]
star=tf('star','★')
for sx,off,sp,col,sz in [(90,0,90,'0xFFE066',34),(230,300,70,'white',26),(380,520,110,'0xFFE066',30),(560,120,80,'white',34),(700,420,100,'0xFFE066',28),(840,640,75,'white',30),(150,200,60,'0xFFF3B0',22),(780,80,65,'0xFFF3B0',24)]:
    c.append(f"drawtext=fontfile={NGX}:textfile={star}:fontsize={sz}:fontcolor={col}:x={sx}:y='mod(t*{sp}+{off},780)-50'")
big=tf('big','광산장년회'); l2=tf('l2','구역장님과 함께 시작하세요'); l3=tf('l3','사랑하고 응원합니다')
c.append(f"drawtext=fontfile={BHS}:textfile={big}:fontsize='130*min(1,max(0.01,(t-0.1)/0.35))+14*sin(max(0,t-0.45)*10)*exp(-3*max(0,t-0.45))*gte(t,0.45)':fontcolor=0xFFE066:borderw=5:bordercolor=0x0B3D1E:x='(w-text_w)/2':y='230-text_h/2'")
c.append(f"drawtext=fontfile={JUA}:textfile={l2}:fontsize=64:fontcolor=white:borderw=3:bordercolor=0x0B3D1E:x='(w-text_w)/2+700*pow(max(0,1-(t-0.8)/0.5),2)':y=345:alpha='min(1,max(0,(t-0.8)/0.3))'")
c.append(f"drawtext=fontfile={BRUSH}:textfile={l3}:fontsize=78:fontcolor=0xFFF3B0:x='(w-text_w)/2':y='470+40*pow(max(0,1-(t-1.6)/0.5),2)':alpha='min(1,max(0,(t-1.6)/0.4))'")
parts.append("color=c=black:s=960x720:r=30:d=2.95,"+','.join(c)+"[card]")

labels=''.join(f'[s{i}]' for i in range(n))+'[card]'
parts.append(f"{labels}concat=n={n+1}:v=1:a=0,setpts=PTS-STARTPTS[cat]")
parts.append("[cat]eq=saturation=1.12:contrast=1.04:brightness='0.5*exp(-8*(t-27.4))*gte(t,27.4)+0.3*exp(-10*(t-24.233))*gte(t,24.233)':eval=frame,vignette=angle=PI/6,fade=t=in:st=0:d=0.4[g]")
parts.append("[g]split[a][b]")
parts.append("[b]crop=700:150:130:475,boxblur=30:3,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.55:t=fill[bl]")
parts.append("[a][bl]overlay=130:475:enable='between(t,0,3.366)'[o]")

fx=[]
# typed opening caption in original style
txt='구역장님과 함께 시작하세요'
fx.append("drawbox=x=150:y=500:w=660:h=3:color=0xD7263D:t=fill:enable='between(t,0,3.366)'")
fx.append("drawbox=x=150:y=597:w=660:h=3:color=0xD7263D:t=fill:enable='between(t,0,3.366)'")
L=len(txt)
for k in range(1,L+1):
    t0=0.12*k; t1=0.12*(k+1) if k<L else 3.366
    p=tf(f'ty{k}',txt[:k])
    fx.append(f"drawtext=fontfile={NSQ}:textfile={p}:fontsize=50:fontcolor=white:borderw=2:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3:x=165:y=528:enable='between(t,{t0:.2f},{t1:.3f})'")
def cap(name,s,font,size,col,bcol,t0,t1,y=610,bw=4,anim='up'):
    p=tf(name,s)
    if anim=='up': ya=f"{y}+36*pow(max(0,1-(t-{t0})/0.35),2)"; xa="(w-text_w)/2"
    else: ya=str(y); xa=f"(w-text_w)/2-600*pow(max(0,1-(t-{t0})/0.4),2)"
    return (f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor={col}:borderw={bw}:bordercolor={bcol}:shadowcolor=black@0.6:shadowx=3:shadowy=3:"
            f"x='{xa}':y='{ya}':alpha='min(1,max(0,(t-{t0})/0.25))':enable='between(t,{t0},{t1})'")
fx+= [
 cap('c1','한 주의 시작도, 구역장님과 함께',JUA,54,'white','black',3.5,6.0),
 cap('c2','구역 식구들의 든든한 길동무',DH,60,'0xFFE066','0x4a3300',6.2,8.3,anim='left'),
 cap('c3','기쁨도 나누고, 마음도 나누며',GG,68,'0xFFF3B0','0x5A3A00',8.5,10.5),
 cap('c4','때로는 힘든 길도, 함께라서 든든합니다',BHS,48,'0xFF9F1C','black',10.7,13.3,anim='left'),
 cap('c5','믿음의 길을 달려가는 우리',NSQ,54,'white','0x0B3D6E',13.5,15.3),
 cap('c6','구역장님의 기도와 사랑이 길을 밝힙니다',BRUSH,78,'white','black',15.5,19.8,bw=4,anim='left'),
 cap('c7','웃음과 감사가 가득한 우리 구역',JUA,56,'0x9BF6FF','0x03243B',20.0,24.1),
 cap('c8','오늘도 힘차게 출발!',BHS,70,'0xFFE066','0xD7263D',24.4,27.3,bw=6),
]
parts.append("[o]"+','.join(fx)+"[v]")
open(S+'/f3.txt','w',encoding='utf-8').write(';\n'.join(parts))
