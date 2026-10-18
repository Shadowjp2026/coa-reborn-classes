# What changed from v0.1.0 to v0.2.0

v0.1.0 (2026-10-12) put the 9 classic classes into the CoA Character Advancement window, but the trees were a
mechanical copy of the WotLK talent tabs placed on the CoA template. v0.2.0 (2026-10-17/18) redraws every tree
by hand to the CoA standard ("adapt the classic classes to CoA, not CoA to the classic classes"), adds the Death
Knight as a CoA-style class, and fixes the server/client problems found while testing v0.1.0.

Numbers come from the generator's verifier (`tools/v2/verifica_v2.py`) and from the read-only audit of the 36 v0.1.0
trees. "Cost" = points needed to buy the whole tree (one option per choice pair). Budget at level 60 = 26 ability
points (class tree) / 25 talent points (spec tree), the same for all 31 classes.

## 1. Systems

| Area | v0.1.0 | v0.2.0 | Type |
|---|---|---|---|
| Tree source | `modelo_classe.py` copies WotLK tabs into the CoA template by position | `tools/v2/gera_v2.py` builds every node from a hand-written layout (`tools/v2/classes/design_<class>.py`); only the binary record shape comes from the template | changed |
| Verification | duplicate-spell gate only | `verifica_v2.py`: protection (21 CoA classes, Support, other classics byte-identical), integrity, gates/reach, cost, ranks/grid, choice pairs, levels, identities, trainer/book; `pente_v2.py` post-install sweep | added |
| Class tree (AE) | 21–33 points, 98% actives, rows 4–9 unreachable for Warrior/Priest, rows 8–9 for Rogue/Mage | 33–36 nodes, cost 36–37, utility/control/defensives, rows reachable (≥13 points in rows 0–3, ≥30 in rows 0–7) | fixed |
| Spec trees (TE) | 54–76 points (closes only 46–65% at level 80), 55% of nodes with 3 ranks | 23–30 nodes, cost 34–36, 64–73% single-rank, capstone row 9 | fixed |
| Base kit | most basic abilities were paid nodes, or exclusive to one spec | free base kit per class (stances/forms, basic attacks, taunt, interrupt, buffs) from trainer/Book; nothing essential depends on a quest | changed |
| Trainer / Book | sold the same spells the tree charged for (346 trainer + 376 Book overlaps) | rank 1 of every paid node removed from class trainer, village trainer and Book 900100 (`sql/world-v2`, `treinador_v2.py`) | fixed |
| Spec automatics | levels inherited from the template (e.g. Arcane Blast 64→20) | 4 automatics per spec at 20/30/40/50, matched to the original level | fixed |
| Identities | 16 of 27 were 51-point capstones given at level 10 | one coherent identity per spec at level 10 (capstones moved back to row 9) | fixed |
| Grid | 35 class nodes in columns 9–10 | columns 0–8 only; column 10 reserved for identity + automatics | fixed |
| Per-tab gates (server) | only the client checked the 8/23 and 9/24 tab gates | server refuses uploaded builds that break a tab gate (patch 0008) | added |
| Talent reset | none after a tree change | one free reset per `ShadowCore.TalentResetRevision` (patch 0008) | added |
| Paladin generator | legacy `gera_paladino.py` (ranks 1-2-3, duplicates) | same v2 generator as the other classes | changed |
| Existing characters | — | `migra_v2.py` removes the old tree entries and grants the level-1 kit | added |
| Level cap | 60 (trees designed for 60) | 60. A level-80 progression (passives 20/40/60/80, rows 9/10 at 60–76) was shipped and then reverted; the generator is kept in `tools/reference/level80/` | unchanged |
| Bots (mod-playerbots) | level builds from the original table | `tools/v2/bots-level60/gera_builds_bots.py` regenerates `CoaLevelBuildData.h` from the new trees: 3,570 picks, 0 gate problems, 26/25 points spent at 60 | changed |
| Support (4th spec) | frozen | still frozen, untouched (byte-identical) | unchanged |
| Character creation | the client's CharBaseInfo offered race×class pairs the server refused (90 pairs) | the creation screen shows exactly the pairs in the server's `playercreateinfo` (client diff `race-class-filter`) | fixed |
| Server stability | — | `Map::GetHeight` refuses NaN/inf coordinates (a bot path bug made the VMAP ray walk loop forever; patch 0010) | fixed |

## 2. Per class — trees

| Class | v0.1.0 class tree cost | v0.2.0 class tree (nodes / cost) | v0.1.0 spec costs | v0.2.0 specs (nodes / cost) | Into the tree | Out to the free kit | Moved/retyped | Removed (no source left) |
|---|---|---|---|---|---|---|---|---|
| Warrior | 22 (rows 4–9 unreachable) | 33 / 37 | Arms 64, Fury 62, Prot 54 | Arms 30/36, Fury 28/35, Prot 28/35 | 27 | 18 | 37 | 0 |
| Paladin | 32 | 35 / 37 | Holy 56, Prot 55, Ret 56 | Holy 27/35, Prot 28/35, Ret 28/35 | 38 | 30 | 44 | 0 |
| Hunter | 30 | 34 / 37 | BM 57, MM 61, SV 74 | BM 25/35, MM 23/35, SV 23/35 | 14 | 27 | 40 | 9 |
| Rogue | 24 (rows 8–9 unreachable) | 33 / 37 | Assa 61, Combat 60, Sub 58 | 28/35 each | 28 | 19 | 39 | 0 |
| Priest | 21 (rows 4–9 unreachable) | 34 / 37 | Disc 59, Holy 75, Shadow 56 | 29/35 each | 33 | 18 | 41 | 2 |
| Shaman | 32 | 36 / 37 | Ele 59, Enh 76, Resto 55 | Ele 28/35, Enh 27/35, Resto 27/35 | 26 | 26 | 31 | 6 |
| Mage | 25 (rows 8–9 unreachable, incl. Ice Block) | 33 / 37 | Arcane 72, Fire 62, Frost 64 | 28/34 each | 30 | 19 | 32 | 9 |
| Warlock | 31 | 34 / 36 | Aff 57, Demo 63, Destro 57 | Aff 27/34, Demo 27/34, Destro 28/34 | 35 | 32 | 38 | 1 |
| Druid | 33 | 35 / 36 | Balance 63, Feral 65, Resto 60 | Balance 27/35, Feral 28/35, Resto 27/35 | 15 | 29 | 38 | 2 |
| Death Knight | — (not included) | 33 nodes | — | 23 nodes per spec (Blood/Frost/Unholy) | new class | — | — | — |

"Removed (no source left)" are nodes taken out on purpose because they did nothing in game (no script / no handler) or
duplicated another node: Hunter Explosive Shot (Charged Up), Hunting for Sport, Deadly Focus, Shadow Artillery, the two
Trap Launcher/Launch trap pairs, Dual Wield (it created a "Fury" spellbook tab); Mage Cremation, Mindshift, Scorch (Scorched Earth), Arcane Recovery/Momentum/Attunement/
Barrier, Touch of the Magi, Deep Freeze; Shaman Earthen Guardian, Totemic Bond, Earthen Attunement, Two-Handed Weapon
Specialization, Shield Specialization, Spirit Guard; Priest Blessed Vengeance, Epiphany of Light; Warlock Summoner's
Armor; Druid Frenzied Swipe, Poison Rain.

Examples of new CoA-style nodes: Warrior Avatar, Storm Bolt, Heroic Leap, Ravager, Colossus Smash; Mage Ring of Frost,
Alter Time, Shimmer, Meteor, Glacial Spike; Shaman Capacitor Totem, Healing Rain, Elemental Blast; Warlock Hand of
Gul'dan, Burning Rush; Druid Solar Beam, Ursol's Vortex, Stampeding Roar; Hunter Binding Shot, Barbed Shot, Stampede;
Priest Halo, Leap of Faith, Holy Word: Chastise; Rogue Marked for Death, Kingsbane, Death Mark; Paladin Execution
Sentence, Blinding Light, A New Dawn. Full per-class lists: `docs/v2/CLASSES.md`.

## 3. Per class — fixes and balance

| Class | Fix / change in v0.2.0 |
|---|---|
| Hunter | Kill Command twin (1134026) now fires the pet attack: the effect was hard-wired to stock 34026 (patch 0006) |
| Hunter | Tame Beast / Call / Dismiss / Revive / Feed Pet and Auto Shot (stock 75, required by the core) are part of the free kit; no basic ability depends on a quest |
| Hunter | Pet talent tree drawn inside the CoA talent window with CoA-style links (client add-on `client/addons/ShadowCorePetTalents`); `.petreset` resets pet talents for gold (`CoA.PetTalentReset.Cost`, default 50000 copper) and resyncs the window (patch 0009) |
| Hunter | Three nodes that did nothing in game removed (see above); "Fury" tab in the Hunter spellbook traced to Dual Wield's twin pointing at the Warrior skill line (documented) |
| Rogue | Form 30 Stealth bar kept for classic Rogues after the upstream SQL cleared it for Runeshroud ("option C", patch 0007) |
| Rogue | Poisons (2060001/2060011) given as level-1 kit through the Book |
| Shaman | Master Totem item given at creation (`playercreateinfo_item`) — totems no longer need the quest chain |
| Paladin | Seal of Righteousness kit (1121084) at level 1; moved to the v2 generator (no more 1-2-3 legacy ranks) |
| Priest | Lesser Heal kit (1102050) at level 1 |
| Warrior | 4 spec automatics (Overpower, Whirlwind, Shield Block, Shield Wall) no longer sold by trainer/Book: only the spec gets them |
| Death Knight | New class on the CoA system: level 1 start in the race's own zone, class stats 1–54, 2H starting weapon, Reborn skills 11770–11772; twin fixes for Death Coil, presences, diseases (Pestilence, Glyph of Disease, Icy Talons, Crypt Fever/Ebon Plague, Tundra Stalker), Empower Rune Weapon, Hysteria, Unholy Blight, Master of Ghouls, Sudden Doom, Dancing Rune Weapon; Dungeon Finder quest 13188/13189 only for campaign DKs (patch 0006). **Creation is disabled by default** (`CharacterCreating.Disabled.ClassMask = 32` and the button hidden in the client); the code and data stay |
| All classic | Damage audit of the classic "twins" (stock id + 1,100,000): 782 damage spells, median 1.0× of the CoA versions, 58 at ≥2×; root cause = twins copied from the original WotLK Spell.dbc instead of CoA's rebalanced one. **Documented only, not changed in v0.2.0** (see KNOWN-ISSUES) |
| All | Points per level unchanged: ability/talent 1/0 at 10, 6/5 at 20, 11/10 at 30, 16/15 at 40, 21/20 at 50, 26/25 at 60 |

## 4. Files

| v0.1.0 | v0.2.0 |
|---|---|
| `core/patches/0001–0005` | + `0006` Kill Command + DK twins, `0007` Rogue stealth bar, `0008` per-tab gates + free reset, `0009` `.petreset`, `0010` NaN guard |
| `tools/` (v1 generators) | + `tools/v2/` (generator, verifier, sweep, trainer/migration SQL, class designs incl. DK, bots builds), `tools/reference/level80/` |
| `sql/world/` | + `sql/world-v2/` (exact production diff + rollback) |
| `client/diffs`, `client/dbc-deltas` | + `client/diffs/v2/`, `client/dbc-deltas/v2/` (deltas on top of a v0.1.0 install), `client/addons/ShadowCorePetTalents/` |
