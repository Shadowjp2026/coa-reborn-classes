#!/usr/bin/env python3
"""DK v2 (TESTE) - monta (NAO executa) o SQL de dados: M1, M3, M4, M5, M9 (+D3, D6, D7), M12 (script) e junta o M10 do treinador_v2.py.
Uso: dados_dk.py <pasta_dk>  -> grava <pasta_dk>/dados-dk.sql e <pasta_dk>/dados-dk-rollback.sql"""
import sys, os, subprocess, collections, importlib.util
D = sys.argv[1]
def q(sql):
    out = subprocess.run(["docker", "exec", os.environ.get("DB_CONTAINER", "ac-database"), "mysql", "-u" + os.environ.get("DB_USER", "root"), "-p" + os.environ["DB_PASS"], "-N", "-B", "acore_world", "-e", sql], capture_output=True, text=True, check=True).stdout
    return [l.split("\t") for l in out.splitlines() if l.strip()]
s_ = importlib.util.spec_from_file_location("d", os.path.join(os.environ.get("COA_ROOT", "."), "v2/classes/design_deathknight.py")); d = importlib.util.module_from_spec(s_); s_.loader.exec_module(d)
L = ["-- DK v2 (TEST database) - gerado por dados_dk.py; backup em backup/db/*.sql", "START TRANSACTION;"]
R = ["-- ROLLBACK dos dados do DK v2 (TESTE): reimporta as tabelas do backup", "-- docker exec -i $DB_CONTAINER mysql -u$DB_USER -p$DB_PASS acore_world < backup/db/<tabela>.sql (para cada tabela abaixo)"]
# M1 - stats 1-54 da classe 6 = Warrior
assert q("SELECT count(*) FROM player_class_stats WHERE Class=6 AND Level<55")[0][0] == "0"
L += ["-- M1: player_class_stats classe 6 niveis 1-54 = classe 1 (o DK 55-80 ja e praticamente o Warrior)",
      "INSERT INTO player_class_stats (Class,Level,BaseHP,BaseMana,Strength,Agility,Stamina,Intellect,Spirit) SELECT 6,Level,BaseHP,BaseMana,Strength,Agility,Stamina,Intellect,Spirit FROM player_class_stats WHERE Class=1 AND Level<55;"]
# M3 - posicao: copia da linha da mesma raca (classe 1; sem Warrior: 2, depois 8, depois qualquer outra)
rows = q("SELECT race,class,map,zone,position_x,position_y,position_z,orientation FROM playercreateinfo")
by = collections.defaultdict(dict)
for r in rows: by[int(r[0])][int(r[1])] = r[2:]
L.append("-- M3: posicao inicial do DK = zona inicial da propria raca (so UPDATE das linhas que ja existem; disponibilidade raca x classe intocada)")
for race in sorted(by):
    if 6 not in by[race]: continue
    src = next((c for c in (1, 2, 8) + tuple(sorted(by[race])) if c != 6 and c in by[race]), None)
    assert src, race
    m, z, x, y, zz, o = by[race][src]
    L.append(f"UPDATE playercreateinfo SET map={m},zone={z},position_x={x},position_y={y},position_z={zz},orientation={o} WHERE race={race} AND class=6; -- copia da classe {src}")
# M4 - itens nivel 1 (D8: so playercreateinfo_item). Pecas = Warrior da raca (CharStartOutfit do servidor); arma 2 maos que o DK sabe usar
import struct
b = open(os.path.join(os.environ.get("COA_ROOT", "."), "data/dbc/CharStartOutfit.dbc"), "rb").read(); n, f, rs = struct.unpack_from("<III", b, 4)
war = {}
for i in range(n):
    o = 20 + i*rs; race, cls = b[o+4], b[o+5]
    if cls != 1 or race in war: continue
    war[race] = [x for x in struct.unpack_from("<24i", b, o+8) if x > 0]
TWO_H_OK = {12282, 49778, 23346}   # 2H machado / 2H espada (o DK tem 44/172/43/55; nao tem 2H maca nem arremesso)
info = {int(r[0]): (int(r[1]), int(r[2])) for r in q("SELECT entry,class,InventoryType FROM item_template WHERE entry IN (%s)" % ",".join(str(x) for v in war.values() for x in v))}
L.append("-- M4: itens nivel 1 por raca (as pecas do Warrior da raca + Hearthstone + arma de 2 maos); o conjunto Acherus (nivel 55) continua vindo do CharStartOutfit e vai para a bolsa; a linha 40582 -1 (que tira a Scourgestone) fica")
for race in sorted(by):
    if 6 not in by[race]: continue
    items = war.get(race)
    if not items:
        src = next(c for c in (2, 8) if c in by[race]); L.append(f"-- raca {race} sem Warrior no DBC"); continue
    weapon = [x for x in items if info.get(x, (0, 0))[0] == 2]
    keep = [x for x in items if info.get(x, (0, 0))[0] != 2]
    w = next((x for x in weapon if x in TWO_H_OK), 12282)
    for it in keep + [w]:
        L.append(f"INSERT INTO playercreateinfo_item (race,class,itemid,amount,Note) VALUES ({race},6,{it},1,'DK v2: kit nivel 1');")
# M5 - pericias Reborn na criacao (como as outras 9)
L.append("-- M5: pericias Reborn do DK na criacao (ensinam Blood Strike, Icy Touch, Plague Strike, Blood Presence, Death Coil, Death Grip, Frost Fever, Blood Plague, Runic Focus)")
for sk in (11770, 11771, 11772):
    L.append(f"INSERT INTO playercreateinfo_skills (raceMask,classMask,skill,`rank`,comment) VALUES (0,32,{sk},0,'CoA60 classico: pericia Reborn da classe (habilidades iniciais), todas as racas');")
# M12 - script do Death Coil nas gemeas (o C++ da build teste-dk lanca as pecas gemeas)
L.append("-- M12: spell_dk_death_coil nas gemeas do Death Coil (ranks 1-5)")
for s in (1147541, 1149892, 1149893, 1149894, 1149895):
    L.append(f"INSERT INTO spell_script_names (spell_id,ScriptName) VALUES ({s},'spell_dk_death_coil');")
# M10 (+ nos pagos do Livro) - do treinador_v2.py
L.append("-- M10 + Livro: rank 1 dos 9 nos pagos sai do treinador 13 e do Livro 900100 (treinador_v2.py)")
L += [l for l in open(os.path.join(D, "treinador-base.sql")).read().splitlines() if l.startswith("DELETE")]
# M9 - Livro 900100: niveis pela curva (kit + melhorias D2-A) e preco pela escada do treinador do Warrior (mesma regra do Reborn)
price = {}
for lv, mc in q("SELECT ReqLevel, max(MoneyCost) FROM trainer_spell WHERE TrainerId=1 GROUP BY ReqLevel"): price[int(lv)] = int(mc)
def cost(lv): return price[max(k for k in price if k <= lv)]
book = {int(r[0]): (int(r[1]), int(r[2]), int(r[3])) for r in q("SELECT SpellId,ReqLevel,MoneyCost,ReqAbility1 FROM trainer_spell WHERE TrainerId=900100")}
want = {}
for name, s, lv in d.BASE:
    if lv > 1: want[s] = (lv, name)
RUNES = {53343: 20, 53341: 20, 53342: 23, 54447: 23, 53331: 33, 53323: 39, 54446: 39, 53344: 48, 62158: 55, 70164: 55}
for s, lv in RUNES.items(): want[s] = (lv, "runa")
for l in open(os.path.join(D, "ranks_curva.tsv")).read().splitlines()[1:]:
    st, tw, nm, rk, lw, lp = l.split("\t"); want[int(tw)] = (int(lp), f"{nm} {rk}")
# D3: sem Death Gate. Death Coil: as linhas 49892-49895 do Livro sao o stock "Grave Coil" (custo de raiva, inutil para o DK) -> trocar pela gemea Death Coil r2-r5
L.append("-- D3: Death Gate nao e entregue")
L.append("DELETE FROM trainer_spell WHERE TrainerId=900100 AND SpellId=50977;")
L.append("-- Death Coil: Livro trazia o stock 'Grave Coil' (raiva) r1 e r7-r10; o DK usa a gemea Death Coil (r1 pela pericia 11772). r1 stock sai; r7-r10 stock viram a gemea r2-r5 (mesma cadeia do SpellRank do cliente)")
L.append("DELETE FROM trainer_spell WHERE TrainerId=900100 AND SpellId=47541;")
prev = 1147541
for stock, twin in ((49892, 1149892), (49893, 1149893), (49894, 1149894), (49895, 1149895)):
    assert stock in book and twin not in book
    lv = want[twin][0]; mc = cost(lv)
    L.append(f"UPDATE trainer_spell SET SpellId={twin},ReqAbility1={prev},ReqLevel={lv},MoneyCost={mc} WHERE TrainerId=900100 AND SpellId={stock}; -- {want[twin][1]}")
    prev = twin; want.pop(twin)
L.append("-- M9: Livro 900100 - nivel pela curva (§4.1 kit, §3 runas/montaria, ranks_curva.tsv melhorias) e preco = escada do treinador do Warrior no mesmo nivel (gratis continua gratis)")
miss = []
for s, (lv, nm) in sorted(want.items(), key=lambda kv: (kv[1][0], kv[0])):
    if s not in book: miss.append((s, nm)); continue
    old_lv, old_mc, _ = book[s]; mc = cost(lv) if old_mc else 0
    L.append(f"UPDATE trainer_spell SET ReqLevel={lv},MoneyCost={mc} WHERE TrainerId=900100 AND SpellId={s}; -- {nm} (era nivel {old_lv}, {old_mc})")
# D7: Corpse Dust -> Glyph of Raise Dead (gemea 1160200, passiva NO_REAGENT_USE) no Livro junto do Raise Dead
L.append("-- D7: Raise Dead sem cadaver pede Corpse Dust; opcao menos invasiva = Glyph of Raise Dead (gemea 1160200, passiva) no Livro no nivel 14, gratis")
assert 1160200 not in book
L.append("INSERT INTO trainer_spell (TrainerId,SpellId,MoneyCost,ReqSkillLine,ReqSkillRank,ReqAbility1,ReqAbility2,ReqAbility3,ReqLevel,VerifiedBuild) VALUES (900100,1160200,0,0,0,1146584,0,0,14,0);")
L.append("COMMIT;")
for s, nm in miss: L.append(f"-- AVISO: {s} {nm} nao esta no Livro (sem UPDATE)")
open(os.path.join(D, "dados-dk.sql"), "x").write("\n".join(L) + "\n")
R += [f"-- {t}" for t in ("player_class_stats", "playercreateinfo", "playercreateinfo_item", "playercreateinfo_skills", "spell_script_names", "trainer_spell")]
open(os.path.join(D, "dados-dk-rollback.sql"), "x").write("\n".join(R) + "\n")
print(len(L), "linhas; avisos", miss)
