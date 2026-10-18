#!/bin/bash
# So SELECT no banco de TESTE; grava numa pasta NOVA. Uso: exporta_dados.sh <pasta_nova>
set -e; D=$1; [ -e "$D" ] && { echo "pasta ja existe"; exit 1; }; mkdir -p "$D"
Q="docker exec $DB_CONTAINER mysql -u$DB_USER -p$DB_PASS -N -B -e"
$Q "SELECT Id,Type,Requirement FROM acore_world.trainer" 2>/dev/null > $D/tr_types.tsv
$Q "SELECT TrainerId,SpellId,ReqLevel,MoneyCost,ReqAbility1 FROM acore_world.trainer_spell" 2>/dev/null > $D/tr_spells.tsv
$Q "SELECT first_spell_id,spell_id,\`rank\` FROM acore_world.spell_ranks" 2>/dev/null > $D/ranks.tsv
$Q "SELECT racemask,classmask,Spell FROM acore_world.playercreateinfo_spell_custom" 2>/dev/null > $D/create_custom.tsv
$Q "SELECT guid,name,class,level FROM acore_characters.characters WHERE class IN (1,2,3,4,5,7,8,9,11)" 2>/dev/null > $D/chars.tsv
wc -l $D/*.tsv
G=$(awk -F"\t" "{printf \"%s%s\", (NR>1?\",\":\"\"), \$1}" $D/chars.tsv)
[ -n "$G" ] && $Q "SELECT guid,spell,specMask FROM acore_characters.character_spell WHERE guid IN ($G)" 2>/dev/null > $D/char_spells.tsv
[ -n "$G" ] && $Q "SELECT guid,source,data FROM acore_characters.character_settings WHERE guid IN ($G) AND source LIKE \"core.ascension_slot%\"" 2>/dev/null > $D/char_slots.tsv
true
