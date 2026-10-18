#!/usr/bin/env python3
"""Cria verifica_v2_dk.py a partir de verifica_v2.py: excecao de protecao SO para o ClassType da classe nova
(linhas originais fora da faixa: so o byte 479 pode mudar e so ganhando 0x8) + Essence (V34) da classe."""
import os
H = os.path.join(os.environ.get("COA_ROOT", "."), "v2") + "/"
s = open(H + "verifica_v2.py").read()
def sub(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
sub('"""Verificacao generica (somente leitura). Uso: verifica_v2.py <classe> <dir_antes> <dir_gerado>',
    '"""Verificacao DK v2 / classe nova (somente leitura) - copia do verifica_v2.py com a excecao do D10.\nUso: verifica_v2_dk.py <classe> <dir_antes> <dir_gerado>\n'
    'Excecao (so quando cfg["nova"]): linhas do ClassType da classe FORA da faixa podem mudar so o byte 479 e so ganhando 0x8;\n'
    'Essence: so os campos 7-8 das linhas da classe podem mudar e precisam ser = classe 29 (V34). Todo o resto: byte-identico.')
sub('''for i, r in enumerate(oa):
    if not mine(r) and na[i] != r: prot.append(f"linha {u(r,0)} (ClassType {u(r,32)}) mudou")''',
'''def so_desativou(a, b):   # D10: unica mudanca permitida fora da faixa = byte 479 |= 0x8
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
if mismatch: erros.append(f"Essence da classe {cfg['cls']} diferente da classe 29 em {len(mismatch)} linhas")''')
sub('print("PROTECAO:", "OK" if not prot else prot[:10])',
    'print(f"DESATIVADAS FORA DA FAIXA (ClassType {CT}): {sum(1 for r in fora if ub(r, 479) & 0x8)} de {len(fora)}")\nprint("PROTECAO:", "OK" if not prot else prot[:10])')
open(H + "verifica_v2_dk.py", "x").write(s); print("verifica_v2_dk.py criado")
