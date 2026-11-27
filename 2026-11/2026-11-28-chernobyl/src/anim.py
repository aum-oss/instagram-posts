
# ============================================================ animação
def key(o, path, t, val, interp=None):
    setattr(o, path, val); o.keyframe_insert(path, frame=F(t))
def mkey(m, t, rgb):
    m.diffuse_color = (*rgb, 1); m.keyframe_insert('diffuse_color', frame=F(t))

T_DESCEM = wt(3, 'descem'); T_AGUA3 = wt(3, 'água')
T_CAIDO = wt(4, 'caído'); T_PUX = wt(4, 'puxaram'); T_SOBR = wt(4, 'Sobraram')
T_APERTA = wt(5, 'aperta'); T_TODAS = wt(5, 'Todas')
T_GRAF = wt(6, 'grafite'); T_AGUA6 = wt(6, 'água'); T_EMP = wt(6, 'empurrou'); T_ESQ = wt(6, 'esquentaram')
T_DISP = wt(7, 'disparou'); T_VAPOR = wt(7, 'vapor'); T_ARR = wt(7, 'arremessou')

# mundo (cor de fundo por cena)
for t, c in ((0, NIGHT), (s3, LAB), (s5, PANELBG), (T_TODAS, LAB)):
    w.color = c; w.keyframe_insert('color', frame=F(t))
set_interp(w, 'CONSTANT')

# janelas piscam no "teste"
T_TESTE = wt(2, 'teste')
for k, (t, c) in enumerate(((T_TESTE - 0.01, hexc('ffd76a')), (T_TESTE + 0.15, hexc('fff6d0')), (T_TESTE + 0.35, hexc('ffd76a')), (T_TESTE + 0.5, hexc('fff6d0')), (T_TESTE + 0.7, hexc('ffd76a')))):
    mkey(WIN, t, c)
set_interp(WIN, 'CONSTANT')

# barras de controle
def rkey(r, t, bottom):
    r.location.z = rod_z(bottom); r.keyframe_insert('location', frame=F(t))
for k, r in enumerate(rods):
    out = k not in STAY
    rkey(r, s3, 1.0); rkey(r, T_DESCEM, 1.0); rkey(r, T_DESCEM + 1.2, 0.4)
    if out:
        st = T_PUX + 0.15 + (k % 12) * 0.12 + random.uniform(0, 0.15)
        rkey(r, st, 0.4); rkey(r, st + 1.3, 4.8)
        rkey(r, T_TODAS, 4.8); rkey(r, T_TODAS + 3.0, 3.6); rkey(r, T_ARR, 2.3)
    else:
        rkey(r, T_TODAS, 0.4); rkey(r, T_TODAS + 3.0, 0.15)
    # emperra: treme na explosão
    rkey(r, T_ARR + 0.3, (2.3 if out else 0.15) + random.uniform(0.2, 0.6))
    rkey(r, T_ARR + 1.2, (2.3 if out else 0.15) + random.uniform(0.1, 0.4))
    r.rotation_euler = (0, 0, 0); r.keyframe_insert('rotation_euler', frame=F(T_ARR + 0.2))
    r.rotation_euler = (random.uniform(-0.12, 0.12), random.uniform(-0.12, 0.12), 0); r.keyframe_insert('rotation_euler', frame=F(T_ARR + 1.0))

# medidor
def gkey(t, v):
    gfill.scale.x = 8.2 * v; gfill.keyframe_insert('scale', frame=F(t))
gkey(s3, 0.55); gkey(T_CAIDO - 0.1, 0.55); gkey(T_CAIDO + 0.8, 0.07)
gkey(T_PUX + 0.5, 0.07); gkey(T_PUX + 2.5, 0.2); gkey(T_DISP - 0.1, 0.22); gkey(T_DISP + 0.6, 1.9)
for t, c in ((s3, hexc('41c46f')), (T_CAIDO + 0.5, hexc('ffd23f')), (T_DISP + 0.1, hexc('e0281e'))):
    mkey(GAUGE, t, c)
# cores do núcleo
for t, c in ((s3, hexc('3aa0e0')), (T_AGUA3 - 0.05, hexc('3aa0e0')), (T_AGUA3 + 0.25, hexc('8fd4ff')), (T_AGUA3 + 0.7, hexc('3aa0e0')),
             (T_DISP - 0.1, hexc('3aa0e0')), (T_DISP + 0.5, hexc('ff8a2a')), (T_VAPOR + 0.3, hexc('fff0b0'))):
    mkey(WATER_C, t, c)
for t, c in ((s3, hexc('55555e')), (T_DISP - 0.1, hexc('55555e')), (T_DISP + 0.8, hexc('8a3424'))):
    mkey(GRAPH_C, t, c)

# tampa voa
p0 = plate.location.copy()
key(plate, 'location', T_ARR - 0.05, p0.copy()); key(plate, 'rotation_euler', T_ARR - 0.05, (0, 0, 0))
key(plate, 'location', T_ARR + 1.3, (p0.x + 0.6, p0.y - 0.8, 15.5)); key(plate, 'rotation_euler', T_ARR + 1.3, (1.1, 0.35, 0.1))
key(plate, 'location', T_ARR + 3.0, (p0.x + 0.8, p0.y - 0.5, 7.2)); key(plate, 'rotation_euler', T_ARR + 3.0, (1.45, 0.4, 0.12))
# destroços
for d in debris:
    p = d.location.copy()
    key(d, 'scale', T_ARR - 0.05, (0, 0, 0)); key(d, 'scale', T_ARR + 0.05, (1, 1, 1))
    key(d, 'location', T_ARR, p.copy())
    dx = random.uniform(-11, 11); dy = random.uniform(-8, 3); dz = random.uniform(6, 15)
    key(d, 'location', T_ARR + 1.0, (p.x + dx * 0.6, p.y + dy * 0.6, p.z + dz))
    key(d, 'location', T_ARR + 3.2, (p.x + dx, p.y + dy, 0.3))
    key(d, 'rotation_euler', T_ARR, (0, 0, 0))
    key(d, 'rotation_euler', T_ARR + 3.2, (random.uniform(-6, 6), random.uniform(-6, 6), random.uniform(-6, 6)))
# vapor
for k, o in enumerate(steam):
    p = o.location.copy(); t0 = T_VAPOR - 0.2 + k * 0.06
    key(o, 'scale', t0 - 0.01, (0, 0, 0)); key(o, 'location', t0, p.copy())
    r = random.uniform(1.6, 3.2)
    key(o, 'scale', t0 + 1.5, (r, r, r * 0.9)); key(o, 'location', t0 + 1.5, (p.x, p.y, p.z + random.uniform(2, 5)))
    key(o, 'scale', TOTAL + 0.5, (r * 1.5, r * 1.5, r * 1.3)); key(o, 'location', TOTAL + 0.5, (p.x + random.uniform(-2, 2), p.y + 1, p.z + random.uniform(8, 13)))

# botão AZ-5 (afunda no "aperta")
b0 = button.location.copy()
nrm = Vector((0, math.sin(math.radians(62)) * 0, 0))
key(button, 'location', T_APERTA - 0.05, b0.copy())
key(button, 'location', T_APERTA + 0.15, (b0.x, b0.y + 0.05, b0.z - 0.09))
mkey(BTN, T_APERTA - 0.05, hexc('e0281e')); mkey(BTN, T_APERTA + 0.15, hexc('ff5a3c'))

# close no canal
KGR = mat('kgr', hexc('4a4a52'))
for o in bpy.data.objects:
    if o.name.startswith('kblock'): o.data.materials.clear(); o.data.materials.append(KGR)
def kkey(t, bottom):
    krod.location.z = krod_z(bottom); krod.keyframe_insert('location', frame=F(t))
    lab_g.location.z = bottom + 1.25; lab_g.keyframe_insert('location', frame=F(t))
    lab_b.location.z = min(9.5, bottom + 4.2); lab_b.keyframe_insert('location', frame=F(t))
    kwater.scale.z = min(7.4, bottom); kwater.keyframe_insert('scale', frame=F(t))
kkey(s6, 7.4); kkey(T_EMP - 0.1, 7.4); kkey(T_EMP + 2.4, 3.0)
for o, t in ((lab_b, s6 + 0.4), (lab_g, T_GRAF - 0.1), (lab_w, T_AGUA6 - 0.1)):
    key(o, 'scale', s6 - 0.05 if t > s6 + 0.1 else s6 - 0.2, (0, 0, 0)); key(o, 'scale', t, (0, 0, 0)); key(o, 'scale', t + 0.3, (1, 1, 1))
for t, c in ((s6, hexc('4a4a52')), (T_ESQ - 0.1, hexc('4a4a52')), (T_ESQ + 1.0, hexc('c8501e'))):
    mkey(KGR, t, c)
for t, c in ((s6, hexc('3aa0e0')), (T_ESQ - 0.1, hexc('3aa0e0')), (T_ESQ + 1.0, hexc('9ad8ff'))):
    mkey(WATER, t, c)

# ------------------------------------------------------------ câmera (calculada quadro a quadro)
bpy.ops.object.camera_add(); cam = bpy.context.object; S.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.clip_end = 1000
bpy.ops.object.empty_add(); tgt = bpy.context.object
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
SEGS = [
    [(0.0, (-26, -60, 12), (4, 0, 10), 30), (s2, (-18, -50, 9), (2, 0, 10), 32), (s3, (4, -44, 7), (2, 0, 10), 32)],
    [(s3, (CX - 2, -16, 8.5), (CX, 1.5, 3.8), 22), (s4, (CX + 3, -14.5, 8), (CX + 0.5, 1.5, 3.8), 23),
     (T_PUX - 0.3, (CX - 1, -16, 9.5), (CX + 0.5, 1.5, 4.6), 22), (s5, (CX + 4, -17, 10.5), (CX + 1, 1.5, 5.0), 22)],
    [(s5, (PX + 1.0, -7, 3.4), (PX, 0.5, 1.6), 30), (T_APERTA - 0.4, (PX + 0.3, -3.2, 2.3), (PX, 0.45, 1.3), 32),
     (T_TODAS, (PX + 0.1, -2.6, 2.0), (PX, 0.45, 1.3), 34)],
    [(T_TODAS, (CX + 3, -16, 9), (CX, 1.5, 4.6), 22), (s6, (CX + 1, -14, 7.5), (CX, 1.5, 4.0), 22)],
    [(s6, (KX + 0.5, -12, 8), (KX, 0, 6.0), 24), (T_EMP, (KX + 1, -11, 6.5), (KX, 0, 5.0), 24), (s7, (KX - 1, -10, 5.5), (KX, 0, 4.5), 24)],
    [(s7, (CX, -17, 7), (CX, 1.5, 4.0), 22), (T_ARR, (CX + 1, -18, 8), (CX, 1.5, 5.0), 21),
     (T_ARR + 3, (CX + 3, -27, 12), (CX, 1.5, 9), 20), (TOTAL + 0.5, (CX + 5, -31, 13), (CX, 1.5, 9), 20)],
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
