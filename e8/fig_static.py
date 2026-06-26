"""E8 static mandala figure with annotation block."""
import sys
sys.path.insert(0,'e8'); sys.path.insert(0,'octonions')
import mandala, figkit

if __name__=="__main__":
    P,rad,ring_idx,nring,E,R=mandala.setup()
    viz=mandala.render(P,ring_idx,nring,E,S=1500,ss=2,ang=0.0,edge_bright=0.42,pt_bright=1.3)
    body=("This is the root system of E₈ — the largest exceptional Lie group, dimension 248 — seen "
          "edge-on. E₈ has 240 'roots' (its shortest nonzero symmetry vectors) living in EIGHT "
          "dimensions; here they are projected onto the single special plane (the Coxeter plane) in "
          "which the symmetry is most evenly spread. The 240 points fall into 8 perfect rings of 30 "
          "— 30 being the Coxeter number of E₈ — and the 6,720 lines join every pair of roots that "
          "sit at 60° to each other. The result is the most famous picture in Lie theory. E₈ is the "
          "bottom-right corner of the Freudenthal magic square, the place where octonions meet "
          "octonions; this mandala is, in a real sense, a portrait of what the 8-dimensional numbers "
          "can do.")
    fig=figkit.caption(viz,"E₈ · THE 240 ROOTS","The E₈ Coxeter-plane mandala",
                       body,accent=(150,200,255),W=1500)
    figkit.save(fig,"e8/01_e8_mandala.png")
    print("done",fig.size)
