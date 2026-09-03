# Census — The Sunflower of Fifths

alpha = log2(3) = 1.584962500721; continued fraction of alpha-1: [0, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1]

convergent denominators: [1, 1, 2, 5, 12, 41, 53, 306, 665, 15601]
intermediate (semiconvergent) denominators: [1, 1, 2, 3, 5, 7, 12, 17, 29, 41, 53, 94, 147, 200, 253, 306, 359, 665, 971, 1636, 2301, 2966, 3631, 4296, 4961, 5626, 6291, 6956, 7621, 8286, 8951, 9616, 10281, 10946, 11611, 12276, 12941, 13606, 14271, 14936, 15601, 16266]

## Fifth error of each family (1200*||m alpha|| cents = how far m fifths miss a whole number of octaves)

| m | cents | record? | name |
|---|---|---|---|
| 1 | 498.0450 | yes | fifth (3:2) |
| 2 | 203.9100 | yes | whole tone 9:8 |
| 3 | 294.1350 |  |  |
| 5 | 90.2250 | yes | 5-tone (slendro-like) |
| 7 | 113.6850 |  | 7-tone |
| 12 | 23.4600 | yes | 12-TET / Pythagorean comma |
| 17 | 66.7650 |  | 17-TET |
| 29 | 43.3050 |  | 29-TET |
| 41 | 19.8450 | yes | 41-TET |
| 53 | 3.6150 | yes | 53-TET (Mercator) |
| 94 | 16.2299 |  | 94-TET |
| 147 | 12.6149 |  |  |
| 200 | 8.9998 |  |  |
| 253 | 5.3848 |  |  |
| 306 | 1.7697 | yes | 306-TET |
| 359 | 1.8453 |  |  |
| 665 | 0.0756 | yes | 665-TET (Satanic comma) |
| 971 | 1.6942 |  |  |
| 1636 | 1.6186 |  |  |
| 2301 | 1.5430 |  |  |
| 2966 | 1.4674 |  |  |
| 3631 | 1.3919 |  |  |
| 4296 | 1.3163 |  |  |
| 4961 | 1.2407 |  |  |
| 5626 | 1.1651 |  |  |
| 6291 | 1.0896 |  |  |
| 6956 | 1.0140 |  |  |
| 7621 | 0.9384 |  |  |
| 8286 | 0.8628 |  |  |
| 8951 | 0.7873 |  |  |
| 9616 | 0.7117 |  |  |
| 10281 | 0.6361 |  |  |
| 10946 | 0.5605 |  |  |
| 11611 | 0.4850 |  |  |
| 12276 | 0.4094 |  |  |
| 12941 | 0.3338 |  |  |
| 13606 | 0.2582 |  |  |
| 14271 | 0.1827 |  |  |
| 14936 | 0.1071 |  |  |
| 15601 | 0.0315 | yes | 15601-TET |
| 16266 | 0.0441 |  |  |
| 31867 | 0.0126 | yes |  |

## Nearest-family hand-overs: analytic minimiser of d(m,k)^2 = (2 pi sqrt(k) ||m alpha||)^2 + m^2/(4k)

| takes over at seed k | family m | radius sqrt(k) |
|---|---|---|
| 5 | 5 | 2.2 |
| 12 | 12 | 3.5 |
| 213 | 53 | 14.6 |
| 9130 | 306 | 95.6 |
| 31888 | 665 | 178.6 |

## Nearest-family hand-overs measured by KD-tree on 300000 seeds (first k where the new value holds for 90% of the next 300 seeds)

| seed k | family m | radius | opposed families seen in this era (2nd neighbour, non-multiples) |
|---|---|---|---|
| 204 | 53 | 14.3 | [306, 12] |
| 9094 | 306 | 95.4 | [665, 53] |
| 31734 | 665 | 178.1 | [306] |

analytic and measured hand-overs agree (within 2% in k): **True**
