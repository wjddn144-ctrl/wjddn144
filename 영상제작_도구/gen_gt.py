from PIL import ImageFont
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'; BHS=FD+'BlackHanSans-Regular.ttf'; DH=FD+'DoHyeon-Regular.ttf'
def tf(name,s):
    p=f'{S}/t9/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p
END=33.552
cuts=[0,2.63,4.4,5.333,6.366,7.433,8.133,9.833,10.666,12.033,14.1,15.766,16.4997,17.733,18.966,20.2,22.033,23.066,24.766,29.0,END]
Z=[("1.0+0.1*in_time/2.63",.5,.5),("1.0+0.08*in_time/1.8",.5,.5),("1.12-0.1*in_time/0.9",.5,.5),("1.0",.5,.5),("1.0",.5,.5),
   ("1.0+0.12*in_time/0.7",.4,.7),("1.0",.5,.5),("1.0+0.1*in_time/0.8",.5,.5),("1.0+0.06*in_time/1.4",.5,.5),("1.0+0.1*in_time/2.0",.5,.45),
   ("1.0+0.12*in_time/1.7",.5,.5),("1.0+0.05*in_time/0.7",.5,.5),("1.0",.5,.5),("1.0+0.1*in_time/1.2",.5,.5),("1.0",.5,.5),
   ("1.0+0.04*in_time/1.2",.5,.5),("1.0",.5,.5),("1.0+0.05*in_time/1.0",.5,.5),("1.0+0.1*in_time/4.2",.5,.4),("1.0+0.03*in_time/4.5",.5,.5)]
# keep the green caption screens and card shots free of zoom so text stays crisp
for i in (4,6,12,14,16): Z[i]=("1.0",.5,.5)
n=len(Z); P=[f"[0:v]scale=1920:1440:flags=lanczos,split={n}"+''.join(f'[v{i}]' for i in range(n))]
assert len(cuts)==n+1
for i,(z,fx,fy) in enumerate(Z):
    a,b=cuts[i],cuts[i+1]
    P.append(f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,zoompan=z='{z}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d=1:s=960x720:fps=30[s{i}]")
P.append(''.join(f'[s{i}]' for i in range(n))+f"concat=n={n}:v=1:a=0,setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.2,fade=t=out:st={END-0.35:.2f}:d=0.35[g]")
fx=[]
cm=tf('cm','광산장년회'); _tw=int(ImageFont.truetype(BHS,26).getlength('광산장년회'))
fx.append(f"drawbox=x={960-26-_tw-9-3}:y=13:w={_tw+18+6}:h=46:color=0xF5C518:t=3:enable='lt(t,29.0)'")
fx.append(f"drawtext=fontfile={BHS}:textfile={cm}:fontsize=26:fontcolor=white:box=1:boxcolor=0x1F7A3F:boxborderw=9:x=w-text_w-26:y=22:enable='lt(t,29.0)'")
p=tf('lyr','영혼의 갈증은 역시 구역장님입니다')
fx.append(f"drawtext=fontfile={DH}:textfile={p}:fontsize=54:fontcolor=white:borderw=5:bordercolor=0x0B3D1E:shadowcolor=black@0.6:shadowx=3:shadowy=3:x='(w-text_w)/2':y='640+30*pow(max(0,1-(t-26.3)/0.3),2)':alpha='min(1,max(0,(t-26.3)/0.2))':enable='between(t,26.3,28.7)'")
P.append("[g]"+','.join(fx)+"[v]")
open(S+'/f_gt.txt','w',encoding='utf-8').write(';\n'.join(P))
