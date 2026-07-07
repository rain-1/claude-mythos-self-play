"""Assemble the 3x3 grid — rows A/B/C, columns The World / The Shadow / The Return."""
from PIL import Image

FILES = [
    ["A1_the_world", "A2_the_shadow", "A3_the_return"],
    ["B1_the_world", "B2_the_shadow", "B3_the_return"],
    ["C1_the_world", "C2_the_shadow", "C3_the_return"],
]


def assemble(indir=".", out="00_what_reaches_us_grid.png", cell=1024, gutter=28,
             bg=(6, 7, 10)):
    W = 3 * cell + 4 * gutter
    sheet = Image.new("RGB", (W, W), bg)
    for r, row in enumerate(FILES):
        for c, name in enumerate(row):
            im = Image.open(f"{indir}/{name}.png").convert("RGB")
            im = im.resize((cell, cell), Image.LANCZOS)
            x = gutter + c * (cell + gutter)
            y = gutter + r * (cell + gutter)
            sheet.paste(im, (x, y))
    sheet.save(f"{indir}/{out}")
    print(f"grid saved: {indir}/{out}  ({W}x{W})")


if __name__ == "__main__":
    import sys
    assemble(indir=sys.argv[1] if len(sys.argv) > 1 else ".")
