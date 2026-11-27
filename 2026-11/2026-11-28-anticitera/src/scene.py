"""Cena 3D do Anticítera (Blender/bpy, motor Workbench). Uso:
python3 scene.py preview t1,t2,...   -> PNGs de quadros soltos em prev/
python3 scene.py render START END    -> frames em frames/ (índices de quadro)
"""
import bpy, math, json, sys, os
from mathutils import Vector

FPS = 30
T = json.load(open('/home/claude/anti3d/timing.json'))
WD = json.load(open('/home/claude/anti3d/words.json'))
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
SEA = hexc('2f7f99'); STUDIO = hexc('2a2522')
SAND = mat('sand', hexc('d8c08e')); SAND2 = mat('sand2', hexc('cbb17c'))
ROCK = mat('rock', hexc('6f7a80')); WEED = mat('weed', hexc('3f9e57'))
CLAY = mat('clay', hexc('c06a3a')); MARBLE = mat('marble', hexc('eeeae0'))
PATINA = mat('patina', hexc('5f9b7f')); PATINA2 = mat('patina2', hexc('4a7f68'))
BRONZE = mat('bronze', hexc('c9923c')); BRONZE2 = mat('bronze2', hexc('a8742e'))
WOOD = mat('wood', hexc('7a4a2a')); WOOD2 = mat('wood2', hexc('5e3820'))
GOLD = mat('gold', hexc('ffd23f')); SILVER = mat('silver', hexc('d9dde2'))
DARK = mat('dark', hexc('1f1f22')); TABLE = mat('table', hexc('3b2a20'))
w.color = SEA

def gear(loc, r, teeth, m, thick=0.08, spokes=0, name='gear', hole=False):
    """engrenagem de frente para a câmera (eixo Y)."""
    x, y, z = loc
    parts = [cyl((x, y, z), r, thick, m, rot=(math.pi / 2, 0, 0), verts=48, name=name)]
    tl = max(0.05, r * 0.12)
    for j in range(teeth):
        a = j / teeth * 2 * math.pi
        t = box((x + (r + tl * 0.4) * math.cos(a), y, z + (r + tl * 0.4) * math.sin(a)),
                (tl, thick, tl * 0.7), m, 'tooth')
        t.rotation_euler = (0, -a, 0); parts.append(t)
    for j in range(spokes):
        a = j / spokes * math.pi
        s = box((x, y - thick * 0.6, z), (r * 1.7, thick * 0.6, r * 0.12), BRONZE2, 'spoke')
        s.rotation_euler = (0, -a, 0); parts.append(s)
    parts.append(cyl((x, y - thick * 0.7, z), r * 0.12, thick * 1.4, BRONZE2, rot=(math.pi / 2, 0, 0), name='hub'))
    g = join(parts, name)
    return g

# ------------------------------------------------------------ fundo do mar (x ~ 0)
for i in range(-10, 11):
    box((i * 1.0, 3, -0.25), (1.0, 26, 0.5), SAND if i % 2 else SAND2, 'sand')
import random
random.seed(7)
for i in range(14):
    x = random.uniform(-8, 8); y = random.uniform(-2, 9)
    if abs(x) < 2 and y < 2: continue
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.4, 1.2), location=(x, y, 0.1), subdivisions=1)
    o = bpy.context.object; o.scale.z = 0.6; o.data.materials.append(ROCK)
for i in range(22):
    x = random.uniform(-8, 8); y = random.uniform(-1, 9)
    if abs(x) < 1.8 and y < 2: continue
    h = random.uniform(0.8, 2.2)
    o = box((x, y, h / 2), (0.08, 0.08, h), WEED, 'weed'); o.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), 0)
def amphora(loc, rot):
    x, y, z = loc
    p = [cyl((x, y, z), 0.32, 0.9, CLAY, name='amph'),
         cyl((x, y, z + 0.6), 0.12, 0.4, CLAY, name='neck')]
    bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0.05, depth=0.4, location=(x, y, z - 0.6)); c = bpy.context.object
    c.rotation_euler = (math.pi, 0, 0); c.data.materials.append(CLAY); p.append(c)
    o = join(p, 'amphora'); o.rotation_euler = rot; return o
amphora((-2.4, 1.5, 0.35), (0, 1.35, 0.3)); amphora((2.6, 2.4, 0.35), (0.2, 1.4, -0.8))
amphora((-1.2, 3.6, 0.7), (0, 0, 0)); amphora((3.4, -0.4, 0.35), (0, 1.5, 1.2))
col = cyl((-3.2, 0.4, 0.4), 0.4, 3.0, MARBLE, rot=(0, math.pi / 2, 0.5), name='column', verts=16)
col2 = cyl((1.8, 5.0, 1.2), 0.45, 2.4, MARBLE, name='column2', verts=16)
# casco do navio (tábuas)
for k in range(6):
    o = box((0.5 + k * 0.1, 6.5, 0.3 + k * 0.25), (7.0, 0.3, 0.2), WOOD2, 'hull'); o.rotation_euler = (0.5, 0, 0.12)
# raios de luz

# o bloco corroído: duas metades + engrenagens dentro
BL = Vector((0, 0, 0.45))
half1 = box((BL.x - 0.36, BL.y, BL.z), (0.7, 1.0, 0.7), PATINA, 'half1', 0.08)
half2 = box((BL.x + 0.36, BL.y, BL.z), (0.7, 1.0, 0.7), PATINA2, 'half2', 0.08)
inner = []
for (dx, dz, r, n) in ((0, 0, 0.26, 18), (0.3, 0.12, 0.14, 10), (-0.27, -0.1, 0.16, 11)):
    inner.append(gear((BL.x + dx, BL.y - 0.1, BL.z + dz), r, n, BRONZE, thick=0.05, spokes=2, name='ig'))

# ------------------------------------------------------------ a máquina reconstruída (x ~ 20)
MX = 20.0
box((MX, 0.5, -0.2), (12, 10, 0.4), TABLE, 'table')
box((MX, 0, 2.5), (4.2, 1.2, 5.0), WOOD, 'mbox', 0.06)
box((MX, -0.61, 2.5), (4.0, 0.03, 4.8), WOOD2, 'mfront')
box((MX, 0.61, 2.5), (4.0, 0.03, 4.8), WOOD2, 'mback')
G = {}
G['b1'] = gear((MX, -0.72, 2.7), 1.35, 56, BRONZE, thick=0.08, spokes=2, name='b1')
G['g2'] = gear((MX + 1.95, -0.74, 2.7), 0.5, 21, BRONZE2, thick=0.08, name='g2')
G['g3'] = gear((MX - 0.0, -0.74, 4.72), 0.58, 24, BRONZE2, thick=0.08, name='g3')
G['g4'] = gear((MX - 1.8, -0.76, 3.65), 0.38, 16, BRONZE, thick=0.08, name='g4')
# ponteiros do Sol e da Lua no centro
sunp = join([box((MX, -0.9, 2.7 + 0.6), (0.08, 0.04, 1.2), GOLD, 'sunarm'),
             cyl((MX, -0.92, 2.7 + 1.2), 0.16, 0.05, GOLD, rot=(math.pi / 2, 0, 0), name='sunball')], 'sunp')
moonp = join([box((MX, -0.98, 2.7 + 0.45), (0.06, 0.04, 0.9), SILVER, 'moonarm')], 'moonp')
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(MX, -1.0, 2.7 + 0.95)); mb = bpy.context.object
mb.data.materials.append(SILVER)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.175, location=(MX + 0.01, -1.01, 2.7 + 0.95)); md = bpy.context.object
md.scale.x = 0.5; md.location.x += 0.09; md.data.materials.append(DARK)
moonp = join([moonp, mb, md], 'moonp')
bpy.context.view_layer.update()
def set_origin(o, pt):
    bpy.context.scene.cursor.location = pt
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# recria os ponteiros com a origem no centro do mostrador
set_origin(sunp, (MX, -0.9, 2.7)); set_origin(moonp, (MX, -0.98, 2.7))
# manivela no lado direito
crank = join([cyl((MX + 2.25, 0, 2.7), 0.08, 0.5, DARK, rot=(0, math.pi / 2, 0), name='axle'),
              box((MX + 2.5, 0, 3.0), (0.08, 0.12, 0.7), BRONZE2, 'arm'),
              cyl((MX + 2.7, 0, 3.3), 0.07, 0.4, WOOD2, rot=(0, math.pi / 2, 0), name='handle')], 'crank')
set_origin(crank, (MX + 2.25, 0, 2.7))
# pino e fenda (canto inferior esquerdo da frente)
PS = Vector((MX - 1.2, -0.74, 1.0))
qg = gear((PS.x, PS.y, PS.z), 0.62, 26, BRONZE, thick=0.07, name='qg')
slot = box((PS.x, PS.y - 0.06, PS.z + 0.38), (0.09, 0.03, 0.5), DARK, 'slot')
qpt = box((PS.x, PS.y - 0.08, PS.z + 0.95), (0.05, 0.03, 0.5), SILVER, 'qpoint')
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(PS.x, PS.y - 0.1, PS.z + 1.25)); qm = bpy.context.object; qm.data.materials.append(SILVER)
qg = join([qg, slot, qpt, qm], 'qg'); set_origin(qg, tuple(PS))
PC = PS + Vector((0.16, 0, 0.0))  # eixo do braço com o pino (deslocado)
parm = join([box((PC.x, PC.y - 0.14, PC.z + 0.17), (0.07, 0.03, 0.34), BRONZE2, 'parm'),
             cyl((PC.x, PC.y - 0.14, PC.z), 0.06, 0.05, DARK, rot=(math.pi / 2, 0, 0), name='phub'),
             cyl((PC.x, PC.y - 0.12, PC.z + 0.34), 0.05, 0.12, GOLD, rot=(math.pi / 2, 0, 0), name='pin')], 'parm')
set_origin(parm, tuple(PC))
PIN_R = 0.34
# mostrador de trás: espiral + glifos de eclipse + mostrador olímpico
BK = Vector((MX, 0.66, 2.6))
pts = []
for i in range(400):
    a = i / 400 * 4 * 2 * math.pi
    r = 0.45 + 1.15 * i / 400
    pts.append((BK.x + r * math.cos(a), BK.y, BK.z + r * math.sin(a)))
tube(pts, 0.025, GOLD, 'spiral')
bpointer = box((BK.x, BK.y + 0.05, BK.z + 0.85), (0.06, 0.03, 1.7), SILVER, 'bpointer'); set_origin(bpointer, tuple(BK))
glyphs = []
for k in range(8):
    a = 0.6 + k * 0.78; r = 0.6 + k * 0.13
    m = mat('glyph%d' % k, hexc('4a4038'), unique=True)
    g = cyl((BK.x + r * math.cos(a), BK.y + 0.04, BK.z + r * math.sin(a)), 0.1, 0.03, m, rot=(math.pi / 2, 0, 0), name='glyph')
    glyphs.append(m)
OL = Vector((MX + 1.35, 0.66, 4.45))
olymp = []
for k in range(4):
    m = mat('oly%d' % k, hexc('4a4038'), unique=True); olymp.append(m)
    a = k * math.pi / 2 + math.pi / 4
    cyl((OL.x + 0.18 * math.cos(a), OL.y + 0.04, OL.z + 0.18 * math.sin(a)), 0.13, 0.03, m, rot=(math.pi / 2, 0, 0), name='oly')
cyl((OL.x, OL.y + 0.02, OL.z), 0.42, 0.02, DARK, rot=(math.pi / 2, 0, 0), name='olybase')

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


# ------------------------------------------------------------ roteiro
s1, s2, s3, s4, s5, s6, s7 = SC
w.color = SEA; w.keyframe_insert('color', frame=1)
w.keyframe_insert('color', frame=F(s4 - 0.25))
w.color = STUDIO; w.keyframe_insert('color', frame=F(s4 + 0.2))
set_interp(w, 'LINEAR')
# bloco abre em "viram"
t_open = wt(3, 'viram')
for o, dx in ((half1, -1), (half2, 1)):
    x0 = o.location.x
    o.keyframe_insert('location', frame=F(t_open - 0.1))
    o.location.x = x0 + dx * 0.75; o.rotation_euler = (0, dx * 0.35, 0)
    o.keyframe_insert('location', frame=F(t_open + 0.8)); o.keyframe_insert('rotation_euler', frame=F(t_open + 0.8))
    o.rotation_euler = (0, 0, 0); o.keyframe_insert('rotation_euler', frame=F(t_open - 0.1))
for g in inner:
    g.scale = (0.6, 0.6, 0.6); g.keyframe_insert('scale', frame=F(t_open))
    g.scale = (1.05, 1.05, 1.05); g.keyframe_insert('scale', frame=F(t_open + 0.9))
    g.location.z += 0.0; g.keyframe_insert('location', frame=F(t_open))
    g.location.y -= 0.2; g.location.z += 0.15; g.keyframe_insert('location', frame=F(t_open + 0.9))
# ângulos por quadro
t_crank = wt(4, 'manivela')
f_end = int(math.ceil(TOTAL * FPS)) + 1
def theta(t):
    if t < t_crank - 0.3: return 0.0
    return (t - (t_crank - 0.3)) * 2 * math.pi / 1.6
for f in range(int(F(s3)), f_end + 1):
    t = (f - 1) / FPS
    th = theta(t); b = th / 5.0
    crank.rotation_euler = (th, 0, 0); crank.keyframe_insert('rotation_euler', frame=f)
    G['b1'].rotation_euler = (0, b, 0); G['b1'].keyframe_insert('rotation_euler', frame=f)
    G['g2'].rotation_euler = (0, -b * 56 / 21, 0); G['g2'].keyframe_insert('rotation_euler', frame=f)
    G['g3'].rotation_euler = (0, -b * 56 / 24, 0); G['g3'].keyframe_insert('rotation_euler', frame=f)
    G['g4'].rotation_euler = (0, -b * 56 / 16, 0); G['g4'].keyframe_insert('rotation_euler', frame=f)
    sunp.rotation_euler = (0, b, 0); sunp.keyframe_insert('rotation_euler', frame=f)
    moonp.rotation_euler = (0, b * 3.2, 0); moonp.keyframe_insert('rotation_euler', frame=f)
    bpointer.rotation_euler = (0, -b * 0.6, 0); bpointer.keyframe_insert('rotation_euler', frame=f)
    phi = th * 0.45
    parm.rotation_euler = (0, phi, 0); parm.keyframe_insert('rotation_euler', frame=f)
    px = PC.x + PIN_R * math.sin(phi); pz = PC.z + PIN_R * math.cos(phi)
    psi = math.atan2(px - PS.x, pz - PS.z)
    qg.rotation_euler = (0, psi, 0); qg.keyframe_insert('rotation_euler', frame=f)
    for g in inner:
        g.rotation_euler = (0, t * 0.8, 0); g.keyframe_insert('rotation_euler', frame=f)
# glifos de eclipse e mostrador olímpico acendem
t_ecl = wt(5, 'eclipses'); t_oly = wt(5, 'Olímpicos')
for k, m in enumerate(glyphs):
    for t, c in ((t_ecl - 0.01 + k * 0.12, hexc('4a4038')), (t_ecl + k * 0.12, hexc('ffd23f'))):
        m.diffuse_color = (*c, 1); m.keyframe_insert('diffuse_color', frame=F(t))
    set_interp(m, 'CONSTANT')
for k, m in enumerate(olymp):
    for t, c in ((t_oly - 0.01 + k * 0.1, hexc('4a4038')), (t_oly + k * 0.1, [hexc('2d6fd6'), hexc('e8c547'), hexc('41c46f'), hexc('e04a3a')][k])):
        m.diffuse_color = (*c, 1); m.keyframe_insert('diffuse_color', frame=F(t))
    set_interp(m, 'CONSTANT')

# ------------------------------------------------------------ câmera
bpy.ops.object.camera_add(); cam = bpy.context.object; S.camera = cam
cam.data.lens = 30; cam.data.sensor_fit = 'VERTICAL'
bpy.ops.object.empty_add(); tgt = bpy.context.object
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
t_sol = wt(4, 'Sol'); t_dentes = wt(5, 'dentes')
SHOTS = [
    (0.0, (0.5, -8.5, 6.5), (0, 0.5, 0.5), 30),
    (s2, (2.0, -6.0, 3.5), (0, 0.8, 0.6), 30),
    (s2 + 5.5, (-4.5, -4.5, 2.5), (0, 1.0, 0.8), 28),
    (s3 - 0.3, (1.5, -3.6, 1.8), (0, 0, 0.5), 32),
    (s4 - 0.35, (0.4, -3.6, 1.6), (0, 0, 0.6), 30),
    (s4 + 0.35, (MX + 1.5, -9.0, 3.5), (MX, 0, 2.7), 30),
    (t_crank + 0.2, (MX + 5.0, -4.0, 3.5), (MX + 2.0, 0, 2.9), 32),
    (t_sol - 0.6, (MX + 0.5, -6.5, 3.0), (MX, -0.7, 2.8), 32),
    (s5 + 0.5, (MX - 0.8, -4.2, 2.6), (MX + 0.6, -0.7, 2.7), 34),
    (t_dentes + 2.5, (MX + 5.5, 3.5, 3.2), (MX, 0.6, 2.7), 30),
    (t_ecl - 1.5, (MX + 0.3, 5.2, 3.0), (MX, 0.66, 2.9), 32),
    (s6 - 0.2, (MX + 0.5, 5.5, 3.2), (MX, 0.66, 3.0), 32),
    (s6 + 1.2, (MX - 1.0, -4.0, 1.7), (MX - 1.15, -0.74, 1.3), 32),
    (s7 - 0.2, (MX - 0.8, -4.2, 1.8), (MX - 1.15, -0.74, 1.3), 32),
    (TOTAL, (MX + 2.5, -12.5, 4.5), (MX, 0, 2.6), 30),
]
for t, p, g, lens in SHOTS:
    cam.location = p; cam.keyframe_insert('location', frame=F(t))
    tgt.location = g; tgt.keyframe_insert('location', frame=F(t))
    cam.data.lens = lens; cam.data.keyframe_insert('lens', frame=F(t))
for o in (cam, tgt, cam.data):
    for fc in fcurves(o):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'
# corte seco entre o mar e a máquina (sem passar voando pela areia)
for o in (cam, tgt):
    for fc in fcurves(o):
        for kp in fc.keyframe_points:
            if abs(kp.co[0] - F(s4 - 0.35)) < 0.5: kp.interpolation = 'CONSTANT'
# ------------------------------------------------------------ execução
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    if mode == 'preview':
        os.makedirs('/home/claude/anti3d/prev', exist_ok=True)
        for t in [float(x) for x in sys.argv[2].split(',')]:
            S.frame_set(int(F(t)))
            S.render.filepath = '/home/claude/anti3d/prev/t%05.1f.png' % t
            bpy.ops.render.render(write_still=True)
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs('/home/claude/anti3d/frames', exist_ok=True)
        for f in range(a, b + 1):
            out = '/home/claude/anti3d/frames/%05d.png' % f
            if os.path.exists(out): continue
            S.frame_set(f); S.render.filepath = out + '.tmp.png'
            bpy.ops.render.render(write_still=True)
            os.rename(out + '.tmp.png', out)
