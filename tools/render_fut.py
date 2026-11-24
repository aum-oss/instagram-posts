"""Layout "transmissão de TV" para o @futestrelas2026.

Uso: python3 tools/render_fut.py <post.json> <pasta_saida>
post.json usa as mesmas cenas do render.py (hook / item / tip / cta) e aceita:
  "handle": "@futestrelas2026"
  "scoreboard": ["PAL", "EST", "SÁB 28/11 · 17H"]   (opcional, placar estilo TV no topo)
  "colors": [[0,110,60], [200,30,40]]                (opcional, cor de cada time)
Gera reel.mp4 e cover.jpg. Texto fica dentro da área segura do Reels (y 230-1440, 230 px livres à direita).
"""
import os, sys, json, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

GF = '/usr/share/fonts/truetype/google-fonts/ofl/'
ANTON = GF + 'anton/Anton-Regular.ttf'
FB = GF + 'firasans/FiraSans-Black.ttf'
FS = GF + 'firasans/FiraSans-SemiBold.ttf'
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]

W, H, FPS = 1080, 1920, 30
X0, MAXW = 80, 770
YEL = (255, 212, 0); WHITE = (255, 255, 255); INK = (8, 14, 24); NAVY = (12, 22, 44)

def wrap(text, font, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out

def fit_font(lines_text, path, size, maxw, minsize=60):
    while size > minsize:
        f = F(path, size)
        if all(f.getlength(w) <= maxw for w in lines_text.split()): return f
        size -= 6
    return F(path, minsize)

def pitch():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    band = 160
    for i, y in enumerate(range(0, H, band)):
        d.rectangle([0, y, W, y + band], fill=(30, 122, 58) if i % 2 else (36, 138, 66))
    line = (225, 245, 230)
    d.line([(0, H // 2), (W, H // 2)], fill=line, width=8)
    d.ellipse([W // 2 - 230, H // 2 - 230, W // 2 + 230, H // 2 + 230], outline=line, width=8)
    d.ellipse([W // 2 - 14, H // 2 - 14, W // 2 + 14, H // 2 + 14], fill=line)
    d.rectangle([W // 2 - 330, -10, W // 2 + 330, 260], outline=line, width=8)
    d.rectangle([W // 2 - 330, H - 260, W // 2 + 330, H + 10], outline=line, width=8)
    img = img.filter(ImageFilter.GaussianBlur(3))
    # escurece para o texto ler bem (vinheta)
    ov = Image.new('L', (W, H)); od = ImageDraw.Draw(ov)
    for y in range(H):
        c = abs(y - H * 0.45) / (H * 0.55)
        od.line([(0, y), (W, y)], fill=int(110 + 120 * min(1, c)))
    dark = Image.new('RGB', (W, H), (4, 18, 10))
    return Image.composite(dark, img, ov).convert('RGBA')

def stroke_text(d, xy, text, font, fill, sw=6, anchor='la'):
    d.text(xy, text, font=font, fill=fill, stroke_width=sw, stroke_fill=INK, anchor=anchor)

def chrome(p):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    sb = p.get("scoreboard")
    if sb:
        a, b, info = sb
        ca, cb = [tuple(c) for c in p.get("colors", [[0, 110, 60], [200, 30, 40]])]
        f = F(FB, 46); fi = F(FB, 34)
        y0, h = 236, 76
        x = X0
        d.rounded_rectangle([x, y0, x + 560, y0 + h], 14, fill=NAVY)
        d.rectangle([x + 14, y0 + 16, x + 26, y0 + h - 16], fill=ca)
        d.text((x + 40, y0 + h // 2), a, font=f, fill=WHITE, anchor='lm')
        d.text((x + 190, y0 + h // 2), "x", font=F(FS, 40), fill=(170, 180, 200), anchor='mm')
        d.text((x + 230, y0 + h // 2), b, font=f, fill=WHITE, anchor='lm')
        d.rectangle([x + 360, y0 + 16, x + 372, y0 + h - 16], fill=cb)
        tw = fi.getlength(info)
        d.rounded_rectangle([x + 560 + 10, y0, x + 560 + 10 + tw + 40, y0 + h], 14, fill=YEL)
        d.text((x + 560 + 30, y0 + h // 2), info, font=fi, fill=INK, anchor='lm')
    tag = p.get("tag", "")
    if tag:
        f = F(FB, 32); tw = f.getlength(tag)
        d.rounded_rectangle([X0, 330, X0 + tw + 40, 384], 10, fill=(220, 30, 40))
        d.text((X0 + 20, 357), tag, font=f, fill=WHITE, anchor='lm')
    d.text((X0, 1400), p.get("handle", ""), font=F(FS, 40), fill=WHITE, anchor='ls')
    return L

def scene(sc):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    k = sc[0]
    if k == "hook":
        y = 560
        f1 = F(FB, 58)
        for ln in wrap(sc[1], f1, MAXW):
            stroke_text(d, (X0, y), ln, f1, WHITE, 5); y += 74
        y += 20
        fb = fit_font(sc[2], ANTON, 170, MAXW)
        for ln in wrap(sc[2], fb, MAXW):
            stroke_text(d, (X0, y), ln, fb, YEL, 8); y += int(fb.size * 1.12)
    elif k == "item":
        num, title, sub = sc[1], sc[2], sc[3]
        d.rounded_rectangle([X0, 560, X0 + 120, 680], 18, fill=YEL)
        d.text((X0 + 60, 620), num, font=F(ANTON, 90), fill=INK, anchor='mm')
        y = 720; ft = fit_font(title, ANTON, 110, MAXW)
        for ln in wrap(title, ft, MAXW):
            stroke_text(d, (X0, y), ln.upper(), ft, WHITE, 7); y += int(ft.size * 1.12)
        fs = F(FS, 46); lines = wrap(sub, fs, MAXW - 50)
        y += 26; hb = 40 + 62 * len(lines)
        d.rounded_rectangle([X0, y, X0 + MAXW, y + hb], 16, fill=(6, 16, 30, 215))
        d.rectangle([X0, y, X0 + 12, y + hb], fill=YEL)
        yy = y + 22
        for ln in lines: d.text((X0 + 36, yy), ln, font=fs, fill=WHITE); yy += 62
    elif k == "tip":
        y = 600; f = fit_font(sc[1], ANTON, 150, MAXW)
        stroke_text(d, (X0, y), sc[1].upper(), f, YEL, 8); y += int(f.size * 1.3)
        fl = F(FB, 60)
        for ln in sc[2]:
            for l2 in wrap(ln, fl, MAXW):
                stroke_text(d, (X0, y), l2, fl, WHITE, 5); y += 80
            y += 14
    elif k == "cta":
        y = 700; f = fit_font(sc[1], ANTON, 130, MAXW)
        for ln in wrap(sc[1].upper(), f, MAXW):
            stroke_text(d, (X0, y), ln, f, WHITE, 8); y += int(f.size * 1.12)
    return L

DUR = {"hook": 2.4, "item": 3.4, "tip": 3.6, "cta": 3.0}

def music(seconds, path, seed=0):
    import wave
    sr = 44100; n = int(seconds * sr); out = np.zeros(n)
    rng = np.random.default_rng(seed)
    bpm = 122; beat = 60 / bpm
    bass = [55.0, 55.0, 65.41, 49.0]
    for i in range(int(seconds / beat) + 1):
        s = int(i * beat * sr)
        if s >= n: break
        L = min(int(0.3 * sr), n - s); t = np.arange(L) / sr
        out[s:s + L] += 0.55 * np.sin(2 * np.pi * (50 + 70 * np.exp(-t * 30)) * t) * np.exp(-t * 10)  # bumbo
        f0 = bass[(i // 4) % 4]
        Lb = min(int(beat * sr), n - s); tb = np.arange(Lb) / sr
        out[s:s + Lb] += 0.18 * np.sign(np.sin(2 * np.pi * f0 * tb)) * np.exp(-tb * 4)
        if i % 2 == 1:  # palma
            Lc = min(int(0.12 * sr), n - s)
            out[s:s + Lc] += 0.22 * rng.standard_normal(Lc) * np.exp(-np.arange(Lc) / sr * 35)
        hs = int((i + 0.5) * beat * sr)
        if hs < n:
            Lh = min(int(0.03 * sr), n - hs)
            out[hs:hs + Lh] += 0.07 * rng.standard_normal(Lh) * np.exp(-np.arange(Lh) / sr * 120)
    out = np.convolve(out, np.ones(4) / 4, mode='same')
    t = np.arange(n) / sr
    out *= np.minimum(1, np.minimum(t / 0.3, (seconds - t) / 1.2))
    out = out / (np.abs(out).max() + 1e-9) * 0.45
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype(np.int16).tobytes())

def ease(x): return 1 - (1 - min(max(x, 0), 1)) ** 3

def render(p, folder):
    base = Image.alpha_composite(pitch(), chrome(p))
    scenes = [(scene(s), DUR.get(s[0], 3.2) * float(p.get("pace", 1.0))) for s in p["scenes"]]
    total = sum(dd for _, dd in scenes)
    wav = os.path.join(folder, "_music.wav"); music(total, wav, seed=abs(hash(p.get("id", ""))) % 1000)
    mp4 = os.path.join(folder, "reel.mp4")
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", mp4],
                            stdin=subprocess.PIPE)
    elapsed, cover = 0.0, None
    for idx, (layer, dd) in enumerate(scenes):
        nf = int(dd * FPS)
        for fi in range(nf):
            t = fi / FPS; a = ease(t / 0.22)
            frame = base.copy()
            # "punch": a cena entra grande e assenta (efeito de corte rápido)
            s = 1 + 0.12 * (1 - a)
            if s > 1.001:
                lw, lh = int(W * s), int(H * s)
                lay = layer.resize((lw, lh), Image.BILINEAR)
                lay = lay.crop(((lw - W) // 2, (lh - H) // 2, (lw - W) // 2 + W, (lh - H) // 2 + H))
            else:
                lay = layer
            frame.alpha_composite(lay)
            if t < 0.08:  # flash branco curto na troca de cena
                frame = Image.blend(frame, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.35 * (1 - t / 0.08))
            dr = ImageDraw.Draw(frame)
            prog = (elapsed + t) / total
            dr.rectangle([0, 0, W, 12], fill=(10, 30, 18)); dr.rectangle([0, 0, int(W * prog), 12], fill=YEL)
            rgb = frame.convert('RGB')
            if idx == 0 and fi == nf - 1: cover = rgb
            proc.stdin.write(rgb.tobytes())
        elapsed += dd
    proc.stdin.close(); proc.wait(); os.remove(wav)
    cover.save(os.path.join(folder, "cover.jpg"), quality=90)
    return total

if __name__ == "__main__":
    p = json.load(open(sys.argv[1], encoding="utf-8")); folder = sys.argv[2]
    os.makedirs(folder, exist_ok=True)
    print("reel", round(render(p, folder), 1), "s ->", folder)
