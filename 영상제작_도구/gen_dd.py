S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
SM=FD+'SongMyung-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'
from PIL import ImageFont
def tf(name,s):
    p=f'{S}/t8/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p
END=30.395
cuts=[0,4.723,6.039,7.254,9.953,11.708,13.361,14.846,17.106,18.085,19.097,20.615,23.585,25.238,26.318,27.634,END]
Z=[("1.0+0.10*in_time/4.72",.5,.45),("1.12",None,.5),("1.0+0.12*in_time/1.2",.5,.5),("1.15-0.15*in_time/2.7",.5,.5),
   ("1.0+0.12*in_time/1.75",.5,.45),("1.0+0.06*in_time/1.65",.5,.5),("1.12-0.1*in_time/1.5",.5,.5),("1.0+0.1*in_time/2.2",.5,.5),
   ("1.0+0.05*in_time/1.0",.5,.5),("1.0",.5,.5),("1.0+0.1*in_time/1.5",.5,.45),("1.0+0.14*in_time/3.0",.5,.38),
   ("1.0+0.08*in_time/1.65",.5,.5),("1.1-0.1*in_time/1.1",.5,.5),("1.0+0.06*in_time/1.3",.5,.5),("1.0",.5,.5)]
n=len(Z)
P=[f"[0:v]scale=1920:1312:flags=lanczos,split={n}"+''.join(f'[v{i}]' for i in range(n))]
for i,(z,fx,fy) in enumerate(Z):
    a,b=cuts[i],cuts[i+1]; d=b-a
    x=f"(iw-iw/zoom)*{fx}" if fx is not None else f"(iw-iw/zoom)*(0.2+0.6*in_time/{d:.2f})"
    P.append(f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)*{fy}':d=1:s=960x656:fps=30[s{i}]")
P.append(''.join(f'[s{i}]' for i in range(n))+f"concat=n={n}:v=1:a=0,setpts=PTS-STARTPTS[cat]")
P.append(f"[cat]eq=saturation=1.15:contrast=1.04:brightness='0.28*exp(-9*(t-21.0))*gte(t,21.0)':eval=frame,fade=t=in:st=0:d=0.3,fade=t=out:st={END-0.35:.2f}:d=0.35[g]")
fx=[]
cm=tf('cm','광산장년회'); _tw=int(ImageFont.truetype(BHS,26).getlength('광산장년회'))
fx.append(f"drawbox=x={960-26-_tw-9-3}:y=13:w={_tw+18+6}:h=46:color=0xF5C518:t=3")
fx.append(f"drawtext=fontfile={BHS}:textfile={cm}:fontsize=26:fontcolor=white:box=1:boxcolor=0x1F7A3F:boxborderw=9:x=w-text_w-26:y=22")
def cap(name,s,t0,t1,y=585,size=50):
    p=tf(name,s)
    return (f"drawtext=fontfile={SM}:textfile={p}:fontsize={size}:fontcolor=white:borderw=4:bordercolor=black:shadowcolor=0xB8860B:shadowx=3:shadowy=3:"
            f"x='(w-text_w)/2':y='{y}+30*pow(max(0,1-(t-{t0})/0.3),2)':alpha='min(1,max(0,(t-{t0})/0.2))':enable='between(t,{t0},{t1})'")
fx+= [cap('c1','구역모임의 가을엔 웃음소리가 있습니다',5.7,8.75,size=46),
      cap('c2','사랑이 있습니다',8.8,10.6),
      cap('c3','구역의 웃음,',15.5,17.0),
      cap('c4','구역의 사랑,',17.0,18.2),
      cap('c5','구역장님',18.2,19.9,size=60),
      cap('c6','그래,',20.8,22.2,size=60),
      cap('c7','그래, 이 사랑이야!',22.2,23.9,size=60),
      cap('c8','따뜻한 사랑 맛',23.9,26.4),
      cap('c9','광산장년구역장',26.4,28.3,size=52),
      cap('c10','구역장님, 구역장님',28.3,29.9,y=22,size=46)]
P.append("[g]"+','.join(fx)+"[v]")
open(S+'/f_dd.txt','w',encoding='utf-8').write(';\n'.join(P))
