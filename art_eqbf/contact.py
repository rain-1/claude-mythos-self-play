from PIL import Image
ims = [Image.open(p).resize((840, 840), Image.LANCZOS)
       for p in ("hero_4096.png", "wells_2560.png", "braid_2560.png")]
sheet = Image.new("RGB", (840 * 3 + 40, 880), (5, 5, 8))
for i, im in enumerate(ims):
    sheet.paste(im, (i * 860 + 10, 20))
sheet.save("contact_sheet.png")
print("saved contact sheet")
