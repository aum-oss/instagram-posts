import os, re, subprocess, sys, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))

B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
_fc = {}
def F(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]
RED = (255, 80, 60); WHITE = (255, 255, 255); GREY = (200, 205, 215); DIM = (150, 160, 180)
HANDLE = "@digitalnomad2050"
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿‍️]+")
def clean(t): return EMOJI.sub("", t).strip()

def background(W, H):
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(10 + 55 * t ** 2), int(12 + 4 * t), int(20 + 10 * (1 - t))))
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(22, 30, 45))
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=(22, 30, 45))
    return img

def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit(text, path, size, maxw, minsize=40):
    while size > minsize and F(path, size).getlength(text) > maxw: size -= 4
    return F(path, size)

# ---------------- REELS ----------------
W, H, FPS = 1080, 1920, 30
X0, MAXW = 90, 900

def tag_layer(tag):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F(B, 34); tw = f.getlength("⚠ " + tag)
    d.rounded_rectangle([X0, 230, X0 + tw + 44, 288], 12, fill=(220, 38, 38))
    d.text((X0 + 22, 241), "⚠ " + tag, font=f, fill=WHITE)
    d.text((W // 2, 1640), HANDLE, font=F(MONO, 32), fill=DIM, anchor='mm')
    return L

def scene_layer(sc):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    kind = sc[0]
    if kind == "hook":
        f = F(B, 70); y = 640
        for ln in wrap(clean(sc[1]), f, MAXW):
            d.text((X0, y), ln, font=f, fill=WHITE); y += 90
        y += 30
        fb = F(B, 120)
        for ln in wrap(clean(sc[2]), fb, MAXW):
            ff = fit(ln, B, 120, MAXW)
            d.text((X0, y), ln, font=ff, fill=RED); y += 140
    elif kind == "item":
        num, title, sub = sc[1], clean(sc[2]), clean(sc[3])
        d.ellipse([X0, 620, X0 + 150, 770], fill=RED)
        d.text((X0 + 75, 695), num, font=F(B, 86), fill=WHITE, anchor='mm')
        y = 840; f = F(B, 68)
        for ln in wrap(title, f, MAXW): d.text((X0, y), ln, font=f, fill=WHITE); y += 86
        y += 20; fs = F(R, 50)
        for ln in wrap(sub, fs, MAXW): d.text((X0, y), ln, font=fs, fill=GREY); y += 66
    elif kind == "sms":
        sender, text = clean(sc[1]), clean(sc[2])
        d.text((X0, 560), "Mensagem recebida:", font=F(R, 44), fill=GREY)
        fs = F(R, 50); lines = wrap(text, fs, MAXW - 100)
        h = 120 + 66 * len(lines)
        d.rounded_rectangle([X0, 640, X0 + MAXW, 640 + h], 40, fill=(38, 44, 60), outline=(90, 100, 125), width=3)
        d.text((X0 + 50, 670), sender, font=F(B, 44), fill=(130, 190, 255))
        y = 740
        for ln in lines: d.text((X0 + 50, y), ln, font=fs, fill=WHITE); y += 66
        d.text((X0, 640 + h + 50), "Parece real, né?", font=F(B, 56), fill=RED)
    elif kind == "tip":
        f = F(B, 84); d.text((X0, 650), clean(sc[1]), font=f, fill=RED)
        y = 790; fl = F(B, 64)
        for ln in sc[2]:
            for l2 in wrap(clean(ln), fl, MAXW): d.text((X0, y), l2, font=fl, fill=WHITE); y += 84
    elif kind == "cta":
        f = F(B, 78); y = 760
        for ln in wrap(clean(sc[1]), f, MAXW):
            d.text((W // 2, y), ln, font=f, fill=WHITE, anchor='ma'); y += 100
        d.text((W // 2, y + 40), "Siga " + HANDLE, font=F(B, 52), fill=RED, anchor='ma')
    return L

def dur(sc):
    k = sc[0]
    if k == "hook": return 3.2
    if k == "sms": return 4.2
    if k == "tip": return 4.0
    if k == "cta": return 3.0
    return 3.0

def music(seconds, path, seed=0):
    # trilha calma estilo lo-fi/ambient: pads suaves, baixo senoidal, batida leve
    import wave
    sr = 44100; n = int(seconds * sr); t = np.arange(n) / sr
    bpm = 84; beat = 60 / bpm; out = np.zeros(n)
    rng = np.random.default_rng(seed)
    A = 220.0
    chords = [[0, 3, 7, 10], [-4, 0, 3, 7], [-9, -5, -2, 3], [-2, 2, 5, 9]]  # Am7, Fmaj7, C/E-ish, G6
    bar = 4 * beat; nbar = int(seconds / bar) + 1
    for b in range(nbar):
        s = int(b * bar * sr)
        if s >= n: break
        L = min(int(bar * sr * 1.05), n - s); tt = np.arange(L) / sr
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (L / sr - tt) / 0.6)
        ch = chords[b % 4]
        pad = sum(np.sin(2 * np.pi * A * 2 ** (k / 12) * tt + rng.uniform(0, 6)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * tt))
                  for k in ch)
        out[s:s + L] += 0.10 * pad * env
        root = A / 2 * 2 ** (ch[0] / 12)
        out[s:s + L] += 0.22 * np.sin(2 * np.pi * root * tt) * env
    nb = int(seconds / beat) + 1
    for i in range(nb):
        s = int(i * beat * sr)
        if s >= n: break
        if i % 2 == 0:
            Lk = min(int(0.25 * sr), n - s); tk = np.arange(Lk) / sr
            out[s:s + Lk] += 0.35 * np.sin(2 * np.pi * (45 + 40 * np.exp(-tk * 25)) * tk) * np.exp(-tk * 12)
        hs = int((i + 0.5) * beat * sr)
        if hs < n:
            HL = min(int(0.04 * sr), n - hs)
            out[hs:hs + HL] += 0.03 * rng.standard_normal(HL) * np.exp(-np.arange(HL) / sr * 90)
    # suavização (passa-baixa simples)
    k = 6; out = np.convolve(out, np.ones(k) / k, mode='same')
    fade = np.minimum(1, np.minimum(t / 1.0, (seconds - t) / 1.5))
    out = out * fade; out = out / (np.abs(out).max() + 1e-9) * 0.35
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

def ease(x): return 1 - (1 - min(max(x, 0), 1)) ** 3

def render_reel(p, folder):
    bg = background(W, H).convert('RGBA'); tag = tag_layer(p["tag"])
    base = Image.alpha_composite(bg, tag)
    pace = float(p.get("pace", 1.75))  # >1 = cenas mais longas (ex.: 1.5 = 50% mais tempo em cada tela)
    scenes = [(scene_layer(s), dur(s) * pace) for s in p["scenes"]]
    total = sum(d for _, d in scenes)
    wav = os.path.join(folder, "_music.wav"); music(total, wav, seed=hash(p["id"]) % 1000)
    mp4 = os.path.join(folder, "reel.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
           "-shortest", "-movflags", "+faststart", mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    elapsed = 0.0; cover = None
    for idx, (layer, d) in enumerate(scenes):
        nf = int(d * FPS)
        for fi in range(nf):
            t = fi / FPS; a = ease(t / 0.35)
            frame = base.copy()
            if a < 1:
                lay = layer.copy(); alpha = lay.getchannel('A').point(lambda v: int(v * a)); lay.putalpha(alpha)
                frame.alpha_composite(lay, (0, int((1 - a) * 60)))
            else:
                frame.alpha_composite(layer)
            dd = ImageDraw.Draw(frame)
            prog = (elapsed + t) / total
            dd.rectangle([0, 0, W, 10], fill=(40, 46, 62)); dd.rectangle([0, 0, int(W * prog), 10], fill=RED)
            rgb = frame.convert('RGB')
            if idx == 0 and fi == nf - 1: cover = rgb
            proc.stdin.write(rgb.tobytes())
        elapsed += d
    proc.stdin.close(); proc.wait(); os.remove(wav)
    cover.save(os.path.join(folder, "cover.jpg"), quality=90)
    return total

# ---------------- CAROUSELS ----------------
CW, CH = 1080, 1350
def carousel(p, folder):
    files = []
    def save(img, i):
        fn = f"slide{i:02d}.jpg"; img.save(os.path.join(folder, fn), quality=92); files.append(fn)
    tagt, l1, l2, sub = p["cover"]; n = len(p["slides"]) + 2
    img = background(CW, CH); d = ImageDraw.Draw(img)
    f = F(B, 34); tw = f.getlength(tagt)
    d.rounded_rectangle([80, 90, 80 + tw + 44, 148], 12, fill=(220, 38, 38)); d.text((102, 101), tagt, font=f, fill=WHITE)
    d.text((80, 430), l1, font=fit(l1, B, 100, 920), fill=WHITE)
    d.text((80, 560), l2, font=fit(l2, B, 120, 920), fill=RED)
    d.text((80, 760), sub, font=F(R, 42), fill=GREY)
    d.text((CW - 80, CH - 90), "arraste →", font=F(B, 40), fill=WHITE, anchor='ra')
    d.text((80, CH - 90), HANDLE, font=F(MONO, 30), fill=DIM)
    save(img, 1)
    for i, (num, title, lines) in enumerate(p["slides"], start=2):
        img = background(CW, CH); d = ImageDraw.Draw(img)
        d.text((CW - 80, 100), f"{i}/{n}", font=F(MONO, 34), fill=DIM, anchor='ra')
        d.ellipse([80, 300, 240, 460], fill=RED); d.text((160, 380), num, font=F(B, 90), fill=WHITE, anchor='mm')
        d.text((80, 520), title, font=fit(title, B, 84, 920), fill=WHITE)
        y = 660
        for ln in lines: d.text((80, y), ln, font=F(R, 54), fill=GREY); y += 74
        d.text((80, CH - 90), HANDLE, font=F(MONO, 30), fill=DIM)
        save(img, i)
    e1, e2, e3 = p["end"]
    img = background(CW, CH); d = ImageDraw.Draw(img)
    d.text((CW // 2, 470), e1, font=F(B, 90), fill=WHITE, anchor='ma')
    d.text((CW // 2, 580), e2, font=fit(e2, B, 90, 920), fill=RED, anchor='ma')
    d.text((CW // 2, 760), clean(e3), font=fit(clean(e3), R, 50, 920), fill=GREY, anchor='ma')
    d.text((CW // 2, 880), "Siga " + HANDLE, font=F(B, 50), fill=WHITE, anchor='ma')
    save(img, n)
    return files

if __name__ == "__main__":
    # Uso: python3 tools/render.py <post.json> <pasta_saida>
    # post.json: mesmo formato dos itens de posts (type reel|carousel, scenes / cover+slides+end, tag)
    p = json.load(open(sys.argv[1], encoding="utf-8")); folder = sys.argv[2]
    os.makedirs(folder, exist_ok=True)
    if p["type"] == "reel":
        p["scenes"] = [tuple(x) for x in p["scenes"]]
        print("reel", round(render_reel(p, folder), 1), "s ->", folder)
    else:
        p["slides"] = [tuple(x) for x in p["slides"]]
        print("carousel", carousel(p, folder))
