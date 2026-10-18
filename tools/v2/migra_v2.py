#!/usr/bin/env python3
"""Monta (NAO executa) o SQL de migracao dos personagens da classe no banco de TESTE (Receita v2 §14.3, versao de teste):
zera os slots de build salvos e tira as magias das arvores (antiga e nova) que nao sao kit base; kit e treinador ficam.
Uso: migra_v2.py <classe> <dir_dbc_antes> <dir_dbc_depois> <pasta_dados>"""
import struct, sys, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
CL, A, B, D = sys.argv[1:5]
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cfg = mod(os.path.join(HERE, "classes", "config.py"), "c").CLASSES[CL]; d = mod(os.path.join(HERE, "classes", f"design_{CL}.py"), "d")
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]; fl = lambda r: struct.unpack_from("<I", r, 479)[0]
def rows(p):
    b = open(os.path.join(p, "CharacterAdvancement.dbc"), "rb").read(); n = struct.unpack_from("<I", b, 4)[0]; rs = struct.unpack_from("<I", b, 12)[0]
    return [b[20+i*rs:20+(i+1)*rs] for i in range(n)]
kit = {s for _, s, _ in d.BASE}; sp = set()
for p in (A, B):
    for r in rows(p):
        if u(r, 32) == cfg["ct"] and cfg["base"] <= u(r, 0) < cfg["base"] + 200 and not fl(r) & 0x9 and (u(r, 14) or u(r, 15)):
            sp |= {u(r, i) for i in range(5, 10) if u(r, i)}
sp -= kit
G = [l.split("\t")[0] for l in open(os.path.join(D, "chars.tsv")) if l.strip() and int(l.split("\t")[2]) == cfg["cls"]]
print(f"-- {CL} (TESTE): personagens {G or 'nenhum'}")
if G and sp:
    g = ",".join(G); s = ",".join(map(str, sorted(sp)))
    print(f"DELETE FROM acore_characters.character_settings WHERE guid IN ({g}) AND source LIKE 'core.ascension_slot.%';")
    print(f"DELETE FROM acore_characters.character_spell WHERE guid IN ({g}) AND spell IN ({s});")
    print(f"DELETE FROM acore_characters.character_action WHERE guid IN ({g}) AND type=0 AND action IN ({s});")

# regra do pente fino do Warrior: kit base que vinha de linha automatica que saiu -> entregar aos personagens que ja existem
chars = [l.rstrip("\n").split("\t") for l in open(os.path.join(D, "chars.tsv")) if l.strip() and int(l.split("\t")[2]) == cfg["cls"]]
lvkit = {s: lv for _, s, lv in d.BASE}
for g, name, c, lv in chars:
    for s, klv in sorted(lvkit.items()):
        if klv <= int(lv) and klv <= 1:
            print(f"INSERT IGNORE INTO acore_characters.character_spell (guid,spell,specMask) VALUES ({g},{s},255); -- kit nivel {klv}")
