"""Assemble a contact sheet of the three panels for cohesion judging."""
import sys
from PIL import Image

def main(paths, out="proto/contact.png", h=900):
    ims = [Image.open(p) for p in paths]
    ims = [im.resize((int(im.width * h / im.height), h), Image.LANCZOS) for im in ims]
    W = sum(im.width for im in ims) + 40 * (len(ims) + 1)
    sheet = Image.new("RGB", (W, h + 80), (8, 8, 10))
    x = 40
    for im in ims:
        sheet.paste(im, (x, 40))
        x += im.width + 40
    sheet.save(out)
    print("saved", out)

if __name__ == "__main__":
    main(sys.argv[1:4] if len(sys.argv) > 3 else
         ["proto/parliament_proto.png", "proto/loom_proto.png", "proto/partition_proto.png"])
