#!/usr/bin/env python3
"""Verificacao DK v2 / classe nova (somente leitura) - copia do verifica_v2.py com a excecao do D10.
Uso: verifica_v2_dk.py <classe> <dir_antes> <dir_gerado>
Excecao (so quando cfg["nova"]): linhas do ClassType da classe FORA da faixa podem mudar so o byte 479 e so ganhando 0x8;
Essence: so os campos 7-8 das linhas da classe podem mudar e precisam ser = classe 29 (V34). Todo o resto: byte-identico.
0 ok, 2 bloqueio, 4 protecao violada (alguma linha fora da classe/faixa mudou)."""
import struct, sys, os, collections, itertools, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
CL, A, B = sys.argv[1], sys.argv[2], sys.argv[3]
s_ = importlib.util.spec_from_file_location("cfg", os.path.join(HERE, "classes", "config.py")); m_ = importlib.util.module_from_spec(s_); s_.loader.exec_module(m_); cfg = m_.CLASSES[CL]
def load(d, n):
    b = open(os.path.join(d, n), "rb").read(); m, c, f, rs, ss = struct.unpack("<4sIIII", b[:20])
    return [b[20+i*rs:20+(i+1)*rs] for i in range(c)], b[20+c*rs:]
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]; ub = lambda r, o: struct.unpack_from("<I", r, o)[0]
fx = lambda r: struct.unpack_from("<f", r, 398)[0]; fy = lambda r: struct.unpack_from("<f", r, 402)[0]
S = lambda st, o: st[o:st.find(b"\0", o)].decode("utf8", "replace")
CT, LO, HI = cfg["ct"], cfg["base"], cfg["base"] + 200
mine = lambda r: u(r, 32) == CT and LO <= u(r, 0) < HI
erros, prot = [], []
oa, osa = load(A, "CharacterAdvancement.dbc"); na, nsa = load(B, "CharacterAdvancement.dbc")
if not nsa.startswith(osa): prot.append("bloco de strings antigo alterado")
oid = {u(r, 0): r for r in oa}; nid = {u(r, 0): r for r in na}
def so_desativou(a, b):   # D10: unica mudanca permitida fora da faixa = byte 479 |= 0x8
    return cfg.get("nova") and u(a, 32) == CT and len(a) == len(b) and a[:479] == b[:479] and a[483:] == b[483:] and ub(b, 479) == ub(a, 479) | 0x8
for i, r in enumerate(oa):
    if not mine(r) and na[i] != r and not so_desativou(r, na[i]): prot.append(f"linha {u(r,0)} (ClassType {u(r,32)}) mudou")
fora = [r for r in na if u(r, 32) == CT and not mine(r)]
if cfg.get("nova") and [u(r, 0) for r in fora if not ub(r, 479) & 0x8]: erros.append(f"linhas originais do ClassType {CT} ainda vivas: {len([r for r in fora if not ub(r, 479) & 0x8])}")
# Essence (V34): so campos 7-8 da classe; = classe 29 por (nivel, modo)
oe, oes = load(A, "CharacterAdvancementEssence.dbc")
ne, nes = load(B, "CharacterAdvancementEssence.dbc") if os.path.exists(os.path.join(B, "CharacterAdvancementEssence.dbc")) else (oe, oes)
if len(oe) != len(ne) or oes != nes: prot.append("Essence mudou de tamanho/strings")
for r0, r1 in zip(oe, ne):
    d = [i for i in range(len(r0)//4) if u(r0, i) != u(r1, i)]
    if d and (u(r0, 2) != cfg["cls"] or any(i not in (7, 8) for i in d)): prot.append(f"Essence {u(r0,0)} campos {d}")
ref = {(u(r, 1), u(r, 6)): (u(r, 7), u(r, 8)) for r in ne if u(r, 2) == 29}
mismatch = [u(r, 0) for r in ne if u(r, 2) == cfg["cls"] and (u(r, 7), u(r, 8)) != ref.get((u(r, 1), u(r, 6)))]
if mismatch: erros.append(f"Essence da classe {cfg['cls']} diferente da classe 29 em {len(mismatch)} linhas")
for r in na[len(oa):]:
    if not mine(r): prot.append(f"linha nova fora da classe/faixa {u(r,0)}")
oc, ocs = load(A, "ChrSpecs.dbc"); nc, ncs = load(B, "ChrSpecs.dbc")
if len(oc) != len(nc) or ocs != ncs: prot.append("ChrSpecs mudou de tamanho/strings")
for r0, r1 in zip(oc, nc):
    if r0 != r1:
        diff = [i for i in range(len(r0)//4) if u(r0, i) != u(r1, i)]
        if S(ocs, u(r0, 1)) != cfg["token"] or any(i not in range(24, 29) for i in diff): prot.append(f"ChrSpecs {u(r0,0)} campos {diff}")
sp, _ = load(A, "Spell.dbc"); spells = {u(r, 0) for r in sp}
act = [r for r in na if mine(r) and not ub(r, 479) & 0x9]
if len(set(u(r, 0) for r in na)) != len(na): erros.append("id duplicado")
for i, r in oid.items():
    if mine(r) and i not in nid: erros.append(f"id {i} sumiu")
for r in act:
    s = [u(r, i) for i in range(5, 14) if u(r, i)]
    if len(s) > 3: erros.append(f"{u(r,0)} com {len(s)} ranks")
    for x in s:
        if x not in spells: erros.append(f"{u(r,0)} magia inexistente {x}")
def o(a, b_, c): v = (b_[0]-a[0])*(c[1]-a[1])-(b_[1]-a[1])*(c[0]-a[0]); return (v > 0)-(v < 0)
def dist(p, a, b_):
    ax, ay = a; bx, by = b_; px, py = p; dx, dy = bx-ax, by-ay; t = max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(ax+t*dx-px, ay+t*dy-py)
res = {}
for tn, tab in cfg["tabs"].items():
    rows = [r for r in act if u(r, 33) == tab]
    paid = [r for r in rows if (u(r, 14) or u(r, 15)) and not ub(r, 479) & 0x100000]
    autos = [r for r in rows if ub(r, 479) & 0x100000]
    cell = collections.defaultdict(list)
    for r in rows: cell[(fx(r), fy(r))].append(r)
    for c, rs in cell.items():
        if len(rs) > 1 and not (len(rs) == 2 and u(rs[0], 29) and u(rs[0], 29) == u(rs[1], 29)): erros.append(f"{tn} casa {c} com {len(rs)} nos fora de par")
    for r in rows:
        if fx(r) > 8 and not (tab != 87 and fx(r) == 10): erros.append(f"{tn} {u(r,0)} na coluna {fx(r)}")
    g = 38 if tab == 87 else 39; want = (9, 24) if tab == 87 else (8, 23)
    for r in paid:
        y = fy(r); exp = 0 if y < 4 else want[0] if y < 8 else want[1]
        if u(r, g) != exp or u(r, 77 - g) != 0: erros.append(f"{tn} {u(r,0)} portao {u(r,38)}/{u(r,39)} esperado {exp}")
        if u(r, 26): erros.append(f"{tn} {u(r,0)} no pago com nivel {u(r,26)}")
        if (u(r, 14) if tab == 87 else u(r, 15)) != 1: erros.append(f"{tn} {u(r,0)} custo por rank != 1")
    ids = {u(r, 0) for r in rows}; byi = {u(r, 0): r for r in rows}
    E = set()
    for r in paid:
        for k in range(15):
            p = ub(r, 415 + 4*k)
            if not p: continue
            if p not in ids: erros.append(f"{tn} {u(r,0)} seta para fora da aba/classe {p}")
            elif fy(byi[p]) >= fy(r): erros.append(f"{tn} {u(r,0)} seta para cima/lado")
            else: E.add(((fx(byi[p]), fy(byi[p])), (fx(r), fy(r))))
    for a, b_ in itertools.combinations(sorted(E), 2):
        if len({*a, *b_}) == 4 and o(a[0], a[1], b_[0])*o(a[0], a[1], b_[1]) < 0 and o(b_[0], b_[1], a[0])*o(b_[0], b_[1], a[1]) < 0: erros.append(f"{tn} setas cruzam {a} x {b_}")
    for e in E:
        for c in cell:
            if c not in e and dist(c, *e) < 0.45: erros.append(f"{tn} seta {e} passa sobre {c}")
    soltos = [u(r, 0) for r in rows if fx(r) <= 8 and fy(r) > 0 and r in paid and not any(ub(r, 415+4*k) for k in range(15))]
    if soltos: erros.append(f"{tn} nos sem seta fora da linha 0: {soltos}")
    seen = set(); cost = r03 = r07 = 0
    for r in paid:
        gk = u(r, 29) or ("n", u(r, 0))
        if gk in seen: continue
        seen.add(gk); n = sum(1 for i in range(5, 10) if u(r, i)); cost += n
        if fy(r) < 4: r03 += n
        if fy(r) < 8: r07 += n
    ch = collections.defaultdict(list)
    for r in paid:
        for k in range(15):
            if ub(r, 415+4*k): ch[ub(r, 415+4*k)].append(u(r, 0))
    alc = set(); st = [u(r, 0) for r in paid if fy(r) == 0]
    while st:
        x = st.pop()
        if x in alc: continue
        alc.add(x); st += ch[x]
    if len(alc) != len(paid): erros.append(f"{tn}: {len(paid)-len(alc)} nos inalcancaveis")
    if tab == 87:
        if not 36 <= cost <= 40: erros.append(f"{tn}: custo {cost}")
        if r03 < 13 or r07 < 30: erros.append(f"{tn}: portoes apertados {r03}/{r07}")
        if [r for r in rows if ub(r, 479) & 0x100000]: erros.append(f"{tn}: automatica na aba de classe")
    else:
        if not 34 <= cost <= 36: erros.append(f"{tn}: custo {cost}")
        if r03 < 12 or r07 < 28: erros.append(f"{tn}: portoes apertados {r03}/{r07}")
        if len(autos) != 4 or sorted(u(r, 26) for r in autos) != [20, 30, 40, 50]: erros.append(f"{tn}: automaticas {sorted(u(r,26) for r in autos)}")
    one = sum(1 for r in paid if sum(1 for i in range(5, 10) if u(r, i)) == 1) * 100 // max(1, len(paid))
    res[tn] = dict(nos=len(paid), custo=cost, linhas03=r03, linhas07=r07, rank1=f"{one}%", autos=len(autos))
for r in nc:
    if S(ncs, u(r, 1)) == cfg["token"]:
        i = nid.get(u(r, 28))
        if not i or not mine(i) or ub(i, 479) & 0x8 or not ub(i, 479) & 0x40000 or (fx(i), fy(i)) != (10.0, 0.0) or u(i, 5) != u(r, 24): erros.append(f"ChrSpecs {S(ncs,u(r,2))}: identidade incoerente")
print(f"DESATIVADAS FORA DA FAIXA (ClassType {CT}): {sum(1 for r in fora if ub(r, 479) & 0x8)} de {len(fora)}")
print("PROTECAO:", "OK" if not prot else prot[:10])
for k, v in res.items(): print(k, v)
print("ERROS:", len(erros)); [print("  -", e) for e in erros[:60]]
sys.exit(4 if prot else 2 if erros else 0)
