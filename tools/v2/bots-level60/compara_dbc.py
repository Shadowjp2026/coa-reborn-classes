# Compara CharacterAdvancement.dbc antigo (60) x atual (80) campo a campo, por id de linha.
import struct, sys, collections
def load(p):
    b = open(p, "rb").read()
    m, c, f, rs, ss = struct.unpack("<4sIIII", b[:20])
    rows = {struct.unpack_from("<I", b, 20 + i*rs)[0]: b[20+i*rs:20+(i+1)*rs] for i in range(c)}
    return rows, f, rs, b[20+c*rs:]
old, fo, rso, so = load(sys.argv[1]); new, fn, rsn, sn = load(sys.argv[2])
print("campos", fo, fn, "| tam linha", rso, rsn, "| linhas", len(old), len(new), "| strings iguais", so == sn)
print("so no antigo", len(set(old)-set(new)), "| so no atual", len(set(new)-set(old)))
diff = collections.Counter(); rowsdiff = 0; other = []
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]
for k in old.keys() & new.keys():
    a, b = old[k], new[k]
    if a == b: continue
    rowsdiff += 1
    fs = [i for i in range(fo) if a[i*4:i*4+4] != b[i*4:i*4+4]]
    for i in fs: diff[i] += 1
    if set(fs) - {26, 38, 39}: other.append((k, fs))
print("linhas diferentes", rowsdiff, "| campos alterados:", dict(diff))
print("linhas com campo fora de 26/38/39:", len(other), other[:5])
# por ClassType (campo 32) as linhas alteradas
ct = collections.Counter(u(new[k], 32) for k in old.keys() & new.keys() if old[k] != new[k])
print("alteradas por ClassType(32):", dict(sorted(ct.items())))
print("nivel max (26) antigo/atual:", max(u(r,26) for r in old.values()), max(u(r,26) for r in new.values()))
