#!/usr/bin/env python3
"""Gera SQL seletivo (por chave primaria) das diferencas producao -> teste em tabelas do acore_world.
So le os dois bancos (SELECT). Saida: 02-world-classes-v2.sql (aplica) e 92-rollback-world-classes-v2.sql (desfaz).
Uso: gera_sql_diff.py <pasta_saida> tabela [tabela...]"""
import subprocess, sys, os
OUT, TABLES = sys.argv[1], sys.argv[2:]
PROD = ["docker", "exec", os.environ["PROD_DB_CONTAINER"], "mysql", "-u" + os.environ.get("DB_USER", "root"), "-p" + os.environ["PROD_DB_PASS"], "-N", "-B", "acore_world", "-e"]  # faithful copy of production
TEST = ["docker", "exec", os.environ["TEST_DB_CONTAINER"], "mysql", "-u" + os.environ.get("DB_USER", "root"), "-p" + os.environ["TEST_DB_PASS"], "-N", "-B", "acore_world", "-e"]

def q(cmd, sql):
    r = subprocess.run(cmd + [sql], capture_output=True, text=True, check=True)
    return [l.split("\t") for l in r.stdout.splitlines()]

def lit(v):
    if v == "NULL":
        return "NULL"
    return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"

apply_sql, back_sql, summary = [], [], []
for t in TABLES:
    cols = [c[0] for c in q(TEST, f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='acore_world' AND TABLE_NAME='{t}' ORDER BY ORDINAL_POSITION")]
    pcols = [c[0] for c in q(PROD, f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='acore_world' AND TABLE_NAME='{t}' ORDER BY ORDINAL_POSITION")]
    assert cols == pcols, f"{t}: colunas diferentes entre producao e teste"
    pk = [c[0] for c in q(TEST, f"SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA='acore_world' AND TABLE_NAME='{t}' AND CONSTRAINT_NAME='PRIMARY' ORDER BY ORDINAL_POSITION")]
    pk = pk or cols   # sem chave primaria (ex.: spell_script_names): a linha inteira e a chave
    sel = "SELECT " + ",".join(f"`{c}`" for c in cols) + f" FROM `{t}`"
    prod = {tuple(r[cols.index(k)] for k in pk): r for r in q(PROD, sel)}
    test = {tuple(r[cols.index(k)] for k in pk): r for r in q(TEST, sel)}
    gone = [k for k in prod if k not in test]
    new = [k for k in test if k not in prod]
    changed = [k for k in test if k in prod and test[k] != prod[k]]
    where = lambda k: " AND ".join(f"`{c}`={lit(v)}" for c, v in zip(pk, k))
    ins = lambda row: f"INSERT INTO acore_world.`{t}` ({','.join('`'+c+'`' for c in cols)}) VALUES ({','.join(lit(v) for v in row)});"
    apply_sql.append(f"-- {t}: remove {len(gone)}, novas {len(new)}, alteradas {len(changed)} (chave {','.join(pk)})")
    back_sql.append(f"-- {t}")
    for k in gone + changed:
        apply_sql.append(f"DELETE FROM acore_world.`{t}` WHERE {where(k)};")
    for k in new + changed:
        apply_sql.append(ins(test[k]))
    for k in new + changed:
        back_sql.append(f"DELETE FROM acore_world.`{t}` WHERE {where(k)};")
    for k in gone + changed:
        back_sql.append(ins(prod[k]))
    summary.append(f"{t}: remove {len(gone)} | novas {len(new)} | alteradas {len(changed)}")

hdr = "-- ShadowCore: classes v2 (9 classicas + Death Knight) - diferencas exatas producao -> teste, por chave primaria\n"
with open(os.path.join(OUT, "02-world-classes-v2.sql"), "x") as f:
    f.write(hdr + "START TRANSACTION;\n" + "\n".join(apply_sql) + "\nCOMMIT;\n")
with open(os.path.join(OUT, "92-rollback-world-classes-v2.sql"), "x") as f:
    f.write("-- Rollback de 02-world-classes-v2.sql (devolve as linhas da producao)\nSTART TRANSACTION;\n" + "\n".join(back_sql) + "\nCOMMIT;\n")
print("\n".join(summary))
