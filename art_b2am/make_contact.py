"""Assemble the triptych contact sheet: hero large on top, two companions below."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def load(p, s):
    return np.array(Image.open(p).convert("RGB").resize((s, s), Image.LANCZOS))

def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try: return ImageFont.truetype(p, sz)
    except Exception: return ImageFont.load_default()

def main(out="contact_sheet.png"):
    pad = 46
    gap = 26
    HS = 1560
    CS = (HS - gap) // 2           # two companions span the hero width
    title_h = 128
    W = HS + 2 * pad
    H = title_h + HS + gap + CS + pad + 54
    sheet = Image.new("RGB", (W, H), (6, 6, 9))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 30), "THE NEGATION OF THE NEGATION", font=font(54, True), fill=(238, 228, 208))
    d.text((pad, 94),
           "three self-negating orders  ·  the paperfolding dragon · the Thue–Morse spectrum · the base-(−1+i) tiling",
           font=font(24), fill=(150, 160, 185))
    # hero
    sheet.paste(Image.fromarray(load("hero_the_fold.png", HS)), (pad, title_h))
    d.text((pad + 10, title_h + HS - 42),
           "THE FOLD   ·   paperfolding dragon, k = 19   ·   each fold = the complement of the reversed previous fold",
           font=font(22), fill=(214, 208, 216))
    # companions
    y2 = title_h + HS + gap
    sheet.paste(Image.fromarray(load("companion_the_shattering.png", CS)), (pad, y2))
    sheet.paste(Image.fromarray(load("companion_the_tiling.png", CS)), (pad + CS + gap, y2))
    # footer
    d.text((pad, y2 + CS + 14),
           "verified:  Woods–Robbins ∏((2n+1)/(2n+2))^((−1)^tₙ)=1/√2 (1.2e−13)  ·  Prouhet–Tarry–Escott equal power sums  ·  ∫wₖdθ=1",
           font=font(20), fill=(140, 150, 175))
    sheet.save(out)
    print("saved", out, sheet.size)

if __name__ == "__main__":
    main()
