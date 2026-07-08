"""Assemble the triptych contact sheet for final judgement."""
from PIL import Image

panels = [
    ("nursery_of_numbers_4096.png", "I. THE NURSERY OF NUMBERS"),
    ("chord_genesis_2560.png", "II. CHORD GENESIS"),
    ("one_cell_speaks_2560.png", "III. ONE CELL SPEAKS"),
]
TH = 840
ims = []
for f, _ in panels:
    im = Image.open(f).convert("RGB")
    ims.append(im.resize((TH, TH), Image.LANCZOS))
pad = 28
W = 3 * TH + 4 * pad
H = TH + 2 * pad
sheet = Image.new("RGB", (W, H), (6, 6, 10))
for k, im in enumerate(ims):
    sheet.paste(im, (pad + k * (TH + pad), pad))
sheet.save("variants/contact_sheet.png")
print("saved variants/contact_sheet.png")
