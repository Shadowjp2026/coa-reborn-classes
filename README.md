# CoA Reborn Classes — classic classes inside the CoA Character Advancement (study project)

> **Educational / study project. Non-commercial.** Not affiliated with, endorsed by, or connected to
> Blizzard Entertainment, Project Ascension, or the maintainers of the AzerothCore CoA forks it builds on.
> This repository contains **only our own patches, scripts and data deltas**. It ships **no** game client
> files (no DBC, MPQ, BLP or original Lua). Everything client-side is rebuilt from files you already own.

## What it is
A set of server patches, data generators and client-patch build scripts that let the **9 classic
classes** (Warrior, Paladin, Hunter, Rogue, Priest, Shaman, Mage, Warlock, Druid) be played on a
"Conquest of Azeroth" realm **through the same Character Advancement (talent) system as the 21 CoA
classes**, side by side on one realm (`CoA.ClassModel = "coa wcr"`), with a level cap of 60.
Death Knight is included since v0.2.0 (creation disabled by default).

## v0.2.0 — classes v2 (2026-10-18)
- The 9 classic trees **redrawn by hand to the CoA standard** (class tree 33–36 nodes, specs 23–30 nodes, all rows
  reachable, free base kit, one source per ability) with a new generator + verifier (`tools/v2/`).
- **Death Knight v2** on the CoA system (included, creation disabled by default).
- Server: **per-tab talent gates** enforced, **free talent reset** per revision, **`.petreset`**, Kill Command and DK
  twin fixes, classic **Rogue Stealth** bar kept, NaN crash guard.
- Hunter **pet talents inside the CoA window**; character creation shows exactly the **server's race×class pairs**.
- What changed from v0.1.0, class by class: **[docs/COMPARISON-v0.1-v0.2.md](docs/COMPARISON-v0.1-v0.2.md)** ·
  changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md) · install: [docs/INSTALL.md](docs/INSTALL.md) (v0.2.0 section).

## Features (v0.1.0)
- Unified realm: CoA classes and classic classes on the same realm (`coa wcr` class model).
- Classic classes use the CoA talent window (CoATalentFrame) with their 3 original specializations each.
- Generated talent trees for the 9 classes (stable IDs, CoA grid/spacing, automatic dependencies,
  baseline abilities that cost no points, level-60 rule).
- Server-side talent upload/validation for classic clients, spec slots, spec switching, automatic
  abilities on login/level-up.
- Duplicate-spell audit gate (`tools/audita_duplicadas.py --trava`) run after every regeneration.
- Bloody Book (mod-spellbook) level limit for classic classes (`Spellbook.Classic.MaxLevel`).
- Starting action bars of the classic classes point at the spells actually learned.
- Client patch build pipeline (diffs + DBC row deltas + MPQ packer).

## Frozen
- **Support (4th spec for Paladin/Priest/Druid/Shaman)** is included but **FROZEN/disabled by default**
  (`tools/congela_support.py`, `SUPPORT_CONGELADA` flag, `sql/support-frozen/`). See docs/INSTALL.md.

## Known limitations
See [KNOWN-ISSUES.md](KNOWN-ISSUES.md). Highlights: racial abilities for some custom races,
character-creation outfit preview, class guide listing, starting weapons/zero-damage weapons, some
trainer ranks. **Most features were verified only partially in game.**

## Layout
| Path | Content |
|---|---|
| `core/patches/` | `git format-patch` series for the server source (AGPL, see LICENSE-NOTES.md) |
| `tools/` | Python/Bash generators, audits and the DBC delta tool (`dbcdelta.py`) |
| `tools/support-frozen/` | Support spec generators (frozen) |
| `tools/race-class-matrix/` | race × class matrix helpers used for CharBaseInfo |
| `tools/reference/` | one-off fix generators kept for reference (need audit data, not runnable as is) |
| `sql/world/` | world DB changes |
| `sql/support-frozen/` | Support SQL (freeze / reactivate) — do not apply unless you un-freeze |
| `client/diffs/` | unified diffs against your own client Lua files |
| `client/dbc-deltas/` | row-level deltas against your own client DBC files |
| `client/build/` | MPQ packer source + build/extract scripts |
| `tools/v2/` | v2 generator, verifier, sweep, trainer/migration SQL, class designs (incl. Death Knight), bot builds |
| `tools/reference/level80/` | level-80 progression generator (released, then reverted; reference) |
| `sql/world-v2/` | exact production diff of the v2 tables + rollback |
| `client/dbc-deltas/v2/` | DBC row deltas from a v0.1.0 install to v2 |
| `client/diffs/v2/` | character creation (race×class filter, DK button), pet talents TOC line |
| `client/addons/ShadowCorePetTalents/` | our pet talent tree for the CoA window |
| `docs/` | install, changelog, troubleshooting, v0.1→v0.2 comparison, `docs/v2/` (per-class lists, Death Knight) |

Start with [docs/INSTALL.md](docs/INSTALL.md).
