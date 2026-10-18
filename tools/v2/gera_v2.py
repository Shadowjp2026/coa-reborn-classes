#!/usr/bin/env python3
"""Gerador v2 generico (Receita v2 §4, §14.2) - SO PARA O AMBIENTE DE TESTE.
Uso: gera_v2.py <classe> <dir_dbc_atual> <dir_saida_nova>
- parte dos DBC atuais (instalados no teste, com as outras classes ja feitas) e grava numa pasta NOVA;
- so mexe em linhas do ClassType da classe DENTRO da faixa de 200 ids dela (a Support usa ClassType classico em 142000+);
- monta cada no do zero a partir de classes/design_<classe>.py; do molde (linhas originais do Warrior, pristinas em src-original) vem so a forma binaria;
- ids: reaproveita o id ativo pela chave (aba, nome); ids que saem viram DISABLED; novos vem dos ids livres da faixa;
- ChrSpecs: so os campos 24-28 das 3 specs da classe."""
import struct, sys, os, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
CL, SRC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
assert not os.path.exists(OUT), "a pasta de saida precisa ser nova"
def mod(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cfg = mod(os.path.join(HERE, "classes", "config.py"), "cfg").CLASSES[CL]
design = mod(os.path.join(HERE, "classes", f"design_{CL}.py"), "design")
os.makedirs(OUT)
def load(d, name):
    b = open(os.path.join(d, name), "rb").read(); m, n, f, rs, ss = struct.unpack("<4sIIII", b[:20])
    return dict(f=f, rs=rs, recs=[bytearray(b[20+i*rs:20+(i+1)*rs]) for i in range(n)], strs=bytearray(b[20+n*rs:]))
def save(name, d):
    hdr = struct.pack("<4sIIII", b"WDBC", len(d["recs"]), d["f"], d["rs"], len(d["strs"]))
    open(os.path.join(OUT, name), "xb").write(hdr + b"".join(d["recs"]) + bytes(d["strs"]))
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]
def su(r, i, v): struct.pack_into("<I", r, i*4, v)
ub = lambda r, o: struct.unpack_from("<I", r, o)[0]
def sub_(r, o, v): struct.pack_into("<I", r, o, v)
def S(d, o): e = d["strs"].find(b"\x00", o); return bytes(d["strs"][o:e]).decode("utf8", "replace")
def addstr(d, text): off = len(d["strs"]); d["strs"] += text.encode("utf8") + b"\x00"; return off
F_ID, F_REQ, F_SPELLS, F_AE, F_TE, F_GROUP, F_CT, F_TAB, F_GATE_AE, F_GATE_TE, F_NAME, F_ICON = 0, 2, 5, 14, 15, 29, 32, 33, 38, 39, 47, 64
B_POSX, B_POSY, B_CONN, B_FLAGS = 398, 402, 415, 479
CT, LO, HI, TABS = cfg["ct"], cfg["base"], cfg["base"] + 200, cfg["tabs"]
mine = lambda r: u(r, F_CT) == CT and LO <= u(r, F_ID) < HI
ca = load(SRC, "CharacterAdvancement.dbc"); chr_ = load(SRC, "ChrSpecs.dbc")
sp = load(SRC, "Spell.dbc"); icons = load(SRC, "SpellIcon.dbc")
tmpl = load(os.path.join(HERE, "src-original"), "CharacterAdvancement.dbc")
T = {u(r, F_ID): bytes(r) for r in tmpl["recs"] if u(r, F_ID) in (140319, 140322, 140211, 140308, 140200)}
T_ACTIVE, T_PASSIVE, T_SPEC, T_SIG, T_AUTO = (bytearray(T[i]) for i in (140319, 140322, 140211, 140308, 140200))
spell = {u(r, 0): r for r in sp["recs"]}
iconpath = {u(r, 0): S(icons, u(r, 1)) for r in icons["recs"]}
byid = {u(r, F_ID): r for r in ca["recs"]}
active = [r for r in ca["recs"] if mine(r) and not ub(r, B_FLAGS) & 0x9]
bykey = {}
for r in sorted(active, key=lambda r: u(r, F_ID)): bykey.setdefault((u(r, F_TAB), S(ca, u(r, F_NAME))), u(r, F_ID))
free = [i for i in range(LO, HI) if i not in byid]
groups_used = {u(r, F_GROUP) for r in ca["recs"]}
icon_by_spell = {}
for r in ca["recs"]:
    for i in range(F_SPELLS, F_SPELLS + 5):
        if u(r, i) and u(r, F_ICON): icon_by_spell.setdefault(u(r, i), u(r, F_ICON))
def icon_for(spells):
    for s in spells:
        if s in icon_by_spell: return icon_by_spell[s]
    path = iconpath.get(u(spell[spells[-1]], 133), "")
    return addstr(ca, path.split("\\")[-1] or "INV_Misc_QuestionMark")
report = {"classe": CL, "reusados": 0, "novos": 0, "desativados": [], "nos": {}}
newid = {}
reserved = set(cfg["ident"].values())
def take_id(tab, name):
    k = (tab, name)
    if k in bykey and bykey[k] not in reserved:
        report["reusados"] += 1; return bykey.pop(k)
    assert free, "faixa da classe sem id livre"
    report["novos"] += 1; return free.pop(0)
def build(tmpl_, nid, tab, x, y, spells, ae, te, level, name, flags=None):
    r = bytearray(tmpl_)
    su(r, F_ID, nid); su(r, F_CT, CT); su(r, F_TAB, tab)
    for i in range(F_REQ, F_REQ + 3): su(r, i, 0)
    for i in range(F_SPELLS, F_SPELLS + 9): su(r, i, 0)
    for k, s in enumerate(spells):
        assert s in spell, f"magia inexistente {s} ({name})"; su(r, F_SPELLS + k, s)
    su(r, F_AE, ae); su(r, F_TE, te)
    for i in (26, 27, 28): su(r, i, level)
    su(r, F_GROUP, 0); su(r, F_GATE_AE, 0); su(r, F_GATE_TE, 0)
    struct.pack_into("<f", r, B_POSX, float(x)); struct.pack_into("<f", r, B_POSY, float(y))
    for k in range(15): sub_(r, B_CONN + 4*k, 0)
    old = byid.get(nid)
    su(r, F_NAME, u(old, F_NAME) if old is not None and S(ca, u(old, F_NAME)) == name else addstr(ca, name))
    su(r, F_ICON, icon_for(spells))
    if flags is not None: sub_(r, B_FLAGS, flags)
    return r
out_rows = {}
sig_by_key = {k: spn for spn, k in design.SIG.items()}
signature = {}
for tname, (nodes, kind, g1, g2) in design.TREES.items():
    tab = TABS[tname]; flat = []
    for n in nodes:
        if isinstance(n, list):
            grp = next(g for g in range(9370001, 9399999) if g not in groups_used); groups_used.add(grp)
            for m in n: flat.append((m, grp))
        else: flat.append((n, 0))
    for (key, (x, y), name, spells, ap, cd, pais, orig, nota), grp in flat:
        nid = take_id(tab, name); newid[(tname, key)] = nid
        if tname == "Class" and y == 0:
            r = build(T_SIG, nid, tab, x, y, spells, 1, 0, 0, name); signature[sig_by_key[key]] = nid
        elif tname == "Class":
            r = build(T_ACTIVE if ap == "A" else T_PASSIVE, nid, tab, x, y, spells, 1, 0, 0, name, flags=0)
        else:
            r = build(T_SPEC, nid, tab, x, y, spells, 0, 1, 0, name, flags=0)
        su(r, F_GROUP, grp)
        if 4 <= y <= 7: su(r, F_GATE_AE if kind == "AE" else F_GATE_TE, g1)
        if y >= 8: su(r, F_GATE_AE if kind == "AE" else F_GATE_TE, g2)
        out_rows[nid] = (r, tname, key, pais)
        report["nos"][f"{tname}:{name}"] = dict(id=nid, pos=[x, y], magias=spells, grupo=grp)
for nid, (r, tname, key, pais) in list(out_rows.items()):
    links = []
    for p in pais:
        pid = newid[(tname, p)]; links.append(pid)
        pg = u(out_rows[pid][0], F_GROUP)
        if pg: links += [i for i, (rr, tn, kk, _) in out_rows.items() if tn == tname and u(rr, F_GROUP) == pg and i not in links]
    assert len(links) <= 15
    for k, i in enumerate(links): sub_(r, B_CONN + 4*k, i)
for tname, ex in design.EXTRA.items():
    tab = TABS[tname]; iid = cfg["ident"][tname]
    r = bytearray(byid[iid]); idn, ids, _ = ex["ident"]
    for i in range(F_SPELLS, F_SPELLS + 9): su(r, i, 0)
    su(r, F_SPELLS, ids); su(r, F_ICON, icon_for([ids])); sub_(r, B_FLAGS, ub(r, B_FLAGS) & ~0x8)
    out_rows[iid] = (r, tname, "ident", [])
    bykey.pop((tab, S(ca, u(r, F_NAME))), None)
    core = out_rows[newid[(tname, design.CORE[tname])]][0]
    su(core, F_REQ, iid); su(core, F_REQ + 1, signature[tname])
    for k, (lvl, name, s, ap) in enumerate(ex["auto"]):
        nid = take_id(tab, name)
        r = build(T_AUTO, nid, tab, 10, 2 + 2*k, [s], 0, 0, lvl, name)
        out_rows[nid] = (r, tname, "auto", [])
        report["nos"][f"{tname}:auto:{name}"] = dict(id=nid, pos=[10, 2+2*k], nivel=lvl, magia=s)
    srow = next(r for r in chr_["recs"] if S(chr_, u(r, 1)) == cfg["token"] and S(chr_, u(r, 2)).upper() == tname.upper())
    capstone = next((m for n in design.TREES[tname][0] for m in (n if isinstance(n, list) else [n]) if m[1][1] == 9), None)
    ex3 = [u(core, F_SPELLS), ex["auto"][0][2], capstone[3][-1] if capstone else ex["auto"][1][2]]
    su(srow, 24, ids); su(srow, 25, ex3[0]); su(srow, 26, ex3[1]); su(srow, 27, ex3[2]); su(srow, 28, iid)
for r in active:   # toda linha ativa da classe que nao esta no desenho novo vira DISABLED (inclui duplicatas de mesmo nome)
    nid = u(r, F_ID)
    if nid not in out_rows:
        sub_(r, B_FLAGS, ub(r, B_FLAGS) | 0x8); report["desativados"].append(f"{nid} {S(ca, u(r, F_NAME))} (aba {u(r, F_TAB)})")
idx = {u(r, F_ID): i for i, r in enumerate(ca["recs"])}
for nid, (r, *_) in out_rows.items():
    if nid in idx: ca["recs"][idx[nid]] = r
    else: ca["recs"].append(r)
save("CharacterAdvancement.dbc", ca); save("ChrSpecs.dbc", chr_)
json.dump(report, open(os.path.join(OUT, "relatorio-gerador.json"), "x"), indent=1, ensure_ascii=False)
print(f"{CL}: reusados {report['reusados']} | novos {report['novos']} | desativados {len(report['desativados'])} | linhas {len(ca['recs'])}")
