# Gera CharacterAdvancement.dbc com a progressao ate 80 (31 classes). So muda os campos 26 (nivel), 38/39 (portao).
import os,struct,collections,json,sys
SRC=os.path.join(os.environ.get("DBC_DIR","env/dist/data/dbc"),"CharacterAdvancement.dbc"); OUT=sys.argv[1]
b=bytearray(open(SRC,"rb").read()); m,c,f,rs,ss=struct.unpack("<4sIIII",b[:20])
off=lambda i: 20+i*rs
u=lambda i,k: struct.unpack_from("<I",b,off(i)+4*k)[0]; put=lambda i,k,v: struct.pack_into("<I",b,off(i)+4*k,v)
ub=lambda i,o: struct.unpack_from("<I",b,off(i)+o)[0]; fl=lambda i,o: struct.unpack_from("<f",b,off(i)+o)[0]
rk=lambda i: max(1,len([u(i,k) for k in range(5,10) if u(i,k)]))
NEW={"TAL":{0:(11,0),1:(11,0),2:(16,0),3:(16,0),4:(26,8),5:(26,8),6:(35,12),7:(45,16),8:(60,24),9:(72,30)},
     "HAB":{0:(10,0),1:(10,0),2:(16,0),3:(16,0),4:(27,9),5:(27,9),6:(38,14),7:(50,19),8:(65,27),9:(76,33)}}
AUTO={30:40,40:60,50:80}
CTS=set(range(14,35))|set(range(36,46))
act=lambda i: u(i,32) in CTS and not ub(i,479)&0x9
tabs=collections.defaultdict(list)
for i in range(c):
    if act(i): tabs[(u(i,32),u(i,33))].append(i)
log=collections.Counter(); changes=[]
for key,I in tabs.items():
    te=any(u(i,15)>0 for i in I); kind="TAL" if te else "HAB"; cf=15 if te else 14; gf=39 if te else 38
    paid=[i for i in I if u(i,cf)>0]
    if len(paid)<10: log["abas pequenas mantidas"]+=1; continue
    log["abas "+kind]+=1
    for i in paid:
        y=int(fl(i,402)); lv,g=NEW[kind][y]
        oldlv,oldg=u(i,26),u(i,gf)
        if oldg not in (0,8,23,9,24): log["portao fora do padrao (mantido)"]+=1; continue
        nl=max(oldlv,lv)
        if (nl,g)!=(oldlv,oldg): put(i,26,nl); put(i,gf,g); changes.append((u(i,0),"nivel %d->%d portao %d->%d"%(oldlv,nl,oldg,g))); log["nos alterados"]+=1
    for i in I:
        if ub(i,479)&0x100000 and u(i,26) in AUTO:
            changes.append((u(i,0),"passiva nivel %d->%d"%(u(i,26),AUTO[u(i,26)]))); put(i,26,AUTO[u(i,26)]); log["passivas movidas"]+=1
open(OUT,"wb").write(b)
json.dump(changes,open(OUT+".mudancas.json","w"))
print(dict(log))
