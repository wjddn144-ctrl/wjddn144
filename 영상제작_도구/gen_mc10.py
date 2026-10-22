from PIL import ImageFont
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'; BHS=FD+'BlackHanSans-Regular.ttf'; MJ='/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf'
def tf(name,s):
    p=f'{S}/t10/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p
END=32.88
cuts=[0,4.15,5.15,6.19,10.72,12.53,17.16,19.37,21.5,23.37,24.3,25.3,27.34,29.24,31.41,END]
Z=[("1.0+0.06*in_time/4.15",.5),("1.06-0.04*in_time/1.0",.5),("1.0+0.04*in_time/1.0",.5),("1.03+0.04*in_time/4.5",.5),
   ("1.0+0.06*in_time/1.8",.5),("1.0+0.05*in_time/4.6",.5),("1.05-0.04*in_time/2.2",.5),("1.0+0.06*in_time/2.1",.5),
   ("1.0+0.04*in_time/1.9",.5),("1.0+0.05*in_time/0.93",.5),("1.0+0.04*in_time/1.0",.5),("1.0+0.06*in_time/2.0",.5),
   ("1.0+0.05*in_time/1.9",.5),("1.0+0.06*in_time/2.1",.5),("1.0+0.05*in_time/1.5",.5)]
n=len(Z); assert len(cuts)==n+1
P=[f"[0:v]scale=2560:1440:flags=lanczos,split={n}"+''.join(f'[v{i}]' for i in range(n))]
for i,(z,fy) in enumerate(Z):
    a,b=cuts[i],cuts[i+1]
    P.append(f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,zoompan=z='{z}':x='(iw-iw/zoom)*0.5':y='(ih-ih/zoom)*0.9':d=1:s=1280x720:fps=30[s{i}]")
P.append(''.join(f'[s{i}]' for i in range(n))+f"concat=n={n}:v=1:a=0,setpts=PTS-STARTPTS,eq=saturation=1.08,fade=t=in:st=0:d=0.3,fade=t=out:st={END-0.5:.2f}:d=0.5[g]")
fx=[]
cm=tf('cm','광산장년회'); _tw=int(ImageFont.truetype(BHS,30).getlength('광산장년회'))
fx.append(f"drawbox=x={1280-30-_tw-12-3}:y=15:w={_tw+24+6}:h=54:color=0xF5C518:t=3")
fx.append(f"drawtext=fontfile={BHS}:textfile={cm}:fontsize=30:fontcolor=white:box=1:boxcolor=0x1F7A3F:boxborderw=12:x=w-text_w-30:y=24")
t1=tf('ti','광산장년구역장님과'); t2=tf('ti2','잘했군 잘했어')
fx.append(f"drawtext=fontfile={BHS}:textfile={t1}:fontsize=58:fontcolor=white:borderw=5:bordercolor=0x16301F:x='(w-text_w)/2':y='70+30*pow(max(0,1-t/0.35),2)':alpha='min(1,t/0.25)':enable='between(t,0,3.2)'")
fx.append(f"drawtext=fontfile={BHS}:textfile={t2}:fontsize=76:fontcolor=0xFFE066:borderw=6:bordercolor=0x16301F:x='(w-text_w)/2':y='140+30*pow(max(0,1-(t-0.2)/0.35),2)':alpha='min(1,max(0,(t-0.2)/0.25))':enable='between(t,0,3.2)'")
SUB=[(0.05,4.1,'엊그제 챙겨 놓은 구역 식구들은 보았소?'),(4.2,5.1,'보았지~'),(5.2,6.15,'어쨌소?'),(6.25,10.7,'새로 오신 분께도 인사드렸지~'),
     (10.75,12.5,'잘했군 잘했어'),(12.6,14.7,'잘했군 잘했군 잘했어~'),(14.8,17.1,'섬긴 보람이 있다지~'),(17.7,18.4,'마누라~'),(18.45,19.35,'왜그라요~'),
     (19.45,23.35,'우리 구역장님이 이끄는 모임에 가 봤소?'),(24.0,24.7,'가 봤지요~'),(24.75,25.3,'어땠소?'),
     (25.4,29.2,'따뜻한 사랑에 정신을 못 차릴 정이지~'),(29.6,31.3,'구역모임에 일 년에 50번씩 간대~'),(31.7,32.7,'궁께 식구들 많이 모여~')]
for k,(a,b,s) in enumerate(SUB):
    p=tf(f's{k}',s)
    fx.append(f"drawtext=fontfile={MJ}:textfile={p}:fontsize=46:fontcolor=white:borderw=3:bordercolor=black@0.8:shadowcolor=black@0.7:shadowx=2:shadowy=2:x='(w-text_w)/2':y=662:alpha='min(1,(t-{a})/0.12)':enable='between(t,{a},{b})'")
P.append("[g]"+','.join(fx)+"[v]")
P.append(f"[1:a:0]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.8[am]")
P.append(f"[1:a:1]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.0[ad]")
P.append(f"[am][ad]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.3,afade=t=out:st={END-0.5:.2f}:d=0.5[aout]")
open(S+'/f_mc10.txt','w',encoding='utf-8').write(';\n'.join(P))
