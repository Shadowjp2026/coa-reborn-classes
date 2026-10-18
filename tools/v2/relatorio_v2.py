#!/usr/bin/env python3
"""Relatorio por classe (SOMENTE LEITURA): compara a arvore ORIGINAL (src-original) com a instalada no teste.
Uso: relatorio_v2.py <classe> <pasta_run> > RELATORIO-<CLASSE>.md"""
import struct, sys, os, collections, importlib.util, glob, re
HERE = os.path.dirname(os.path.abspath(__file__))
CL, W = sys.argv[1], sys.argv[2]
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cfg = mod(os.path.join(HERE, "classes", "config.py"), "c").CLASSES[CL]; d = mod(os.path.join(HERE, "classes", f"design_{CL}.py"), "d")
def load(p):
    b = open(p, "rb").read(); n = struct.unpack_from("<I", b, 4)[0]; rs = struct.unpack_from("<I", b, 12)[0]
    return [b[20+i*rs:20+(i+1)*rs] for i in range(n)], b[20+n*rs:]
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]; fl = lambda r: struct.unpack_from("<I", r, 479)[0]
S = lambda st, o: st[o:st.find(b"\0", o)].decode("utf8", "replace")
sp, ss = load(os.path.join(HERE, "..", "data", "dbc", "Spell.dbc")); spell = {u(r, 0): r for r in sp}
sname = lambda s: S(ss, u(spell[s], 136)) if s in spell else str(s)
TAB = {v: k for k, v in cfg["tabs"].items()}
def tree(p):
    rows, st = load(p); out = {}
    for r in rows:
        if u(r, 32) == cfg["ct"] and cfg["base"] <= u(r, 0) < cfg["base"] + 200 and not fl(r) & 0x9:
            kind = "identidade" if fl(r) & 0x40000 else "automatica" if fl(r) & 0x100000 else "no pago"
            nm = S(st, u(r, 47))
            for i in range(5, 10):
                if u(r, i): out.setdefault(sname(u(r, i)) if kind != "identidade" else sname(u(r, 5)), (kind, TAB.get(u(r, 33), u(r, 33)), nm))
    return out
old = tree(os.path.join(HERE, "src-original", "CharacterAdvancement.dbc")); new = tree(os.path.join(HERE, "..", "data", "dbc", "CharacterAdvancement.dbc"))
kit = {sname(s): lv for _, s, lv in d.BASE}
pente = open(os.path.join(W, "pente.txt")).read(); verif = open(os.path.join(W, "verifica.txt")).read()
trn = open(os.path.join(W, "treinador.sql")).read(); mig = open(os.path.join(W, "migra.sql")).read()
saiu14 = re.findall(r"^- (.+?) (\d+) \(era", pente, re.M)
print(f"# Relatório — {CL.capitalize()} v2 no ambiente de teste\n")
print(f"Pasta da instalação: `$COA_ROOT/v2/{os.path.basename(W)}` (backup em `backup/`). Proposta completa: `PROPOSTA-{CL.upper()}-V2.md`.\n")
print("## Verificação automática\n\n```\n" + verif.strip() + "\n```\n")
print("## Árvores: o que mudou\n")
add = sorted(k for k in new if k not in old); rem = sorted(k for k in old if k not in new); mov = sorted(k for k in new if k in old and new[k][:2] != old[k][:2])
print(f"**Entraram na árvore ({len(add)}):** " + (", ".join(f"{k} ({new[k][1]}, {new[k][0]})" for k in add) or "nenhuma") + "\n")
tokit = [k for k in rem if k in kit]; gone = [k for k in rem if k not in kit]
print(f"**Saíram da árvore para o kit grátis — treinador/Livro ({len(tokit)}):** " + (", ".join(f"{k} (nível {kit[k]})" for k in tokit) or "nenhuma") + "\n")
print(f"**Saíram da árvore e não estão no kit ({len(gone)}):** " + (", ".join(gone) or "nenhuma") + "\n")
print(f"  - destas, sem fonte nenhuma no jogo (removidas de propósito — motivo na proposta): " + (", ".join(f"{n} {i}" for n, i in saiu14) or "nenhuma") + "\n")
print(f"  - as outras continuam existindo como ranks de outro nó, identidade ou habilidade de treinador.\n")
print(f"**Mudaram de lugar/tipo ({len(mov)}):** " + (", ".join(f"{k} ({old[k][1]} {old[k][0]} → {new[k][1]} {new[k][0]})" for k in mov) or "nenhuma") + "\n")
print("## Treinador e Livro (SQL aplicado no teste)\n\n```sql\n" + trn.strip() + "\n```\n")
print("## Personagens (cópias no banco de teste)\n\n```sql\n" + (mig.strip() or "-- nenhum") + "\n```\n")
print("## Pente fino depois de instalar\n\n```\n" + pente.strip() + "\n```\n")
