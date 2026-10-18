# Valida uma CoaLevelBuildData.h contra um CharacterAdvancement.dbc e o orcamento de essencia, ate MAXL.
# Regras = as do servidor (nivel campo 26, requisitos 2-4, orcamento por nivel, portao por aba 38/39).
import re, struct, sys, collections
H, DBC, ESS, MAXL = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
def load(p):
    b = open(p, "rb").read(); m, c, f, rs, ss = struct.unpack("<4sIIII", b[:20])
    return [b[20+i*rs:20+(i+1)*rs] for i in range(c)]
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]
rows = {u(r,0): dict(tab=u(r,33), ae=u(r,14), te=u(r,15), lvl=u(r,26), gate=u(r,39) if u(r,15) else u(r,38),
        req=[u(r,i) for i in (2,3,4) if u(r,i)]) for r in load(DBC)}
budget = collections.defaultdict(dict)
for r in load(ESS):
    v = struct.unpack_from("<9I", r)
    if not any(v[3:7]): budget[v[2]][v[1]] = (v[7], v[8])
picks = [tuple(map(int, m)) for m in re.findall(r"\{(\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\}", open(H).read())]
byspec = collections.defaultdict(list)
for p in picks: byspec[(p[0], p[1])].append(p)
bad = collections.Counter(); spent60 = []; above = 0; ex = {}
for (cls, spec), pl in byspec.items():
    have = {}; spent = [0, 0]
    for p in sorted(pl, key=lambda p: p[2]):
        L, tree, ent, rank = p[2], p[3], p[4], p[5]
        if L > MAXL: above += 1; continue
        e = rows.get(ent)
        if not e: bad["entrada inexistente"] += 1; ex.setdefault("entrada inexistente", p); continue
        if e["lvl"] > L: bad["nivel"] += 1; ex.setdefault("nivel", p)
        if any(q in rows and (rows[q]["ae"] or rows[q]["te"]) and not have.get(q) for q in e["req"]): bad["requisito"] += 1; ex.setdefault("requisito", p)
        if e["gate"]:
            inv = sum(rows[k]["ae" if tree == 0 else "te"]*v for k, v in have.items() if rows[k]["tab"] == e["tab"] and rows[k]["gate"] < e["gate"])
            if inv < e["gate"]: bad["portao"] += 1; ex.setdefault("portao", p)
        cost = (e["ae"] if tree == 0 else e["te"]) * (rank - have.get(ent, 0))
        spent[tree] += cost; have[ent] = rank
        if spent[tree] > budget[cls].get(L, (0, 0))[tree]: bad["orcamento"] += 1; ex.setdefault("orcamento", p)
    b = budget[cls].get(MAXL, (0, 0)); spent60.append((spent[0], spent[1], b[0], b[1]))
print(H.split("/")[-1], "| picks", len(picks), "| specs", len(byspec), "| picks acima de", MAXL, above)
print("  problemas:", dict(bad) or "nenhum", ex if bad else "")
print("  gasto no %d (hab/tal) min %d/%d de %d/%d | specs abaixo do orcamento-1: %d" % (MAXL, min(s[0] for s in spent60), min(s[1] for s in spent60),
      spent60[0][2], spent60[0][3], sum(1 for s in spent60 if s[0] < s[2]-1 or s[1] < s[3]-1)))
