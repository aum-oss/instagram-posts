"""Cena 3D do kit 72h (Blender/bpy, motor Workbench). Uso:
python3 scene.py preview t1,t2,...   -> PNGs de quadros soltos em prev/
python3 scene.py render START END    -> frames em frames/ (índices de quadro)
"""
import bpy, math, json, sys, os
from mathutils import Vector

FPS = 30
T = json.load(open('/home/claude/kit3d/timing.json'))
WD = json.load(open('/home/claude/kit3d/words.json'))
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
SKY = hexc('bfe3f5'); SKY_STORM = hexc('3a4250')
GRASS = mat('grass', hexc('7cc46a')); GRASS2 = mat('grass2', hexc('6ab35a'))
FLOORW = mat('floorw', hexc('d9a86c')); FLOORW2 = mat('floorw2', hexc('c9965a'))
WALL = mat('wall', hexc('f3ead8')); WALL2 = mat('wall2', hexc('e7d9bf'))
TRIM = mat('trim', hexc('8a5a34')); DARK = mat('dark', hexc('2b2d31'))
RED = mat('red', hexc('e04a3a')); ORANGE = mat('orange', hexc('f08a2a'))
BLUE = mat('blue', hexc('3d8fe0')); WATER = mat('water', hexc('5ab4ec'))
YEL = mat('yel', hexc('ffd23f')); WHITE = mat('white', hexc('fafafa'))
GREEN = mat('green', hexc('41c46f')); METAL = mat('metal', hexc('9aa0a8'))
TREE = mat('tree', hexc('3f9e57')); TRUNK = mat('trunk', hexc('7a4a2a'))
WIN_ON = hexc('ffe08a'); WIN_OFF = hexc('2a3340')
win_m = mat('window', WIN_ON, unique=True)
lamp_m = mat('lampbulb', WIN_ON, unique=True)
w.color = SKY

# ------------------------------------------------------------ chão e casa (diorama)
for i in range(-8, 9):
    box((i * 1.0, 2, -0.25), (1.0, 20, 0.5), GRASS if i % 2 else GRASS2, 'grass')
box((0, 0, 0.05), (6.4, 6.4, 0.2), FLOORW, 'floor', 0.03)
for i in range(-3, 3):
    box((i + 0.5, 0, 0.16), (0.98, 6.2, 0.03), FLOORW2 if i % 2 else FLOORW, 'plank')
box((0, 3.1, 2.1), (6.4, 0.25, 4.0), WALL, 'backwall', 0.02)
box((-3.1, 0, 2.1), (0.25, 6.4, 4.0), WALL2, 'leftwall', 0.02)
box((0, 3.1, 4.15), (6.6, 0.35, 0.15), TRIM, 'trimb')
box((-3.1, 0, 4.15), (0.35, 6.6, 0.15), TRIM, 'triml')
# janela na parede do fundo
box((1.2, 2.96, 2.6), (1.8, 0.08, 1.4), TRIM, 'winframe')
box((1.2, 2.92, 2.6), (1.6, 0.05, 1.2), win_m, 'winglass')
box((1.2, 2.88, 2.6), (0.06, 0.04, 1.2), TRIM, 'winbar')
box((1.2, 2.88, 2.6), (1.6, 0.04, 0.06), TRIM, 'winbar2')
# porta na parede da esquerda
box((-2.96, -1.2, 1.25), (0.08, 1.2, 2.3), TRIM, 'door')
cyl((-2.9, -0.75, 1.25), 0.07, 0.08, YEL, rot=(0, math.pi / 2, 0), name='knob')
# luminária de teto
cyl((0.0, 0.6, 3.95), 0.03, 0.6, DARK, name='cord')
cyl((0.0, 0.6, 3.55), 0.45, 0.35, mat('shade', hexc('f2c14e')), name='shade', verts=24)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.0, 0.6, 3.35)); b = bpy.context.object
b.data.materials.append(lamp_m)
# estante com latas e garrafas
box((-2.6, 1.6, 1.4), (0.6, 2.2, 0.08), TRIM, 'shelf1')
box((-2.6, 1.6, 2.3), (0.6, 2.2, 0.08), TRIM, 'shelf2')
for j in range(5):
    cyl((-2.6, 0.75 + j * 0.42, 1.62), 0.15, 0.36, [RED, YEL, GREEN, RED, BLUE][j], name='can')
for j in range(4):
    cyl((-2.6, 0.85 + j * 0.5, 2.62), 0.13, 0.55, WATER, name='bottle')
# mesa e sofá
box((1.6, 0.4, 0.95), (1.6, 1.0, 0.1), TRIM, 'tabletop', 0.02)
for dx in (-0.7, 0.7):
    for dy in (-0.4, 0.4):
        box((1.6 + dx, 0.4 + dy, 0.5), (0.08, 0.08, 0.8), TRIM, 'tleg')
box((1.6, 2.3, 0.6), (2.4, 0.8, 0.6), BLUE, 'sofa', 0.08)
box((1.6, 2.65, 1.1), (2.4, 0.2, 0.8), BLUE, 'sofaback', 0.08)
# árvores lá fora
for (x, y) in ((5.0, 4.0), (-5.2, 4.6), (6.0, -1.5), (-6.0, -2.0)):
    cyl((x, y, 0.8), 0.18, 1.6, TRUNK, name='trunk')
    bpy.ops.mesh.primitive_cone_add(radius1=1.0, depth=2.4, location=(x, y, 2.6), vertices=8)
    o = bpy.context.object; o.data.materials.append(TREE)

# ------------------------------------------------------------ mochila (aparece na cena 6)
pack_parts = []
pack_parts.append(box((0, 0, 0.8), (1.5, 0.9, 1.3), ORANGE, 'packbody', 0.2))
pack_parts.append(box((0, -0.5, 0.6), (1.0, 0.2, 0.7), RED, 'pocket', 0.1))
pack_parts.append(box((0, 0.1, 1.48), (1.4, 0.8, 0.12), RED, 'flap', 0.05))
for dx in (-0.45, 0.45):
    pack_parts.append(box((dx, 0.5, 0.8), (0.14, 0.08, 1.2), DARK, 'strap'))
pack = join(pack_parts, 'pack')
pack.location = (0, 0, 0.8)

# ------------------------------------------------------------ itens do kit
def item(kind):
    parts = []
    if kind == 'agua':
        parts.append(cyl((0, 0, 0), 0.16, 0.6, WATER, name='b'))
        parts.append(cyl((0, 0, 0.36), 0.07, 0.12, BLUE, name='cap'))
    elif kind == 'comida':
        parts.append(cyl((0, 0, 0), 0.2, 0.3, RED, name='can'))
        parts.append(cyl((0, 0, 0.16), 0.2, 0.02, METAL, name='lid'))
    elif kind == 'lanterna':
        parts.append(cyl((0, 0, 0), 0.08, 0.55, DARK, name='body', rot=(math.pi / 2, 0, 0)))
        parts.append(cyl((0, -0.32, 0), 0.13, 0.14, YEL, name='head', rot=(math.pi / 2, 0, 0)))
    elif kind == 'radio':
        parts.append(box((0, 0, 0), (0.55, 0.22, 0.36), GREEN, 'rbody', 0.04))
        parts.append(cyl((-0.1, -0.12, 0), 0.11, 0.03, DARK, name='spk', rot=(math.pi / 2, 0, 0)))
        parts.append(cyl((0.2, 0, 0.4), 0.015, 0.5, METAL, name='ant', rot=(0, 0.4, 0)))
    elif kind == 'carregador':
        parts.append(box((0, 0, 0), (0.3, 0.12, 0.5), DARK, 'pb', 0.04))
        parts.append(box((0, -0.065, 0.05), (0.12, 0.02, 0.08), GREEN, 'led'))
    elif kind == 'remedios':
        parts.append(cyl((0, 0, 0), 0.15, 0.36, WHITE, name='pill'))
        parts.append(cyl((0, 0, 0.22), 0.16, 0.08, RED, name='pcap'))
        parts.append(box((0, -0.155, 0), (0.14, 0.01, 0.04), RED, 'cross1'))
        parts.append(box((0, -0.155, 0), (0.04, 0.01, 0.14), RED, 'cross2'))
    elif kind == 'higiene':
        parts.append(box((0, 0, 0), (0.34, 0.22, 0.14), mat('soap', hexc('f59ac0')), 'soap', 0.05))
        parts.append(box((0.05, 0, 0.12), (0.5, 0.05, 0.04), BLUE, 'brush'))
    o = join(parts, 'item_' + kind)
    return o

KIT = [('agua', 'água'), ('comida', 'comida'), ('lanterna', 'lanterna'), ('radio', 'rádio'),
       ('carregador', 'carregador'), ('remedios', 'remédios'), ('higiene', 'higiene')]
items = []
for k, word in KIT:
    o = item(k); items.append((o, word))

# ------------------------------------------------------------ chuva e enchente
drops = []
import random
random.seed(4)
for i in range(160):
    x = random.uniform(-7, 7); y = random.uniform(-6, 8); z = random.uniform(0, 8)
    drops.append(box((x, y, z), (0.03, 0.03, 0.45), mat('rain', hexc('a9d6f5')), 'drop'))
rain = join(drops, 'rain')
flood = box((0, 1, -0.4), (30, 30, 0.1), WATER, 'flood')

# ------------------------------------------------------------ animação: helpers
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
def keycol(m, pts):
    for t, c in pts:
        m.diffuse_color = (*c, 1); m.keyframe_insert('diffuse_color', frame=F(t))
def keyworld(pts):
    for t, c in pts:
        w.color = c; w.keyframe_insert('color', frame=F(t))
    set_interp(w, 'LINEAR')

# céu: normal -> tempestade (cena 3) -> clareia (cena 4) -> apagão (cena 5) -> normal
t_temp = wt(3, 'temporal'); t_ok = wt(4, 'explicou:')
t_ench = wt(5, 'enchente'); t_apag = wt(5, 'apagão'); t_casa = wt(5, 'Nesses')
keyworld([(0, SKY), (t_temp - 0.6, SKY), (t_temp + 0.4, SKY_STORM),
          (wt(3, 'catástrofe') - 0.05, SKY_STORM), (wt(3, 'catástrofe'), (0.95, 0.95, 1.0)),
          (wt(3, 'catástrofe') + 0.12, SKY_STORM),
          (t_ok - 0.2, SKY_STORM), (t_ok + 1.0, SKY),
          (t_ench - 0.3, SKY), (t_ench + 0.5, SKY_STORM), (t_casa + 0.8, SKY_STORM), (s6 + 0.2, SKY)])
# luzes da casa: apagam na tempestade e no apagão
for m in (win_m, lamp_m):
    keycol(m, [(0, WIN_ON), (t_temp + 1.2, WIN_ON), (t_temp + 1.25, WIN_OFF), (t_ok + 0.6, WIN_OFF), (t_ok + 0.65, WIN_ON),
               (t_apag - 0.05, WIN_ON), (t_apag, WIN_OFF), (s6 + 0.3, WIN_OFF), (s6 + 0.35, WIN_ON)])
    set_interp(m, 'CONSTANT')
# chuva: aparece na tempestade e na enchente, cai em loop
rain.location = (0, 0, 30); rain.keyframe_insert('location', frame=1)
def rain_on(a, b):
    f0, f1 = int(F(a)), int(F(b))
    rain.location = (0, 0, 30); rain.keyframe_insert('location', frame=f0 - 1)
    for f in range(f0, f1 + 1):
        ph = ((f - f0) % 12) / 12.0
        rain.location = (0, 0, 2.0 - ph * 4.0); rain.keyframe_insert('location', frame=f)
    rain.location = (0, 0, 30); rain.keyframe_insert('location', frame=f1 + 1)
rain_on(t_temp - 0.3, t_ok + 0.8)
rain_on(t_ench - 0.3, t_casa + 0.6)
set_interp(rain, 'CONSTANT')
# enchente sobe e desce
for t, z in ((0, -0.4), (t_ench - 0.1, -0.4), (t_ench + 1.0, 0.45), (t_casa + 0.6, 0.45), (s6 + 0.2, -0.4)):
    flood.location.z = z; flood.keyframe_insert('location', index=2, frame=F(t))
# mochila: escondida até a cena 6
pack.scale = (0, 0, 0); pack.keyframe_insert('scale', frame=F(s6 - 0.01))
pack.scale = (1.15, 1.15, 1.15); pack.keyframe_insert('scale', frame=F(s6 + 0.35))
pack.scale = (1, 1, 1); pack.keyframe_insert('scale', frame=F(s6 + 0.55))
# itens caem na mochila em cada palavra
TOP = Vector((0, 0, 1.65))
for i, (o, word) in enumerate(items):
    t = wt(6, word if word != 'rádio' else 'rádio')
    start = Vector((-1.2 + 0.4 * (i % 7), -1.0, 3.6))
    o.scale = (0, 0, 0); o.location = start; o.keyframe_insert('scale', frame=1); o.keyframe_insert('location', frame=1)
    o.keyframe_insert('scale', frame=F(t - 0.12))
    o.keyframe_insert('location', frame=F(t - 0.12))
    o.scale = (1.6, 1.6, 1.6); o.keyframe_insert('scale', frame=F(t + 0.05))
    o.location = start + Vector((0, 0, 0.25)); o.keyframe_insert('location', frame=F(t + 0.3))
    o.rotation_euler = (0, 0, 0); o.keyframe_insert('rotation_euler', frame=F(t + 0.3))
    o.location = TOP; o.keyframe_insert('location', frame=F(t + 0.75))
    o.rotation_euler = (0.6, 0.3, 1.5); o.keyframe_insert('rotation_euler', frame=F(t + 0.75))
    o.scale = (1.2, 1.2, 1.2); o.keyframe_insert('scale', frame=F(t + 0.75))
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=F(t + 0.95))
    # mochila "engole" o item
    pack.scale = (1, 1, 1); pack.keyframe_insert('scale', frame=F(t + 0.8))
    pack.scale = (1.08, 1.08, 0.94); pack.keyframe_insert('scale', frame=F(t + 0.95))
    pack.scale = (1, 1, 1); pack.keyframe_insert('scale', frame=F(t + 1.15))
# no fim, a mochila vai pra perto da porta
pack.location = (0, 0, 0.8); pack.keyframe_insert('location', frame=F(s7 + 0.3))
pack.location = (-2.2, -1.2, 0.8); pack.keyframe_insert('location', frame=F(s7 + 1.6))

# ------------------------------------------------------------ câmera
bpy.ops.object.camera_add(); cam = bpy.context.object; S.camera = cam
cam.data.lens = 30; cam.data.sensor_fit = 'VERTICAL'
bpy.ops.object.empty_add(); tgt = bpy.context.object
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
SHOTS = [
    (0.0, (7.5, -11.0, 7.5), (0, 0.8, 1.6), 30),
    (s2, (5.5, -8.5, 6.0), (0, 0.8, 1.8), 30),
    (s3 - 0.5, (-4.5, -9.0, 5.5), (0, 0.8, 1.8), 30),
    (s3 + 3.0, (3.0, -12.5, 4.5), (0, 1.0, 2.2), 28),
    (s4 + 3.5, (6.0, -9.5, 6.5), (0, 0.8, 1.6), 30),
    (s5 + 4.0, (0.0, -12.0, 6.0), (0, 0.5, 1.4), 28),
    (s6 - 0.3, (2.5, -6.0, 4.0), (0, 0, 1.3), 30),
    (s6 + 6.0, (-2.0, -5.5, 3.8), (0, 0, 1.3), 30),
    (s7 + 0.5, (1.0, -6.0, 3.8), (-0.5, 0, 1.2), 30),
    (TOTAL, (8.0, -13.0, 7.5), (0, 0.5, 1.5), 30),
]
for t, p, g, lens in SHOTS:
    cam.location = p; cam.keyframe_insert('location', frame=F(t))
    tgt.location = g; tgt.keyframe_insert('location', frame=F(t))
    cam.data.lens = lens; cam.data.keyframe_insert('lens', frame=F(t))
for o in (cam, tgt, cam.data):
    for fc in fcurves(o):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'

# ------------------------------------------------------------ execução
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    if mode == 'preview':
        os.makedirs('/home/claude/kit3d/prev', exist_ok=True)
        for t in [float(x) for x in sys.argv[2].split(',')]:
            S.frame_set(int(F(t)))
            S.render.filepath = '/home/claude/kit3d/prev/t%05.1f.png' % t
            bpy.ops.render.render(write_still=True)
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs('/home/claude/kit3d/frames', exist_ok=True)
        for f in range(a, b + 1):
            out = '/home/claude/kit3d/frames/%05d.png' % f
            if os.path.exists(out): continue
            S.frame_set(f); S.render.filepath = out + '.tmp.png'
            bpy.ops.render.render(write_still=True)
            os.rename(out + '.tmp.png', out)
