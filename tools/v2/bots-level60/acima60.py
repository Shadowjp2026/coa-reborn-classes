import struct, sys, collections
b = open(sys.argv[1], "rb").read(); m, c, f, rs, ss = struct.unpack("<4sIIII", b[:20])
u = lambda r, i: struct.unpack_from("<I", r, i*4)[0]
cnt = collections.Counter(); ex = {}
for i in range(c):
    r = b[20+i*rs:20+(i+1)*rs]
    if u(r, 26) > 60:
        k = (u(r, 32), u(r, 26), bool(u(r, 14) or u(r, 15)))
        cnt[k] += 1; ex.setdefault(k, u(r, 0))
for k, v in sorted(cnt.items()): print("ClassType", k[0], "nivel", k[1], "pago" if k[2] else "gratis", v, "ex id", ex[k])
