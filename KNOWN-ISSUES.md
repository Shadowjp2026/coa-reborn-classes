# Known issues (from the 2026-10-12 audits)

Severity: CRITICAL = cannot create/play · IMPORTANT = wrong item/ability · VISUAL = appearance/UI.
No CRITICAL issue is known. 626 valid race/class pairs were audited (106 without any issue; most of the
rest only had the starting action bar problem, fixed in v0.1.0).

| # | Issue | Severity | Status |
|---|---|---|---|
| 1 | Classic starting action bars pointed at stock spell IDs (character knows the 11xxxxx "twin") | VISUAL | fixed (sql/world, untested in game) |
| 2 | Warrior received Devastate (Protection identity) from the book at level 1 | IMPORTANT | fixed (sql/world) |
| 3 | Judgement 10321 shown green at trainers but duplicates what the tree grants | IMPORTANT | fixed (sql/world) |
| 4 | City trainers list stock IDs; rank chains may look trainable but fail. The Warcraft Reborn trainer rewriter already maps them in memory on `coa wcr` realms — needs in-game confirmation before changing data (`tools/reference/b1_treinadores.py`) | IMPORTANT | open |
| 5 | Starting weapon without the matching weapon skill (Rogue, Hunter, one Warrior body type) | IMPORTANT | open (plan: swap the item, no extra proficiency) |
| 6 | Some CoA starting weapons have zero weapon damage (7 classes, 14 items) | IMPORTANT | open (verify first) |
| 7 | Missing/incorrect racials for some races (classic Draenei/Goblin; Vulpera, Earthen, High Order Skyborne; Windshaper Skyborne gets Troll racials) | IMPORTANT | open (part needs a core build) |
| 8 | Same starting item granted twice on 18 pairs | minor | open |
| 9 | A Ranger starting item requires a reagent that does not exist | minor | open |
| 10 | Character-creation preview shows naked characters (client outfit table empty for many pairs); real gear is fine | VISUAL | open (client-only fix planned) |
| 11 | Class Guide (role/subrole view) does not list the 9 classic classes | VISUAL | open |
| 12 | 6 race/class pairs accepted by the server but hidden in the client | minor | open |
| 13 | Paladin tree still uses ranks 1-2-3 (others 1/3/5) | balance | fixed in v0.2.0 (v2 generator) |
| 14 | Not every DB change made during development is exported to `sql/` yet (e.g. classic starting skills for custom races, some trainer/book rows, skill-line renames) | packaging | partly fixed: v0.2.0 ships the exact production diff of the v2 tables (`sql/world-v2`) |
| 15 | Support specs frozen; Paladin Support v2 (29 nodes) untested in game | — | frozen |

## v0.2.0 (classes v2) — open items

| # | Issue | Severity | Status |
|---|---|---|---|
| 16 | Characters created before v0.2.0 do not get the Shaman Master Totem item (only new characters do); send it by mail | IMPORTANT | open |
| 17 | Hunter Steady Shot ranks above 1: stock ranks 34120/49051/49052 have no twin, so only rank 1 is reachable; the Reborn chain 1156641→1156647 exists but is not wired | IMPORTANT | open |
| 18 | Kill Command effect is fixed in the core for the twin 1134026 only (patch 0006); other twin pet abilities with hard-coded IDs were not audited | IMPORTANT | open |
| 19 | Beast Mastery identity/automatic lands at level 59 | balance | open (owner decision) |
| 20 | Shaman: 6 tank/2H nodes from the WotLK tree have no CoA equivalent yet | balance | open |
| 21 | Some v2 nodes use a spell whose own level is higher than the row (e.g. Heroic Throw 80 in row 2); verified by the sweep, needs in-game check | VISUAL | open |
| 22 | Classic-class damage: the twins (stock+1,100,000) carry the original WotLK numbers, not CoA's rebalanced values (782 damage spells, 58 at ≥2× the CoA version). Audit done, nothing changed yet | balance | open |
| 23 | Death Knight: implemented and tested on the test realm only; creation is disabled by default (`CharacterCreating.Disabled.ClassMask = 32` + hidden button) | — | disabled |
| 24 | Level 80 progression was released and reverted; `tools/reference/level80` is kept for reference only (bots stop ~22–24 points short above 60 without a regenerated build table) | — | reference |
| 25 | Prestige rewards reference items that do not exist (1287330, 375250, 84/104 Chromie items) — found during the level-80 audit, not ours | minor | upstream |
| 26 | Hunter: Call Stabled Pet twin requires level 80; trainer/Book levels differ for 9 Hunter spells (city shows the twin's SpellLevel, Book its ReqLevel) | minor | open |
| 27 | Most v2 changes were verified by the tools and on a test realm; in-game confirmation is partial | — | — |
