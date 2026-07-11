"""Assemble a contact sheet of the three finals for cohesion judgement."""
import numpy as np
from PIL import Image

panels = ["final/sun_of_nothing_4096.png",
          "final/braid_of_rings_3200.png",
          "final/loss_families_2560.png"]
TH = 640
ims = []
for p in panels:
    im = Image.open(p)
    w = int(im.width * TH / im.height)
    ims.append(im.resize((w, TH), Image.LANCZOS))
gap = 24
Wt = sum(im.width for im in ims) + gap * (len(ims) + 1)
sheet = Image.new("RGB", (Wt, TH + 2 * gap), (8, 8, 10))
x = gap
for im in ims:
    sheet.paste(im, (x, gap))
    x += im.width + gap
sheet.save("proto/contact_sheet.png")
print("saved proto/contact_sheet.png", sheet.size)
