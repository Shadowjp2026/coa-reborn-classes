#!/usr/bin/env python3
"""Pente fino generico (SOMENTE LEITURA). Uso: pente_v2.py <classe> <dir_dbc> <pasta_dados_exportados>
Le os DBC instalados e os .tsv exportados por SELECT; imprime os achados por secao."""
import struct, sys, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
CL, DBC, D = sys.argv[1:4]
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cfg = mod(os.path.join(HERE, "classes", "config.py"), "c").CLASSES[CL]; d = mod(os.path.join(HERE, "classes", f"design_{CL}.py"), "d")
def load(n):
    b = open(os.path.join(DBC, n), "rb").read(); m, c, f, rs, ss = struct.unpack("<4sIIII", b[:20])
    return [b[20+i*rs:20+(i+1)*rs] for i in range(c)], b[20+c*rs:]
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]; ub = lambda r, o: struct.unpack_from("<I", r, o)[0]
fy = lambda r: struct.unpack_from("<f", r, 402)[0]
S = lambda st, o: st[o:st.find(b"\0", o)].decode("utf8", "replace")
ca, cs = load("CharacterAdvancement.dbc"); sp, ss = load("Spell.dbc")
spell = {u(r, 0): r for r in sp}
sname = lambda s: S(ss, u(spell[s], 136)) if s in spell else "?"
slevel = lambda s: u(spell[s], 38) if s in spell else 0
CT, LO, HI = cfg["ct"], cfg["base"], cfg["base"] + 200
TAB = {v: k for k, v in cfg["tabs"].items()}
mine = [r for r in ca if u(r, 32) == CT and LO <= u(r, 0) < HI]
act = [r for r in mine if not ub(r, 479) & 0x9]; dis = [r for r in mine if ub(r, 479) & 0x8]
paid = [r for r in act if (u(r, 14) or u(r, 15)) and not ub(r, 479) & 0x100000]
auto = [r for r in act if ub(r, 479) & 0x100000]; ident = [r for r in act if ub(r, 479) & 0x40000]
sps = lambda r: [u(r, i) for i in range(5, 10) if u(r, i)]
nodespell = collections.defaultdict(list)
for r in act:
    for s in sps(r): nodespell[s].append(r)
tsv = lambda n: [l.rstrip("\n").split("\t") for l in open(os.path.join(D, n)) if l.strip()]
trainers = [int(i) for i, t, rq in tsv("tr_types.tsv") if int(t) == 0 and int(rq) == cfg["cls"]]
raw = collections.defaultdict(dict)
for t, s, lv, *_ in tsv("tr_spells.tsv"): raw[int(t)][int(s)] = int(lv)
twin = lambda s: s + 1100000 if s < 1100000 and (s + 1100000) in spell else s
eff = {}
for t in trainers: eff[t] = {twin(s): lv for s, lv in raw[t].items()}
eff[900100] = dict(raw[900100])
first = {}; ladder = collections.defaultdict(list)
for f, s, rk in tsv("ranks.tsv"): first[int(s)] = int(f); ladder[int(f)].append((int(rk), int(s)))
chain = lambda s: [x for _, x in sorted(ladder[first[s]])] if s in first else [s]
def where(s):
    out = [f"{'Livro' if t == 900100 else 'treinador ' + str(t)}(nv {eff[t][s]})" for t in eff if s in eff[t]]
    return ", ".join(out)
A = collections.OrderedDict()
def add(sec, msg): A.setdefault(sec, []).append(msg)
kit = {s for _, s, _ in d.BASE}
for r in paid:
    s = sps(r)[0]
    for c in chain(s)[:chain(s).index(s) + 1] if s in chain(s) else [s]:
        if where(c) and c not in kit: add("1. Duas fontes: no pago tambem vendido", f"{TAB[u(r,33)]} {sname(s)} {c}: {where(c)}")
for r in auto + ident:
    s = sps(r)[0]
    for c in chain(s)[:chain(s).index(s) + 1] if s in chain(s) else [s]:
        if where(c): add("2. Automatica/identidade vendida para todas as specs", f"{TAB[u(r,33)]} {sname(s)} {c}: {where(c)}")
for name, s, lv in d.BASE:
    w = where(s)
    if not w and not any(where(c) for c in chain(s)[:1]):
        cc = [l for l in tsv("create_custom.tsv") if int(l[2]) == s and int(l[1]) & (1 << (cfg["cls"] - 1))]
        if not cc: add("3. Kit base sem fonte (treinador/Livro/criacao)", f"{name} {s} (nivel {lv})")
    elif w:
        lvs = [eff[t][s] for t in eff if s in eff[t]]
        if min(lvs) > lv + 4: add("3b. Kit base mais tarde que o plano", f"{name} {s}: plano {lv}, fonte {w}")
    if s in nodespell: add("3c. Kit base tambem e no", f"{name} {s}")
for r in paid + auto:
    s = sps(r)[-1]; ch = chain(s)
    if len(ch) > 1 and s in ch and ch.index(s) < len(ch) - 1:
        nxt = ch[ch.index(s)+1:]; sold = [c for c in nxt if where(c)]
        if not sold: add("4. Rank preso (ranks maiores nao vendidos)", f"{TAB[u(r,33)]} {sname(s)} {s}: rank {ch.index(s)+1}/{len(ch)}")
        elif len(sold) < len(nxt): add("4b. Escada de ranks com buraco", f"{TAB[u(r,33)]} {sname(s)}: {len(sold)}/{len(nxt)} ranks maiores a venda")
for s, rs in nodespell.items():
    if len(rs) > 1: add("6. Magia repetida em nos", f"{sname(s)} {s}: " + ", ".join(f"{TAB[u(r,33)]}:{u(r,0)}" for r in rs))
for r in paid:
    n = S(cs, u(r, 47)); s = sname(sps(r)[-1])
    if n != s: add("8. Nome do no diferente da magia (aviso)", f"{TAB[u(r,33)]} '{n}' -> '{s}'")
cm = 1 << (cfg["cls"] - 1)
for rm, cmask, s in tsv("create_custom.tsv"):
    if int(cmask) & cm and int(s) in nodespell: add("9. Magia de no dada na criacao", f"{s} {sname(int(s))}")
for r in paid:
    s = sps(r)[-1]; y = fy(r)
    if slevel(s) >= 40 and y <= 3: add("5. Magia de nivel alto em linha baixa (teste em jogo)", f"{TAB[u(r,33)]} {sname(s)} {s}: nivel da magia {slevel(s)}, linha {int(y)}")
names_now = {S(cs, u(r, 47)) for r in act} | {sname(s) for r in act for s in sps(r)}
for r in dis:
    s = sps(r)[0] if sps(r) else 0
    if not s: continue
    nm = sname(s)
    if nm in names_now or s in kit or where(s) or any(where(c) for c in chain(s)) or any(c in nodespell for c in chain(s)): continue
    add("14. Habilidade que existia e nao tem mais fonte", f"{nm} {s} (era {S(cs,u(r,47))}, aba {u(r,33)})")
for sec, items in A.items():
    print(f"\n## {sec} ({len(items)})"); [print("-", i) for i in items]
print(f"\nRESUMO {CL}: secoes {len(A)} | pagos {len(paid)} | automaticas {len(auto)} | identidades {len(ident)} | treinadores {trainers}")
# personagens da classe (copias no banco de teste)
chars = [l for l in tsv("chars.tsv") if int(l[2]) == cfg["cls"]]
csp = collections.defaultdict(dict)
if os.path.exists(os.path.join(D, "char_spells.tsv")):
    for g, s, m in tsv("char_spells.tsv"): csp[int(g)][int(s)] = int(m)
slots = collections.defaultdict(list)
if os.path.exists(os.path.join(D, "char_slots.tsv")):
    for g, src, data in tsv("char_slots.tsv"): slots[int(g)].append((src, data))
actid = {u(r, 0) for r in act}
oldspells = {s for r in dis for s in sps(r)} - set(nodespell) - kit
for g, name, c, lv in chars:
    g = int(g); P = []
    for src, data in slots[g]:
        v = data.split(); n = int(v[3]) if len(v) > 3 else 0
        bad = [i for i in v[4:4+2*n:2] if int(i) not in actid]
        if bad: P.append(f"{src} com {len(bad)} ids que nao existem mais (troca de slot seria recusada)")
    miss = [nm for nm, s, l in d.BASE if l <= int(lv) and s not in csp[g] and not any(x in csp[g] for x in chain(s))]
    if miss: P.append(f"sem {len(miss)} habilidades do kit ate o nivel {lv}: " + ", ".join(miss[:12]))
    orf = [s for s in csp[g] if s in oldspells and csp[g][s]]
    if orf: P.append(f"{len(orf)} magias da arvore antiga ainda ativas")
    print(f"\n## Personagem {name} (guid {g}, nivel {lv}): " + ("OK" if not P else "; ".join(P)))
