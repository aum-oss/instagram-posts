"""Cena 3D da Enigma (Blender/bpy, motor Workbench). Uso:
python3 scene.py preview t1,t2,...   -> PNGs de quadros soltos em prev/
python3 scene.py render START END    -> frames em frames/ (índices de quadro)
"""
import bpy, math, json, sys, os
from mathutils import Vector

FPS = 30
T = json.load(open('/home/claude/enigma3d/timing.json'))
WD = json.load(open('/home/claude/enigma3d/words.json'))
def wt(scene, word, k=0):
    """tempo de início da k-ésima ocorrência de uma palavra na cena (1-based)."""
    hits = [s for w, s, e in WD[scene - 1] if w.strip('.,').lower() == word.lower()]
    return hits[k]
SC = [s for s, d in T['scenes']]
TOTAL = T['total']
def F(t): return t * FPS + 1

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.fps = FPS
S.frame_start = 1; S.frame_end = int(math.ceil(TOTAL * FPS))
S.render.engine = 'BLENDER_WORKBENCH'
S.render.resolution_x, S.render.resolution_y = 1080, 1920
S.display.render_aa = '16'
sh = S.display.shading
sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
sh.show_shadows = True; sh.shadow_intensity = 0.45
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.cavity_ridge_factor = 0.6; sh.cavity_valley_factor = 1.0
sh.curvature_ridge_factor = 0.5; sh.curvature_valley_factor = 0.7
sh.show_object_outline = True; sh.object_outline_color = (0.05, 0.04, 0.04)
S.display.light_direction = (-0.35, -0.45, 0.82)
S.display.shadow_shift = 0.08
w = bpy.data.worlds.new('w'); S.world = w; w.color = (0.93, 0.88, 0.80)
S.render.image_settings.file_format = 'PNG'
S.view_settings.view_transform = 'Standard'
S.view_settings.exposure = 0.55
S.display.render_aa = 'FXAA'

FONT = bpy.data.fonts.load('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf')

_m = {}
def mat(name, rgb, unique=False):
    if not unique and name in _m: return _m[name]
    m = bpy.data.materials.new(name); m.diffuse_color = (*rgb, 1)
    _m[name] = m; return m

def hexc(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

def box(loc, size, m, name='box', bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new('b', 'BEVEL'); b.width = bevel; b.segments = 3
    o.data.materials.append(m); return o

def cyl(loc, r, depth, m, rot=(0, 0, 0), verts=32, name='cyl', bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name
    if bevel:
        b = o.modifiers.new('b', 'BEVEL'); b.width = bevel; b.segments = 2
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def text(body, loc, size, m, rot=(0, 0, 0), name='txt', extrude=0.004):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.font = FONT
    cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = extrude
    o = bpy.data.objects.new(name, cu); S.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return o

def tube(pts, r, m, name='tube'):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    cu.bevel_depth = r; cu.bevel_resolution = 4; cu.use_fill_caps = True
    cu.bevel_factor_mapping_end = 'SPLINE'
    o = bpy.data.objects.new(name, cu); S.collection.objects.link(o); o.data.materials.append(m)
    return o

def join(objs, name):
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    o = bpy.context.object; o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return o

# ------------------------------------------------------------ cores
WOOD = mat('wood', hexc('8a5a34')); WOOD2 = mat('wood2', hexc('a06a3e'))
PANEL = mat('panel', hexc('2b2d31')); METAL = mat('metal', hexc('8d9096'))
KEY = mat('key', hexc('f1ece1')); KEYTXT = mat('keytxt', hexc('1d1d1f'))
LAMPTXT = mat('lamptxt', hexc('f4efe4')); BRASS = mat('brass', hexc('c99a3c'))
REFL = mat('refl', hexc('7b4bd6')); RED = mat('red', hexc('d84a3a'))
CREAM = mat('cream', hexc('efe6d6')); FLOOR1 = mat('floor1', hexc('d4a873')); FLOOR2 = mat('floor2', hexc('c99a62'))
DESK = mat('desk', hexc('c77d45')); DARK = mat('dark', hexc('222226'))
SIG = mat('sig', hexc('3fd2ff')); SIG2 = mat('sig2', hexc('ff8a2a'))
GREEN = mat('green', hexc('41c46f')); WHITE = mat('white', hexc('fafafa'))
LAMP_OFF = hexc('3a3c42'); LAMP_ON = hexc('ffd23f'); LAMP_ON2 = hexc('ff8a2a')

# ------------------------------------------------------------ sala
for i in range(-10, 26):
    box((i * 1.0, 4, -3.05), (1.0, 30, 0.1), FLOOR1 if i % 2 else FLOOR2, 'plank')
box((8, 3.6, 2), (40, 0.2, 10), CREAM, 'wall')
box((8, 3.45, -2.8), (40, 0.1, 0.4), mat('rodape', hexc('b78a5c')), 'rodape')
# mesa
box((0, 0.4, -0.12), (6.4, 4.6, 0.24), DESK, 'desk', 0.03)
for x in (-3.0, 3.0):
    for y in (-1.7, 2.5):
        box((x, y, -1.6), (0.18, 0.18, 2.8), DARK, 'leg')
# quadro (mapa) na parede
box((-2.3, 3.47, 2.6), (2.6, 0.06, 1.9), mat('frame', hexc('5b3a22')), 'frame')
box((-2.3, 3.43, 2.6), (2.35, 0.04, 1.65), mat('map', hexc('9cc6e0')), 'map')
for (x, z, sx, sz) in ((-2.9, 2.9, .7, .5), (-2.0, 2.4, 1.0, .6), (-1.7, 3.05, .5, .35), (-2.7, 2.15, .4, .3)):
    box((x, 3.40, z), (sx, 0.03, sz), mat('land', hexc('9fc07f')), 'land')
# relógio
cyl((2.4, 3.46, 3.0), 0.55, 0.08, mat('clock', hexc('f7f3ea')), rot=(math.pi / 2, 0, 0), name='clock')
cyl((2.4, 3.50, 3.0), 0.6, 0.06, DARK, rot=(math.pi / 2, 0, 0), name='clockrim')
box((2.4, 3.40, 3.15), (0.04, 0.02, 0.32), DARK, 'hand')
box((2.52, 3.40, 3.0), (0.25, 0.02, 0.04), DARK, 'hand2')
# caneca e luminária
cyl((2.6, -0.9, 0.25), 0.22, 0.5, RED, name='mug')
cyl((2.6, 1.9, 0.05), 0.35, 0.1, DARK, name='lampbase')
box((2.6, 1.9, 0.9), (0.08, 0.08, 1.7), DARK, 'lamparm')
cyl((2.35, 1.6, 1.75), 0.32, 0.4, mat('lampshade', hexc('f2c14e')), rot=(0.7, 0, 0.3), name='shade')

# ------------------------------------------------------------ Enigma
box((0, 0.05, 0.6), (3.5, 2.95, 1.2), WOOD, 'case', 0.05)
box((0, 0.05, 1.22), (3.3, 2.75, 0.06), PANEL, 'top')
# tampa aberta atrás
lid = box((0, 1.95, 1.85), (3.5, 0.1, 1.4), WOOD2, 'lid', 0.04)
lid.rotation_euler = (math.radians(14), 0, 0)
# placa frontal (plugboard)
box((0, -1.44, 0.55), (3.2, 0.06, 0.8), PANEL, 'plug')
ROWS = ["QWERTZUIO", "ASDFGHJK", "PYXCVBNML"]
def grid_pos(letter, ys):
    for r, row in enumerate(ROWS):
        if letter in row:
            i = row.index(letter); n = len(row)
            return Vector(((i - (n - 1) / 2) * 0.36, ys[r], 0))
KEY_Y = (-0.25, -0.62, -0.99); LAMP_Y = (0.95, 0.65, 0.35)
keys = {}; lamps = {}; lampmats = {}
for row in ROWS:
    for L in row:
        p = grid_pos(L, KEY_Y)
        stem = cyl((p.x, p.y, 1.32), 0.035, 0.2, METAL, verts=12, name='stem')
        cap = cyl((p.x, p.y, 1.45), 0.14, 0.07, KEY, name='key_' + L, bevel=0.015)
        rim = cyl((p.x, p.y, 1.44), 0.155, 0.05, METAL, name='rim')
        t = text(L, (p.x, p.y, 1.49), 0.17, KEYTXT, name='kt_' + L)
        keys[L] = join([cap, stem, rim, t], 'key_' + L)
        q = grid_pos(L, LAMP_Y)
        lm = mat('lamp_' + L, LAMP_OFF, unique=True); lampmats[L] = lm
        lamps[L] = cyl((q.x, q.y, 1.27), 0.13, 0.05, lm, name='lamp_' + L)
        text(L, (q.x, q.y, 1.30), 0.15, LAMPTXT, name='lt_' + L)
# rotores (eixo X), atrás
RX = {'refl': -1.1, 'I': -0.62, 'II': -0.17, 'III': 0.28, 'entry': 0.72}
RY, RZ = 1.25, 1.38
rot_objs = {}
for k in ('I', 'II', 'III'):
    x = RX[k]
    core = cyl((x, RY, RZ), 0.36, 0.3, BRASS, rot=(0, math.pi / 2, 0), verts=48, name='rotor_' + k, bevel=0.02)
    ring = cyl((x + 0.17, RY, RZ), 0.39, 0.06, DARK, rot=(0, math.pi / 2, 0), verts=26, name='ring_' + k)
    # marcador branco para ver o giro
    mk = box((x + 0.17, RY, RZ + 0.39), (0.08, 0.08, 0.06), WHITE, 'mark_' + k)
    parts = [core, ring, mk]
    for j in range(13):  # ranhuras
        a = j / 13 * 2 * math.pi
        g = box((x - 0.04, RY + 0.36 * math.sin(a), RZ + 0.36 * math.cos(a)), (0.16, 0.05, 0.04), BRASS, 'grip')
        g.rotation_euler = (-a, 0, 0); parts.append(g)
    rot_objs[k] = join(parts, 'rotor_' + k)
refl = cyl((RX['refl'], RY, RZ), 0.36, 0.22, REFL, rot=(0, math.pi / 2, 0), verts=48, name='reflector', bevel=0.02)
cyl((RX['entry'], RY, RZ), 0.3, 0.2, METAL, rot=(0, math.pi / 2, 0), verts=32, name='entry', bevel=0.02)
cyl(((RX['refl'] + RX['entry']) / 2, RY, RZ), 0.05, 2.3, METAL, rot=(0, math.pi / 2, 0), verts=12, name='axle')
box((0, RY, 1.28), (2.4, 0.9, 0.12), PANEL, 'rotorbed')
# rótulos dos rotores
for k, x in RX.items():
    lab = {'refl': 'REFLETOR', 'I': 'I', 'II': 'II', 'III': 'III', 'entry': ''}[k]
    if lab and k != 'refl':
        text(lab, (x, RY - 0.42, 1.36), 0.14, LAMPTXT, rot=(math.radians(60), 0, 0), name='rl_' + k)
# soquetes do plugboard
sock = {}
for i, L in enumerate("QWERTZUIO"):
    pass
PLUG = "QWERTZUIOASDFGHJKPYXCVBNML"
for i, L in enumerate(PLUG):
    r = i // 13; c = i % 13
    x = (c - 6) * 0.23; z = 0.75 - r * 0.38
    for dz in (0.05, -0.05):
        cyl((x, -1.48, z + dz), 0.035, 0.03, DARK, rot=(math.pi / 2, 0, 0), verts=10, name='sock')
    text(L, (x, -1.475, z + 0.13), 0.08, LAMPTXT, rot=(math.pi / 2, 0, 0), name='pl_' + L)
    sock[L] = Vector((x, -1.5, z))
# um cabo plugado de exemplo (A<->Q) e (E<->Z)
def cable(a, b, m):
    pa, pb = sock[a], sock[b]
    mid = (pa + pb) / 2 + Vector((0, -0.35, -0.25))
    pts = []
    for i in range(21):
        t = i / 20
        p = (1 - t) ** 2 * pa + 2 * (1 - t) * t * mid + t * t * pb
        pts.append(tuple(p))
    tube(pts, 0.03, m, 'cable')
cable('A', 'Q', RED); cable('E', 'Z', mat('cable2', hexc('2d6fd6')))

# ------------------------------------------------------------ Bombe (à direita)
BX = 9.0
box((BX, 2.2, -0.6), (5.0, 1.6, 4.9), mat('bombebody', hexc('3e4452')), 'bombe', 0.05)
box((BX, 2.2, 1.95), (5.1, 1.7, 0.2), mat('bombe_top', hexc('3a3a40')), 'btop')
drum_cols = [hexc(h) for h in ('d84a3a', '2b2d31', 'e8c547', '2d6fd6', '41c46f', 'f1ece1')]
drums = []
for bank in range(3):
    for r in range(3):
        for c in range(4):
            x = BX - 1.9 + bank * 1.45 + c * 0.32 - 0.48 + 0.48
            x = BX - 2.1 + bank * 1.55 + c * 0.36
            z = 1.1 - r * 1.25
            dm = mat('drum%d' % ((bank * 3 + r + c) % 6), drum_cols[(bank * 3 + r + c) % 6])
            d = cyl((x, 1.35, z), 0.16, 0.12, dm, rot=(math.pi / 2, 0, 0), verts=32, name='drum')
            mk = box((x, 1.28, z + 0.11), (0.05, 0.02, 0.07), WHITE, 'dmark')
            drums.append(join([d, mk], 'drum'))
    text(['I', 'II', 'III'][bank], (BX - 2.1 + bank * 1.55 + 0.54, 1.33, 1.6), 0.18, LAMPTXT, rot=(math.pi / 2, 0, 0))
bulb_m = mat('bulb', hexc('5a2020'), unique=True)
cyl((BX + 2.05, 1.30, 1.62), 0.24, 0.12, bulb_m, rot=(math.pi / 2, 0, 0), name='bulb')
text('BOMBE', (BX - 0.2, 1.33, 1.95), 0.3, mat('btxt', hexc('e8c547')), rot=(math.pi / 2, 0, 0))

# ------------------------------------------------------------ animação: helpers
def key_loc(o, t, loc, interp='BEZIER'):
    o.location = loc; o.keyframe_insert('location', frame=F(t))
def fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    act = ad.action
    if hasattr(act, 'fcurves'):
        try: return list(act.fcurves)
        except Exception: pass
    out = []
    for ly in act.layers:
        for st in ly.strips:
            for cb in st.channelbags: out += list(cb.fcurves)
    return out
def set_interp(obj_or_data, kind='BEZIER'):
    for fc in fcurves(obj_or_data):
        for kp in fc.keyframe_points: kp.interpolation = kind

def lamp_on(L, t0, t1, col=LAMP_ON):
    m = lampmats[L]
    for t, c in ((t0 - 0.01, LAMP_OFF), (t0, col), (t1, col), (t1 + 0.15, LAMP_OFF)):
        m.diffuse_color = (*c, 1); m.keyframe_insert('diffuse_color', frame=F(t))
    set_interp(m, 'CONSTANT')
    o = lamps[L]
    for t, k in ((t0 - 0.01, 1), (t0 + 0.12, 1.45), (t1, 1.45), (t1 + 0.15, 1)):
        o.scale = (k, k, k); o.keyframe_insert('scale', frame=F(t))

def press(L, t, dur=0.35):
    k = keys[L]; z0 = k.location.z
    for tt, z in ((t - 0.01, z0), (t + 0.08, z0 - 0.08), (t + dur, z0 - 0.08), (t + dur + 0.12, z0)):
        k.location.z = z; k.keyframe_insert('location', index=2, frame=F(tt))
    k.location.z = z0

def signal(path, t0, t1, m, name, fade_at=None, knots=None):
    """tubo que cresce de t0 a t1 + bolinha na ponta. knots: [(índice do ponto, tempo), ...]"""
    o = tube(path, 0.045, m, name)
    cu = o.data
    # bolinha
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=path[0]); b = bpy.context.object
    b.data.materials.append(m); bpy.ops.object.shade_smooth()
    seg = [(Vector(path[i + 1]) - Vector(path[i])).length for i in range(len(path) - 1)]
    tot = sum(seg)
    def at(u):
        d = u * tot
        for i, s in enumerate(seg):
            if d <= s or i == len(seg) - 1:
                return Vector(path[i]).lerp(Vector(path[i + 1]), min(1, d / s if s else 1))
            d -= s
    cum = [0]
    for sg in seg: cum.append(cum[-1] + sg)
    K = [(t0, 0.0)] + [(tk, cum[i] / tot) for i, tk in (knots or [])] + [(t1, 1.0)]
    def u_of(t):
        for (ta, ua), (tb, ub) in zip(K, K[1:]):
            if t <= tb: return ua + (ub - ua) * max(0, (t - ta) / (tb - ta))
        return 1.0
    f0, f1 = int(F(t0)), int(F(t1))
    for f in range(f0 - 1, f1 + 2):
        cu.bevel_factor_end = u_of((f - 1) / FPS) if f >= f0 else 0.0
        cu.keyframe_insert('bevel_factor_end', frame=f)
    b.scale = (0, 0, 0); b.keyframe_insert('scale', frame=f0 - 1)
    b.scale = (1, 1, 1); b.keyframe_insert('scale', frame=f0)
    for f in range(f0, f1 + 1):
        b.location = at(u_of((f - 1) / FPS)); b.keyframe_insert('location', frame=f)
    b.scale = (1, 1, 1); b.keyframe_insert('scale', frame=f1 + 4)
    b.scale = (0, 0, 0); b.keyframe_insert('scale', frame=f1 + 10)
    if fade_at is not None:
        o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=F(fade_at))
        o.scale = (1, 1, 0.001); o.keyframe_insert('scale', frame=F(fade_at) + 8)
        o.scale = (1, 1, 1)
    return o

def route(key, lamp, plug_to):
    """caminho por cima da máquina: tecla -> plugboard -> rotores -> refletor -> volta -> lâmpada."""
    k = grid_pos(key, KEY_Y); l = grid_pos(lamp, LAMP_Y)
    sa = sock[key]; sb = sock[plug_to]
    zt = 1.62; zb = 1.52
    p = [(k.x, k.y, 1.52), (k.x, k.y, zt), (k.x, -1.42, zt), (sa.x, -1.62, sa.z + 0.1), (sa.x, -1.62, sa.z - 0.15),
         (sb.x, -1.62, sb.z - 0.15), (1.45, -1.62, sb.z), (1.45, -1.55, zt), (1.45, RY, zt + 0.25),
         (RX['entry'] + 0.2, RY, RZ + 0.28), (RX['refl'], RY, RZ + 0.28), (RX['refl'] - 0.24, RY, RZ),
         (RX['refl'], RY, RZ - 0.06), (RX['entry'] + 0.25, RY, RZ - 0.06), (1.2, RY - 0.4, zt),
         (l.x, l.y, zt), (l.x, l.y, 1.36)]
    return p

# ------------------------------------------------------------ roteiro
s1, s2, s3, s4, s5, s6, s7 = SC
# cena 3: A -> G
t_press1 = wt(3, 'O', 0) - 0.25
press('A', t_press1, 0.5)
t_sig0 = wt(3, 'sinal'); t_lamp = wt(3, 'virou')
signal(route('A', 'G', 'Q'), t_sig0, t_lamp - 0.15, SIG, 'sig1', fade_at=s4 + 0.6,
       knots=[(3, wt(3, 'cabos') + 0.2), (9, wt(3, 'atravessa') + 0.1), (11, wt(3, 'refletor') + 0.2), (13, wt(3, 'volta') + 0.3)])
lamp_on('G', t_lamp - 0.15, s4 + 0.6)
# cena 4: aperta A de novo, rotor III gira, sai T
t_press2 = wt(4, 'Aperta')
press('A', t_press2 + 0.3, 0.5)
r3 = rot_objs['III']; e0 = r3.rotation_euler.copy()
r3.keyframe_insert('rotation_euler', frame=F(t_press2 + 0.3))
r3.rotation_euler = (e0.x + 2 * math.pi / 26 * 2, e0.y, e0.z)
r3.keyframe_insert('rotation_euler', frame=F(wt(4, 'girou')))
t_l2 = wt(4, 'letra')
signal(route('A', 'T', 'Q'), wt(4, 'girou') + 0.2, t_l2, SIG2, 'sig2', fade_at=s5 + 0.3)
lamp_on('T', t_l2, s5 + 0.3, LAMP_ON2)
# cena 5: refletor pulsa (escala)
for t, sc_ in ((wt(5, 'refletor') - 0.1, 1.0), (wt(5, 'refletor') + 0.15, 1.25), (wt(5, 'refletor') + 0.4, 1.0),
               (wt(5, 'nunca'), 1.0), (wt(5, 'nunca') + 0.25, 1.25), (wt(5, 'nunca') + 0.5, 1.0)):
    refl.scale = (sc_, sc_, sc_); refl.keyframe_insert('scale', frame=F(t))
# cena 6: tambores da Bombe giram, lâmpada fica verde em "certa"
t_spin0 = wt(6, 'Bombe') - 0.3; t_ok = wt(6, 'certa')
for i, d in enumerate(drums):
    e = d.rotation_euler.copy()
    d.keyframe_insert('rotation_euler', frame=F(s6))
    d.rotation_euler = (e.x, e.y + (1 if i % 2 else -1) * (2 * math.pi) * (5 + i % 4), e.z)
    d.keyframe_insert('rotation_euler', frame=F(t_ok))
for t, c in ((t_ok - 0.01, hexc('5a2020')), (t_ok, hexc('41ff7a'))):
    bulb_m.diffuse_color = (*c, 1); bulb_m.keyframe_insert('diffuse_color', frame=F(t))
set_interp(bulb_m, 'CONSTANT')

# ------------------------------------------------------------ câmera
bpy.ops.object.camera_add(); cam = bpy.context.object; S.camera = cam
cam.data.lens = 30; cam.data.sensor_fit = 'VERTICAL'
bpy.ops.object.empty_add(); tgt = bpy.context.object
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
A = grid_pos('A', KEY_Y)
SHOTS = [  # (tempo, posição da câmera, alvo, lente)
    (0.0, (0.0, -10.5, 6.8), (0, 0.4, 0.9), 30),
    (s2 - 0.3, (0.3, -6.0, 4.6), (0, 0.3, 1.1), 30),
    (s2 + 2.5, (3.6, -4.8, 4.2), (0, 0.4, 1.2), 30),
    (s3 - 0.4, (-0.4, -3.4, 3.0), (A.x, A.y, 1.35), 30),
    (s3 + 1.0, (-0.2, -4.4, 4.4), (0, -0.1, 1.2), 28),
    (s3 + 5.0, (0.9, -4.0, 5.2), (0, 0.3, 1.25), 28),
    (s4 - 0.2, (0.2, -4.3, 5.0), (0, 0.3, 1.25), 28),
    (s4 + 3.0, (2.2, -2.6, 3.6), (0.3, 0.9, 1.35), 30),
    (s5 - 0.2, (1.8, -2.6, 3.4), (0.0, 0.9, 1.35), 30),
    (s5 + 1.5, (-3.4, -1.0, 2.6), (RX['refl'], RY, RZ), 32),
    (s6 - 0.1, (-3.0, -1.6, 2.8), (RX['refl'], RY, RZ), 32),
    (s6 + 3.0, (3.5, -6.5, 3.2), (4.5, 1.5, 0.6), 28),
    (s6 + 6.0, (BX, -7.6, 0.3), (BX, 1.6, -0.5), 28),
    (s7 - 0.2, (BX - 0.4, -7.0, 0.5), (BX, 1.6, -0.3), 28),
    (TOTAL, (4.6, -16.5, 4.2), (4.6, 1.2, -0.3), 26),
]
for t, p, g, lens in SHOTS:
    cam.location = p; cam.keyframe_insert('location', frame=F(t))
    tgt.location = g; tgt.keyframe_insert('location', frame=F(t))
    cam.data.lens = lens; cam.data.keyframe_insert('lens', frame=F(t))
# câmera não para: interpolação suave
for o in (cam, tgt, cam.data):
    for fc in fcurves(o):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'

# ------------------------------------------------------------ execução
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    if mode == 'preview':
        os.makedirs('/home/claude/enigma3d/prev', exist_ok=True)
        for t in [float(x) for x in sys.argv[2].split(',')]:
            S.frame_set(int(F(t)))
            S.render.filepath = '/home/claude/enigma3d/prev/t%05.1f.png' % t
            bpy.ops.render.render(write_still=True)
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs('/home/claude/enigma3d/frames', exist_ok=True)
        for f in range(a, b + 1):
            out = '/home/claude/enigma3d/frames/%05d.png' % f
            if os.path.exists(out): continue
            S.frame_set(f); S.render.filepath = out + '.tmp.png'
            bpy.ops.render.render(write_still=True)
            os.rename(out + '.tmp.png', out)
