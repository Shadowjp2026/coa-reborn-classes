# Death Knight v2

Built on the same v2 generator as the classic classes (`tools/v2/gera_v2_nova.py`, design in
`tools/v2/classes/design_deathknight.py`, checker `tools/v2/verifica_v2_dk.py`). Tested on a test realm only;
**creation is disabled by default** in v0.2.0.

## What it is
- Class tree (tab 87): 33 paid nodes; Blood / Frost / Unholy (tabs 26 / 12 / 27): 23 paid nodes each, 3 identities
  (142400–142402) and 12 automatics at 20/30/40/50. 117 new CharacterAdvancement rows in 142400–142516; the 116
  original rows of ClassType 45 are only flagged DISABLED (byte 479 |= 0x8), nothing deleted. ChrSpecs 79–81 fields
  24–28; Essence of class 6 = the curve of class 29.
- Starts at level 1 in the race's own starting zone (`playercreateinfo` rows of class 6 point at the zone of class 1;
  race 10 uses Paladin's, race 56 Mage's).
- `player_class_stats` class 6 levels 1–54 = copy of class 1 (stock data only had 55–80).
- Starting gear: level-1 Warrior pieces of the race + Hearthstone + a 2H weapon the DK can use (Worn Greatsword 49778 /
  Worn Battleaxe 12282 / Battleworn Claymore 23346; Tauren get the axe). 291 `playercreateinfo_item` rows; no DBC change.
- Reborn skills 11770/11771/11772 at creation (teach Blood Strike, Icy Touch, Plague Strike, Blood Presence, Death Coil,
  Death Grip, Frost Fever, Blood Plague, Runic Focus).
- Book 900100: levels follow the kit curve, prices follow the Warrior trainer ladder; Death Gate removed from the Book;
  the stock "Grave Coil" (rage cost) replaced by the DK twin; Glyph of Raise Dead sold so Raise Dead works without a corpse.
- Core (patch 0006): Death Coil twins, exclusive presences, disease twins (Pestilence, Glyph of Disease, Icy Talons,
  Crypt Fever / Ebon Plague, Tundra Stalker, Frost Fever outside the binary-spell list), Empower Rune Weapon, Hysteria,
  Unholy Blight, Master of Ghouls, Sudden Doom, Dancing Rune Weapon. Dungeon Finder asks for quest 13188/13189 only when
  `StartHeroicPlayerLevel >= 55` (campaign DK).

## Enable it
`worldserver.conf`: remove 32 from `CharacterCreating.Disabled.ClassMask`, and for a level-1 DK:
`HeroicCharactersPerRealm = 10`, `CharacterCreating.MinLevelForHeroicCharacter = 0`, `StartHeroicPlayerLevel = 1`,
`StartHeroicPlayerMoney = 0`. Client: in the CharacterCreate.lua built per docs/INSTALL.md, remove `and classID ~= 6` from the class-button loop
(the DK goes to the third row of class buttons).

## Not done
Runeforging, Acherus mount and Death Gate still come only from the campaign quests; in-game testing is partial.
