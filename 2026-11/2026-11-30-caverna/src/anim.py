
# ============================================================ animação
def key(o, path, t, val):
    setattr(o, path, val); o.keyframe_insert(path, frame=F(t))
def mkey(m, t, rgb):
    m.diffuse_color = (*rgb, 1); m.keyframe_insert('diffuse_color', frame=F(t))
def interp(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if t <= b: return va + (vb - va) * ease_io((t - a) / (b - a))
    return keys[-1][1]
def pos(u):
    if u < 0: return (-23 + u * 40, 0.6)
    return at(u)

T_ENTRAM = wt(2, 'entram'); T_PASSEIO = wt(2, 'passeio'); T_CHUVA2 = wt(2, 'chuva'); T_FECHA = wt(2, 'fecha'); T_FUNDO = wt(2, 'fundo')
T_13 = wt(3, '13'); T_MERG = wt(4, 'mergulhar')
T_CHUVA5 = wt(5, 'chuva'); T_MORREU = wt(5, 'morreu')
T_MASK = wt(6, 'máscara', 1); T_DORM = wt(6, 'dormindo')
f_end = int(math.ceil(TOTAL * FPS)) + 1

for t, c in ((0, NIGHT), (s6, DEEP), (s7, NIGHT)):
    w.color = c; w.keyframe_insert('color', frame=F(t))
set_interp(w, 'CONSTANT')

# meninos: posição ao longo do túnel (quadro a quadro, de 2 em 2)
for k, o in enumerate(kids):
    du = -0.013 * k; dz = random.uniform(-0.25, 0.25)
    keys = [(s2, -0.18 + du), (T_ENTRAM, -0.16 + du), (T_ENTRAM + 2.5, 0.06 + du), (T_PASSEIO + 1, 0.14 + du),
            (T_CHUVA2, 0.17 + du), (T_FECHA + 0.3, 0.2 + du), (T_FECHA + 2.0, 0.42 + du), (T_FUNDO + 2.5, 0.97)]
    st = s7 + 0.1 + k * 0.42
    out_keys = [(st, 0.97), (st + 1.4, -0.16 - k * 0.028)]
    lx = 14.7 + (k % 7) * 0.33; lz = 3.55 + (k // 7) * 0.36
    for f in range(1, f_end + 1, 2):
        t = (f - 1) / FPS
        if t < st:
            u = interp(keys, t)
            x, z = pos(u)
            if t > T_FUNDO + 2.4: x, z = lx, lz
            elif u > 0.9: x, z = x + (lx - x) * ((u - 0.9) / 0.07), z + (lz - z) * ((u - 0.9) / 0.07)
            else: z += dz * 0.5
        else:
            u = interp(out_keys, t); x, z = pos(u)
        o.location = (x, -1.1, z); o.keyframe_insert('location', frame=f)
# água enchendo o túnel
cu = wfill.data
cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=F(T_CHUVA2))
cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=F(T_FUNDO + 1.5))
# mergulhadores britânicos
for k, o in enumerate(divers):
    keys = [(s3, -0.14 - 0.03 * k), (T_13 - 0.4, 0.93 - 0.02 * k)]
    for f in range(1, f_end + 1, 2):
        t = (f - 1) / FPS
        x, z = pos(interp(keys, t)); o.location = (x, -1.25, z + 0.35); o.keyframe_insert('location', frame=f)
    key(o, 'scale', s3 - 0.1, (0, 0, 0)); key(o, 'scale', s3, (1, 1, 1)); key(o, 'scale', s7 - 0.05, (1, 1, 1)); key(o, 'scale', s7, (0, 0, 0))
    set_interp(o, 'LINEAR')
# trechos submersos ficam vermelhos
for i, (m, o) in enumerate(zip(SUMP, sumps)):
    mkey(m, 0, hexc('e0281e'))
    key(o, 'scale', 0, (0, 0, 0)); key(o, 'scale', T_MERG + i * 0.7, (0, 0, 0)); key(o, 'scale', T_MERG + i * 0.7 + 0.35, (1, 1, 1))
# Saman: aparece na cena 5 e a luz se apaga
key(saman, 'scale', 0, (0, 0, 0)); key(saman, 'scale', s5 - 0.05, (0, 0, 0)); key(saman, 'scale', s5 + 0.3, (1, 1, 1))
mkey(SAMAN, s5, hexc('5fe0ff')); mkey(SAMAN, T_MORREU, hexc('5fe0ff')); mkey(SAMAN, T_MORREU + 1.2, hexc('3a3a40'))
for c_ in cyls:
    key(c_, 'scale', 0, (0, 0, 0)); key(c_, 'scale', s5 - 0.05, (0, 0, 0)); key(c_, 'scale', s5 + 0.4, (1, 1, 1))
# chuva
for d in drops:
    x0 = d.location.x
    key(d, 'scale', 0, (0, 0, 0))
    for (a, b) in ((T_CHUVA2 - 0.3, s3), (T_CHUVA5 - 0.3, T_MORREU - 1.0)):
        t = a + random.uniform(0, 0.6)
        while t < b:
            per = random.uniform(0.55, 0.8)
            d.location = (x0, -3, 34); d.keyframe_insert('location', frame=F(t))
            d.scale = (1, 1, 1); d.keyframe_insert('scale', frame=F(t))
            d.location = (x0, -3, 2); d.keyframe_insert('location', frame=F(t + per - 0.03))
            d.scale = (0, 0, 0); d.keyframe_insert('scale', frame=F(t + per))
            t += per
    set_interp(d, 'LINEAR')

# travessia: mergulhador guiando o menino sedado
for f in range(int(F(s6)) - 2, int(F(s7)) + 3):
    t = (f - 1) / FPS
    x = KX - 15 + 30 * ease_io((t - s6) / (s7 - s6)) if s6 <= t <= s7 else (KX - 15 if t < s6 else KX + 15)
    bob = math.sin(t * 2.2) * 0.08
    diver.location = (x, -0.3, 2.9 + bob); diver.rotation_euler = (0, -0.06 + math.sin(t * 1.3) * 0.03, 0)
    diver.keyframe_insert('location', frame=f); diver.keyframe_insert('rotation_euler', frame=f)
    kid_fig.location = (x - 2.3, -0.3, 2.5 + bob * 0.5); kid_fig.keyframe_insert('location', frame=f)
    mask.location = (x - 2.3 + 0.8, -0.56, 2.56 + bob * 0.5); mask.keyframe_insert('location', frame=f)
    link.location = (x - 1.15, -0.3, 2.65 + bob * 0.7); link.keyframe_insert('location', frame=f)
for o in (diver, kid_fig, mask, link): set_interp(o, 'LINEAR')
key(mask, 'scale', s6 - 0.1, (0, 0, 0)); key(mask, 'scale', T_MASK - 0.05, (0, 0, 0)); key(mask, 'scale', T_MASK + 0.3, (1.3, 1.3, 1.3)); key(mask, 'scale', T_MASK + 0.5, (1, 1, 1))
for k, b in enumerate(kbub):
    t = s6 + k * 0.4
    while t < s7:
        dx = diver.location.x
        xx = KX - 15 + 30 * ease_io((t - s6) / (s7 - s6)) + 1.2
        b.location = (xx, -0.45, 3.1); b.keyframe_insert('location', frame=F(t)); b.scale = (1, 1, 1); b.keyframe_insert('scale', frame=F(t))
        b.location = (xx + 0.2, -0.45, 5.0); b.keyframe_insert('location', frame=F(t + 1.6)); b.scale = (0, 0, 0); b.keyframe_insert('scale', frame=F(t + 1.62))
        t += 4.0
    set_interp(b, 'LINEAR')

# ------------------------------------------------------------ câmera
bpy.ops.object.camera_add(); cam = bpy.context.object; S.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.clip_end = 2000
bpy.ops.object.empty_add(); tgt = bpy.context.object
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
SX, SZ = at(U_SAMAN)
SEGS = [
    [(0.0, (0, -78, 9), (0, 0, 6), 22), (s2, (-4, -70, 8), (-2, 0, 5), 22)],
    [(s2, (-19, -30, 5), (-19, 0, 2.5), 24), (T_CHUVA2, (-15, -30, 6), (-15, 0, 2.5), 24), (T_FECHA + 1, (-8, -40, 7), (-6, 0, 3), 24),
     (s3, (4, -42, 7), (6, 0, 3), 24)],
    [(s3, (-17, -32, 5), (-17, 0, 2.5), 24), (T_13 - 0.5, (11, -30, 5), (12, 0, 3), 24), (s4, (13, -24, 5), (13.5, 0, 3.2), 26)],
    [(s4, (-3, -80, 9), (-3, 0, 5), 22), (s5, (-3, -76, 9), (-3, 0, 5), 22)],
    [(s5, (SX + 2, -46, 7), (SX + 1, 0, 3.5), 24), (T_MORREU - 0.5, (SX, -30, 5), (SX, 0, 2.6), 24), (s6, (SX - 1, -28, 5), (SX, 0, 2.6), 24)],
    [(s6, (KX - 14, -10, 3.4), (KX - 14, 0, 2.8), 22), (s7, (KX + 14, -10, 3.4), (KX + 14, 0, 2.8), 22)],
    [(s7, (-5, -58, 7), (-5, 0, 3), 22), (s8, (-9, -62, 8), (-8, 0, 3.5), 22)],
    [(s8, (-9, -62, 8), (-8, 0, 3.5), 22), (TOTAL + 0.5, (-2, -85, 12), (-2, 0, 6), 22)],
]
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
starts = [sg[0][0] for sg in SEGS]
for f in range(1, f_end + 1):
    t = (f - 1) / FPS
    k = max(i for i, s in enumerate(starts) if s <= t + 1e-6)
    ks = SEGS[k]
    if t >= ks[-1][0]: p, g, l = ks[-1][1], ks[-1][2], ks[-1][3]
    else:
        j = max(i for i, kk in enumerate(ks) if kk[0] <= t)
        a, b = ks[j], ks[j + 1]
        u = ease_io((t - a[0]) / (b[0] - a[0]))
        p, g = lerp(a[1], b[1], u), lerp(a[2], b[2], u); l = a[3] + (b[3] - a[3]) * u
    cam.location = p; cam.keyframe_insert('location', frame=f)
    tgt.location = g; tgt.keyframe_insert('location', frame=f)
    cam.data.lens = l; cam.data.keyframe_insert('lens', frame=f)
