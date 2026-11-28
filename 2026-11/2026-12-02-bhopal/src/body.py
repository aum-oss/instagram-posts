
# ============================================================ BHOPAL
import random
random.seed(11)
s1, s2, s3, s4, s5, s6, s7, s8 = SC
def ease_io(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
NIGHT = hexc('141d33'); LAB = hexc('24222a')
GROUND = mat('ground', hexc('2b3326')); DIRT = mat('dirt', hexc('5a4e3c')); ROAD = mat('road', hexc('3a3d42'))
CONC = mat('conc', hexc('bdb6aa')); CONC2 = mat('conc2', hexc('8f897f')); STEEL = mat('steel', hexc('b8bec6')); STEEL2 = mat('steel2', hexc('6d757e'))
WIN = mat('win', hexc('ffd76a')); MOON = mat('moon', hexc('f6eec8')); REDL = mat('redl', hexc('5a1a16'))
GAS = mat('gas', hexc('d3dca2')); LIQ = mat('liq', hexc('d8c64e')); WATERM = mat('waterm', hexc('3aa0e0'))
THERM = mat('therm', hexc('41c46f')); FRAME = mat('frame', hexc('121214')); TXT = mat('txt', hexc('ffffff'))
XR = mat('xr', hexc('e0281e')); FLOOR = mat('floor', hexc('34313a')); BUB = mat('bub', hexc('fff6c8'))
HOUSE = [mat('h%d' % i, hexc(c)) for i, c in enumerate(['c9a27e', 'b98c6a', 'd8c3a5', '9fb3a8', 'c48f7a', 'a89a8a'])]

# ------------------------------------------------ cidade + fábrica (origem)
box((0, -20, -0.05), (300, 300, 0.1), GROUND, 'ground')
box((0, 20, 0.0), (64, 44, 0.08), DIRT, 'yard')
for (x, y, sx, sy) in ((0, -2, 64, 0.4), (0, 42, 64, 0.4), (-32, 20, 0.4, 44), (32, 20, 0.4, 44)):
    box((x, y, 0.9), (sx, sy, 1.8), CONC2, 'wall')
box((0, -6, 0.02), (300, 3, 0.04), ROAD, 'road')
box((-18, 12, 4), (16, 10, 8), CONC, 'bld1'); box((-18, 30, 3), (12, 12, 6), CONC, 'bld2')
box((20, 34, 5), (14, 8, 10), CONC2, 'bld3')
for x in range(-24, -11, 3):
    box((x, 6.9, 5.5), (1.2, 0.1, 0.8), WIN, 'fw')
box((4, 22, 1.2), (22, 9, 2.4), CONC2, 'mound')
for k, x in enumerate((-2, 4, 10)):
    cyl((x, 22, 2.8), 1.6, 9, STEEL, rot=(math.pi / 2, 0, 0), name='mictank')
cyl((14, 30, 15), 1.0, 30, STEEL2, name='scrubber')
cyl((22, 22, 17.5), 0.45, 35, STEEL2, name='flare')
for z in (6, 12, 18):
    tube([(-10, 16, z * 0 + 7), (14, 16, 7)], 0.35, STEEL2, 'rack')
tube([(-10, 18, 5), (4, 18, 5), (4, 22, 5)], 0.3, STEEL2, 'pipeA')
alarm = cyl((-18, 12, 8.6), 0.6, 1.2, REDL, name='alarm')
cyl((-80, 150, 70), 6, 0.5, MOON, rot=(math.pi / 2, 0, 0), name='moon')
# casas
groups = {i: [] for i in range(len(HOUSE))}
wins = []
def house(x, y):
    w = random.uniform(2.4, 3.6); d = random.uniform(2.4, 3.4); h = random.uniform(1.8, 3.0)
    i = random.randrange(len(HOUSE))
    groups[i].append(box((x, y, h / 2), (w, d, h), HOUSE[i], 'house'))
    if random.random() < 0.35: wins.append(box((x, y - d / 2 - 0.03, h * 0.55), (0.7, 0.06, 0.6), WIN, 'hw'))
for gx in range(-70, 71, 5):
    for gy in range(-75, -8, 5):
        if random.random() < 0.85: house(gx + random.uniform(-1, 1), gy + random.uniform(-1, 1))
for gx in range(38, 80, 5):
    for gy in range(-5, 50, 5):
        if random.random() < 0.8: house(gx + random.uniform(-1, 1), gy + random.uniform(-1, 1))
for i, objs in groups.items():
    if objs: join(objs, 'houses%d' % i)
if wins: join(wins, 'hwins')
# nuvem de gás (escondida até a cena 7)
cloud = []
for k in range(42):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(14 + random.uniform(-2, 2), 30 + random.uniform(-2, 2), 30))
    o = bpy.context.object; o.data.materials.append(GAS); bpy.ops.object.shade_smooth(); cloud.append(o)

# ------------------------------------------------ tanque em corte (x = TX)
TX = 200.0
box((TX, 2.5, -0.8), (16, 9, 1.6), CONC2, 'tbase')
cutter = box((TX, -10, 3.5), (30, 20, 30), FRAME, 'cutter'); cutter.hide_render = True; cutter.hide_viewport = True
import bmesh
def half_shell(r, L, m, name):
    o = cyl((TX, 2.0, 3.5), r, L, m, rot=(0, math.pi / 2, 0), verts=64, name=name)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.05], context='VERTS')
    bm.to_mesh(o.data); bm.free()
    sd = o.modifiers.new('sd', 'SOLIDIFY'); sd.thickness = 0.18
    return o
tank = half_shell(3.0, 12.0, STEEL, 'tank')
liq = cyl((TX, 2.0, 3.5), 2.78, 11.7, LIQ, rot=(0, math.pi / 2, 0), verts=64, name='liq')
cut2 = box((TX, 2.0, 3.5 + 1.0 + 5), (30, 20, 10), FRAME, 'cut2'); cut2.hide_render = True; cut2.hide_viewport = True
b3 = liq.modifiers.new('cut', 'BOOLEAN'); b3.object = cutter; b3.operation = 'DIFFERENCE'
b4 = liq.modifiers.new('cut2', 'BOOLEAN'); b4.object = cut2; b4.operation = 'DIFFERENCE'
text('TANQUE E610 · 42 t', (TX, -0.2, 7.6), 0.62, TXT, rot=(math.pi / 2, 0, 0), name='tlabel')
# cano de água
PIPE = [(TX - 13, 1.0, 9.5), (TX - 4.0, 1.0, 9.5), (TX - 4.0, 1.0, 6.4)]
tube(PIPE, 0.35, STEEL2, 'pipe')
wpipe = tube([(x, y - 0.05, z) for x, y, z in PIPE], 0.42, WATERM, 'wpipe')
wpipe.data.bevel_factor_end = 0.0
# válvula de alívio + respiro
cyl((TX + 3.5, 2.0, 7.0), 0.35, 1.4, STEEL2, name='vstem')
vcap = cyl((TX + 3.5, 2.0, 7.85), 0.55, 0.3, mat('vcap', hexc('e0a020')), name='vcap')
tube([(TX + 3.5, 2.0, 8.0), (TX + 3.5, 2.0, 13.0)], 0.3, STEEL2, 'vent')
# termômetro
THX = TX + 7.6
box((THX, 2.0, 4.0), (0.9, 0.5, 8.2), FRAME, 'thframe')
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
thfill = bpy.context.object; thfill.name = 'thfill'
for v in thfill.data.vertices: v.co.z += 0.5
thfill.location = (THX, 1.7, 0.0); thfill.scale = (0.6, 0.3, 0.8); thfill.data.materials.append(THERM)
text('°C', (THX, 1.7, 8.8), 0.7, TXT, rot=(math.pi / 2, 0, 0), name='thlabel')
bubbles = []
for k in range(26):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.16, location=(TX + random.uniform(-5, 5), -0.12, 1.2))
    o = bpy.context.object; o.data.materials.append(BUB); bubbles.append(o)
plume = []
for k in range(18):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(TX + 3.5, 2.0, 13.0))
    o = bpy.context.object; o.data.materials.append(GAS); bpy.ops.object.shade_smooth(); plume.append(o)

# ------------------------------------------------ as 3 proteções (x = PX)
PX = 300.0
box((PX, 3, -0.1), (30, 20, 0.2), FLOOR, 'pfloor')
fr = box((PX - 5, 1, 1.2), (2.8, 2.2, 2.4), STEEL, 'fridge')
for k in range(5): box((PX - 5, -0.12, 0.5 + k * 0.4), (2.4, 0.06, 0.12), STEEL2, 'grille')
cyl((PX, 1, 3.5), 0.8, 7, STEEL2, name='vgs')
cyl((PX + 5, 1, 4.5), 0.35, 9, STEEL2, name='flare2')
cyl((PX + 5, 1, 9.2), 0.6, 0.4, STEEL, name='burner')
labs = [text('REFRIGERAÇÃO', (PX - 5, -1.6, 8.0), 0.58, TXT, rot=(math.pi / 2, 0, 0), name='l1'),
        text('LAVADOR', (PX, -1.6, 9.2), 0.58, TXT, rot=(math.pi / 2, 0, 0), name='l2'),
        text('DE GÁS', (PX, -1.6, 8.55), 0.58, TXT, rot=(math.pi / 2, 0, 0), name='l2b'),
        text('CHAMA', (PX + 5, -1.6, 11.0), 0.58, TXT, rot=(math.pi / 2, 0, 0), name='l3')]
xs = []
for k, (x, z) in enumerate(((PX - 5, 1.4), (PX, 3.5), (PX + 5, 4.5))):
    a = box((x, -1.9, z), (3.2, 0.3, 0.5), XR, 'xa'); a.rotation_euler = (0, math.radians(45), 0)
    b = box((x, -1.9, z), (3.2, 0.3, 0.5), XR, 'xb'); b.rotation_euler = (0, math.radians(-45), 0)
    xo = join([a, b], 'X%d' % k); xs.append(xo)
