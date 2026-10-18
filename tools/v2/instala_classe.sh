#!/bin/bash
# Instala UMA classe v2 no AMBIENTE DE TESTE (nunca na producao). Uso: instala_classe.sh <classe>
# backup -> exporta (SELECT) -> gera em pasta nova -> verifica -> SQL treinador/migracao -> para teste -> aplica -> sobe -> pente fino
set -e
CL=$1; cd "$COA_ROOT/v2"; T=$(date +%m%d-%H%M%S); W=run-$CL-$T; mkdir $W
[ "$(docker inspect -f "{{.Name}}" $WORLD_CONTAINER)" = "/$WORLD_CONTAINER" ] || { echo "container de teste nao encontrado"; exit 1; }
# 1) backup
mkdir $W/backup; cp -p ../data/dbc/CharacterAdvancement.dbc ../data/dbc/ChrSpecs.dbc $W/backup/
bash exporta_dados.sh $W/dados-antes > /dev/null
G=$(awk -F"\t" -v c=$(python3 -I -c "import importlib.util as i;s=i.spec_from_file_location(\"c\",\"classes/config.py\");m=i.module_from_spec(s);s.loader.exec_module(m);print(m.CLASSES[\"$CL\"][\"cls\"])") "\$3==c{printf \"%s%s\", (n++?\",\":\"\"), \$1}" $W/dados-antes/chars.tsv)
docker exec $DB_CONTAINER mysqldump -u$DB_USER -p$DB_PASS --no-create-info acore_world trainer_spell 2>/dev/null > $W/backup/trainer_spell-completo.sql
[ -n "$G" ] && docker exec $DB_CONTAINER mysqldump -u$DB_USER -p$DB_PASS --no-create-info --where="guid IN ($G)" acore_characters character_spell character_settings character_action 2>/dev/null > $W/backup/personagens.sql
# 2) gera + verifica
python3 -I gera_v2.py $CL ../data/dbc $W/out
python3 -I verifica_v2.py $CL ../data/dbc $W/out | tee $W/verifica.txt; V=${PIPESTATUS[0]}
[ "$V" = 0 ] || { echo "VERIFICACAO FALHOU ($V) - nada aplicado"; exit 1; }
python3 -I treinador_v2.py $CL $W/dados-antes > $W/treinador.sql
python3 -I migra_v2.py $CL ../data/dbc $W/out $W/dados-antes > $W/migra.sql
# 3) aplica no teste
docker stop $WORLD_CONTAINER > /dev/null
cp $W/out/CharacterAdvancement.dbc $W/out/ChrSpecs.dbc ../data/dbc/
docker exec -i $DB_CONTAINER mysql -u$DB_USER -p$DB_PASS < $W/treinador.sql 2>&1 | grep -v Warning || true
docker exec -i $DB_CONTAINER mysql -u$DB_USER -p$DB_PASS < $W/migra.sql 2>&1 | grep -v Warning || true
docker start $WORLD_CONTAINER > /dev/null
for i in $(seq 1 40); do docker logs --since 3m $WORLD_CONTAINER 2>&1 | grep -q "daemon) ready" && break; sleep 10; done
docker logs --since 3m $WORLD_CONTAINER 2>&1 | sed "s/\x1b\[[0-9;]*m//g" | grep -E "Loaded [0-9]+ CoA talent|daemon\) ready|ABORT" | cut -c1-140 | tee $W/subida.txt
# 4) pente fino
bash exporta_dados.sh $W/dados-depois > /dev/null
python3 -I pente_v2.py $CL ../data/dbc $W/dados-depois > $W/pente.txt; tail -3 $W/pente.txt
# 5) patch do cliente (7 DBC, igual ao servidor)
mkdir $W/zzw; for n in CharacterAdvancement CharacterAdvancementEssence CharacterAdvancementTabTypes ChrSpecs SkillLine SkillLineAbility SkillRaceClassInfo; do cp ../data/dbc/$n.dbc $W/zzw/; A+=($n.dbc "DBFilesClient\\$n.dbc"); done
(cd $W/zzw && LD_LIBRARY_PATH=$MPQ_TOOLS $MPQ_TOOLS/mkpatch ../patch-ZZW.MPQ "${A[@]}" | tail -1)
md5sum ../data/dbc/CharacterAdvancement.dbc $W/patch-ZZW.MPQ "$PROD_DBC/CharacterAdvancement.dbc"
echo "PRONTO $W"
