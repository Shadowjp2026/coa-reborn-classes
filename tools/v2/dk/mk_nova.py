#!/usr/bin/env python3
"""Cria gera_v2_nova.py (modo 'classe nova') a partir de gera_v2.py, sem tocar no original."""
import os
H = os.path.join(os.environ.get("COA_ROOT", "."), "v2") + "/"
s = open(H + "gera_v2.py").read()
def sub(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
sub('"""Gerador v2 generico (Receita v2 §4, §14.2) - SO PARA O AMBIENTE DE TESTE.',
    '"""Gerador v2 - MODO CLASSE NOVA (DK v2, 17/10) - copia do gera_v2.py com 4 acrescimos, SO PARA O AMBIENTE DE TESTE.\n'
    'Acrescimos (so quando cfg["nova"]): (1) cria as 3 linhas de identidade a partir do molde 140268 (src-original);\n'
    '(2) desativa (byte 479 |= 0x8, nunca apaga) as linhas originais do ClassType FORA da faixa; (3) Essence da classe =\n'
    'curva da classe 29 (normal e modo, campos 7-8); (4) grava tambem CharacterAdvancementEssence.dbc na saida.\n'
    'Para as 9 classes ja feitas use o gera_v2.py original (este arquivo recusa classe sem cfg["nova"]).\n')
sub('T = {u(r, F_ID): bytes(r) for r in tmpl["recs"] if u(r, F_ID) in (140319, 140322, 140211, 140308, 140200)}',
    'assert cfg.get("nova"), "gera_v2_nova.py so para classe nova (cfg[\'nova\']); use gera_v2.py"\n'
    'T = {u(r, F_ID): bytes(r) for r in tmpl["recs"] if u(r, F_ID) in (140319, 140322, 140211, 140308, 140200, 140268)}\nT_IDENT = bytearray(T[140268])')
sub('free = [i for i in range(LO, HI) if i not in byid]',
    'free = [i for i in range(LO, HI) if i not in byid and i not in cfg["ident"].values()]')
sub('''    tab = TABS[tname]; iid = cfg["ident"][tname]
    r = bytearray(byid[iid]); idn, ids, _ = ex["ident"]''',
'''    tab = TABS[tname]; iid = cfg["ident"][tname]
    idn, ids, _ = ex["ident"]
    if iid in byid: r = bytearray(byid[iid])
    else:   # (1) identidade nova a partir do molde: so id, ClassType, aba, nome (mesmo formato "Arms Warrior")
        r = bytearray(T_IDENT); su(r, F_ID, iid); su(r, F_CT, CT); su(r, F_TAB, tab)
        su(r, F_NAME, addstr(ca, f"{tname} {cfg['nome']}")); report["novos"] += 1''')
sub('''idx = {u(r, F_ID): i for i, r in enumerate(ca["recs"])}''',
'''# (2) linhas originais do ClassType fora da faixa: so o byte 479 |= 0x8 (DISABLED), nada mais
report["desativados_fora"] = []
for r in ca["recs"]:
    if u(r, F_CT) == CT and not (LO <= u(r, F_ID) < HI) and not ub(r, B_FLAGS) & 0x8:
        sub_(r, B_FLAGS, ub(r, B_FLAGS) | 0x8); report["desativados_fora"].append(u(r, F_ID))
# (3) Essence: AE/TE (campos 7-8) da classe = classe 29 no mesmo nivel (campo 1) e modo (campo 6)
ess = load(SRC, "CharacterAdvancementEssence.dbc"); ref = {(u(r, 1), u(r, 6)): (u(r, 7), u(r, 8)) for r in ess["recs"] if u(r, 2) == 29}
report["essence_mudadas"] = 0
for r in ess["recs"]:
    if u(r, 2) == cfg["cls"]:
        k = (u(r, 1), u(r, 6)); assert k in ref and all(u(r, i) == 0 for i in (3, 4, 5)), f"essence sem par {k}"
        if (u(r, 7), u(r, 8)) != ref[k]: su(r, 7, ref[k][0]); su(r, 8, ref[k][1]); report["essence_mudadas"] += 1
idx = {u(r, F_ID): i for i, r in enumerate(ca["recs"])}''')
sub('save("CharacterAdvancement.dbc", ca); save("ChrSpecs.dbc", chr_)',
    'save("CharacterAdvancement.dbc", ca); save("ChrSpecs.dbc", chr_); save("CharacterAdvancementEssence.dbc", ess)')
sub('''print(f"{CL}: reusados {report['reusados']} | novos {report['novos']} | desativados {len(report['desativados'])} | linhas {len(ca['recs'])}")''',
    '''print(f"{CL}: reusados {report['reusados']} | novos {report['novos']} | desativados {len(report['desativados'])} | desativados fora da faixa {len(report['desativados_fora'])} | essence {report['essence_mudadas']} | linhas {len(ca['recs'])}")''')
open(H + "gera_v2_nova.py", "x").write(s); print("gera_v2_nova.py criado")
