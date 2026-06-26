"""The von Dyck debug-trick figure: broken vs fixed {7,3} tiling, side by side."""
import numpy as np, sys, math
sys.path.insert(0,'debug_note'); sys.path.insert(0,'octonions')
import dbg, figkit
from PIL import Image, ImageDraw

def render(W=1600):
    Re_bug=math.tanh(math.acosh(math.cos(math.pi/3)/math.sin(math.pi/7))/2)
    Re_fix=math.tanh(math.acosh(1/(math.tan(math.pi/7)*math.tan(math.pi/3)))/2)
    pw=720
    pbug=dbg.panel(Re_bug,pw); pfix=dbg.panel(Re_fix,pw)
    Hh=pw+220
    img=Image.new("RGB",(W,Hh),(8,9,17)); d=ImageDraw.Draw(img)
    img.paste(pbug,(60,150)); img.paste(pfix,(W-60-pw,150))
    ft=figkit.font("DejaVuSans-Bold.ttf",40); fm=figkit.font("DejaVuSans.ttf",30)
    fc=figkit.font("DejaVuSans-Bold.ttf",34)
    # headers
    d.text((60,40),"THE BUG",font=ft,fill=(255,120,120))
    d.text((60,96),"cosh R = cos(π/3)/sin(π/7)   ⟵ inradius",font=fm,fill=(200,160,160))
    d.text((W-60-pw,40),"THE FIX",font=ft,fill=(120,235,160))
    d.text((W-60-pw,96),"cosh R = cot(π/7)·cot(π/3)   ⟵ circumradius",font=fm,fill=(150,210,170))
    # center diagnostic
    cx=W/2
    d.text((cx-150,150+pw*0.36),"(ab)²",font=figkit.font("DejaVuSans-Bold.ttf",54),fill=(235,240,250))
    d.text((cx-150,150+pw*0.36+70),"=? I",font=figkit.font("DejaVuSans-Bold.ttf",40),fill=(160,170,195))
    d.text((cx-150,150+pw*0.36+140),"0.078",font=fc,fill=(255,120,120))
    d.text((cx-150,150+pw*0.36+185),"5e−17",font=fc,fill=(120,235,160))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("A debugging story worth keeping. Building the Klein quartic's {7,3} heptagon tiling, the "
          "tiles a few rings out dissolved into the overlapping scribble on the LEFT. Nothing in "
          "the rendering was wrong — the GEOMETRY was. I had placed each heptagon's vertices using "
          "cosh R = cos(π/3)/sin(π/7), which is the INRADIUS (centre to edge-midpoint), not the "
          "circumradius (centre to vertex). With the vertices in the wrong place, the rotations "
          "that should glue neighbouring tiles no longer matched up, and copies drifted over each "
          "other. The trick that found it in seconds: the tiling group is the von Dyck group "
          "⟨a,b | a⁷ = b³ = (ab)² = 1⟩, where a spins a heptagon about its centre and b spins it "
          "about a vertex. So I didn't stare at pixels — I just asked the computer whether the "
          "DEFINING RELATION held: is (ab)² the identity? The broken geometry gave 0.078 (loudly "
          "NO); the correct circumradius cosh R = cot(π/7)·cot(π/3) gave 5×10⁻¹⁷ (yes, to machine "
          "precision), and the tiling on the RIGHT snapped into place. Lesson: when a construction "
          "is governed by a group, verify a group RELATION — an algebraic identity localises a "
          "geometric bug far faster than the eye can.")
    fig=figkit.caption(viz,"DEBUG NOTE · THE VON DYCK TRICK",
                       "Check the relation, not the pixels",body,accent=(255,180,90))
    figkit.save(fig,"debug_note/von_dyck_debug.png")
    print("done",fig.size)
