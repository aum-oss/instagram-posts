
# ============================================================ animação
def key(o, path, t, val):
    setattr(o, path, val); o.keyframe_insert(path, frame=F(t))
def mkey(m, t, rgb):
    m.diffuse_color = (*rgb, 1); m.keyframe_insert('diffuse_color', frame=F(t))

T_REF = wt(4, 'refrigeração'); T_LAV = wt(4, 'lavador'); T_CHA = wt(4, 'chama')
T_AGUA = wt(5, 'água'); T_REA = wt(6, 'reação'); T_200 = wt(6, '200'); T_VAL = wt(6, 'válvula'); T_ESC = wt(6, 'escapam')
T_DESCE = wt(7, 'desce'); T_ALARME = wt(7, 'alarme'); T_NAO = wt(8, 'Não')

for t, c in ((0, NIGHT), (s3, LAB), (s7, NIGHT), (T_NAO, LAB)):
    w.color = c; w.keyframe_insert('color', frame=F(t))
set_interp(w, 'CONSTANT')

# proteções: X aparece em cada uma
for xo, t in zip(xs, (T_REF, T_LAV, T_CHA)):
    key(xo, 'scale', s4 - 0.2, (0, 0, 0)); key(xo, 'scale', t - 0.05, (0, 0, 0))
    key(xo, 'scale', t + 0.18, (1.25, 1.25, 1.25)); key(xo, 'scale', t + 0.35, (1, 1, 1))

# água no cano
cu = wpipe.data
cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=F(T_AGUA - 0.1))
cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=F(T_AGUA + 1.8))
# termômetro
def th(t, v):
    thfill.scale.z = 8.0 * v; thfill.keyframe_insert('scale', frame=F(t))
th(s3, 0.1); th(T_REA - 0.1, 0.1); th(T_REA + 1.5, 0.45); th(T_200 - 0.2, 0.55); th(T_200 + 0.8, 1.0)
for t, c in ((s3, hexc('41c46f')), (T_REA + 0.8, hexc('ffd23f')), (T_200 + 0.4, hexc('e0281e'))):
    mkey(THERM, t, c)
for t, c in ((s3, hexc('d8c64e')), (T_AGUA + 1.8, hexc('d8c64e')), (T_200 + 0.6, hexc('ee8a2e'))):
    mkey(LIQ, t, c)
# bolhas
for k, b in enumerate(bubbles):
    x0 = b.location.x
    key(b, 'scale', s3, (0, 0, 0)); key(b, 'scale', T_AGUA + 1.6, (0, 0, 0))
    t = T_AGUA + 1.8 + random.uniform(0, 0.9); per = random.uniform(0.7, 1.1)
    while t < s7 + 0.5:
        b.location = (x0 + random.uniform(-0.3, 0.3), -0.12, 1.0); b.keyframe_insert('location', frame=F(t))
        b.scale = (1, 1, 1); b.keyframe_insert('scale', frame=F(t))
        b.location = (x0 + random.uniform(-0.3, 0.3), -0.12, 4.3); b.keyframe_insert('location', frame=F(t + per - 0.04))
        b.scale = (0, 0, 0); b.keyframe_insert('scale', frame=F(t + per))
        t += per; per = max(0.35, per * 0.93)
    set_interp(b, 'LINEAR')
# válvula salta
c0 = vcap.location.copy()
key(vcap, 'location', T_VAL - 0.05, c0.copy()); key(vcap, 'rotation_euler', T_VAL - 0.05, (0, 0, 0))
key(vcap, 'location', T_VAL + 0.6, (c0.x + 1.5, c0.y - 1.0, c0.z + 4.0)); key(vcap, 'rotation_euler', T_VAL + 0.6, (2.0, 1.0, 0))
key(vcap, 'location', T_VAL + 1.4, (c0.x + 3.0, c0.y - 2.0, -0.2))
# pluma saindo do respiro
for k, o in enumerate(plume):
    t0 = T_VAL + 0.2 + k * 0.28
    key(o, 'scale', s3, (0, 0, 0)); key(o, 'scale', t0, (0, 0, 0)); key(o, 'location', t0, (TX + 3.5, 2.0, 13.0))
    r = random.uniform(1.0, 2.2)
    key(o, 'scale', t0 + 2.5, (r, r, r)); key(o, 'location', t0 + 2.5, (TX + 3.5 + random.uniform(-3, 3), 2.0 + random.uniform(-1, 1), 13.0 + random.uniform(3, 7)))
    key(o, 'scale', s7 + 1, (r * 1.4, r * 1.4, r * 1.4)); key(o, 'location', s7 + 1, (TX + 3.5 + random.uniform(-6, 6), 2.0, 16 + random.uniform(2, 6)))
# nuvem sobre a cidade
for k, o in enumerate(cloud):
    key(o, 'scale', 0, (0, 0, 0)); key(o, 'scale', s7 - 0.01, (0, 0, 0))
    p0 = (14 + random.uniform(-3, 3), 30 + random.uniform(-3, 3), 26 + random.uniform(0, 8))
    r0 = random.uniform(2.0, 3.5)
    key(o, 'location', s7, p0); key(o, 'scale', s7, (r0, r0, r0))
    fx = random.uniform(-55, 60); fy = random.uniform(-70, 10)
    tA = T_DESCE + random.uniform(0.5, 3.5)
    key(o, 'location', tA, ((p0[0] + fx) / 2, (p0[1] + fy) / 2, random.uniform(6, 10)))
    r1 = random.uniform(5, 8); key(o, 'scale', tA, (r1, r1, r1 * 0.45))
    key(o, 'location', T_NAO, (fx, fy, random.uniform(2.5, 4.5)))
    r2 = random.uniform(8, 12); key(o, 'scale', T_NAO, (r2, r2, r2 * 0.3))
# alarme pisca só um instante
for t, c in ((0, hexc('5a1a16')), (T_ALARME - 0.05, hexc('5a1a16')), (T_ALARME + 0.05, hexc('ff2a1a')), (T_ALARME + 0.35, hexc('5a1a16')),
             (T_ALARME + 0.6, hexc('ff2a1a')), (T_ALARME + 0.9, hexc('5a1a16'))):
    mkey(REDL, t, c)
set_interp(REDL, 'CONSTANT')
# janelas das casas apagam quando a nuvem chega
for t, c in ((0, hexc('ffd76a')), (T_DESCE + 2.5, hexc('ffd76a')), (T_DESCE + 5.0, hexc('6a5a30'))):
    mkey(WIN, t, c)

# ------------------------------------------------------------ câmera (quadro a quadro)
bpy.ops.object.camera_add(); cam = bpy.context.object; S.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.clip_end = 2000
bpy.ops.object.empty_add(); tgt = bpy.context.object
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
SEGS = [
    [(0.0, (-40, -125, 55), (0, 0, 4), 24), (s2, (-28, -108, 44), (0, 2, 4), 24), (s3, (-6, -62, 24), (2, 18, 5), 26)],
    [(s3, (TX - 1, -26, 8), (TX + 0.9, 0, 1.8), 21), (s4, (TX + 1.5, -24, 7.5), (TX + 0.9, 0, 1.8), 22)],
    [(s4, (PX, -28, 6.5), (PX, 0, 1.4), 23), (s5, (PX, -26, 6), (PX, 0, 1.4), 23)],
    [(s5, (TX - 3, -21, 8.5), (TX - 1.0, 0, 2.6), 22), (s6, (TX, -25, 8), (TX + 0.9, 0, 2.6), 21),
     (T_ESC, (TX + 1, -27, 10), (TX + 1, 0, 7.0), 22), (s7, (TX + 2, -29, 12), (TX + 1, 0, 9.0), 22)],
    [(s7, (45, -95, 34), (8, -10, 6), 24), (T_DESCE + 4, (35, -88, 28), (5, -18, 3), 24), (s8, (30, -95, 34), (2, -20, 2), 24)],
    [(s8, (20, -115, 58), (0, -22, 0), 24), (T_NAO, (12, -125, 72), (0, -22, 0), 24)],
    [(T_NAO, (PX, -26, 6.5), (PX, 0, 1.4), 23), (TOTAL + 0.5, (PX, -30, 7.5), (PX, 0, 1.6), 23)],
]
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
f_end = int(math.ceil(TOTAL * FPS)) + 1
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
