"""Assemble a triptych contact sheet for final judgment."""
from PIL import Image

tiles = [("wall_at_zero.png", "THE WALL AT ZERO"),
         ("same_shadow.png", "THE SAME SHADOW"),
         ("comet.png", "THE COMET THAT OUTRUNS PROOF")]
T = 680
sheet = Image.new("RGB", (T * 3 + 48 * 4, T + 96), (8, 9, 16))
x = 48
for fn, _ in tiles:
    im = Image.open(fn).resize((T, T), Image.LANCZOS)
    sheet.paste(im, (x, 48))
    x += T + 48
sheet.save("contact_sheet.png")
print("saved contact_sheet.png")
