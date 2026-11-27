
# ============================================================ CHERNOBYL
import random
random.seed(7)
s1, s2, s3, s4, s5, s6, s7 = SC
NIGHT = hexc('16213a'); LAB = hexc('24222a'); PANELBG = hexc('1f2a26')

CONC = mat('conc', hexc('cfc8bb')); CONC2 = mat('conc2', hexc('a9a297'))
GROUND = mat('ground', hexc('2c3a30')); ROAD = mat('road', hexc('3a3d42'))
WIN = mat('win', hexc('ffd76a')); RED = mat('red', hexc('d23b2e')); WHITE = mat('white', hexc('f2f0ea'))
MOON = mat('moon', hexc('f6eec8'))
GRAPH = mat('graph', hexc('4a4a52')); STEEL = mat('steel', hexc('9aa3ad')); STEEL2 = mat('steel2', hexc('6d757e'))
ABS = mat('abs', hexc('1c1c1f')); TIP = mat('tip', hexc('9a9ca4'))
WATER = mat('water', hexc('3aa0e0')); WATER_C = mat('water_c', hexc('3aa0e0'))
GAUGE = mat('gauge', hexc('41c46f')); FRAME = mat('frame', hexc('121214'))
DESK = mat('desk', hexc('8fa39a')); DESK2 = mat('desk2', hexc('6f8479'))
BTN = mat('btn', hexc('e0281e')); YEL = mat('yel', hexc('ffd23f'))
GRAPH_C = mat('graph_c', hexc('55555e')); STEAM = mat('steam', hexc('eceef0'))
TXT = mat('txt', hexc('ffffff')); TXTY = mat('txty', hexc('ffd23f'))

# ------------------------------------------------ usina (x = 0)
plane = box((10, 10, -0.05), (260, 200, 0.1), GROUND, 'ground')
box((10, -16, 0.01), (120, 6, 0.04), ROAD, 'road')
reac = box((0, 0, 7), (16, 12, 14), CONC, 'reactor', bevel=0.1)
box((0, 0, 14.6), (14, 10, 1.2), CONC2, 'roof')
hall = box((24, 0, 5), (32, 10, 10), CONC2, 'hall', bevel=0.1)
box((24, 0, 10.4), (32, 9, 0.8), CONC, 'hallroof')
for z in (3, 6, 9, 12):
    for x in range(-6, 7, 2):
        box((x, -6.02, z), (1.1, 0.1, 0.9), WIN, 'w')
for z in (2.5, 6.5):
    for x in range(10, 40, 3):
        box((x, -5.02, z), (1.6, 0.1, 0.9), WIN, 'w')
for k in range(10):  # chaminé listrada
    cyl((-4, 7, 16 + k * 2.6 + 1.3), 1.5 - k * 0.05, 2.6, RED if k % 2 else WHITE, name='stack')
box((-4, 7, 8), (3.6, 3.6, 16), CONC2, 'stackbase')
cyl((-60, 120, 60), 5, 0.5, MOON, rot=(math.pi / 2, 0, 0), name='moon')
for x in (-20, -10, 40, 50):
    cyl((x, -13, 3), 0.15, 6, STEEL2, name='poste'); box((x, -13, 6.1), (0.8, 0.5, 0.3), WIN, 'lamp')
txt4 = text('4', (0, -6.1, 13.0), 2.2, RED, rot=(math.pi / 2, 0, 0), name='n4')

# ------------------------------------------------ núcleo em corte (x = CX)
CX = 200.0
cols = []
for i in range(9):
    for j in range(5):
        cols.append(box((CX - 3.6 + i * 0.9, 0.45 + j * 0.9, 2.0), (0.72, 0.72, 4.0), GRAPH, 'col'))
graph = join(cols, 'graphite'); graph.data.materials.clear(); graph.data.materials.append(GRAPH_C)
chans = []
CH = []
for i in range(1, 9):
    for j in range(5):
        x, y = CX - 4.05 + i * 0.9, j * 0.9
        CH.append((x, y))
        chans.append(cyl((x, y, 2.0), 0.14, 4.0, WATER_C, verts=16, name='ch'))
water = join(chans, 'channels')
box((CX, 2.0, -0.3), (9.6, 4.8, 0.6), STEEL2, 'base')
box((CX, 4.6, 2.5), (10.4, 0.4, 6.0), CONC2, 'backwall')
for sx in (-1, 1):
    box((CX + sx * 5.0, 2.2, 2.5), (0.4, 4.8, 6.0), CONC2, 'sidewall')
plate = box((CX, 2.0, 4.45), (9.4, 4.4, 0.5), STEEL, 'plate', bevel=0.05)
plabel = text('TAMPA · 1.000 t', (CX, -0.25, 4.45), 0.34, TXT, rot=(math.pi / 2, 0, 0), name='plabel')
plabel.parent = plate; plabel.location = (0, -2.23, 0)  # origem do plate = centro
# barras de controle: 20 (8 ficam, 12 saem)
RODPOS = [CH[k] for k in range(len(CH)) if CH[k][1] < 2.0]  # 3 fileiras da frente: 24 posições
random.shuffle(RODPOS); RODPOS = sorted(RODPOS[:20], key=lambda p: (p[1], p[0]))
rods = []
for (x, y) in RODPOS:
    a = cyl((x, y, 1.2 + 2.0), 0.17, 4.0, ABS, verts=16, name='abs')
    tp = cyl((x, y, 0.6), 0.17, 1.2, TIP, verts=16, name='tipc')
    r = join([a, tp], 'rod'); rods.append(r)   # comprimento 5.2, centro = base + 2.6
STAY = set(random.sample(range(20), 8))
def rod_z(bottom): return bottom + 2.6
# medidor de potência (horizontal, acima do núcleo)
box((CX, 5.0, 11.5), (8.6, 0.3, 1.2), FRAME, 'gframe')
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
gfill = bpy.context.object; gfill.name = 'gfill'
for v in gfill.data.vertices: v.co.x += 0.5
gfill.location = (CX - 4.1, 4.75, 11.5); gfill.scale = (8.2 * 0.55, 0.35, 0.85); gfill.data.materials.append(GAUGE)
text('POTÊNCIA', (CX, 4.9, 12.65), 0.6, TXT, rot=(math.pi / 2, 0, 0), name='glabel')
# destroços e vapor (escondidos até a explosão)
debris = []
for k in range(46):
    s = random.uniform(0.18, 0.55)
    d = box((CX + random.uniform(-3.5, 3.5), random.uniform(0.2, 3.5), 4.2), (s, s, s * 1.4), random.choice([GRAPH, CONC2, STEEL2]), 'deb')
    debris.append(d)
steam = []
for k in range(16):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(CX + random.uniform(-3.5, 3.5), random.uniform(0.5, 3.5), 4.6))
    o = bpy.context.object; o.data.materials.append(STEAM); bpy.ops.object.shade_smooth(); steam.append(o)

# ------------------------------------------------ painel (x = PX)
PX = 300.0
box((PX, 0.6, 0.45), (6, 1.6, 0.9), DESK2, 'deskbase')
pan = box((PX, 0.5, 1.15), (6, 1.4, 0.12), DESK, 'panel'); pan.rotation_euler = (math.radians(-28), 0, 0)
box((PX, 1.6, 2.2), (6, 0.2, 2.6), DESK, 'upright')
for i in range(14):
    for j in range(4):
        c = random.choice([hexc('ffd23f'), hexc('41c46f'), hexc('f2f0ea'), hexc('2d6fd6')])
        cyl((PX - 2.6 + i * 0.4, 1.48, 1.4 + j * 0.42), 0.08, 0.08, mat('l%d%d' % (i, j), c), rot=(math.pi / 2, 0, 0), verts=12, name='led')
for i in range(5):
    cyl((PX - 2.4 + i * 1.2, 1.48, 3.05), 0.32, 0.06, WHITE, rot=(math.pi / 2, 0, 0), name='dial')
    box((PX - 2.4 + i * 1.2 + 0.08, 1.44, 3.1), (0.04, 0.02, 0.26), ABS, 'needle').rotation_euler = (0, random.uniform(-0.9, 0.9), 0)
ring = cyl((PX, 0.45, 1.2), 0.46, 0.08, YEL, rot=(math.radians(62), 0, 0), name='ring')
button = cyl((PX, 0.43, 1.25), 0.34, 0.22, BTN, rot=(math.radians(62), 0, 0), name='az5')
lab5 = text('AZ-5', (PX, 1.47, 1.95), 0.32, TXT, rot=(math.pi / 2, 0, 0), name='az5lab')
for i in (-1, 1):
    cyl((PX + i * 1.5, 0.43, 1.25), 0.14, 0.12, mat('g%d' % i, hexc('41c46f')), rot=(math.radians(62), 0, 0), name='sb')

# ------------------------------------------------ close no canal (x = KX)
KX = 400.0
for sx in (-1, 1):
    box((KX + sx * 1.75, 0.0, 4.0), (2.3, 2.0, 8.0), GRAPH, 'kblock')
box((KX, 0.95, 4.0), (1.2, 0.1, 8.0), STEEL2, 'kback')
bpy.ops.mesh.primitive_cube_add(size=1, location=(KX, 0.2, 0.0))
kwater = bpy.context.object; kwater.name = 'kwater'
for v in kwater.data.vertices: v.co.z += 0.5
kwater.scale = (1.1, 1.2, 7.4); kwater.data.materials.append(WATER)
ka = cyl((KX, 0.0, 2.6 + 2.5), 0.46, 5.0, ABS, verts=32, name='kabs')
kt = cyl((KX, 0.0, 1.25), 0.46, 2.5, TIP, verts=32, name='ktip')
krod = join([ka, kt], 'krod')   # comprimento 7.6, centro = base + 3.8
K_TOP = 7.6
def krod_z(bottom): return bottom + 3.8
lab_b = text('BORO', (KX + 1.75, -1.05, 9.5), 0.55, TXT, rot=(math.pi / 2, 0, 0), name='lab_b')
lab_g = text('GRAFITE', (KX + 1.75, -1.05, 7.0), 0.5, TXTY, rot=(math.pi / 2, 0, 0), name='lab_g')
lab_w = text('ÁGUA', (KX - 1.75, -1.05, 3.5), 0.6, mat('txtb', hexc('7cc6ff')), rot=(math.pi / 2, 0, 0), name='lab_w')
