#!/usr/bin/env python3
"""Monta (NAO executa) o SQL do treinador/Livro de uma classe. Uso: treinador_v2.py <classe> <pasta_dados_exportados> > arquivo.sql
Regra (Receita v2 §4.6/§14.4 + ordem do dono): magia de no pago, automatica ou identidade sai do treinador da classe e do Livro 900100
(o rank usado e os ranks abaixo dele; ranks acima ficam como melhoria). Kit base que falta entra pela lista KIT_ADD do design."""
import sys, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
CL, D = sys.argv[1], sys.argv[2]
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cfg = mod(os.path.join(HERE, "classes", "config.py"), "c").CLASSES[CL]; d = mod(os.path.join(HERE, "classes", f"design_{CL}.py"), "d")
tsv = lambda n: [l.rstrip("\n").split("\t") for l in open(os.path.join(D, n)) if l.strip()]
trainers = [int(i) for i, t, rq in tsv("tr_types.tsv") if int(t) == 0 and int(rq) == cfg["cls"]] + [900100]
rows = collections.defaultdict(set)
for t, s, *_ in tsv("tr_spells.tsv"): rows[int(t)].add(int(s))
first = {}; ladder = collections.defaultdict(list)
for f, s, rk in tsv("ranks.tsv"): first[int(s)] = int(f); ladder[int(f)].append((int(rk), int(s)))
def below(s):  # o rank s e os de baixo
    if s not in first: return [s]
    ch = [x for _, x in sorted(ladder[first[s]])]; return ch[:ch.index(s) + 1]
used = []
for tn, (nodes, *_) in d.TREES.items():
    for n in nodes:
        for m in (n if isinstance(n, list) else [n]): used.append((f"{tn}:{m[2]}", m[3][0]))
for tn, ex in d.EXTRA.items():
    used.append((f"{tn}:identidade {ex['ident'][0]}", ex["ident"][1]))
    for lv, nm, s, ap in ex["auto"]: used.append((f"{tn}:auto {nm}", s))
kit = {s for _, s, _ in d.BASE}
dele = collections.defaultdict(list)
for label, s in used:
    for x in below(s):
        if x in kit: continue
        for ident in {x, x - 1100000 if x > 1100000 else x}:
            for t in trainers:
                if ident in rows[t]: dele[t].append((ident, label))
print(f"-- {CL} (TESTE): treinadores da classe {trainers[:-1]} + Livro 900100")
total = 0
for t in sorted(dele):
    ids = sorted({i for i, _ in dele[t]}); total += len(ids)
    print(f"-- treinador {t}: " + "; ".join(sorted({f'{i} ({l})' for i, l in dele[t]})))
    print(f"DELETE FROM acore_world.trainer_spell WHERE TrainerId={t} AND SpellId IN ({','.join(map(str, ids))});")
for t, s, lv in getattr(d, "KIT_ADD", []):
    if s not in rows[t]:
        print(f"INSERT IGNORE INTO acore_world.trainer_spell (TrainerId,SpellId,MoneyCost,ReqLevel) VALUES ({t},{s},0,{lv}); -- kit base sem fonte"); total += 1
print(f"-- total de linhas: {total}")
