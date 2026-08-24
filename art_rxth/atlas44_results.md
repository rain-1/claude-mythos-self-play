# Atlas 44 — scan results (generated post-hunt)

## window [8.3e+11, 8.8e+11)
# range [830000000000,880000000000) |S∩range|=6579955884
l=3 g=24 maximal_runs=285345 first_start=830000064103
l=3 g=25 maximal_runs=42771 first_start=830000591424
l=3 g=48 maximal_runs=67 first_start=830118625663
l=4 g=24 maximal_runs=1968 first_start=830010749303
l=4 g=25 maximal_runs=121 first_start=830055385262
l=5 g=24 maximal_runs=12 first_start=833764021775
l=5 g=25 maximal_runs=2 first_start=830595732286

drift r34(25) this window: 2.829e-03

## window [8.8e+11, 1.2e+12)
# range [880000000000,1200000000000) |S∩range|=41965096185
l=3 g=24 maximal_runs=1859078 first_start=880000326943
l=3 g=25 maximal_runs=282388 first_start=880000280559
l=3 g=48 maximal_runs=448 first_start=881511384473
l=4 g=24 maximal_runs=13398 first_start=880002618401
l=4 g=25 maximal_runs=712 first_start=880422754286
l=5 g=24 maximal_runs=37 first_start=880839632503
l=5 g=25 maximal_runs=1 first_start=1158245890366
l=6 g=24 maximal_runs=1 first_start=982614621929

drift r34(25) this window: 2.521e-03

## hunt_alarms_830000000000_880000000000.txt

FIRST l=5 g=14 start=830294728100
FIRST l=5 g=25 start=830595732286
   -> mod 144 = 94 (gate demands 94)
OCC l=5 g=25 start=830595732286
   -> mod 144 = 94 (gate demands 94)
FIRST l=5 g=24 start=833764021775
OCC l=5 g=24 start=833764021775
OCC l=5 g=24 start=836953019225
FIRST l=5 g=17 start=837679051982
OCC l=5 g=24 start=852637869001
OCC l=5 g=24 start=853672600151
OCC l=5 g=24 start=855038163977
OCC l=5 g=24 start=856806935903
OCC l=5 g=24 start=861758710025
OCC l=5 g=24 start=862109331329
OCC l=5 g=25 start=862954027582
   -> mod 144 = 94 (gate demands 94)
OCC l=5 g=24 start=863487449303
OCC l=5 g=24 start=872625436201
OCC l=5 g=24 start=872814562175
OCC l=5 g=24 start=878989264201

## hunt_alarms_880000000000_1200000000000.txt

FIRST l=5 g=24 start=880839632503
OCC l=5 g=24 start=880839632503
FIRST l=5 g=14 start=880958619044
FIRST l=5 g=17 start=882671448782
OCC l=5 g=24 start=908904876527
OCC l=5 g=24 start=920861910601
OCC l=5 g=24 start=923643718879
OCC l=5 g=24 start=925294007353
OCC l=5 g=24 start=953397286175
OCC l=5 g=24 start=957404250529
OCC l=5 g=24 start=958470484927
OCC l=5 g=24 start=968054253977
OCC l=5 g=24 start=982614621929
FIRST l=6 g=24 start=982614621929
   -> SEXTET/beyond: mod 16 = 9, mod 9 = 5 (gate: ±1 mod 8, ≢0 mod 3)
OCC l=6 g=24 start=982614621929
   -> SEXTET/beyond: mod 16 = 9, mod 9 = 5 (gate: ±1 mod 8, ≢0 mod 3)
L6+! l=6 gap=24 start=982614621929
   -> SEXTET/beyond: mod 16 = 9, mod 9 = 5 (gate: ±1 mod 8, ≢0 mod 3)
FIRST l=5 g=23 start=983296201058
OCC l=5 g=23 start=983296201058
OCC l=5 g=24 start=988140502177
OCC l=5 g=24 start=1003116325927
OCC l=5 g=23 start=1015400407058
OCC l=5 g=24 start=1015806187679
OCC l=5 g=24 start=1022543903527
OCC l=5 g=24 start=1029704111729
OCC l=5 g=24 start=1036449865079
OCC l=5 g=24 start=1041911767753
OCC l=5 g=24 start=1051447853377
OCC l=5 g=24 start=1053095133479
OCC l=5 g=24 start=1060345869703
OCC l=5 g=24 start=1062552744527
OCC l=5 g=24 start=1069116201977
OCC l=5 g=24 start=1072497881729
OCC l=5 g=24 start=1078389223201
OCC l=5 g=24 start=1080624375425
OCC l=5 g=24 start=1084260080201
OCC l=5 g=24 start=1105424051551
OCC l=5 g=24 start=1109670456575
OCC l=5 g=24 start=1118537243329
OCC l=5 g=24 start=1128021648527
OCC l=5 g=24 start=1130272197727
OCC l=5 g=23 start=1132668868706
OCC l=5 g=24 start=1140139239727
FIRST l=5 g=25 start=1158245890366
   -> mod 144 = 94 (gate demands 94)
OCC l=5 g=25 start=1158245890366
   -> mod 144 = 94 (gate demands 94)
OCC l=5 g=24 start=1174461590977
OCC l=5 g=24 start=1178572359175
OCC l=5 g=24 start=1187394804175
OCC l=5 g=24 start=1195297435225
OCC l=5 g=24 start=1196669931679
OCC l=5 g=24 start=1197162586903

## Model scorecard (predictions were pre-committed in atlas44_model.md)
- Recovery scan: predicted EXACTLY 2 ch-25 quintets, both ≡ 94 (mod 144) → **observed exactly 2, both ≡ 94** ✓✓. 4th fence = 862,954,027,582 (certified by factorization; maximal, 15-gap flanks).
- Continuation ch-25: predicted E ≈ 3.3–4.2 (P(silent) 2–4%) → **observed 1** (fence #5 = 1,158,245,890,366 ≡ 94 ✓). The channel went QUIET: the rising-drift extrapolation broke — r34(25) fell back to 2.52e-3 (recovery window: 2.83e-3, inside the predicted [2.7,3.0]e-3; continuation: below it). One fence in 4e11 sits at the ~10% tail of the model: the drift law r34 1.78/1.98/2.49/2.53/2.83 was never a monotone law, just weather.
- Continuation sextets: predicted E ≈ 0.38 (P(≥1) ≈ 32%) → **observed 1: SECOND SEXTET n = 982,614,621,929** ≡ 9 (mod 16), ≡ 5 (mod 9) — obeys the new gate (±1 mod 8, ≢ 0 mod 3); certified by full factorization (consecutive members at offsets 0..120 step 24; flanks gap 7 before, 3 after ⇒ maximal). Sextets over the whole relay: 2 seen vs E ≈ 0.84 — the sixth rung keeps arriving ahead of schedule (P(≥2) ≈ 20%).
- l=6 g=48: predicted silence (E ≪ 0.01) → silent ✓.
- Relay state: **complete to 1.2e12**; |S| this run: 6,579,955,884 + 41,965,096,185 new members scanned.
