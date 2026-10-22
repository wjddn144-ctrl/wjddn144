from PIL import ImageFont
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
SM=FD+'SongMyung-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'
def tf(name,s):
    p=f'{S}/t7/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p
END=30.859
cuts=[0,1.07,6.24,12.25,16.0,23.09,26.2,END]
cam=[("1.2-0.2*in_time/1.07","(iw-iw/zoom)*0.3","(ih-ih/zoom)*0.6"),
     ("1.0+0.16*in_time/5.17","(iw-iw/zoom)*0.5","(ih-ih/zoom)*0.35"),
     ("1.12","(iw-iw/zoom)*(0.15+0.7*in_time/6.01)","(ih-ih/zoom)*0.4"),
     ("1.0+0.08*in_time/3.75","(iw-iw/zoom)*0.5","(ih-ih/zoom)*0.45"),
     ("1.0","(iw-iw/zoom)*0.5","(ih-ih/zoom)*0.5"),
     ("1.0+0.1*in_time/3.11","(iw-iw/zoom)*0.55","(ih-ih/zoom)*0.5"),
     ("1.0","(iw-iw/zoom)*0.5","(ih-ih/zoom)*0.5")]
n=len(cam)
P=[]
P.append("[0:v]crop=700:478:8:0,scale=960:656:flags=lanczos,split=2[m][pp]")
P.append("[pp]crop=840:140:60:450,boxblur=22:4,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.5:t=fill[pb]")
P.append("[m][pb]overlay=60:450:enable='between(t,11.9,14.7)',scale=1920:1312:flags=lanczos,split=%d"%n+''.join(f'[v{i}]' for i in range(n)))
for i,(z,x,y) in enumerate(cam):
    a,b=cuts[i],cuts[i+1]
    P.append(f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,fps=30,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=960x656:fps=30[s{i}]")
P.append(''.join(f'[s{i}]' for i in range(n))+f"concat=n={n}:v=1:a=0,setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.3[base]")
# ---- cards that replace the product shots
P.append("[1:v]scale=1920:1312,split=2[oa][ob]")
P.append("[oa]zoompan=z='1.0+0.03*sin(2*PI*in_time/2.6)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=960x656:fps=30,format=yuva420p,fade=t=in:st=0:d=0.3:alpha=1,setpts=PTS+15.6/TB[ca]")
P.append("[ob]zoompan=z='1.0+0.03*sin(2*PI*in_time/2.6+1)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=960x656:fps=30,format=yuva420p,fade=t=in:st=0:d=0.3:alpha=1,setpts=PTS+25.8/TB[cb]")
P.append("[3:v]format=rgba,split=2[ga][gb]")
P.append("[ga]fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+19.8/TB[gA]")
P.append("[gb]fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+26.8/TB[gB]")
P.append("[2:v]format=rgba,setpts=PTS+29.095/TB[lc]")
P.append("[base][ca]overlay=0:0:eof_action=pass:enable='between(t,15.6,23.09)'[b1]")
P.append("[b1][gA]overlay=40:470:eof_action=pass:enable='between(t,19.8,23.09)'[b2]")
P.append("[b2][cb]overlay=0:0:eof_action=pass:enable='between(t,25.8,29.095)'[b3]")
P.append("[b3][gB]overlay=40:470:eof_action=pass:enable='between(t,26.8,29.095)'[b4]")
P.append(f"[b4][lc]overlay=0:0:eof_action=pass:enable='gte(t,29.095)',fade=t=out:st={END-0.4:.2f}:d=0.4[g]")
# ---- text: corner mark + only what the voice says (lyric style)
fx=[]
cm=tf('cm','광산장년회'); _tw=int(ImageFont.truetype(BHS,26).getlength('광산장년회'))
fx.append(f"drawbox=x={960-26-_tw-9-3}:y=13:w={_tw+18+6}:h=46:color=0xF5C518:t=3")
fx.append(f"drawtext=fontfile={BHS}:textfile={cm}:fontsize=26:fontcolor=white:box=1:boxcolor=0x1F7A3F:boxborderw=9:x=w-text_w-26:y=22")
def cap(name,s,t0,t1,y=588,size=52,pop=None):
    p=tf(name,s)
    fs=f"{size}" if not pop else f"{size}*(1+0.14*({'+'.join(f'exp(-9*max(0,t-{b}))*gte(t,{b})' for b in pop)}))"
    return (f"drawtext=fontfile={SM}:textfile={p}:fontsize='{fs}':fontcolor=white:borderw=4:bordercolor=black:shadowcolor=0xB8860B:shadowx=3:shadowy=3:"
            f"x='(w-text_w)/2':y='{y}+30*pow(max(0,1-(t-{t0})/0.3),2)':alpha='min(1,max(0,(t-{t0})/0.2))':enable='between(t,{t0},{t1})'")
fx.append(cap('l1','구역원 챙기러 나간다',0.2,11.0,pop=[0.2,3.5,6.0,8.7]))
fx.append(cap('l2','내일로 이어지는 우리의 가락처럼',12.2,14.7,size=48))
fx.append(cap('l3','광산장년구역장님의',14.7,16.8))
fx.append(cap('l4','변함없는 섬김도',16.8,18.2))
fx.append(cap('l5','내일로 이어집니다',18.2,19.8))
fx.append(cap('l6','잘한다! 우리 구역장님은 소중한 분이야',22.6,24.9,size=44))
fx.append(cap('l7','우리 구역장님, 우리의 자랑',24.9,26.8,size=48))
P.append("[g]"+','.join(fx)+"[v]")
open(S+'/f_sp.txt','w',encoding='utf-8').write(';\n'.join(P))
