"""Monta o vídeo final: frames 3D + legenda palavra a palavra + selo + logo + chips + narração.
Uso: python3 comp.py [out.mp4] [--preview t1,t2,...]"""
import json, sys, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
D = '/home/claude/anti3d'
T = json.load(open(f'{D}/timing.json')); WD = json.load(open(f'{D}/words.json'))
SC = [s for s, d in T['scenes']]; TOTAL = T['total']; N = int(np.ceil(TOTAL * FPS))
INTER = '/usr/share/fonts/opentype/inter/InterDisplay-%s.otf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
if not os.path.exists(MONO): MONO = INTER % 'Bold'
_fc = {}
def f(w, s, path=None):
    k = (w, s, path)
    if k not in _fc: _fc[k] = ImageFont.truetype(path or INTER % w, s)
    return _fc[k]
LOGO = Image.open('/home/claude/instagram-posts/tools/logo_nomad.png').convert('RGBA')
LOGO = LOGO.resize((int(LOGO.width * 120 / LOGO.height), 120), Image.LANCZOS)
YEL = (255, 210, 63); RED = (226, 76, 58)

def wtime(scene, word, k=0):
    return [s for w, s, e in WD[scene - 1] if w.strip('.,').lower() == word.lower()][k]

# grupos de legenda: 1–3 palavras, quebra em pontuação
GROUPS = []
for sc in WD:
    cur = []
    for item in sc:
        cur.append(item)
        txt = ' '.join(x[0] for x in cur)
        if len(cur) >= 3 or item[0][-1] in '.,!?' or len(txt) > 16:
            GROUPS.append(cur); cur = []
    if cur: GROUPS.append(cur)

def rr(d, box, r, fill): d.rounded_rectangle(box, r, fill=fill)

def caption(im, t):
    g = None
    for i, gr in enumerate(GROUPS):
        end = GROUPS[i + 1][0][1] if i + 1 < len(GROUPS) and GROUPS[i + 1][0][1] - gr[-1][2] < 0.6 else gr[-1][2] + 0.25
        if gr[0][1] - 0.02 <= t < end: g = gr; break
    if not g: return
    fnt = f('Black', 112)
    words = [w.upper() if False else w for w, _, _ in g]
    sp = fnt.getlength(' ')
    widths = [fnt.getlength(w) for w in words]
    tw = sum(widths) + sp * (len(words) - 1)
    if tw > W - 120:
        fnt = f('Black', int(112 * (W - 120) / tw)); widths = [fnt.getlength(w) for w in words]; sp = fnt.getlength(' ')
        tw = sum(widths) + sp * (len(words) - 1)
    x = (W - tw) / 2; y = 1300
    d = ImageDraw.Draw(im)
    pop = min(1, (t - g[0][1]) / 0.08)
    for (w, a, b), ww in zip(g, widths):
        col = YEL if a <= t < b + 0.05 else (255, 255, 255)
        d.text((x, y), w, font=fnt, fill=col, stroke_width=9, stroke_fill=(0, 0, 0), anchor='ls')
        x += ww + sp

def chip(im, text, y, bg, fg=(255, 255, 255), size=96, alpha=1.0):
    fnt = f('Black', size); tw = fnt.getlength(text)
    L = Image.new('RGBA', (int(tw) + 90, size + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rr(d, (0, 0, L.width - 1, L.height - 1), 28, bg + (int(235 * alpha),))
    d.text((45, 30), text, font=fnt, fill=fg + (int(255 * alpha),), anchor='lt')
    im.alpha_composite(L, ((W - L.width) // 2, y))

def tag(im):
    fnt = f('Black', 44); txt = 'RAIO-X · ANTICÍTERA'; tw = fnt.getlength(txt)
    d = ImageDraw.Draw(im)
    rr(d, (70, 150, 70 + tw + 60, 150 + 84), 18, RED + (255,))
    d.text((100, 192), txt, font=fnt, fill=(255, 255, 255), anchor='lm')
    im.alpha_composite(LOGO, (W - LOGO.width - 60, 140))

def terminal(im, t):
    """cartão de terminal no início (já visível no 1º quadro)."""
    if t > SC[1] + 0.6: return
    a = 1.0 if t < SC[1] + 0.2 else (SC[1] + 0.6 - t) / 0.4
    L = Image.new('RGBA', (W - 120, 210), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rr(d, (0, 0, L.width - 1, L.height - 1), 26, (22, 22, 26, int(235 * a)))
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse((34 + i * 40, 30, 58 + i * 40, 54), fill=c + (int(255 * a),))
    d.text((170, 42), 'nomad · ~/curiosidades', font=f('Medium', 34), fill=(150, 150, 160, int(255 * a)), anchor='lm')
    full = 'eclipses sem eletricidade?'
    d.text((34, 140), '>', font=f('Bold', 56, MONO), fill=(255, 120, 80, int(255 * a)), anchor='lm')
    d.text((84, 140), full, font=f('Bold', 56, MONO), fill=(240, 240, 240, int(255 * a)), anchor='lm')
    if int(t * 2) % 2 == 0:
        x = 84 + f('Bold', 56, MONO).getlength(full) + 8
        d.rectangle((x, 110, x + 26, 170), fill=(255, 210, 63, int(255 * a)))
    im.alpha_composite(L, (60, 270))

def specials(im, t):
    ev = [
        (wtime(2, '1901') - 0.1, SC[2] - 0.1, 'ANTICÍTERA · 1901', (20, 60, 80)),
        (wtime(3, '30') - 0.1, SC[3] + 0.2, '+30 ENGRENAGENS', (150, 100, 30)),
        (wtime(5, '235') - 0.1, wtime(5, 'engrenagens') - 0.1, '235 MESES = 19 ANOS', (20, 20, 24)),
        (wtime(5, 'eclipses') - 0.1, wtime(5, 'Olímpicos') - 0.1, 'ECLIPSES', (20, 20, 24)),
        (wtime(5, 'Olímpicos') - 0.1, SC[5] + 0.2, 'JOGOS OLÍMPICOS', (30, 100, 60)),
        (wtime(6, 'rápido') - 0.1, SC[6] + 0.2, 'LUA RÁPIDA · LUA LENTA', (20, 20, 24)),
        (wtime(7, 'Nada') - 0.1, TOTAL + 1, '1.000 ANOS À FRENTE', (226, 76, 58)),
    ]
    for a, b, txt, bg in ev:
        if a <= t < b:
            al = min(1, (t - a) / 0.15, (b - t) / 0.15)
            size = 64 if len(txt) > 16 else 96
            chip(im, txt, 1010 + int((1 - al) * 30), bg, size=size, alpha=al)

def frame(i):
    t = (i - 1) / FPS
    p = f'{D}/frames/{i:05d}.png'
    im = Image.open(p).convert('RGBA')
    # leve vinheta para leitura da legenda
    tag(im); terminal(im, t); specials(im, t); caption(im, t)
    return im.convert('RGB')

def audio(out):
    sr = 24000; n = int(TOTAL * sr) + sr
    a = np.zeros(n, np.float32)
    for k, (s, d) in enumerate(T['scenes']):
        w = wave.open(f'{D}/narr/n{k + 1}.wav'); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
        i0 = int((s + 0.25) * sr); a[i0:i0 + len(v)] += v
    a = np.clip(a, -32767, 32767).astype(np.int16)
    with wave.open(out, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.tobytes())

if __name__ == '__main__':
    if '--preview' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--preview') + 1].split(',')]
        for t in ts:
            frame(int(t * FPS) + 1).save(f'/tmp/c_{t}.jpg', quality=90)
        sys.exit()
    out = sys.argv[1]
    audio(f'{D}/voice.wav')
    tmp = out[:-4] + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', f'{D}/voice.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-af', 'loudnorm=I=-14:TP=-1.5', '-shortest',
                          '-movflags', '+faststart', tmp], stdin=subprocess.PIPE)
    for i in range(1, N + 1):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.rename(tmp, out); print('ok', out)
