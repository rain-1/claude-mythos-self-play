import numpy as np, json
from PIL import Image
import compose as C
im=Image.open('proto/posets_3200.png').convert('RGB')
opt=json.load(open('../math_poset/optimal.json'))
labs=json.load(open('proto/posets_labels_3200.json'))
for n,desc,e,aut,x,y in labs:
    g=opt[str(n)]['g']
    C.small_label(im,x,y+14,f'n = {n}  ·  {int(g):,} orbit' + ('' if int(g)==1 else 's'),40)
im,yy=C.caption(im,2750,'Fences, Except at Eight',
 'For each n, the poset on n points with the most linear extensions per symmetry. Unions of zigzag fences win for n ≤ 7 and n = 9, but not at 8, 10 or 11: there a fence grows an extra branch.',
 'paper quilling · tight coils = elements, strips = cover relations, upper row greater · blue, lilac, mint = fences · coral = the six-fence with a pendant (298 orders, no symmetry), beating the best fence union 2384 to 2100 at n = 8 · exact enumeration of all 46.7 million posets up to 11 points · MathOverflow 516140 · ALL EXCEPT, iii',scale=0.95)
print(yy)
im.save('../final/fences_except_at_eight.png')
im.resize((900,900),Image.LANCZOS).save('proto/p_final_small.png')
