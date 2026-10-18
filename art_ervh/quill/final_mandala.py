import numpy as np
from PIL import Image
import compose as C
im=Image.open('proto/mandala_3200.png').convert('RGB')
W,H=im.size; extra=420
a=np.array(im).astype(float)
bot=a[-6:].mean(axis=(0,1))
canvas=np.ones((H+extra,W,3))*bot
canvas[:H]=a
im=Image.fromarray(canvas.astype(np.uint8))
im,y=C.caption(im,H+20,'Three Generations of Borrowing',
 'Every prime below two million is a ratio of numbers written only with the digits 1, 2, 3, 5 and 7. These 94 primes below a million sit at the end of the longest chains of loans.',
 'gilded gold coils: 2, 3, 5, 7 · cream coils lend once (19, 29, 41, 43, 47, 59, 67) · eyes lend twice (607, 829, 997 …) · each petal is a third-generation prime, its length = log(witness)/log p, e.g. 68899 = 57117271 / 829 · MathOverflow 516126 · ALL EXCEPT, ii',scale=0.85)
print(y, im.size)
im.save('../final/three_generations_of_borrowing.png')
im.resize((800,int(800*im.size[1]/W)),Image.LANCZOS).save('proto/m_final_small.png')
