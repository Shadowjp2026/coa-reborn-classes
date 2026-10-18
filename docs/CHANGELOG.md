# Changelog

## v0.2.0 (2026-10-18) — classes v2
Full comparison with v0.1.0, per class and per system: [COMPARISON-v0.1-v0.2.md](COMPARISON-v0.1-v0.2.md).
- **Trees redrawn to the CoA standard** for the 9 classic classes: hand-written layouts (`tools/v2/classes/`), new
  generator `tools/v2/gera_v2.py`, verifier `verifica_v2.py` (protection of the 21 CoA classes/Support, gates, cost,
  ranks, grid, choice pairs, levels, trainer/Book), post-install sweep `pente_v2.py`. Class trees 33–36 nodes / cost
  36–37; specs 23–30 nodes / cost 34–36 (v0.1.0: 21–33 and 54–76, with unreachable rows).
- **Free base kit** per class from trainer/Book; rank 1 of every paid node removed from trainers and the Book;
  no basic ability depends on a quest (Shaman Master Totem at creation, Rogue poisons, Paladin SoR, Priest Lesser Heal).
- **Death Knight v2** on the CoA system (level 1 start, stats 1–54, gear, skills, Book, core twin fixes) — creation
  disabled by default. See [v2/DEATH-KNIGHT.md](v2/DEATH-KNIGHT.md).
- **Server:** per-tab talent gates enforced on build uploads + one free talent reset per
  `ShadowCore.TalentResetRevision` (0008); Kill Command twin + DK twin fixes (0006); classic Rogue keeps the form-30
  Stealth bar (0007); `.petreset` and pet talent window sync (0009); NaN/inf guard in `Map::GetHeight` (0010).
- **Hunter pet talents** drawn inside the CoA talent window (`client/addons/ShadowCorePetTalents`).
- **Character creation** offers exactly the server's race×class pairs (client diff).
- **Bots:** level-60 build table regenerated from the new trees (`tools/v2/bots-level60`).
- **Level 80** progression was released and reverted to 60; generator kept in `tools/reference/level80`.
- **SQL:** exact production diff of the v2 tables + rollback (`sql/world-v2`).
- **Client:** DBC row deltas on top of a v0.1.0 install (`client/dbc-deltas/v2`), Lua diffs (`client/diffs/v2`).
- Damage audit of the classic twins documented (no change yet). Per-class node lists: [v2/CLASSES.md](v2/CLASSES.md).

## v0.1.0-study (2026-10-12) — first local package, not published
- Unified realm class model `coa wcr` (CoA + classic classes on one realm).
- Classic classes use the CoA Character Advancement path; talent loader skips DISABLED/DEPRECATED rows.
- Talent upload from the classic client accepted (automatic entries of every spec ignored); custom races get class-restricted starting weapon skills.
- Generators for the 9 classic trees (model + per-class JSON), stable IDs, automatic dependencies on the right margin, baseline abilities, level-60 rule, class quests not required.
- Stabilization: duplicate spells disabled structurally, audit gate in the regeneration pipeline.
- Bloody Book: classic-class level limit option; Hunter pet spells via the book.
- Support (4th spec, Paladin v2 with 29 nodes + Priest/Druid/Shaman prototypes) — **frozen** on 2026-10-12; Shaman Enhancement shown as DPS only.
- Block 1 fixes: classic starting action bars, Devastate out of the level-1 book, Judgement 10321 duplicate removed.
- Client: Lua diffs (talent window for classic classes, character creation, spec order, atlas backgrounds) and DBC row deltas; MPQ build scripts.
