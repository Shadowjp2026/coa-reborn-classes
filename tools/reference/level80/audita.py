import os,struct,collections,json,sys
D=os.environ.get("DBC_DIR","env/dist/data/dbc")+"/"
def load(n):
    b=open(D+n,"rb").read(); m,c,f,rs,ss=struct.unpack("<4sIIII",b[:20]); return [b[20+i*rs:20+(i+1)*rs] for i in range(c)], b[20+c*rs:], f
ca,cs,_=load("CharacterAdvancement.dbc")
u=lambda r,i: struct.unpack_from("<I",r,i*4)[0]; ub=lambda r,o: struct.unpack_from("<I",r,o)[0]; fl=lambda r,o: struct.unpack_from("<f",r,o)[0]
S=lambda o: cs[o:cs.find(b"\0",o)].decode("utf8","replace")
es,_,ef=load("CharacterAdvancementEssence.dbc")
TE={}
for r in es:
    v=struct.unpack_from("<9I",r)
    if v[2]==1 and v[3]==0 and v[6]==0: TE[v[1]]=(v[7],v[8])
lvl_te=lambda pts: next((L for L in range(1,81) if TE.get(L,(0,0))[1]>=pts),None)
sb=open(D+"Spell.dbc","rb").read(); n,f,rs,ss=struct.unpack("<4I",sb[4:20]); spells={struct.unpack_from("<I",sb,20+i*rs)[0] for i in range(n)}
allrows={u(r,0):r for r in ca}
CLASSIC={36:"Hunter",37:"Warrior",38:"Rogue",39:"Mage",40:"Priest",41:"Warlock",42:"Druid",43:"Shaman",44:"Paladin",45:"Death Knight"}
COA={14+i:"CoA %d"%(12+i) for i in range(21)}
TABN={87:"Class",95:"Support",96:"Support",97:"Support",98:"Support"}
import importlib.util
spec=importlib.util.spec_from_file_location("cfg",os.path.join(os.environ.get("COA_ROOT","."),"v2/classes/config.py")); cfg=importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
for k,v in cfg.CLASSES.items():
    for tn,tid in v["tabs"].items(): TABN.setdefault((v["ct"],tid),tn)
def tabname(ct,t): return TABN.get((ct,t)) or TABN.get(t) or "aba %d"%t
res=[]
for ct,name in list(CLASSIC.items())+list(COA.items()):
    rows=[r for r in ca if u(r,32)==ct and (not ub(r,479)&0x9 or (ct in CLASSIC and 142000<=u(r,0)<142400))]
    for t in sorted(set(u(r,33) for r in rows)):
        T=[r for r in rows if u(r,33)==t]
        support = all(142000<=u(r,0)<142400 for r in T)
        tal=[r for r in T if S(u(r,1)).startswith("Talent") and u(r,15)>0]
        auto=[r for r in T if ub(r,479)&0x100000]
        abil=[r for r in T if S(u(r,1))=="Ability"]
        ranks=lambda r: max(1,len([u(r,i) for i in range(5,10) if u(r,i)]))
        te_cost=sum(ranks(r)*u(r,15) for r in tal); ae_cost=sum(u(r,14) for r in abil)
        def unlock(r):
            g=u(r,39); lv=u(r,26)
            gl=lvl_te(g) if g else 0
            return max(lv, gl or 0, (lvl_te(1) if u(r,15)>0 else 0))
        rowsy=collections.defaultdict(list)
        for r in tal: rowsy[int(fl(r,402))].append(unlock(r))
        prob=[]
        for r in T:
            for i in range(5,10):
                s=u(r,i)
                if s and s not in spells: prob.append("magia %d inexistente (%s)"%(s,S(u(r,47))))
            for i in (2,3,4):
                q=u(r,i)
                if q and (q not in allrows or ub(allrows[q],479)&0x8): prob.append("requisito %d ausente/desligado (%s)"%(q,S(u(r,47))))
            for k in range(15):
                p=ub(r,415+4*k)
                if p and (p not in allrows or ub(allrows[p],479)&0x8): prob.append("ligacao %d ausente/desligada (%s)"%(p,S(u(r,47))))
            g=u(r,39)
            if g and g>te_cost: prob.append("portao %d > pontos da arvore %d (%s)"%(g,te_cost,S(u(r,47))))
        last=max(tal,key=unlock) if tal else None
        res.append(dict(cls=name,ct=ct,tab=tabname(ct,t),tabid=t,support=support,disabled=all(ub(r,479)&0x8 for r in T),
            first=min((unlock(r) for r in tal),default=None), rows={y:min(v) for y,v in sorted(rowsy.items())},
            last=unlock(last) if last else None, last_name=S(u(last,47)) if last else "", maxgate=max((u(r,39) for r in T),default=0),
            talents=len(tal), ranks=sum(ranks(r) for r in tal), te_cost=te_cost, autos=sorted(u(r,26) for r in auto), abil=len(abil), ae_cost=ae_cost,
            node_max_level=max((u(r,26) for r in T),default=0), prob=sorted(set(prob))))
json.dump(res,open("resultado.json","w"),indent=1)
print("TE por nivel:",{L:TE[L] for L in (10,20,30,40,50,55,60,70,80)})
for x in res:
    if x["ct"] in CLASSIC:
        print("%-12s %-14s%s talentos %2d ranks %2d custo %2d | 1o nv %s | ultima nv %s (%s, portao %d) | autos %s | problemas %d"%(x["cls"],x["tab"]," [SUPPORT]" if x["support"] else "",x["talents"],x["ranks"],x["te_cost"],x["first"],x["last"],x["last_name"][:22],x["maxgate"],x["autos"],len(x["prob"])))
