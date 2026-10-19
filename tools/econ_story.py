import json, sys, os, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
KIT = os.environ.get("PT_KIT") or next(iter(glob.glob("/mnt/skills/**/parsa-target-brand/assets", recursive=True)))
W, H = 1080, 1920
MINT = "#2BE59A"; MINT_D = "#0C8C59"; EMBER = "#FF6B5E"; EMBER_D = "#A8332A"
HANDLE = "@parsatargetfx"
def F(w, s): return ImageFont.truetype(f"{KIT}/fonts/Vazirmatn-{w}.ttf", s)
FA = str.maketrans("0123456789,", "۰۱۲۳۴۵۶۷۸۹٬")
def fa(x): return str(x).translate(FA)
def tl(d, t, f): return d.textlength(t, font=f, direction="rtl", language="fa")
def T(d, xy, t, f, fill, anchor="ra"): d.text(xy, t, font=f, fill=fill, anchor=anchor, direction="rtl", language="fa")
def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if cur and tl(d, t, f) > maxw: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines
def shadow(img, box, r, depth=10, a=140):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); x0, y0, x1, y1 = box
    ImageDraw.Draw(sh).rounded_rectangle((x0+8, y0+depth+14, x1-8, y1+depth+24), r, fill=(0, 0, 0, a))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
def main(p, out):
    D = json.load(open(p, encoding="utf-8"))
    up = D["up"]; good = D.get("good", up); acc, accd = (MINT, MINT_D) if good else (EMBER, EMBER_D)
    img = Image.new("RGBA", (W, H)); top, bot = (214, 236, 240), (225, 232, 228)
    gd = ImageDraw.Draw(img)
    for yy in range(H):
        t = yy/H; gd.line((0, yy, W, yy), fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3))+(255,))
    g = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    ImageDraw.Draw(g).ellipse((-100, 300, 1180, 1000), fill=(255, 255, 255, 150))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(150))); d = ImageDraw.Draw(img)
    logo = Image.open(f"{KIT}/logos/logo-full-silver.png").convert("RGBA")
    lh = 96; logo = logo.resize((int(logo.width*lh/logo.height), lh), Image.LANCZOS)
    lx1 = W-60; lx0 = lx1-logo.width-56; ly0 = 60; ly1 = ly0+lh+36
    shadow(img, (lx0, ly0, lx1, ly1), 30, 6, 70); d = ImageDraw.Draw(img)
    d.rounded_rectangle((lx0, ly0, lx1, ly1), 30, fill=(4, 17, 31)); img.alpha_composite(logo, (lx0+28, ly0+18))
    hb = (150, 360, W-150, 760); shadow(img, hb, 48, 18, 70); d = ImageDraw.Draw(img)
    d.rounded_rectangle((hb[0], hb[1]+18, hb[2], hb[3]+18), 48, fill=accd); d.rounded_rectangle(hb, 48, fill="#FFFFFF")
    T(d, (W//2, 405), D["label"], F("Bold", 48), "#5E7A6C", anchor="ma")
    T(d, (W//2, 480), D["big"], F("ExtraBold", 170), "#0B3B5C", anchor="ma")
    T(d, (W//2, 700), D["unit"], F("Medium", 44), "#5E7A6C", anchor="ma")
    cx, cy, r = hb[2]-20, hb[1]+20, 52
    d.ellipse((cx-r, cy-r+8, cx+r, cy+r+8), fill=accd); d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=acc)
    s = 22
    pts = [(cx, cy-s), (cx-s, cy+s*0.75), (cx+s, cy+s*0.75)] if up else [(cx, cy+s), (cx-s, cy-s*0.75), (cx+s, cy-s*0.75)]
    d.polygon(pts, fill="#FFFFFF")
    y = 880; hf = F("ExtraBold", 66); parts = D["headline"]; full = "".join(t for t, _ in parts); hw = tl(d, full, hf)
    while hw > W-230 and hf.size > 46: hf = F("ExtraBold", hf.size-4); hw = tl(d, full, hf)
    x1 = W-70; x0 = max(70, x1 - hw - 90); shadow(img, (x0, y, x1, y+130), 28, 4, 45); d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y, x1, y+130), 28, fill="#FFFFFF"); xr = x1 - 45
    for t, k in parts:
        col = ("#1E9E5A" if good else "#C9372C") if k == "k" else "#0B3B5C"
        T(d, (xr, y+22), t, hf, col); xr -= tl(d, t, hf)
    y += 190
    bf = F("Bold", 46); lines = wrap(d, D["body"], bf, W-260); bh = 60 + 74*len(lines)
    d.rounded_rectangle((70, y, W-70, y+bh), 28, fill="#F6F2E6"); yy = y + 30
    for ln in lines: T(d, (W-115, yy), ln, bf, "#1B1B1B"); yy += 74
    y += bh + 40
    pl = wrap(d, "پ.ن: " + D["pn"], bf, W-300); ph = 60 + 74*len(pl)
    d.rounded_rectangle((110, y, W-70, y+ph), 28, fill="#D9F2E4"); yy = y + 30
    for ln in pl: T(d, (W-115, yy), ln, bf, "#1B1B1B"); yy += 74
    d.text((W//2, 1790), HANDLE, font=F("Bold", 42), fill="#0B3B5C", anchor="ma")
    img.convert("RGB").save(out, quality=94)
main(sys.argv[1], sys.argv[2])
