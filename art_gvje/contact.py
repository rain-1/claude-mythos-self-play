from PIL import Image
h = Image.open('hero_4096.png').resize((900,900), Image.LANCZOS)
t = Image.open('tower_2560.png').resize((900,900), Image.LANCZOS)
c = Image.open('collapse_2560.png').resize((900,900), Image.LANCZOS)
sheet = Image.new('RGB', (2760, 940), (8,8,12))
sheet.paste(h, (20,20)); sheet.paste(t, (930,20)); sheet.paste(c, (1840,20))
sheet.save('contact_sheet.png')
print('ok')
