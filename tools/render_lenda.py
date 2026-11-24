"""Layout "LENDAS" (editorial / cinema) para o @futestrelas2026.

Uso: python3 tools/render_lenda.py <post.json> <pasta_saida>

Visual de revista + transmissão noturna: gramado e estádio gerados por código
(sem foto de pessoas reais), tipografia Inter Display + Cardo itálico,
paleta preto / marfim / dourado + uma cor de clube (accent).
Cenas aceitas em "scenes" (lista de dicts com "type"):
  hook     {"small", "big", "slam"}
  number   {"chapter", "date", "number", "lines": [...], "note"}
  match    {"chapter", "date", "score": [casa, gols, gols, fora], "title", "chips": [...]}
  passes   {"chapter", "date", "title", "sub", "n": 6}
  stats    {"chapter", "date", "stats": [[valor, rotulo], ...], "note"}
  cta      {"lines": [...], "echo"}
Cada cena aceita "dur" (s). Gera reel.mp4 e cover.jpg.
Área segura do Reels: x 80-850, y 230-1440.
"""
import os, sys, json, subprocess, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OW, OH = 1200, 2134  # fundo maior para movimento de câmera
X0, XR = 84, 850

INTER = '/usr/share/fonts/opentype/inter/InterDisplay-%s.otf'
CARDO_I = '/usr/share/fonts/truetype/google-fonts/ofl/cardo/Cardo-Italic.ttf'
CARDO = '/usr/share/fonts/truetype/google-fonts/ofl/cardo/Cardo-Regular.ttf'
_fc = {}
def F(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
def I(weight, size): return F(INTER % weight, size)

IVORY = (242, 237, 228); GOLD = (200, 164, 100); INK = (9, 9, 11); MUTED = (150, 146, 138)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- fundos
def _noise_tile(n=512, seed=1):
    rng = np.random.default_rng(seed)
    t = np.zeros((n, n))
    for s, a in ((4, .5), (16, .3), (64, .25), (256, .2)):
        g = rng.standard_normal((s, s))
        im = Image.fromarray(((g - g.min()) / (np.ptp(g) + 1e-9) * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        t += a * (np.asarray(im, np.float32) / 255 - .5)
    return t

def stadium(accent, seed=3):
    """Gramado em perspectiva, à noite, com refletores e arquibancada desfocada."""
    rng = np.random.default_rng(seed)
    hz, f, camh = 520.0, 700.0, 22.0
    ys, xs = np.mgrid[0:OH, 0:OW].astype(np.float32)
    img = np.zeros((OH, OW, 3), np.float32)
    below = ys > hz + 1
    z = np.where(below, f * camh / np.maximum(ys - hz, 1), 1e4)
    x = (xs - OW / 2) * z / f
    a = math.radians(-18)
    u = x * math.cos(a) - z * math.sin(a) + 6
    v = x * math.sin(a) + z * math.cos(a) - 8
    tile = _noise_tile()
    tu = ((u * 22).astype(np.int64)) % 512; tv = ((v * 22).astype(np.int64)) % 512
    grain = tile[tv, tu]
    far = clamp_arr(z / 60.0)
    grain = grain * (1 - far)
    stripe = ((np.floor(v / 5.5)).astype(np.int64) % 2) * 2 - 1
    stripe_amt = 0.2 * (1 - 0.4 * far)
    base = np.array([34, 78, 40], np.float32) / 255
    g = 1 + stripe * stripe_amt + grain * 0.55
    # linhas do campo (meio-campo v=40, círculo central, lateral u=-30)
    pix = np.maximum(z / f * 1.3, 0.12)
    def line(d):
        return np.clip(1 - np.abs(d) / pix, 0, 1) * np.minimum(1, 0.2 / pix)
    L = line(v - 40) + line(np.hypot(u - 2, v - 40) - 9.15) + line(u + 30) * (v > -5)
    L += line(v - 92) * (u > -30)  # linha de fundo ao longe
    L = np.clip(L, 0, 1)
    # luz dos refletores (manchas)
    light = 0.38
    for (lu, lv, r, k) in ((-10, 30, 38, .55), (25, 60, 45, .45), (0, 10, 25, .35)):
        light = light + k * np.exp(-((u - lu) ** 2 + (v - lv) ** 2) / r ** 2)
    col = base[None, None, :] * (g * light)[..., None]
    col = col * (1 - L[..., None] * .9) + L[..., None] * np.array([.86, .88, .84]) * light[..., None] * 0.95
    fog = (1 - np.exp(-z / 75.0))[..., None]
    haze = np.array([30, 38, 48], np.float32) / 255
    col = col * (1 - fog) + haze * fog
    img = np.where(below[..., None], col, 0)
    # arquibancada
    top = ~below
    t = clamp_arr((ys - 0) / hz)
    stand = (np.array([8, 9, 12]) / 255)[None, None, :] * (1 - t[..., None]) + (np.array([26, 29, 36]) / 255)[None, None, :] * t[..., None]
    crowd = (tile[(ys.astype(int) * 3) % 512, (xs.astype(int) * 3) % 512] + .5)
    stand = stand * (0.75 + 0.5 * crowd[..., None])
    img = np.where(top[..., None], stand, img)
    # faixa de LED na linha do horizonte
    band = (np.abs(ys - (hz - 10)) < 7)
    acc = np.array(accent, np.float32) / 255
    img[band] = img[band] * .5 + acc * .3
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    # flashes de celular / luzes da torcida
    d = ImageDraw.Draw(im)
    for _ in range(900):
        px, py = rng.uniform(0, OW), rng.uniform(240, hz - 25)
        b = int(rng.uniform(60, 200)); r = rng.uniform(.6, 1.6)
        d.ellipse([px - r, py - r, px + r, py + r], fill=(b, b, int(b * .95)))
    # profundidade de campo: fundo desfocado, primeiro plano nítido
    blur = im.filter(ImageFilter.GaussianBlur(7))
    m = np.clip(1 - (np.arange(OH) - hz) / 260.0, 0, 1) ** 1.5
    m[: int(hz)] = 1
    mask = Image.fromarray((np.repeat(m[:, None], OW, 1) * 255).astype(np.uint8))
    im = Image.composite(blur, im, mask)
    # refletores: bancos de luz + brilho
    glow = Image.new('RGB', (OW, OH), 0); gd = ImageDraw.Draw(glow)
    for cx, cy in ((150, 175), (1060, 140)):
        for i in range(4):
            for j in range(6):
                px, py = cx - 75 + j * 30, cy - 30 + i * 22
                gd.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(255, 250, 235))
    halo = glow.filter(ImageFilter.GaussianBlur(90))
    halo2 = glow.filter(ImageFilter.GaussianBlur(14))
    arr = np.asarray(im, np.float32) + np.asarray(halo, np.float32) * 3.0 + np.asarray(halo2, np.float32) * .9 + np.asarray(glow, np.float32) * .6
    # feixes de luz suaves
    beams = Image.new('L', (OW, OH), 0); bd = ImageDraw.Draw(beams)
    bd.polygon([(150, 175), (40, OH), (520, OH)], fill=22)
    bd.polygon([(1060, 140), (700, OH), (1190, OH)], fill=18)
    beams = np.asarray(beams.filter(ImageFilter.GaussianBlur(40)), np.float32)[..., None]
    arr = arr + beams * np.array([1.0, .98, .9])
    return grade(arr)

def clamp_arr(a): return np.clip(a, 0, 1)

def grade(arr):
    a = np.clip(arr / 255.0, 0, 1)
    a = a / (1 + a * .35) * 1.2                  # compressão de realces
    lum = a.mean(axis=2, keepdims=True)
    shadow = np.array([.02, .045, .06]); warm = np.array([1.03, 1.0, .94])
    a = a * warm + shadow * (1 - lum) * .8      # sombras azuladas, luz quente
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    vig = 1 - .55 * (((xs - a.shape[1] / 2) / (a.shape[1] * .75)) ** 2 + ((ys - a.shape[0] * .55) / (a.shape[0] * .7)) ** 2)
    a = a * np.clip(vig, .25, 1)[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

def tactical(accent):
    """Campo visto de cima, escuro, para a cena de assistências."""
    w, h = 760, 520
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    tile = _noise_tile(512, 7)
    g = .16 + .025 * ((np.floor(xs / 63) % 2) * 2 - 1) + tile[ys.astype(int) % 512, xs.astype(int) % 512] * .08
    arr = np.stack([g * .55, g * 1.15, g * .7], -1)
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im)
    c = (215, 220, 210, 120); lw = 2
    d.rectangle([4, 4, w - 5, h - 5], outline=c, width=lw)
    d.line([w / 2, 4, w / 2, h - 5], fill=c, width=lw)
    d.ellipse([w / 2 - 62, h / 2 - 62, w / 2 + 62, h / 2 + 62], outline=c, width=lw)
    d.rectangle([w - 120, h / 2 - 150, w - 5, h / 2 + 150], outline=c, width=lw)
    d.rectangle([w - 42, h / 2 - 66, w - 5, h / 2 + 66], outline=c, width=lw)
    d.rectangle([4, h / 2 - 150, 120, h / 2 + 150], outline=c, width=lw)
    d.rectangle([4, h / 2 - 66, 42, h / 2 + 66], outline=c, width=lw)
    return im

# ---------------------------------------------------------------- texto
_tc = {}
def text_img(text, font, color, stroke=0, track=0):
    k = (text, font.path, font.size, color, stroke, track)
    if k in _tc: return _tc[k]
    if track:
        widths = [font.getlength(ch) + track for ch in text]
        tw = int(sum(widths)) + 4
    else:
        tw = int(font.getlength(text)) + 4 + stroke * 2
    asc, desc = font.getmetrics()
    im = Image.new('RGBA', (tw + 8, asc + desc + 8 + stroke * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if stroke:
        d.text((stroke + 2, stroke + 2), text, font=font, fill=(0, 0, 0, 0), stroke_width=stroke, stroke_fill=color + (255,))
    elif track:
        x = 2
        for ch, wd in zip(text, widths):
            d.text((x, 2), ch, font=font, fill=color + (255,)); x += wd
    else:
        d.text((2, 2), text, font=font, fill=color + (255,))
    _tc[k] = im
    return im

def put(frame, im, x, y, alpha=1.0, wipe=1.0, anchor='l'):
    if alpha <= 0.003 or wipe <= 0.003: return
    if anchor == 'r': x = x - im.width
    if anchor == 'c': x = x - im.width // 2
    if wipe < 1:
        im = im.crop((0, 0, max(1, int(im.width * wipe)), im.height))
    if alpha < 1:
        a = im.getchannel('A').point(lambda p: int(p * alpha))
        im = im.copy(); im.putalpha(a)
    frame.alpha_composite(im, (int(x), int(y)))

def reveal(frame, im, x, y, t, t0, dur=.55, dy=34, anchor='l', t_out=None):
    p = ease((t - t0) / dur)
    a = p
    if t_out is not None: a *= 1 - ease((t - t_out) / .35)
    put(frame, im, x, y + (1 - p) * dy, a, anchor=anchor)

def wrap(text, font, maxw):
    out, cur = [], ''
    for w in text.split():
        s = (cur + ' ' + w).strip()
        if font.getlength(s) <= maxw: cur = s
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out

# ---------------------------------------------------------------- moldura editorial
def chapter_bar(frame, t, chapter, date, accent, idx_total):
    d = ImageDraw.Draw(frame)
    p = ease(t / .6)
    y = 262
    put(frame, text_img(chapter, I('SemiBold', 30), GOLD, track=4), X0, y - 18, p)
    put(frame, text_img(date, I('Medium', 30), IVORY, track=3), XR, y - 18, p, anchor='r')
    lx0 = X0 + text_img(chapter, I('SemiBold', 30), GOLD, track=4).width + 22
    lx1 = XR - text_img(date, I('Medium', 30), IVORY, track=3).width - 22
    if lx1 > lx0:
        d.line([lx0, y + 2, lx0 + (lx1 - lx0) * p, y + 2], fill=GOLD + (int(160 * p),), width=2)

def side_label(frame, text, alpha):
    im = text_img(text, I('Medium', 22), MUTED, track=6).rotate(90, expand=True)
    put(frame, im, 30, 1420 - im.height, alpha * .8)

def grain_frames(n=6, seed=11):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = rng.normal(0, 9, (H // 2, W // 2)).astype(np.float32)
        im = Image.fromarray(np.clip(g + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        out.append(np.asarray(im, np.int16) - 128)
    return out

# ---------------------------------------------------------------- cenas
def scene_hook(frame, t, s, ctx):
    acc = ctx['accent']
    small = s['small']; big = s['big']; slam = s['slam']
    f1 = I('Light', 54); f2 = F(CARDO_I, 118); f3 = I('Black', 172)
    y = 470
    for i, ln in enumerate(wrap(small, f1, XR - X0)):
        reveal(frame, text_img(ln, f1, IVORY), X0, y, t, .05 + i * .08, .45); y += 66
    y += 10
    for i, ln in enumerate(wrap(big, f2, XR - X0)):
        reveal(frame, text_img(ln, f2, IVORY), X0 - 4, y, t, .25 + i * .1, .5); y += 128
    ts = s.get('slam_at', 1.45)
    if t >= ts:
        p = ease((t - ts) / .22)
        sc = 1.18 - .18 * p
        im = text_img(slam, f3, IVORY)
        im2 = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        yy = y + 40
        put(frame, im2, X0 - 6, yy - (im2.height - im.height) / 2, p)
        d = ImageDraw.Draw(frame)
        w = (im.width - 30) * ease((t - ts - .12) / .35)
        d.rectangle([X0, yy + im.height + 2, X0 + w, yy + im.height + 14], fill=acc + (255,))

def scene_number(frame, t, s, ctx):
    acc = ctx['accent']
    chapter_bar(frame, t, s['chapter'], s['date'], acc, 0)
    big = text_img(s['number'], I('Black', s.get('number_size', 760)), GOLD, stroke=3)
    p = ease((t - .05) / 1.1)
    put(frame, big, s.get('number_x', 300) + (1 - p) * 60, s.get('number_y', 250), .55 * p, wipe=ease_io((t - .05) / 1.2))
    y = s.get('text_y', 820)
    fT = I('Black', 104); fB = F(CARDO_I, 66); fS = I('Regular', 38)
    lines = s['lines']
    reveal(frame, text_img(lines[0], fT, IVORY), X0, y, t, .35); y += 128
    for i, ln in enumerate(lines[1:]):
        for j, w in enumerate(wrap(ln, fB, XR - X0)):
            reveal(frame, text_img(w, fB, IVORY), X0, y, t, .7 + i * .35 + j * .08); y += 78
    if s.get('note'):
        y += 26
        d = ImageDraw.Draw(frame)
        pn = ease((t - 1.5) / .5)
        d.rectangle([X0, y + 8, X0 + 6, y + 8 + 46 * pn], fill=acc + (255,))
        for j, w in enumerate(wrap(s['note'], fS, XR - X0 - 30)):
            reveal(frame, text_img(w, fS, MUTED), X0 + 28, y, t, 1.5 + j * .08); y += 50

def scene_match(frame, t, s, ctx):
    acc = ctx['accent']
    chapter_bar(frame, t, s['chapter'], s['date'], acc, 0)
    fN = I('SemiBold', 44); fG = I('Black', 210); fx = F(CARDO_I, 90)
    y = 370
    if not s.get('score'):
        y = 330
        fT = F(CARDO_I, 76)
        for j, w in enumerate(wrap(s['title'], fT, XR - X0)):
            reveal(frame, text_img(w, fT, IVORY), X0, y, t, .15 + j * .1); y += 86
        return _chips(frame, t, s, ctx, y + 30, .5)
    home, gh, ga, away = s['score']
    reveal(frame, text_img(home.upper(), fN, IVORY, track=8), X0, y, t, .15)
    reveal(frame, text_img(away.upper(), fN, MUTED, track=8), XR, y, t, .25, anchor='r')
    y += 60
    reveal(frame, text_img(gh, fG, IVORY), X0 - 8, y, t, .3, .6)
    reveal(frame, text_img('×', fx, GOLD), (X0 + XR) // 2, y + 70, t, .45, anchor='c')
    reveal(frame, text_img(ga, fG, MUTED), XR, y, t, .4, .6, anchor='r')
    y += 270
    d = ImageDraw.Draw(frame)
    pl = ease((t - .6) / .6)
    d.line([X0, y, X0 + (XR - X0) * pl, y], fill=GOLD + (140,), width=2)
    y += 44
    fT = F(CARDO_I, 76)
    for j, w in enumerate(wrap(s['title'], fT, XR - X0)):
        reveal(frame, text_img(w, fT, IVORY), X0, y, t, .8 + j * .1); y += 86
    _chips(frame, t, s, ctx, y + 30, 1.3)

def _chips(frame, t, s, ctx, y, tstart):
    acc = ctx['accent']
    fC = I('Medium', 40); fNum = I('Black', 40)
    for i, c in enumerate(s['chips']):
        t0 = tstart + i * .45
        p = ease((t - t0) / .4)
        if p <= 0: continue
        lines = wrap(c, fC, XR - X0 - 120)
        hgt = 34 + 50 * len(lines)
        box = Image.new('RGBA', (XR - X0, hgt), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, XR - X0 - 1, hgt - 1], 18, fill=(14, 15, 18, 200), outline=GOLD + (90,), width=2)
        bd.ellipse([24, hgt / 2 - 26, 76, hgt / 2 + 26], fill=acc + (255,))
        num = text_img(str(i + 1), fNum, IVORY)
        box.alpha_composite(num, (int(50 - num.width / 2), int(hgt / 2 - 27)))
        yy = 14
        for ln in lines:
            box.alpha_composite(text_img(ln, fC, IVORY), (100, yy)); yy += 50
        put(frame, box, X0 + (1 - p) * 40, y, p)
        y += hgt + 18

def scene_passes(frame, t, s, ctx):
    acc = ctx['accent']
    chapter_bar(frame, t, s['chapter'], s['date'], acc, 0)
    fT = I('Black', 96); fB = F(CARDO_I, 64)
    y = 330
    for j, w in enumerate(wrap(s['title'], fT, XR - X0)):
        reveal(frame, text_img(w, fT, IVORY), X0, y, t, .15 + j * .1); y += 108
    for j, w in enumerate(wrap(s['sub'], fB, XR - X0)):
        reveal(frame, text_img(w, fB, GOLD), X0, y, t, .45 + j * .1); y += 74
    y += 40
    pitch = ctx['tactical']
    pw = XR - X0
    sc = pw / pitch.width
    pim = pitch.resize((pw, int(pitch.height * sc)), Image.LANCZOS).copy()
    d = ImageDraw.Draw(pim)
    rng = np.random.default_rng(5)
    src = (pw * .42, pim.height * .62)
    n = s.get('n', 6)
    targets = [(pw * rng.uniform(.68, .9), pim.height * rng.uniform(.18, .85)) for _ in range(n)]
    for k, (tx, ty) in enumerate(targets):
        t0 = .9 + k * .32
        p = ease((t - t0) / .55)
        if p <= 0: continue
        cx, cy = (src[0] + tx) / 2, min(src[1], ty) - 90
        pts = []
        for q in np.linspace(0, p, 30):
            bx = (1 - q) ** 2 * src[0] + 2 * (1 - q) * q * cx + q * q * tx
            by = (1 - q) ** 2 * src[1] + 2 * (1 - q) * q * cy + q * q * ty
            pts.append((bx, by))
        d.line(pts, fill=GOLD + (230,), width=4, joint='curve')
        if p >= 1:
            d.ellipse([tx - 11, ty - 11, tx + 11, ty + 11], outline=IVORY + (255,), width=3)
    d.ellipse([src[0] - 22, src[1] - 22, src[0] + 22, src[1] + 22], fill=acc + (255,), outline=IVORY + (255,), width=3)
    lab = text_img(s.get('src_label', '80'), I('Black', 26), IVORY)
    pim.alpha_composite(lab, (int(src[0] - lab.width / 2), int(src[1] - 17)))
    pp = ease((t - .55) / .6)
    put(frame, pim, X0, y + (1 - pp) * 40, pp)

def scene_stats(frame, t, s, ctx):
    acc = ctx['accent']
    chapter_bar(frame, t, s['chapter'], s['date'], acc, 0)
    y = 360
    fV = I('Black', 300); fL = I('Medium', 40)
    for i, (val, lab) in enumerate(s['stats']):
        t0 = .2 + i * .55
        p = ease((t - t0) / 1.0)
        if t < t0: continue
        num = int(round(int(val) * p))
        reveal(frame, text_img(str(num), fV, IVORY if i == 0 else GOLD), X0 - 10, y, t, t0, .4)
        reveal(frame, text_img(lab.upper(), fL, MUTED, track=8), X0 + 4, y + 330, t, t0 + .15)
        y += 440
    if s.get('note'):
        fN = F(CARDO_I, 50)
        for j, w in enumerate(wrap(s['note'], fN, XR - X0)):
            reveal(frame, text_img(w, fN, IVORY), X0, y, t, 1.4 + j * .1); y += 60

def scene_cta(frame, t, s, ctx):
    acc = ctx['accent']
    fA = F(CARDO_I, 92); fB = I('Black', 112)
    y = 520
    lines = s['lines']
    for j, w in enumerate(wrap(lines[0], fA, XR - X0)):
        reveal(frame, text_img(w, fA, IVORY), X0, y, t, .1 + j * .12); y += 104
    y += 16
    for j, w in enumerate(wrap(lines[1], fB, XR - X0)):
        reveal(frame, text_img(w, fB, IVORY), X0, y, t, .5 + j * .12); y += 124
    d = ImageDraw.Draw(frame)
    p = ease((t - .9) / .5)
    d.rectangle([X0, y + 10, X0 + 160 * p, y + 22], fill=acc + (255,))
    y += 80
    reveal(frame, text_img(ctx['handle'], I('SemiBold', 40), GOLD, track=3), X0, y, t, 1.1)

def scene_table(frame, t, s, ctx):
    acc = ctx['accent']
    chapter_bar(frame, t, s['chapter'], s['date'], acc, 0)
    y = 330
    fT = F(CARDO_I, 76)
    for j, w in enumerate(wrap(s['title'], fT, XR - X0)):
        reveal(frame, text_img(w, fT, IVORY), X0, y, t, .1 + j * .1); y += 86
    y += 20
    fH = I('Medium', 26); fR = I('SemiBold', 44); fP = I('Black', 44)
    reveal(frame, text_img('POS   TIME', fH, MUTED, track=4), X0, y, t, .3)
    reveal(frame, text_img('PTS', fH, MUTED, track=4), XR - 20, y, t, .3, anchor='r')
    y += 46
    d = ImageDraw.Draw(frame)
    cut = s.get('cut_after')
    for i, row in enumerate(s['rows']):
        pos, team, pts = row[:3]; extra = row[3] if len(row) > 3 else ''
        t0 = .45 + i * .18
        p = ease((t - t0) / .4)
        hl = team == s.get('highlight')
        rh = 78
        if p > 0:
            box = Image.new('RGBA', (XR - X0, rh - 8), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
            bd.rounded_rectangle([0, 0, XR - X0 - 1, rh - 9], 14, fill=(acc + (215,)) if hl else (14, 15, 18, 185))
            box.alpha_composite(text_img(f'{pos}º', fR, IVORY if hl else MUTED), (20, 8))
            box.alpha_composite(text_img(team, fR, IVORY), (120, 8))
            if extra:
                ex = text_img(extra, I('Medium', 26), IVORY if hl else MUTED)
                box.alpha_composite(ex, (130 + text_img(team, fR, IVORY).width, 22))
            pt = text_img(str(pts), fP, IVORY if hl else GOLD)
            box.alpha_composite(pt, (XR - X0 - 24 - pt.width, 8))
            put(frame, box, X0 + (1 - p) * 30, y, p)
        y += rh
        if cut is not None and i == cut:
            pc = ease((t - (t0 + .2)) / .5)
            d.line([X0, y - 2, X0 + (XR - X0) * pc, y - 2], fill=acc + (255,), width=4)
            put(frame, text_img(s.get('cut_label', 'Z4'), I('Black', 26), acc, track=4), XR, y + 4, pc, anchor='r')
            y += 36
    if s.get('note'):
        y += 16
        fN = I('Regular', 36)
        for j, w in enumerate(wrap(s['note'], fN, XR - X0)):
            reveal(frame, text_img(w, fN, MUTED), X0, y, t, 1.6 + j * .08); y += 48

SCENES = {'table': scene_table, 'hook': scene_hook, 'number': scene_number, 'match': scene_match,
          'passes': scene_passes, 'stats': scene_stats, 'cta': scene_cta}

# ---------------------------------------------------------------- áudio (trilha original gerada)
def score(seconds, path, hits):
    sr = 44100; n = int(seconds * sr); t = np.arange(n) / sr
    out = np.zeros(n)
    chords = [[110.0, 130.81, 164.81], [87.31, 110.0, 130.81], [130.81, 164.81, 196.0], [98.0, 123.47, 146.83]]
    bar = 2.4
    for i in range(int(seconds / bar) + 1):
        s0 = int(i * bar * sr); L = min(int((bar + .8) * sr), n - s0)
        if L <= 0: break
        tt = np.arange(L) / sr
        env = np.minimum(1, tt / .6) * np.exp(-tt * .35)
        for fr in chords[i % 4]:
            for det in (-.6, .6):
                out[s0:s0 + L] += .05 * env * np.sin(2 * np.pi * (fr + det) * tt)
            out[s0:s0 + L] += .03 * env * np.sin(2 * np.pi * fr * 2 * tt)
    beat = bar / 4
    for i in range(int(seconds / beat)):
        s0 = int(i * beat * sr); L = min(int(.35 * sr), n - s0); tt = np.arange(L) / sr
        out[s0:s0 + L] += .32 * np.sin(2 * np.pi * (45 + 60 * np.exp(-tt * 35)) * tt) * np.exp(-tt * 9)
    rng = np.random.default_rng(2)
    for h in hits:  # impacto nas viradas de cena
        s0 = int(h * sr); L = min(int(1.2 * sr), n - s0)
        if L <= 0: continue
        tt = np.arange(L) / sr
        out[s0:s0 + L] += .4 * np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 12)) * tt) * np.exp(-tt * 3.5)
        nz = rng.standard_normal(L) * np.exp(-tt * 6) * .12
        out[s0:s0 + L] += np.convolve(nz, np.ones(30) / 30, mode='same')
    out *= np.minimum(1, np.minimum(t / .2, (seconds - t) / 1.0))
    out = np.tanh(out * 1.4)
    out = out / (np.abs(out).max() + 1e-9) * .5
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- render
def render(p, folder):
    os.makedirs(folder, exist_ok=True)
    accent = tuple(p.get('accent', [190, 22, 34]))
    bg = stadium(accent)
    ctx = {'accent': accent, 'tactical': tactical(accent), 'handle': p.get('handle', '@futestrelas2026')}
    shade = np.zeros((H, W), np.float32)
    yy = np.arange(H)[:, None]
    shade += np.clip(1 - np.abs(yy - 850) / 900, 0, 1) * 150  # escurece a área de texto
    shade = Image.fromarray(shade.clip(0, 255).astype(np.uint8))
    darken = Image.new('RGBA', (W, H), INK + (0,)); darken.putalpha(shade)
    grains = grain_frames()
    scenes = p['scenes']
    durs = [float(s.get('dur', 4.0)) for s in scenes]
    starts = np.cumsum([0] + durs[:-1]); total = sum(durs)
    wav = os.path.join(folder, '_trilha.wav')
    hits = list(starts[1:]) + [s.get('slam_at', 1.45) for s in scenes[:1]]
    if p.get('music'): score(total, wav, hits)  # sem trilha por padrão (pedido do usuário em 24/11)
    else:
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100); w.writeframes(b'\0\0' * int(total * 44100))
    mp4 = os.path.join(folder, 'reel.mp4')
    proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-maxrate', '9M', '-bufsize', '18M',
                             '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', mp4],
                            stdin=subprocess.PIPE)
    nf = int(total * FPS)
    cover_t = p.get('cover_t', 2.4)
    for fi in range(nf):
        T = fi / FPS
        k = int(np.searchsorted(starts, T, side='right') - 1)
        t = T - starts[k]
        # câmera: deslize lento contínuo + leve "respiro"
        cx = (OW - W) * (.5 + .45 * math.sin(T * .12 + 1))
        cy = (OH - H) * (.5 + .45 * math.cos(T * .09))
        frame = bg.crop((int(cx), int(cy), int(cx) + W, int(cy) + H)).convert('RGBA')
        frame.alpha_composite(darken)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        SCENES[scenes[k]['type']](layer, t, scenes[k], ctx)
        if scenes[k].get('label'): side_label(layer, scenes[k]['label'], ease(t / .6))
        # saída da cena: fade + leve subida
        out_p = ease((t - (durs[k] - .3)) / .3) if k < len(scenes) - 1 else 0
        if out_p > 0:
            a = layer.getchannel('A').point(lambda v: int(v * (1 - out_p)))
            layer.putalpha(a)
        frame.alpha_composite(layer, (0, int(-20 * out_p)))
        # flash suave na virada
        if k > 0 and t < .18:
            fl = Image.new('RGBA', (W, H), accent + (int(70 * (1 - t / .18)),)); frame.alpha_composite(fl)
        arr = np.asarray(frame.convert('RGB'), np.int16) + grains[fi % len(grains)][..., None]
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        proc.stdin.write(arr.tobytes())
        if abs(T - cover_t) < .5 / FPS:
            Image.fromarray(arr).save(os.path.join(folder, 'cover.jpg'), quality=92)
    proc.stdin.close(); proc.wait(); os.remove(wav)
    print('ok', mp4, f'{total:.1f}s')

if __name__ == '__main__':
    p = json.load(open(sys.argv[1], encoding='utf-8'))
    render(p, sys.argv[2])
