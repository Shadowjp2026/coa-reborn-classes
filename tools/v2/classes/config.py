# Configuracao das 9 classicas (ClassType, classe, faixa de 200 ids, abas, linhas de identidade de hoje)
CLASSES = {
 "warrior": dict(ct=37, cls=1, base=140200, token="WARRIOR", tabs={"Class": 87, "Arms": 6, "Fury": 5, "Protection": 7}, ident={"Arms": 140268, "Fury": 140232, "Protection": 140300}),
 "paladin": dict(ct=44, cls=2, base=140000, token="PALADIN", tabs={"Class": 87, "Holy": 14, "Protection": 7, "Retribution": 25}, ident={"Holy": 140061, "Protection": 140030, "Retribution": 140092}),
 "hunter":  dict(ct=36, cls=3, base=140400, token="HUNTER", tabs={"Class": 87, "BeastMastery": 4, "Marksmanship": 3, "Survival": 2}, ident={"BeastMastery": 140499, "Marksmanship": 140468, "Survival": 140436}),
 "rogue":   dict(ct=38, cls=4, base=140600, token="ROGUE", tabs={"Class": 87, "Assassination": 10, "Combat": 8, "Subtlety": 9}, ident={"Assassination": 140697, "Combat": 140632, "Subtlety": 140665}),
 "priest":  dict(ct=40, cls=5, base=140800, token="PRIEST", tabs={"Class": 87, "Discipline": 16, "Holy": 14, "Shadow": 15}, ident={"Discipline": 140901, "Holy": 140836, "Shadow": 140868}),
 "shaman":  dict(ct=43, cls=7, base=141200, token="SHAMAN", tabs={"Class": 87, "Elemental": 23, "Enhancement": 24, "Restoration": 20}, ident={"Elemental": 141260, "Enhancement": 141298, "Restoration": 141230}),
 "mage":    dict(ct=39, cls=8, base=141400, token="MAGE", tabs={"Class": 87, "Arcane": 11, "Fire": 13, "Frost": 12}, ident={"Arcane": 141437, "Fire": 141503, "Frost": 141470}),
 "warlock": dict(ct=41, cls=9, base=141600, token="WARLOCK", tabs={"Class": 87, "Affliction": 17, "Demonology": 18, "Destruction": 19}, ident={"Affliction": 141632, "Demonology": 141667, "Destruction": 141698}),
 "druid":   dict(ct=42, cls=11, base=141800, token="DRUID", tabs={"Class": 87, "Balance": 22, "Feral": 21, "Restoration": 20}, ident={"Balance": 141899, "Feral": 141866, "Restoration": 141831}),
 "deathknight": dict(ct=45, cls=6, base=142400, token="DEATHKNIGHT", nome="Death Knight", nova=True, tabs={"Class": 87, "Blood": 26, "Frost": 12, "Unholy": 27}, ident={"Blood": 142400, "Frost": 142401, "Unholy": 142402}),
}
