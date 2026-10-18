# Install

**Read first:** this is a study project. Back up your database, your server tree and your client
`Data` folder before you start. Never install client patches while the game is running.

## Requirements
- Server source: the AzerothCore CoA fork by ilusixn, branch `coa-custom-1.5` at
  `e69c0bf748` ("CoA Custom 1.5.1"), merged with jealous-sound `main` at `6985abb527` (2026-10-10).
  Our patches were produced on top of that merge; on other revisions they may need manual rebasing.
- Playerbots module 1.9.x was present on the test realm (not required by these patches).
- Docker-based AzerothCore setup (the tools call `docker exec <db container> mysql ...`).
- Client: CoA Custom 1.5.1 client (3.3.5a 12340 based) with its own `patch-B/M/T` MPQs.
- Python 3.10+, `patch`, gcc + StormLib (to build `client/build/mkpatch`).

Environment variables used by the tools: `COA_ROOT` (server tree, default `.`), `DB_CONTAINER`
(default `ac-database`), `DB_USER` (default `root`), `DB_PASS`, `WORLD_CONTAINER` (default
`ac-worldserver`), `MPQ_TOOLS` (folder with `mkpatch` + `libstorm.so`).

## 1. Server source
```bash
cd <your azerothcore-wotlk-coa checkout>
git am /path/to/repo/core/patches/000[1-4]-*.patch
git apply /path/to/repo/core/patches/0005-working-tree-changes.patch
```
Then build and recreate the worldserver container (a plain `restart` keeps the old image):
```bash
docker compose build ac-worldserver && docker compose up -d --force-recreate ac-worldserver
```
Set in `coa.conf`: `CoA.ClassModel = "coa wcr"`. Optional (mod-spellbook): `Spellbook.Classic.MaxLevel`.

## 2. Generate the talent DBCs from YOUR server data
The generators read your installed `CharacterAdvancement.dbc` / `ChrSpecs.dbc` / `CharacterAdvancementEssence.dbc`
and write new ones; nothing is shipped pre-generated.
```bash
export COA_ROOT=<server tree>
tools/aplica_todas.sh            # generates the 9 classic trees (see script header)
tools/fecha_regen.sh <in_dir> <out_dir>   # stabilization + Support freeze + duplicate-audit gate
```
`fecha_regen.sh` runs `congela_support.py` while a file named `SUPPORT_CONGELADA` exists in `COA_ROOT`
(create it: `touch $COA_ROOT/SUPPORT_CONGELADA`). The audit gate must print `TRAVA DUPLICADAS: OK`.
Copy the output DBCs to `env/dist/data/dbc/` and restart the worldserver.

## 3. World database
```bash
for f in sql/world/*.sql; do docker exec -i $DB_CONTAINER mysql -u$DB_USER -p$DB_PASS acore_world < "$f"; done
```
Do **not** apply `sql/support-frozen/support_v2_db.sql` (that would re-enable Support rules).
`sql/support-frozen/freeze_support_world.sql` is safe to apply (disables Support rows if present).

## 4. Client patches
```bash
python3 client/build/extract_originals.py orig <client>/Data/patch-T.MPQ <client>/Data/patch-M.MPQ <client>/Data/patch-B.MPQ
ORIG=orig GEN=<generated dbc dir> OUT=out MPQ_TOOLS=<dir with mkpatch+libstorm.so> client/build/build_patches.sh
```
Bases used to build the deltas/diffs: SkillLineAbility, ChrRaces, CharBaseInfo, SkillRaceClassInfo,
CharacterCreate.lua, UIParent.lua, MainMenuBarMicroButtons.lua = `patch-T`; SkillLine = `patch-M`;
the other Lua files = `patch-B`. Copy `out/patch-ZZ*.MPQ` into the client `Data` folder **with the game closed**.

## 5. Verify
- worldserver log: `Loaded N CoA talent entries ... 97 specializations`, no new errors.
- `python3 tools/audita_duplicadas.py env/dist/data/dbc/ --trava` → `TRAVA DUPLICADAS: OK`.
- In game: create a classic character, open the talent window (3 specs), learn a talent, switch spec, relog.

## Uninstall / rollback
- Server: `git revert`/reset the applied patches, restore your backed-up DBCs, restore the DB tables you backed up
  (`playercreateinfo_action`, `trainer_spell`, and the Support tables listed in `sql/support-frozen/`).
- Client: delete `patch-ZZS/ZZV/ZZW/ZZX/ZZY/ZZZ.MPQ` (or restore your previous copies) with the game closed.
- Support un-freeze: remove `SUPPORT_CONGELADA`, restore the pre-freeze DBCs, apply
  `sql/support-frozen/reactivate_support_world.sql`, rebuild client patches.

---

# v0.2.0 — classes v2 (on top of a v0.1.0 install)

Same rules: back up first, client patches only with the game closed. v2 was built and tested on a realm whose source
was the v0.1.0 base plus jealous-sound `main` merged up to 2026-10-17; on other revisions patches 0006–0010 may need
manual rebasing. Extra environment variables: `PROD_DBC` (production dbc folder, for the md5 check in
`instala_classe.sh`), and for `tools/v2/gera_sql_diff.py` `PROD_DB_CONTAINER`/`PROD_DB_PASS`/`TEST_DB_CONTAINER`/`TEST_DB_PASS`.

## 1. Server source
```bash
git am /path/to/repo/core/patches/00{06,07,08,09,10}-*.patch
docker compose build ac-worldserver && docker compose up -d --no-deps --force-recreate ac-worldserver
```
Config (`worldserver.conf`): `ShadowCore.TalentResetRevision = 1` (one free talent reset at next login; raise it after
every tree change). Optional: `CoA.PetTalentReset.Cost` (copper, default 50000). Death Knight stays disabled with
`CharacterCreating.Disabled.ClassMask = 32` (see `docs/v2/DEATH-KNIGHT.md` to enable it).
Patch 0010 is a generic crash guard (NaN coordinates); keep it even without the classes.

## 2. Server DBC — two ways
**a) Apply the deltas** (fastest; your DBCs must be the ones a v0.1.0 install produced — the md5 of the bases is in
the `base_md5` notes below):
```bash
for n in CharacterAdvancement CharacterAdvancementEssence ChrSpecs; do
  python3 tools/dbcdelta.py apply env/dist/data/dbc/$n.dbc client/dbc-deltas/v2/$n.v2.delta.json out/$n.dbc
done
```
Bases (v0.1.0 install): CharacterAdvancement `8f8281ec…`, CharacterAdvancementEssence `8e6513c1…`, ChrSpecs `2bb8aea7…`.
Results: `60b09809…`, `58839256…`, `e74fb0dc…`. The other 4 DBC of the talent patch (TabTypes, SkillLine, SkillLineAbility,
SkillRaceClassInfo) do not change in v2.

**b) Regenerate class by class** on a test realm (what we did):
```bash
export COA_ROOT=<test server tree> DB_CONTAINER=... DB_USER=root DB_PASS=... WORLD_CONTAINER=... MPQ_TOOLS=...
mkdir -p $COA_ROOT/v2 && cp -r tools/v2/* $COA_ROOT/v2/
bash $COA_ROOT/v2/instala_classe.sh warrior      # then priest rogue mage warlock shaman druid paladin hunter
```
Each run: backup → export (SELECT) → `gera_v2.py` → `verifica_v2.py` (stops on any error, and on any byte change to
the 21 CoA classes / Support / other classes) → trainer + migration SQL → apply → restart → `pente_v2.py` sweep →
client `patch-ZZW.MPQ` (7 DBC). The Death Knight uses `gera_v2_nova.py` + `verifica_v2_dk.py` + `dk/`.
`src-original/` (pristine template rows) must be extracted from your own DBC first; it is not shipped.

## 3. World database
```bash
docker exec -i $DB_CONTAINER mysql -u$DB_USER -p$DB_PASS < sql/world-v2/2026-10-17_classes_v2.sql
```
It is the exact diff production → tested realm by primary key (trainer_spell −390/+10/~73, playercreateinfo ~59,
playercreateinfo_item +292, playercreateinfo_skills +3, spell_script_names +5, player_class_stats +54).
Rollback: `sql/world-v2/2026-10-17_classes_v2_rollback.sql`. Existing characters: `tools/v2/migra_v2.py` per class
(or simply let the free reset from patch 0008 refund the points; the level-1 kit is granted by `migra_v2.py`).
Bots (mod-playerbots): regenerate `CoaLevelBuildData.h` with `tools/v2/bots-level60/gera_builds_bots.py <CoaLevelBuildData.h> <CharacterAdvancement.dbc> <CharacterAdvancementEssence.dbc> <out.h> 60` and check it
with `valida_builds.py`.

## 4. Client
- `patch-ZZW.MPQ`: pack the 7 DBC (the 3 from step 2 + the 4 unchanged ones) with `client/build/build_patches.sh` or `mkpatch`.
- Character creation, on top of the CharacterCreate.lua produced by v0.1.0, in this order:
  1. `client/diffs/v2/GlueXML__CharacterCreate.lua.dk-button.diff` (one line: the DK button in the third row);
  2. `client/diffs/v2/GlueXML__CharacterCreate.lua.race-class-filter.diff` (the screen offers exactly the server's
     `playercreateinfo` race×class pairs, and hides the DK again — `classID ~= 6`; drop that condition to show it).
- Pet talents: copy `client/addons/ShadowCorePetTalents/PetTalents.{lua,xml}` to
  `Interface\AddOns\Ascension_CoATalents\ShadowCore\` inside a new patch MPQ (we use `patch-ZZP.MPQ`) together with the
  `Ascension_CoATalents.toc` from your client plus the line in `client/diffs/v2/AddOns__Ascension_CoATalents__Ascension_CoATalents.toc.diff`.

## 5. Verify
- worldserver log: `Loaded N CoA talent entries ... specializations`, no `Skipped CoA talent entry`, no ABORT.
- `python3 tools/v2/verifica_v2.py <class> <dbc dir> <dbc dir>` → `ERROS: 0` for each class.
- In game: buy a node in rows 4–7 only after 9/8 points in the tab; an upload that breaks a gate is refused.
