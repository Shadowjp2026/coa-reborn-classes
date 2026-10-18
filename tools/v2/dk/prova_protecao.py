#!/usr/bin/env python3
"""Prova independente (so leitura): o que mudou entre os 7 DBC do ZZW antes e depois do DK. Uso: prova_protecao.py <antes> <depois>"""
import struct, sys, os, hashlib, collections
A, B = sys.argv[1:3]
def load(d, n):
    b = open(os.path.join(d, n), "rb").read(); m, c, f, rs, ss = struct.unpack("<4sIIII", b[:20])
    return [b[20+i*rs:20+(i+1)*rs] for i in range(c)], b[20+c*rs:], f
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]
ok = True
for n in ("CharacterAdvancementTabTypes", "SkillLine", "SkillLineAbility", "SkillRaceClassInfo"):
    same = open(os.path.join(A, n + ".dbc"), "rb").read() == open(os.path.join(B, n + ".dbc"), "rb").read()
    print(f"{n}: {'IDENTICO' if same else 'MUDOU'}"); ok &= same
oa, osa, _ = load(A, "CharacterAdvancement.dbc"); na, nsa, _ = load(B, "CharacterAdvancement.dbc")
print("CA strings antigas preservadas:", nsa.startswith(osa)); ok &= nsa.startswith(osa)
grp = collections.Counter(); bad = []
def faixa(r):
    i, ct = u(r, 0), u(r, 32)
    if 142000 <= i < 142400: return "Support 142000-142399"
    if 140000 <= i < 142000: return "9 classicas 140000-141999"
    if 142400 <= i < 142600: return "DK 142400-142599"
    if 12 <= ct <= 32 or ct in range(1, 36) and ct not in (45,): return f"CoA/outros CT{ct}"
    return f"CT{ct}"
for i, r in enumerate(oa):
    k = "CT45 original" if u(r, 32) == 45 else faixa(r)
    if na[i] == r: grp[(k, "identica")] += 1
    else:
        diff = [o for o in range(len(r)) if r[o] != na[i][o]]
        if u(r, 32) == 45 and all(479 <= o < 483 for o in diff) and u(na[i], 0) == u(r, 0) and struct.unpack_from("<I", na[i], 479)[0] == struct.unpack_from("<I", r, 479)[0] | 8:
            grp[(k, "so byte 479 |= 0x8")] += 1
        else: grp[(k, "MUDOU")] += 1; bad.append(u(r, 0))
for r in na[len(oa):]: grp[(faixa(r), "nova")] += 1; bad += [u(r, 0)] if not 142400 <= u(r, 0) < 142600 or u(r, 32) != 45 else []
for k, v in sorted(grp.items()): print(f"  CA {k[0]:28s} {k[1]:20s} {v}")
oc, ocs, cf = load(A, "ChrSpecs.dbc"); nc, ncs, _ = load(B, "ChrSpecs.dbc")
chg = [(u(a, 0), [i for i in range(cf) if u(a, i) != u(b, i)]) for a, b in zip(oc, nc) if a != b]
print("ChrSpecs mudadas:", chg, "| strings iguais:", ocs == ncs, "| linhas", len(oc), len(nc))
ok &= ocs == ncs and len(oc) == len(nc) and all(i in (79, 80, 81) and set(d) <= {24, 25, 26, 27, 28} for i, d in chg)
oe, _, ef = load(A, "CharacterAdvancementEssence.dbc"); ne, _, _ = load(B, "CharacterAdvancementEssence.dbc")
ech = collections.Counter((u(a, 2), tuple(i for i in range(ef) if u(a, i) != u(b, i))) for a, b in zip(oe, ne) if a != b)
print("Essence mudadas (classe, campos):", dict(ech)); ok &= all(c == 6 and set(f) <= {7, 8} for c, f in ech)
ok &= not bad
print("LINHAS FORA DO PERMITIDO:", bad[:20] or "nenhuma"); print("RESULTADO:", "PROTEGIDO" if ok else "VIOLACAO")
