"""چالش چارت شبانه — پارسا تارگت
استفاده:
  python3 tools/challenge_story.py q <seed> out.jpg   # استوری سؤال (شب)
  python3 tools/challenge_story.py a <seed> out.jpg   # استوری جواب (صبح فردا، با همان seed)
seed = تاریخ میلادی روز سؤال، مثل 2026-10-24. چارت از روی seed ساخته می‌شود، پس سؤال و جواب همیشه یکی‌اند.
چارت آموزشی و شبیه‌سازی‌شده است (داده‌ی واقعی بازار نیست).
"""
import sys, os, glob, random, math, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
KIT = os.environ.get("PT_KIT") or next(iter(glob.glob("/root/.claude/skills/**/parsa-target-brand/assets", recursive=True) + glob.glob("/mnt/skills/**/parsa-target-brand/assets", recursive=True)))
W, H = 1080, 1920
NAVY = (4, 17, 31); PANEL = (10, 29, 48); GRID = (28, 52, 78)
GOLD = "#F5C451"; MINT = "#2BE59A"; RED = "#FF5D5D"; PAPER = "#EAF2F8"; MUTE = "#8FA6BC"; BLUE = "#3B82F6"
UPC = (38, 214, 140); DNC = (255, 93, 93); EMA_C = (245, 196, 81)
HANDLE = "@parsatargetfx"
FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
def fa(x): return str(x).translate(FA)
def F(w, s): return ImageFont.truetype(f"{KIT}/fonts/Vazirmatn-{w}.ttf", s)
def tl(d, t, f): return d.textlength(t, font=f, direction="rtl", language="fa")
def T(d, xy, t, f, fill, anchor="ma"): d.text(xy, t, font=f, fill=fill, anchor=anchor, direction="rtl", language="fa")
def TL(d, xy, t, f, fill, anchor="ma"): d.text(xy, t, font=f, fill=fill, anchor=anchor)

SETUP = {"h2_buy": 1, "l2_sell": 1, "bo_buy": 3, "bo_sell": 3}
KINDS = {
 "h2_buy":  dict(side="buy",  name="High 2", why="روند صعودی قوی، دو تلاش برای پایین رفتن نزدیک مووینگ بیست، و یه کندل سیگنال صعودی قوی. ورود: بالای سقف کندل سیگنال."),
 "l2_sell": dict(side="sell", name="Low 2",  why="روند نزولی قوی، دو تلاش برای بالا رفتن نزدیک مووینگ بیست، و یه کندل سیگنال نزولی قوی. ورود: زیر کف کندل سیگنال."),
 "bo_buy":  dict(side="buy",  name="بریک‌اوت پولبک", why="سقف رنج با قدرت شکسته شد، قیمت برگشت و سقف قبلی رو تست کرد و یه کندل صعودی قوی ساخت. سقف قبلی حالا حمایته."),
 "bo_sell": dict(side="sell", name="بریک‌اوت پولبک", why="کف رنج با قدرت شکسته شد، قیمت برگشت و کف قبلی رو تست کرد و یه کندل نزولی قوی ساخت. کف قبلی حالا مقاومته."),
}
def gen(seed):
    rng = random.Random(seed)
    kind = rng.choice(list(KINDS))
    path = []; p = 100.0
    def leg(n, step, jit=0.35, redp=0.0):
        nonlocal p
        for _ in range(n):
            s = step + rng.uniform(-jit, jit) * abs(step if step else 0.6)
            if redp and rng.random() < redp: s = -abs(step) * rng.uniform(0.2, 0.5)
            p += s; path.append(p)
    up = KINDS[kind]["side"] == "buy"
    if kind in ("h2_buy", "l2_sell"):
        for _ in range(6): p += rng.uniform(-0.35, 0.35); path.append(p)
        leg(rng.randint(14, 17), 0.85, 0.5, 0.18)          # روند قوی
        leg(rng.randint(3, 4), -0.62, 0.4)                    # پایه‌ی اول
        leg(2, 0.42, 0.3)                                     # H1
        leg(rng.randint(3, 4), -0.55, 0.35)                   # پایه‌ی دوم
        sig_from = p; p += rng.uniform(0.85, 1.1); path.append(p)   # کندل سیگنال
        nq = len(path)
        leg(13, 0.75, 0.6, 0.15)                              # ادامه
    else:
        base = p
        for i in range(12): p = base + 1.6 * math.sin(i * 1.15 + rng.random()) + rng.uniform(-0.3, 0.3); path.append(p)
        top = max(path[-12:])
        p = top - 0.3; leg(3, 1.25, 0.3)                      # شکست
        leg(rng.randint(3, 4), -0.75, 0.3)                    # پولبک
        p = max(p, top + 0.15); path[-1] = p
        p += rng.uniform(0.9, 1.15); path.append(p)           # سیگنال
        nq = len(path)
        leg(13, 0.8, 0.6, 0.15)
    if not up: path = [200 - x for x in path]
    # candles
    C = []; prev = path[0] - (0.3 if up else -0.3)
    for i, c in enumerate(path):
        o = prev; hi = max(o, c) + abs(rng.gauss(0, 0.22)); lo = min(o, c) - abs(rng.gauss(0, 0.22))
        if i == nq - 1:  # کندل سیگنال: بدنه‌ی قوی، بسته شدن نزدیک سقف/کف
            hi, lo = (max(o, c) + 0.05, min(o, c) - 0.18) if up else (max(o, c) + 0.18, min(o, c) - 0.05)
        C.append((o, hi, lo, c)); prev = c
    ema = []; k = 2 / 21; e = path[0]
    for c in path: e = c * k + e * (1 - k); ema.append(e)
    sig = C[nq - 1]
    entry = sig[1] + 0.08 if up else sig[2] - 0.08
    stop = sig[2] - 0.08 if up else sig[1] + 0.08
    risk = abs(entry - stop)
    prior = max(c[1] for c in C[:nq - 1]) if up else min(c[2] for c in C[:nq - 1])
    target = prior if abs(prior - entry) >= risk else (entry + risk * 1.5 if up else entry - risk * 1.5)
    # ادامه باید واقعاً به تارگت برسد
    fut = C[nq:]
    if up and max(c[1] for c in fut) < target: shift = target - max(c[1] for c in fut) + 0.3; C[nq:] = [(o+shift*(i+1)/len(fut), h+shift*(i+1)/len(fut), l+shift*(i+1)/len(fut), c+shift*(i+1)/len(fut)) for i, (o, h, l, c) in enumerate(fut)]
    if not up and min(c[2] for c in fut) > target: shift = min(c[2] for c in fut) - target + 0.3; C[nq:] = [(o-shift*(i+1)/len(fut), h-shift*(i+1)/len(fut), l-shift*(i+1)/len(fut), c-shift*(i+1)/len(fut)) for i, (o, h, l, c) in enumerate(fut)]
    # ورود باید فعال شود و قبل از تارگت استاپ نخورد
    return dict(kind=kind, up=up, C=C, ema=ema, nq=nq, entry=entry, stop=stop, target=target)

def bg():
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse((-250, -250, 800, 700), fill=(59, 130, 246, 40)); gd.ellipse((350, 1350, 1400, 2250), fill=(245, 196, 81, 26))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(170)))
    return img
def header(img, label):
    d = ImageDraw.Draw(img)
    logo = Image.open(f"{KIT}/logos/logo-full-silver.png").convert("RGBA")
    lh = 92; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    img.alpha_composite(logo, (60, 250))
    f = F("Bold", 38); w = tl(d, label, f) + 70
    d.rounded_rectangle((W - 60 - w, 262, W - 60, 334), 36, fill=GOLD); T(d, (W - 60 - w / 2, 276), label, f, "#06111F")
def chart(img, G, upto, box=(40, 560, 1040, 1300), marks=False):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 26, fill=PANEL + (255,), outline=(43, 70, 100, 255), width=2)
    C = G["C"]; n = len(C)
    lo = min(c[2] for c in C); hi = max(c[1] for c in C)
    lo = min(lo, G["stop"]); hi = max(hi, G["stop"])
    pad = (hi - lo) * 0.12; lo -= pad; hi += pad
    px0, px1 = x0 + 30, x1 - 110
    Y = lambda v: y1 - 30 - (v - lo) / (hi - lo) * (y1 - y0 - 70)
    step = (px1 - px0) / n; X = lambda i: px0 + step * (i + 0.5)
    for k in range(1, 5):
        yy = y0 + 20 + k * (y1 - y0 - 40) / 5; d.line((x0 + 10, yy, x1 - 10, yy), fill=GRID + (255,), width=1)
    TL(d, (x0 + 26, y0 + 18), "M5", F("Medium", 26), MUTE, "la")
    T(d, (x1 - 26, y0 + 18), "چارت آموزشی", F("Medium", 26), MUTE, "ra")
    TL(d, (x0 + 26, y0 + 52), "EMA 20", F("Medium", 24), GOLD, "la")
    # EMA
    pts = [(X(i), Y(G["ema"][i])) for i in range(upto)]
    if len(pts) > 1: d.line(pts, fill=EMA_C + (255,), width=4, joint="curve")
    bw = max(6, step * 0.62)
    for i in range(upto):
        o, h, l, c = C[i]; col = UPC if c >= o else DNC
        d.line((X(i), Y(h), X(i), Y(l)), fill=col + (255,), width=3)
        a, b = sorted((Y(o), Y(c))); b = max(b, a + 3)
        d.rectangle((X(i) - bw / 2, a, X(i) + bw / 2, b), fill=col + (255,))
    last = C[upto - 1][3]
    d.rounded_rectangle((x1 - 104, Y(last) - 18, x1 - 12, Y(last) + 18), 6, fill=(UPC if C[upto-1][3] >= C[upto-1][0] else DNC) + (255,))
    TL(d, (x1 - 58, Y(last) - 15), f"{last:.2f}", F("Bold", 22), "#06111F")
    return X, Y, step
def pill(d, cx, cy, txt, f, fill, tc="#06111F", padx=60, h=None):
    w = tl(d, txt, f) + padx * 2; h = h or f.size * 1.75
    d.rounded_rectangle((cx - w / 2, cy - h / 2 + 8, cx + w / 2, cy + h / 2 + 8), h / 2, fill=(0, 0, 0, 90))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=fill)
    T(d, (cx, cy), txt, f, tc, "mm")
def question(seed, out):
    G = gen(seed); img = bg(); header(img, "چالش چارت امشب")
    d = ImageDraw.Draw(img, "RGBA")
    T(d, (W / 2, 365), "اینجا خرید یا فروش؟", F("ExtraBold", 92), PAPER)
    n = fa(SETUP[G["kind"]])
    T(d, (W / 2, 505), f"ستاپ {n} از «ده ستاپ طلایی ال بروکس» | آموزش رایگانش تو بایو", F("Bold", 31), GOLD)
    X, Y, step = chart(img, G, G["nq"])
    d = ImageDraw.Draw(img, "RGBA")
    i = G["nq"] - 1; o, h, l, c = G["C"][i]; cx = X(i); cy = (Y(h) + Y(l)) / 2; r = max(46, (Y(l) - Y(h)) / 2 + 26)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=7)
    qx = (cx + 1000) / 2 + 10; qy = 930
    d.ellipse((qx - 95, qy - 95, qx + 95, qy + 95), fill=(28, 40, 52, 255), outline=GOLD, width=6)
    TL(d, (qx, qy - 6), "?", F("ExtraBold", 140), GOLD, "mm")
    pill(d, 300, 1410, "فروش", F("ExtraBold", 64), RED, "#FFFFFF")
    pill(d, 780, 1410, "خرید", F("ExtraBold", 64), MINT)
    T(d, (W / 2, 1500), "جوابت رو به همین استوری بفرست: «خرید» یا «فروش»", F("Bold", 40), PAPER)
    T(d, (W / 2, 1572), "جواب درست: فردا ساعت ۸:۳۰ صبح، همین‌جا", F("Bold", 40), GOLD)
    T(d, (W / 2, 1640), "چارت آموزشی برای تمرینه؛ پیشنهاد خرید و فروش نیست.", F("Regular", 28), MUTE)
    img.convert("RGB").save(out, quality=93)
def answer(seed, out):
    G = gen(seed); K = KINDS[G["kind"]]; buy = K["side"] == "buy"
    img = bg(); header(img, "جواب چالش دیشب")
    d = ImageDraw.Draw(img, "RGBA")
    word = "خرید" if buy else "فروش"; col = MINT if buy else RED
    pill(d, W / 2, 420, f"جواب: {word}", F("ExtraBold", 84), col, "#06111F" if buy else "#FFFFFF", 70)
    X, Y, step = chart(img, G, len(G["C"]))
    d = ImageDraw.Draw(img, "RGBA")
    i = G["nq"] - 1; xa = X(i) - step; xb = 1040 - 110
    rows = sorted(((Y(v), c_, lab) for v, c_, lab in ((G["target"], MINT, "تارگت"), (G["entry"], BLUE, "ورود"), (G["stop"], RED, "استاپ"))))
    ly = []
    for yv, _, _ in rows: ly.append(max(yv, ly[-1] + 44) if ly else yv)
    for (yy, c_, lab), lyy in zip(rows, ly):
        xx = xa
        while xx < xb: d.line((xx, yy, min(xx + 14, xb), yy), fill=c_, width=3); xx += 24
        f = F("Bold", 26); w = tl(d, lab, f) + 30
        d.rounded_rectangle((xa - w - 6, lyy - 20, xa - 6, lyy + 20), 12, fill=c_); T(d, (xa - 6 - w / 2, lyy), lab, f, "#06111F" if c_ != RED else "#FFFFFF", "mm")
    o, h, l, c = G["C"][i]; cx = X(i); cy = (Y(h) + Y(l)) / 2; r = max(40, (Y(l) - Y(h)) / 2 + 22)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=6)
    # کادر توضیح
    d.rounded_rectangle((60, 1340, W - 60, 1620), 28, fill=(10, 29, 48, 255), outline=(245, 196, 81, 140), width=2)
    f = F("ExtraBold", 46); T(d, (W - 100, 1365), f"ستاپ: {K['name']}" if not K['name'].isascii() else "ستاپ: ", f, GOLD, "ra")
    if K["name"].isascii(): TL(d, (W - 100 - tl(d, "ستاپ: ", f) - 8, 1365), K["name"], f, GOLD, "ra")
    bf = F("Medium", 36); words = K["why"].split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if cur and tl(d, t, bf) > W - 220: lines.append(cur); cur = w_
        else: cur = t
    lines.append(cur); yy = 1440
    for ln in lines[:3]: T(d, (W - 100, yy), ln, bf, PAPER, "ra"); yy += 54
    n = fa(SETUP[G["kind"]])
    T(d, (W / 2, 1648), f"آموزش کامل ستاپ {n} از «ده ستاپ طلایی ال بروکس» رایگانه؛ لینکش تو بایو", F("Bold", 31), GOLD)
    T(d, (W / 2, 1700), "امشب ساعت ۹، چالش بعدی", F("Bold", 34), PAPER)
    img.convert("RGB").save(out, quality=93)
if __name__ == "__main__":
    mode, seed, out = sys.argv[1], sys.argv[2], sys.argv[3]
    (question if mode == "q" else answer)(seed, out)
    print(json.dumps({"seed": seed, "kind": gen(seed)["kind"], "answer": KINDS[gen(seed)["kind"]]["side"]}))
