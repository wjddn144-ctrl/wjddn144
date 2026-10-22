S='/tmp/claude-0/-home-user-wjddn144/abc8043e-b14c-5ac4-9a25-e067a14aebca/scratchpad'
FD=S+'/fonts/'
JUA=FD+'Jua-Regular.ttf'; BHS=FD+'BlackHanSans-Regular.ttf'; GG=FD+'Gaegu-Bold.ttf'
def tf(name,s):
    p=f'{S}/t5/{name}.txt'; open(p,'w',encoding='utf-8').write(s); return p
SRC_END=21.037; CUT_A=9.7; CUT_B=15.79; OFF=CUT_B-CUT_A       # drop 9.7-15.79: the "결혼하자는" dialogue and the shoulder-lean scene
END=SRC_END-OFF
# timeline after the cut
T_STU=CUT_A; T_D=17.08-OFF; T_E=18.25-OFF          # students at window / "전자제품 살땐" / crowd + slogan
cuts=[0,1.58,CUT_A,T_D,T_E,END]
parts=[]
parts.append("[0:v]fps=30,scale=960:720:flags=lanczos,split=2[ra][rb]")
parts.append(f"[ra]trim=start=0:end={CUT_A},setpts=PTS-STARTPTS[xa]")
parts.append(f"[rb]trim=start={CUT_B}:end={SRC_END},setpts=PTS-STARTPTS[xb]")
parts.append("[xa][xb]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS,delogo=x=48:y=16:w=170:h=50:enable='lt(t,%.3f)',split=3[m][pa][pb]"%T_E)
parts.append("[pa]crop=600:120:215:565,boxblur=22:4,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.25:t=fill[pd]")
parts.append("[pb]crop=520:190:215:455,boxblur=24:4,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.2:t=fill[pe]")
parts.append(f"[m][pd]overlay=215:565:enable='between(t,{T_D-0.08:.3f},{T_E+0.05:.3f})'[m1]")
parts.append(f"[m1][pe]overlay=215:455:enable='gte(t,{T_E-0.05:.3f})'[m2]")
sl1=tf('sl1','힘들 땐...'); sl2=tf('sl2','구역모임')
pic=[f"drawtext=fontfile={JUA}:textfile={sl1}:fontsize=62:fontcolor=white:borderw=4:bordercolor=black@0.8:x=240:y=590:enable='between(t,{T_D:.3f},{T_E:.3f})'",
     f"drawtext=fontfile={JUA}:textfile={sl1}:fontsize=46:fontcolor=white:borderw=3:bordercolor=black@0.8:x=245:y=470:enable='gte(t,{T_E:.3f})'",
     f"drawtext=fontfile={BHS}:textfile={sl2}:fontsize=112:fontcolor=0xE60012:borderw=6:bordercolor=white:x=240:y=520:enable='gte(t,{T_E:.3f})'"]
parts.append("[m2]"+','.join(pic)+",scale=1920:1440:flags=lanczos,split=5[v0][v1][v2][v3][v4]")
dB=CUT_A-1.58
cam={0:"1.25-0.25*in_time/1.58",
     1:f"1.0+0.24*in_time/{dB:.2f}+0.1*exp(-7*max(0,in_time-{8.6-1.58:.2f}))*gte(in_time,{8.6-1.58:.2f})",
     2:"1.0+0.22*exp(-3*in_time)",
     3:f"1.0+0.15*in_time/{T_E-T_D:.2f}",
     4:f"1.0+0.06*in_time/{END-T_E:.2f}"}
fxy={0:("(iw-iw/zoom)*0.4","(ih-ih/zoom)*0.45"),
     1:(f"(iw-iw/zoom)*(0.5+0.12*in_time/{dB:.2f})","(ih-ih/zoom)*0.45"),
     2:("(iw-iw/zoom)*0.5+10*sin(in_time*40)*exp(-2*in_time)","(ih-ih/zoom)*0.5"),
     3:("(iw-iw/zoom)*0.35","(ih-ih/zoom)*0.5"),
     4:("(iw-iw/zoom)*0.5","(ih-ih/zoom)*0.5")}
for i in range(5):
    a,b=cuts[i],cuts[i+1]
    parts.append(f"[v{i}]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,zoompan=z='{cam[i]}':x='{fxy[i][0]}':y='{fxy[i][1]}':d=1:s=960x720:fps=30[s{i}]")
parts.append("[s0][s1][s2][s3][s4]concat=n=5:v=1:a=0,setpts=PTS-STARTPTS[cat]")
parts.append(f"[cat]eq=saturation=1.1:brightness='0.35*exp(-9*(t-{T_E:.3f}))*gte(t,{T_E:.3f})+0.25*exp(-9*(t-{CUT_A}))*gte(t,{CUT_A})':eval=frame,fade=t=in:st=0:d=0.2,fade=t=out:st={END-0.3:.2f}:d=0.3[g]")
fx=[]
lg=tf('lg','광산장년회')
fx.append(f"drawtext=fontfile={BHS}:textfile={lg}:fontsize=38:fontcolor=0xE60012:borderw=4:bordercolor=white:x=56:y=22")
def note(name,s,t0,t1,y=610,size=62,font=GG,fill='0xFFC8DD@0.95',col='0x3a1020'):
    p=tf(name,s)
    return (f"drawtext=fontfile={font}:textfile={p}:fontsize={size}:fontcolor={col}:box=1:boxcolor={fill}:boxborderw=14:"
            f"x='(w-text_w)/2':y='{y}+34*pow(max(0,1-(t-{t0})/0.3),2)':alpha='min(1,max(0,(t-{t0})/0.2))':enable='between(t,{t0},{t1})'")
fx.append(note('n1','시간 좀 내주오',2.74,4.9))
fx.append(note('n2','갈 데가 있소',4.95,6.5))
fx.append(note('n3','거기가 어디요?',6.6,8.5))
fx.append(note('n4','구역모임',8.6,9.55,font=JUA,size=64,fill='0xE60012@0.95',col='white'))
fx.append(note('n5','구역장님께 가요!',19.0-OFF,20.95-OFF,y=640,size=62,font=JUA,fill='0xFFE600@0.95',col='0x222222'))
parts.append("[g]"+','.join(fx)+"[v]")
# audio: same cut, with a tiny fade on each side of the join
parts.append(f"[0:a]atrim=start=0:end={CUT_A},asetpts=PTS-STARTPTS,afade=t=out:st={CUT_A-0.12}:d=0.12[aa]")
parts.append(f"[0:a]atrim=start={CUT_B}:end={SRC_END},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.12[ab]")
parts.append("[aa][ab]concat=n=2:v=0:a=1[aout]")
open(S+'/f_hm2.txt','w',encoding='utf-8').write(';\n'.join(parts))
print(END)
