S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
JUA=FD+'Jua-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'
def tf(name,s):
    p=f'{S}/t6/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p
END=15.03
cuts=[0,5.0,6.5,10.52,12.8,END]
cam=[
 ("1.0+0.14*in_time/5.0+0.03*pow(sin(PI*in_time/0.52),2)","(iw-iw/zoom)*0.45","(ih-ih/zoom)*0.5"),                                   # counting beats
 ("1.14+0.04*in_time/1.5","(iw-iw/zoom)*0.5+22*in_time*sin(in_time*38)","(ih-ih/zoom)*0.5+16*in_time*cos(in_time*31)"),               # losing count: wobble that grows
 ("1.0+0.14*(in_time/4.02)+0.03*pow(sin(PI*in_time/0.55),2)","(iw-iw/zoom)*0.45","(ih-ih/zoom)*0.5"),                                 # starting over
 ("1.0+0.22*exp(-2.5*in_time)","(iw-iw/zoom)*0.6","(ih-ih/zoom)*0.5"),                                                               # wall scene, pull back
 ("1.0+0.10*in_time/2.23","(iw-iw/zoom)*0.5","(ih-ih/zoom)*0.55"),                                                                   # slow push-in on the slogan
]
parts=["[0:v]scale=1920:1440:flags=lanczos,split=5[v0][v1][v2][v3][v4]"]
for i,(z,x,y) in enumerate(cam):
    a,b=cuts[i],cuts[i+1]
    parts.append(f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=960x720:fps=30[s{i}]")
parts.append("[s0][s1][s2][s3][s4]concat=n=5:v=1:a=0,setpts=PTS-STARTPTS[cat]")
parts.append(f"[cat]eq=saturation=1.1:brightness='0.3*exp(-9*(t-10.52))*gte(t,10.52)+0.25*exp(-9*(t-12.8))*gte(t,12.8)':eval=frame,fade=t=in:st=0:d=0.2,fade=t=out:st={END-0.3:.2f}:d=0.3[g]")
fx=[]
# corner mark (top right, whole video)
cm=tf('cm','광산장년구역장')
from PIL import ImageFont
_f=ImageFont.truetype(BHS,26); _tw=int(_f.getlength('광산장년구역장'))
fx.append(f"drawtext=fontfile={BHS}:textfile={cm}:fontsize=26:fontcolor=white:box=1:boxcolor=0x1F7A3F:boxborderw=9:x=w-text_w-26:y=22")
fx.append(f"drawbox=x={960-26-_tw-9-3}:y=13:w={_tw+18+6}:h=46:color=0xF5C518:t=3")
# the counter: only what the voice says (one line that keeps changing)
def num(name,s,t0,t1,size=54,fill='0xC8102E@0.92',col='white'):
    p=tf(name,s)
    return (f"drawtext=fontfile={JUA}:textfile={p}:fontsize={size}:fontcolor={col}:box=1:boxcolor={fill}:boxborderw=12:"
            f"x=w-text_w-30:y=86:enable='between(t,{t0},{t1})'")
for k,(s,t0,t1) in enumerate([('백만 스물하나',0.0,0.8),('백만 스물둘',0.8,1.9),('백만 스물셋',1.9,3.0),('백만 스물넷',3.0,4.0),
                             ('백만 스물 두…',4.0,5.1),('에?',5.1,6.0),('아이고!',6.0,6.4),('다시?',6.4,7.0),('하나',7.0,7.65),('둘',7.65,8.25),
                             ('셋',8.25,8.85),('넷',8.85,9.4),('다섯',9.4,10.05),('여섯',10.05,10.6)]):
    fx.append(num(f'c{k}',s.replace('…','...'),t0,t1,size=60 if len(s)<4 else 54,fill='0xFFE600@0.95' if s in('아이고!',) else '0xC8102E@0.92',col='0x222222' if s=='아이고!' else 'white'))
parts.append("[g]"+','.join(fx)+"[v]")
open(S+'/f_en.txt','w',encoding='utf-8').write(';\n'.join(parts))
