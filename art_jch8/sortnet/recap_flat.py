import caption
from PIL import Image
im=Image.open('tmp_flat.png')
caption.caption(im,['Every Swap at Random, Every Wire a Sine',
 'A uniformly random sorting network of 300 wires: neighbours swap one pair at a time until the order is reversed, and every two wires swap exactly once.',
 'All 44,850 swaps are drawn as fine thread; every 25th wire is lifted out in bold. Nothing tells a wire where to go, yet as the wires multiply each path tends to a sine curve',
 '(conjectured by Angel, Holroyd, Romik and Virág; proved by Dauvergne). Already at 300 wires each bold path stays within 2% (rms) of the width of its best-fitting sine.'],int(2250*0.835),scale=3600)
im.save('every_swap_every_sine.png')
