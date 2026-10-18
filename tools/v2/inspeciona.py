import struct,sys,collections
D=sys.argv[1]
def load(n):
    b=open(D+"/"+n,"rb").read(); m,c,f,rs,ss=struct.unpack("<4sIIII",b[:20])
    return [b[20+i*rs:20+(i+1)*rs] for i in range(c)], b[20+c*rs:], f, rs
ca,cs,f,rs=load("CharacterAdvancement.dbc")
u=lambda r,i: struct.unpack_from("<I",r,i*4)[0]; ub=lambda r,o: struct.unpack_from("<I",r,o)[0]
fl=lambda r,o: struct.unpack_from("<f",r,o)[0]
S=lambda s,o: s[o:s.find(b"\0",o)].decode("utf8","replace")
print("fields",f,"rs",rs)
w=[r for r in ca if u(r,32)==37]
print("warrior rows",len(w),"ids",min(u(r,0) for r in w),max(u(r,0) for r in w))
act=[r for r in w if not ub(r,479)&0x9]
print("active",len(act))
for r in sorted(act,key=lambda r:(u(r,33),fl(r,402),fl(r,398))):
    con=[ub(r,415+4*k) for k in range(15) if ub(r,415+4*k)]
    print(u(r,0),"tab",u(r,33),"pos",int(fl(r,398)),int(fl(r,402)),"typ",S(cs,u(r,1)),"req",[u(r,i) for i in (2,3,4) if u(r,i)],"sp",[u(r,i) for i in range(5,10) if u(r,i)],"ae/te",u(r,14),u(r,15),"lv",u(r,26),u(r,27),u(r,28),"grp",u(r,29),"gate",u(r,38),u(r,39),"st",r[414],"con",con,"fl",hex(ub(r,479)),S(cs,u(r,47))[:30])
grp=collections.Counter(u(r,29) for r in ca if u(r,29)); print("groups max",max(grp), "n",len(grp))
