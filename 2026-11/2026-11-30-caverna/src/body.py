
# ============================================================ CAVERNA THAM LUANG
import random, bmesh
random.seed(5)
s1, s2, s3, s4, s5, s6, s7, s8 = SC
def ease_io(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
NIGHT = hexc('121a2e'); DEEP = hexc('0d2238')
MOUNT = mat('mount', hexc('3d5a3a')); ROCK = mat('rock', hexc('6b5a48')); ROCK2 = mat('rock2', hexc('4a3e33'))
GROUND = mat('ground', hexc('2f4a2c')); TUN = mat('tun', hexc('1b1512')); WATER = mat('water', hexc('2f8fd8'))
SUMP = [mat('sump%d' % i, hexc('2f8fd8')) for i in range(3)]
KID = mat('kid', hexc('ffd23f')); DIVER = mat('diver', hexc('5fe0ff')); SAMAN = mat('saman', hexc('5fe0ff'))
TANK = mat('tankc', hexc('c9ccd2')); MOON = mat('moon', hexc('f6eec8')); RAIN = mat('rain', hexc('8fb8e8'))
SUIT = mat('suit', hexc('1d1d22')); KSUIT = mat('ksuit', hexc('3a4a6a')); YEL = mat('yel', hexc('ffd23f'))
MASK = mat('mask', hexc('7fe6ff')); PLANK = mat('plank', hexc('e8762c')); BUB = mat('bub', hexc('cfefff'))
WBACK = mat('wback', hexc('1d5f8f')); ROPE = mat('rope', hexc('f2f0ea'))

# ------------------------------------------------ montanha em corte
OUT = [(-34, 0), (-24, 0), (-20, 4), (-15, 10), (-8, 15), (-2, 21), (3, 18), (8, 20), (14, 14), (20, 10), (26, 4), (34, 0)]
me = bpy.data.meshes.new('mount'); bm = bmesh.new()
vs = [bm.verts.new((x, 0, z)) for x, z in OUT]
f = bm.faces.new(vs)
r = bmesh.ops.extrude_face_region(bm, geom=[f])
for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.y += 10
bm.to_mesh(me); bm.free()
mo = bpy.data.objects.new('mount', me); S.collection.objects.link(mo); me.materials.append(MOUNT)
for p in me.polygons: p.use_smooth = False
box((0, 5, -0.1), (300, 120, 0.2), GROUND, 'ground')
cyl((-40, 120, 55), 5, 0.5, MOON, rot=(math.pi / 2, 0, 0), name='moon')
for k in range(60):
    cyl((random.uniform(-120, 120), 110, random.uniform(25, 110)), 0.25, 0.2, MOON, rot=(math.pi / 2, 0, 0), verts=8, name='star')

PATH = [(-23, 0.9), (-18, 1.8), (-14, 1.1), (-10, 2.6), (-6, 1.5), (-2, 3.0), (2, 2.0), (6, 3.4), (10, 2.5), (14, 3.4)]
L = [0.0]
for (a, b), (c, d) in zip(PATH, PATH[1:]): L.append(L[-1] + math.hypot(c - a, d - b))
def at(u):
    s = max(0.0, min(1.0, u)) * L[-1]
    for i in range(len(PATH) - 1):
        if s <= L[i + 1] or i == len(PATH) - 2:
            k = (s - L[i]) / (L[i + 1] - L[i]); (a, b), (c, d) = PATH[i], PATH[i + 1]
            return (a + (c - a) * k, b + (d - b) * k)
def sub(u0, u1, n=14): return [at(u0 + (u1 - u0) * i / n) for i in range(n + 1)]
tube([(x, -0.25, z) for x, z in PATH], 0.75, TUN, 'tunnel')
box((15.6, -0.5, 3.0), (2.4, 1.0, 0.6), ROCK, 'ledge')
wfill = tube([(x, -0.45, z) for x, z in sub(0.0, 0.7, 40)], 0.62, WATER, 'wfill'); wfill.data.bevel_factor_end = 0.0
SUMPS = [(0.06, 0.22), (0.34, 0.5), (0.58, 0.7)]
sumps = [tube([(x, -0.65, z) for x, z in sub(a, b)], 0.66, SUMP[i], 'sump') for i, (a, b) in enumerate(SUMPS)]
for s_ in sumps: s_.scale = (1, 1, 1)
kids = []
for k in range(13):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.32 if k < 12 else 0.38, location=(-26, -1.1, 0.6))
    o = bpy.context.object; o.data.materials.append(KID); kids.append(o)
divers = []
for k in range(2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.36, location=(-26, -1.2, 0.6))
    o = bpy.context.object; o.data.materials.append(DIVER); divers.append(o)
U_SAMAN = 0.45
sx, sz = at(U_SAMAN)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.36, location=(sx, -1.2, sz))
saman = bpy.context.object; saman.data.materials.append(SAMAN)
cyls = []
for u in (0.25, 0.37, 0.52, 0.62, 0.8):
    x, z = at(u); c_ = cyl((x, -1.05, z + 0.05), 0.16, 0.7, TANK, rot=(0, math.radians(80), 0), verts=12, name='cylo'); cyls.append(c_)
drops = []
for k in range(45):
    d = box((random.uniform(-30, 30), -3, 30), (0.06, 0.06, 1.6), RAIN, 'drop'); drops.append(d)

# ------------------------------------------------ close: travessia debaixo d'água (x = KX)
KX = 300.0
box((KX, 2.5, 2.5), (60, 0.4, 12), WBACK, 'wback')
box((KX, 0.5, 6.3), (60, 5, 2.6), ROCK2, 'ceil')
box((KX, 0.5, -1.4), (60, 5, 2.6), ROCK2, 'floor')
for k in range(14):
    x = KX - 26 + k * 4 + random.uniform(-1, 1)
    box((x, -0.6, 4.9 + random.uniform(-0.2, 0.3)), (random.uniform(1, 2.5), 2.2, random.uniform(0.6, 1.4)), ROCK, 'stal')
    box((x + 2, -0.6, 0.0 + random.uniform(-0.2, 0.2)), (random.uniform(1, 2.5), 2.2, random.uniform(0.5, 1.0)), ROCK, 'stag')
rope = tube([(KX - 23, -0.3, 2.6), (KX + 23, -0.3, 2.9)], 0.04, ROPE, 'guideline')
# mergulhador (deitado, nadando para +x)
dparts = [cyl((0, 0, 0), 0.34, 1.7, SUIT, rot=(0, math.pi / 2, 0), name='dbody')]
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(1.05, 0, 0.05)); h = bpy.context.object; h.data.materials.append(SUIT); dparts.append(h)
dparts.append(cyl((0.1, 0, 0.42), 0.2, 1.1, YEL, rot=(0, math.pi / 2, 0), name='dtank'))
dparts.append(box((-1.25, 0, 0), (0.7, 0.5, 0.06), SUIT, 'fin'))
dparts.append(cyl((1.33, -0.05, 0.15), 0.08, 0.12, YEL, rot=(0, math.pi / 2, 0), name='lamp'))
diver = join(dparts, 'diver_fig')
# menino na maca, sedado
kparts = [box((0, 0, -0.18), (1.6, 0.6, 0.08), PLANK, 'plank'), cyl((0, 0, 0.05), 0.24, 1.2, KSUIT, rot=(0, math.pi / 2, 0), name='kbody')]
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0.78, 0, 0.08)); hk = bpy.context.object; hk.data.materials.append(KSUIT); kparts.append(hk)
kid_fig = join(kparts, 'kid_fig')
mask = cyl((0, 0, 0), 0.2, 0.08, MASK, rot=(math.pi / 2, 0, 0), name='mask')
link = cyl((0, 0, 0), 0.03, 1.0, ROPE, rot=(0, math.pi / 2, 0), name='link')
kbub = []
for k in range(10):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.09, location=(KX, -0.3, 3))
    o = bpy.context.object; o.data.materials.append(BUB); kbub.append(o)
