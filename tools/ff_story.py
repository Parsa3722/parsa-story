import glob, json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
KIT = os.environ.get("PT_KIT") or next(iter(glob.glob("/root/.claude/skills/**/parsa-target-brand/assets", recursive=True) + glob.glob("/mnt/skills/**/parsa-target-brand/assets", recursive=True)))
F = lambda w, s: ImageFont.truetype(f"{KIT}/fonts/Vazirmatn-{w}.ttf", s)
W, H = 1080, 1920
BG = (6, 17, 12); PAPER = "#EAF6EF"; MUTED = "#9DB8AA"; MINT = "#2BE59A"
RED = "#FF6B5E"; RED_E = "#A8332A"; ORG = "#FFA94D"; ORG_E = "#B86A1E"
HANDLE = "@parsatargetfx"
FA = str.maketrans("0123456789.%", "۰۱۲۳۴۵۶۷۸۹٫٪")
def fa(s): return s.translate(FA)
def t(d, xy, s, f, fill, anchor="ra"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, direction="rtl", language="fa")
def card(img, box, edge, r=34, depth=12):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 28, x1, y1 + 40), r, fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0 + depth, x1, y1 + depth), r, fill=edge)
    d.rounded_rectangle(box, r, fill=(14, 34, 25), outline=(43, 229, 154, 60), width=2)
def render(data, out):
    img = Image.new("RGBA", (W, H), BG)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((-200, -300, 900, 700), fill=(43, 229, 154, 40)); gd.ellipse((300, 1400, 1400, 2300), fill=(43, 229, 154, 28))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for y in range(0, H, 60): od.line((0, y, W, y), fill=(255, 255, 255, 7))
    img.alpha_composite(ov)
    logo = Image.open(f"{KIT}/logos/logo-full-silver.png").convert("RGBA")
    lw = 300; logo = logo.resize((lw, int(logo.height * lw / logo.width)))
    img.alpha_composite(logo, (W - lw - 60, 70))
    d = ImageDraw.Draw(img); R = W - 70; y = 120 + logo.height
    t(d, (R, y), "تقویم اقتصادی امروز", F("ExtraBold", 84), PAPER); y += 120
    t(d, (R, y), data["date"], F("Medium", 44), MUTED); y += 80
    lvl = data["level"]
    col, edge, lab = {"high": (RED, RED_E, "خبرهای پراهمیت"), "medium": (ORG, ORG_E, "خبرهای با اهمیت متوسط"), "none": (MINT, "#0C8C59", "روز آرام")}[lvl]
    bf = F("Bold", 40); bw = d.textlength(lab, font=bf, direction="rtl") + 110
    d.rounded_rectangle((R - bw, y + 8, R, y + 82), 37, fill=edge)
    d.rounded_rectangle((R - bw, y, R, y + 74), 37, fill=col)
    t(d, (R - 40, y + 13), lab, bf, "#06110C"); y += 130
    if lvl == "none":
        card(img, (60, y, W - 60, y + 520), (8, 22, 16)); d = ImageDraw.Draw(img)
        t(d, (W // 2, y + 110), "امروز خبر مهمی نداریم", F("ExtraBold", 64), PAPER, anchor="ma")
        t(d, (W // 2, y + 220), "بازار آرومه", F("Bold", 54), MINT, anchor="ma")
        t(d, (W // 2, y + 340), "در ارزهای اصلی، خبر قرمز یا نارنجی", F("Regular", 38), MUTED, anchor="ma")
        t(d, (W // 2, y + 400), "در تقویم امروز نیست.", F("Regular", 38), MUTED, anchor="ma"); y += 580
    for g in data.get("groups", []):
        n = len(g["items"]); h = 150 + n * 150
        card(img, (60, y, W - 60, y + h), (8, 22, 16)); d = ImageDraw.Draw(img)
        t(d, (R - 40, y + 40), g["cur_fa"], F("ExtraBold", 50), PAPER)
        d.text((100, y + 46), g["cur"], font=F("Bold", 44), fill=MINT)
        tb = F("Bold", 40); tw = d.textlength(fa(g["time"]), font=tb) + 60
        x = 100 + d.textlength(g["cur"], font=F("Bold", 44)) + 30
        d.rounded_rectangle((x, y + 40, x + tw + 150, y + 104), 30, fill=(18, 70, 48))
        t(d, (x + tw + 125, y + 50), "ساعت " + fa(g["time"]), tb, MINT)
        yy = y + 140
        for it in g["items"]:
            d.line((100, yy - 14, W - 100, yy - 14), fill=(201, 205, 210, 40), width=2)
            d.ellipse((R - 70, yy + 22, R - 46, yy + 46), fill=col)
            t(d, (R - 90, yy + 8), it["name"], F("Bold", 42), PAPER)
            vals = []
            if it.get("f"): vals.append("پیش‌بینی: " + fa(it["f"]))
            if it.get("p"): vals.append("قبلی: " + fa(it["p"]))
            if vals: t(d, (R - 90, yy + 72), "   |   ".join(vals), F("Regular", 36), MUTED)
            yy += 150
        y += h + 60
    if data.get("tip"):
        card(img, (60, y, W - 60, y + 120), (8, 22, 16), depth=8); d = ImageDraw.Draw(img)
        t(d, (W // 2, y + 34), data["tip"], F("Bold", 40), MINT, anchor="ma"); y += 170
    t(d, (R, H - 230), "معامله در بازارهای مالی ریسک دارد. این محتوا آموزشی است و توصیه سرمایه‌گذاری نیست.", F("Regular", 26), MUTED)
    t(d, (R, H - 175), "منبع: ForexFactory | ساعت‌ها به وقت تهران", F("Regular", 30), MUTED)
    d.text((W // 2, H - 95), HANDLE, font=F("Bold", 40), fill=PAPER, anchor="mm")
    img.convert("RGB").save(out, quality=93)
if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
