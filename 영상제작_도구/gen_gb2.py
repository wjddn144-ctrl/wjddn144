from PIL import ImageFont
S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
JUA=FD+'Jua-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'; DH=FD+'DoHyeon-Regular.ttf'; GG=FD+'Gaegu-Bold.ttf'; SM=FD+'SongMyung-Regular.ttf'
NSQ='/usr/share/fonts/truetype/nanum/NanumSquareB.ttf'
def tf(name,s):
    p=f'{S}/t11/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p
def fit(font,text,maxw,start):
    sz=start
    while sz>20 and ImageFont.truetype(font,sz).getlength(text)>maxw: sz-=2
    return sz
def tw(font,text,sz): return ImageFont.truetype(font,sz).getlength(text)

cuts=[0,5.054,6.5225,7.19,9.058,10.14,13.997]
T1=1.685; CARD=6.5; TOTAL=cuts[-1]+T1+CARD; ENDV=cuts[-1]+T1
kinds=[('zoom',dict(z0=1.0,z1=1.12,fx=.45,fy=.45)),
       ('zoom',dict(z0=1.0,z1=1.18,fx=.35,fy=.4)),
       ('pan',dict(z=1.15,fx0=.3,fx1=.7,fy0=.5,fy1=.5)),
       ('zoom',dict(z0=1.0,z1=1.2,fx=.55,fy=.45)),
       ('zoom',dict(z0=1.0,z1=1.1,fx=.5,fy=.5)),
       ('pan',dict(z=1.12,fx0=.2,fx1=.8,fy0=.5,fy1=.5))]
n=len(kinds); IW,IH=1920,1440
parts=[f"[0:v]fps=30,scale=960:720,delogo=x=40:y=24:w=252:h=88:enable='lt(t,15.68)',scale={IW}:{IH}:flags=lanczos,split={n+1}"+''.join(f'[v{i}]' for i in range(n))+'[vbg]']
def lerp(kp,idx):
    e=str(kp[-1][idx])
    for (t0,*v0),(t1,*v1) in reversed(list(zip(kp[:-1],kp[1:]))):
        e=f"if(lt(t,{t1:.3f}),{v0[idx-1]}+({v1[idx-1]}-{v0[idx-1]})*(t-{t0:.3f})/{t1-t0:.3f},{e})"
    return e
for i,(k,p) in enumerate(kinds):
    a,b=cuts[i],cuts[i+1]; d=b-a
    if k=='zoom':
        z=f"{p['z0']}+({p['z1']}-{p['z0']})*in_time/{d:.3f}"; x=f"(iw-iw/zoom)*{p['fx']}"; y=f"(ih-ih/zoom)*{p['fy']}"
    else:
        z=f"{p['z']}"; x=f"(iw-iw/zoom)*({p['fx0']}+({p['fx1']}-{p['fx0']})*in_time/{d:.3f})"; y=f"(ih-ih/zoom)*({p['fy0']}+({p['fy1']}-{p['fy0']})*in_time/{d:.3f})"
    pre=f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS"
    if i==4:   # product close-up: stick "광산장년회" over the device label and logo (tracked)
        stk=tf('stk','광산장년회')
        base=9.058
        lab=[(9.058,20,125),(9.3,50,138),(9.5,96,142),(9.7,124,140),(9.9,176,136),(10.14,205,134)]
        logo=[(9.058,230,450),(9.3,290,462),(9.5,340,462),(9.7,385,456),(9.9,440,458),(10.14,480,458)]
        lab=[(t-base,x_*2,y_*2) for t,x_,y_ in lab]; logo=[(t-base,x_*2,y_*2) for t,x_,y_ in logo]
        parts.append(f"color=c=0xF5C518:s=640x150:r=30:d=1.2,drawbox=x=8:y=8:w=624:h=134:color=0x2B3A8C:t=fill,drawtext=fontfile={BHS}:textfile={stk}:fontsize=76:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2[sl]")
        parts.append(f"color=c=0xF5C518:s=500:r=30:d=1.2,drawbox=x=8:y=8:w=484:h=104:color=0x2B3A8C:t=fill,drawtext=fontfile={BHS}:textfile={stk}:fontsize=58:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2[sg]".replace("s=500:","s=500x120:"))
        parts.append(pre+"[pj]")
        parts.append(f"[pj][sl]overlay=x='{lerp(lab,1)}-320':y='{lerp(lab,2)}-75':eof_action=pass:eval=frame[pj2]")
        parts.append(f"[pj2][sg]overlay=x='{lerp(logo,1)}-250':y='{lerp(logo,2)}-60':eof_action=pass:eval=frame[pj3]")
        src="[pj3]null"
    else:
        src=pre
    parts.append(f"{src},zoompan=z='{z}':x='{x}':y='{y}':d=1:s=960x720:fps=30[s{i}]")

# ---------- certificate end card (local t) ----------
c=["drawbox=x=0:y=0:w=960:h=720:color=0xF7EBCB:t=fill",
   "drawbox=x=22:y=22:w=916:h=676:color=0x8B1E1E:t=12",
   "drawbox=x=50:y=50:w=860:h=620:color=0xC9A227:t=3"]
star=tf('star','★')
for sx,sy in [(70,70),(850,70),(70,610),(850,610)]:
    c.append(f"drawtext=fontfile={NSQ}:textfile={star}:fontsize=38:fontcolor=0xC9A227:x={sx}:y={sy}")
def ctext(name,s,font,size,col,y,t0,x='(w-text_w)/2',extra=''):
    p=tf(name,s)
    return (f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor={col}:x='{x}':y='{y}+30*pow(max(0,1-(t-{t0})/0.4),2)':"
            f"alpha='min(1,max(0,(t-{t0})/0.35))'{extra}")
c.append(ctext('no','제 1004 호',NSQ,28,'0x5a4a2a',100,0.1,x='110'))
c.append(ctext('t1','상     장',SM,118,'0x8B1E1E',110,0.2))
c.append(ctext('t2','노력상',BHS,66,'0x222222',262,0.6))
nm='광산장년회 총무부'; sz=70
c.append(ctext('t3',nm,JUA,sz,'0x1F3A93',350,1.0))
w=tw(JUA,nm,sz)
c.append(f"drawbox=x='(960-{w:.0f})/2':y=438:w='{w:.0f}*min(1,max(0,(t-1.4)/0.4))':h=4:color=0xC8102E:t=fill")
c.append(ctext('b1','위 총무부는 보이지 않는 곳에서 묵묵히',SM,38,'0x333333',470,1.6))
c.append(ctext('b2','살림과 섬김으로 노력하셨기에',SM,38,'0x333333',518,1.9))
c.append(ctext('b3','감사의 마음을 담아 이 상장을 드립니다',SM,38,'0x333333',566,2.2))
c.append(ctext('f1','광산장년회 일동',JUA,40,'0x8B1E1E',622,2.5,x='470'))
seal=tf('seal','●'); ins=tf('ins','인')
c.append(f"drawtext=fontfile={NSQ}:textfile={seal}:fontsize='20+80*min(1,max(0,(t-2.9)/0.2))+8*exp(-6*max(0,t-3.1))*sin(max(0,t-3.1)*30)':fontcolor=0xC8102E:x=815:y=600:alpha='min(1,max(0,(t-2.9)/0.1))'")
c.append(f"drawtext=fontfile={BHS}:textfile={ins}:fontsize=34:fontcolor=white:x=833:y=628:alpha='min(1,max(0,(t-3.05)/0.1))'")
parts.append("[1:v]fps=30,scale=960:720,setpts=PTS-STARTPTS[card]")


# ---------- title card (replaces the original product end card; voice says "엠씨스퀘어" here) ----------
parts.append(f"[vbg]trim=start=13.8:end=13.9,setpts=PTS-STARTPTS,scale=960:720,fps=30,loop=loop=60:size=3,trim=duration={T1},boxblur=24:4,eq=brightness=0.06:saturation=1.35[tbg]")
l1=tf('tl1','노력하는 총무부와 함께 합니다'); big2=tf('tl2','광산장년회')
tcs=[f"drawtext=fontfile={JUA}:textfile={l1}:fontsize=44:fontcolor=white:borderw=3:bordercolor=black@0.7:x='85+300*pow(max(0,1-t/0.3),2)':y=190:alpha='min(1,t/0.2)'",
     f"drawtext=fontfile={BHS}:textfile={big2}:fontsize='60+70*min(1,max(0,(t-0.05)/0.2))+8*exp(-6*max(0,t-0.25))*sin(max(0,t-0.25)*28)':fontcolor=white:borderw=6:bordercolor=0x1F7A3F:x=100:y=250:alpha='min(1,max(0,(t-0.05)/0.1))'"]
st=tf('st3','★ ★ ★')
tcs.append(f"drawtext=fontfile={NSQ}:textfile={st}:fontsize=64:fontcolor=0xFFE066:borderw=3:bordercolor=0x8a6500:x=640:y='430-20*sin(t*6)':alpha='min(1,max(0,(t-0.4)/0.3))'")
parts.append("[tbg]"+','.join(tcs)+"[tcard]")
labels=''.join(f'[s{i}]' for i in range(n))+'[tcard][card]'
parts.append(f"{labels}concat=n={n+2}:v=1:a=0,setpts=PTS-STARTPTS[cat]")
# drowsy -> awake grade
parts.append("[cat]eq=saturation='0.5+0.5*clip((t-4.6)/2.0,0,1)+0.2*clip((t-6.7)/1.0,0,1)':contrast=1.03:brightness='0.35*exp(-9*(t-6.7))*gte(t,6.7)':eval=frame,"
             "vignette=angle='PI/3.2-(PI/3.2-PI/6)*clip((t-4.6)/2.0,0,1)':eval=frame,"
             f"fade=t=in:st=0:d=0.3,fade=t=out:st={TOTAL-0.4:.2f}:d=0.4[g]")
# eyelid blinks while drowsy (0-5.05)
parts.append("color=c=black:s=960x190:r=30:d=5.06[lidt]")
parts.append("color=c=black:s=960x190:r=30:d=5.06[lidb]")
parts.append("[g][lidt]overlay=x=0:y='-190+120*pow(max(0,sin(t*2.1)),2)':enable='lt(t,5.054)':eof_action=pass[g1]")
parts.append("[g1][lidb]overlay=x=0:y='720-120*pow(max(0,sin(t*2.1)),2)':enable='lt(t,5.054)':eof_action=pass[g2]")
# frosted patches: watermark (top-left) + disclaimer band
parts.append("[g2]split=2[a][b2]")
parts.append("[b2]crop=880:205:40:505,boxblur=28:3,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.25:t=fill[w2]")
parts.append("[a][w2]overlay=40:505:enable='between(t,1.78,5.054)'[o]")

fx=[]
wm=tf('wm','광산장년회')
fx.append(f"drawtext=fontfile={NSQ}:textfile={wm}:fontsize=34:fontcolor=white:borderw=2:bordercolor=black@0.7:x=58:y=50:enable='lt(t,{ENDV})'")
# dialogue captions: marker-pen style, meaning of the spoken line with 구역장 words
def cap(name,s,t0,t1,y,font=GG,start=76,col='0x1a1a1a',box='0xFFE600@0.92',underline=False):
    sz=fit(font,s,840,start); p=tf(name,s)
    en=f"enable='between(t,{t0},{t1})'"
    out=[f"drawtext=fontfile={font}:textfile={p}:fontsize={sz}:fontcolor={col}:box=1:boxcolor={box}:boxborderw=14:"
         f"x='(w-text_w)/2':y='{y}+34*pow(max(0,1-(t-{t0})/0.3),2)':alpha='min(1,max(0,(t-{t0})/0.2))':{en}"]
    if underline:
        w=tw(font,s,sz)
        out.append(f"drawbox=x='(960-{w:.0f})/2':y={y+sz+16}:w={w:.0f}:h=5:color=0xE0202E:t=fill:{en}")
    return out
fx+=cap('s1','아, 공부는 잘 안 되고 얼마 남지도 않았는데…',0.75,3.95,590)
fx+=cap('s2','야, 너는 어떻게 공부하냐?',5.35,6.65,590)
fx+=cap('s3','그냥 열심히 하는 거지 뭐',6.65,7.85,590)
fx+=cap('s4','노력하는 총무부와 함께 합니다',7.85,10.45,590)
fx+=cap('s5','야, 공부나 해',11.0,12.6,590)
parts.append("[o]"+','.join(fx)+"[v]")

# ---------- audio: original + chime + stamp thump, extended to cover the certificate ----------
B=ENDV   # start of the end sequence
parts.append(f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={TOTAL:.3f}[ao]")
def ms(x): return f"{int(round(x*1000))}|{int(round(x*1000))}"
# riser (0 -> 0.9s), boom at 0.9s, three stat pings, final chime at 4.4s
parts.append("aevalsrc='0.42*(t/0.9)*sin(2*PI*(180*t+(1500-180)*t*t/(2*0.9)))+0.18*(t/0.9)*(random(0)*2-1)':d=0.9:s=44100,aformat=channel_layouts=stereo,adelay=%s[rs]"%ms(B))
parts.append("aevalsrc='0.95*sin(2*PI*52*t)*exp(-3.2*t)+0.55*(random(0)*2-1)*exp(-14*t)+0.35*sin(2*PI*104*t)*exp(-6*t)':d=1.6:s=44100,aformat=channel_layouts=stereo,adelay=%s[bm]"%ms(B+0.9))
for k,tp in enumerate((2.9,3.2,3.5)):
    parts.append("aevalsrc='0.35*sin(2*PI*(900+%d*300)*t)*exp(-9*t)':d=0.5:s=44100,aformat=channel_layouts=stereo,adelay=%s[p%d]"%(k,ms(B+tp),k))
parts.append("aevalsrc='0.35*sin(2*PI*880*t)*exp(-3*t)+0.25*sin(2*PI*1318*t)*exp(-3.5*t)+0.2*sin(2*PI*1760*t)*exp(-4*t)':d=1.8:s=44100,aformat=channel_layouts=stereo,adelay=%s[fc]"%ms(B+4.4))
parts.append(f"[ao][rs][bm][p0][p1][p2][fc]amix=inputs=7:duration=first:normalize=0,afade=t=out:st={TOTAL-0.4:.2f}:d=0.4[aout]")
open(S+'/f_gb2.txt','w',encoding='utf-8').write(';\n'.join(parts))
print(TOTAL)
