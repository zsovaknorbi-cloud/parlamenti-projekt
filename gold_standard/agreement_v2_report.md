# Ember–gép egyezés (v2) — agreement.py kimenetek

Blokkok: cap = CAP-főtéma; moral = 7 érzelemkategória; erzelmes = fő mérőszám (érzelmes vs. semleges).

## sonnet_v1_54 · cap — prompt v1, 54 mondat, javítás előtti kézi kódok

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.593 · Cohen's kappa: 0.510

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
1                    0   0.00   0.00   nan   nan  (n < 10: no verdict)
12                   2   0.04    nan  0.00   nan  (n < 10: no verdict)
13                   2   0.04   0.40  1.00  0.57  (n < 10: no verdict)
14                   1   0.02    nan  0.00   nan  (n < 10: no verdict)
15                   3   0.06   0.00  0.00   nan  (n < 10: no verdict)
16                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
17                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
19                   2   0.04   0.50  0.50  0.50  (n < 10: no verdict)
2                    0   0.00   0.00   nan   nan  (n < 10: no verdict)
20                   7   0.13   0.50  0.57  0.53  (n < 10: no verdict)
3                    3   0.06   1.00  0.33  0.50  (n < 10: no verdict)
5                    2   0.04   0.50  0.50  0.50  (n < 10: no verdict)
6                    2   0.04   0.50  1.00  0.67  (n < 10: no verdict)
7                    1   0.02   1.00  1.00  1.00  (n < 10: no verdict)
8                    4   0.07   1.00  1.00  1.00  (n < 10: no verdict)
9                    1   0.02   1.00  1.00  1.00  (n < 10: no verdict)
999                 24   0.44   0.94  0.62  0.75

confusion matrix (rows = reference, columns = compared):
           1    12    13    14    15    16    17    19     2    20     3     5     6     7     8     9   999
1          0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
12         0     0     1     0     0     0     1     0     0     0     0     0     0     0     0     0     0
13         0     0     2     0     0     0     0     0     0     0     0     0     0     0     0     0     0
14         0     0     1     0     0     0     0     0     0     0     0     0     0     0     0     0     0
15         2     0     0     0     0     0     1     0     0     0     0     0     0     0     0     0     0
16         0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
17         0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
19         0     0     0     0     0     0     0     1     1     0     0     0     0     0     0     0     0
2          0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
20         1     0     0     0     1     0     0     0     0     4     0     0     0     0     0     0     1
3          1     0     1     0     0     0     0     0     0     0     1     0     0     0     0     0     0
5          0     0     0     0     0     0     0     0     0     0     0     1     1     0     0     0     0
6          0     0     0     0     0     0     0     0     0     0     0     0     2     0     0     0     0
7          0     0     0     0     0     0     0     0     0     0     0     0     0     1     0     0     0
8          0     0     0     0     0     0     0     0     0     0     0     0     0     0     4     0     0
9          0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     1     0
999        1     0     0     0     0     1     0     1     0     4     0     1     1     0     0     0    15

mismatches: 22
  2026-05-26_AV_Tarr Zoltán_2_q004: reference 19 · compared 2
  2026-05-26_I_Dr. Máthé Zsuzsa_q008: reference 999 · compared 19
  2026-05-26_NRE_Magyar Péter_6_q008: reference 999 · compared 20
  2026-06-01_AV_Kármán András_1_q011: reference 999 · compared 5
  2026-06-01_NRE_Magyar Péter_2_q067: reference 999 · compared 20
  2026-06-08_I_Dr. Latorcai Csaba_q011: reference 12 · compared 17
  2026-06-15_I_Nacsa Lőrinc_q022: reference 999 · compared 6
  2026-06-15_I_Novák Előd_q013: reference 999 · compared 16
  2026-06-16_NRE_Magyar Péter_4_q010: reference 15 · compared 1
  2026-06-29_AV_Tanács Zoltán_4_q003: reference 20 · compared 999
  2026-06-29_NRE_Magyar Péter_1_q155: reference 20 · compared 1
  2026-06-29_NRE_Toroczkai László_1_q044: reference 999 · compared 20
  2026-07-06_A_Takács Péter_q003: reference 3 · compared 1
  2026-07-06_NRE_Dr. Juhász Hajnalka_q034: reference 12 · compared 13
  2026-08-10_AV_Tompa Enikő_1_q016: reference 20 · compared 15
  2026-08-27_A_Dúró Dóra_q014: reference 15 · compared 17
  2026-08-27_NRE_Toroczkai László_1_q053: reference 999 · compared 20
  2026-09-07_NRE_Magyar Péter_7_q009: reference 5 · compared 6
  2026-09-14_AV_Dr. Svéd Tamás_2_q007: reference 15 · compared 1
  2026-09-14_IV_Dr. Apáti István_q007: reference 3 · compared 13
  2026-09-21_A_Dr. Simicskó István_q022: reference 14 · compared 13
  2026-09-22_NRE_Hortay Olivér_q018: reference 999 · compared 1
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v1_54_cap.csv
```

## sonnet_v1_54 · moral — prompt v1, 54 mondat, javítás előtti kézi kódok

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.648 · Cohen's kappa: 0.367

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
11                  29   0.54   0.66  0.86  0.75
3                   15   0.28   0.75  0.60  0.67
5                    3   0.06   0.25  0.33  0.29  (n < 10: no verdict)
6                    1   0.02    nan  0.00   nan  (n < 10: no verdict)
7                    2   0.04    nan  0.00   nan  (n < 10: no verdict)
8                    4   0.07    nan  0.00   nan  (n < 10: no verdict)

confusion matrix (rows = reference, columns = compared):
          11     3     5     6     7     8
11        25     3     1     0     0     0
3          5     9     1     0     0     0
5          2     0     1     0     0     0
6          1     0     0     0     0     0
7          1     0     1     0     0     0
8          4     0     0     0     0     0

mismatches: 19
  2026-05-26_AV_Tarr Zoltán_2_q004: reference 8 · compared 11
  2026-05-26_AV_Toroczkai László_q001: reference 3 · compared 5
  2026-05-26_NRE_Bujdosó Andrea Anna_1_q036: reference 5 · compared 11
  2026-05-26_NRE_Magyar Péter_6_q008: reference 5 · compared 11
  2026-06-01_AV_Dr. Lőrincz Viktória_3_q005: reference 3 · compared 11
  2026-06-15_I_Nacsa Lőrinc_q022: reference 8 · compared 11
  2026-06-16_NRE_Magyar Péter_4_q010: reference 11 · compared 3
  2026-06-22_NRE_Magyar Péter_1_q162: reference 11 · compared 5
  2026-06-29_AV_Tanács Zoltán_4_q003: reference 8 · compared 11
  2026-06-30_NRE_Rétvári Bence_q038: reference 3 · compared 11
  2026-07-06_IV_Németh Balázs Lajos_q011: reference 11 · compared 3
  2026-07-06_NRE_Dr. Juhász Hajnalka_q034: reference 6 · compared 11
  2026-08-27_IV_Dr. Stumpf Péter_2_q022: reference 8 · compared 11
  2026-08-27_NRE_Toroczkai László_1_q053: reference 7 · compared 5
  2026-09-07_NRE_Toroczkai László_2_q021: reference 3 · compared 11
  2026-09-14_AV_Dr. Svéd Tamás_2_q007: reference 11 · compared 3
  2026-09-14_IV_Kapitány István_q015: reference 3 · compared 11
  2026-09-14_IV_Kapitány István_q018: reference 7 · compared 11
  2026-09-21_AV_Novák Előd_q012: reference 3 · compared 11
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v1_54_moral.csv
```

## sonnet_v1_54 · erzelmes — prompt v1, 54 mondat, javítás előtti kézi kódok

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.685 · Cohen's kappa: 0.351

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
erzelmes            25   0.46   0.75  0.48  0.59
semleges            29   0.54   0.66  0.86  0.75

confusion matrix (rows = reference, columns = compared):
          erzelmes semleges
erzelmes        12       13
semleges         4       25

mismatches: 17
  2026-05-26_AV_Tarr Zoltán_2_q004: reference erzelmes · compared semleges
  2026-05-26_NRE_Bujdosó Andrea Anna_1_q036: reference erzelmes · compared semleges
  2026-05-26_NRE_Magyar Péter_6_q008: reference erzelmes · compared semleges
  2026-06-01_AV_Dr. Lőrincz Viktória_3_q005: reference erzelmes · compared semleges
  2026-06-15_I_Nacsa Lőrinc_q022: reference erzelmes · compared semleges
  2026-06-16_NRE_Magyar Péter_4_q010: reference semleges · compared erzelmes
  2026-06-22_NRE_Magyar Péter_1_q162: reference semleges · compared erzelmes
  2026-06-29_AV_Tanács Zoltán_4_q003: reference erzelmes · compared semleges
  2026-06-30_NRE_Rétvári Bence_q038: reference erzelmes · compared semleges
  2026-07-06_IV_Németh Balázs Lajos_q011: reference semleges · compared erzelmes
  2026-07-06_NRE_Dr. Juhász Hajnalka_q034: reference erzelmes · compared semleges
  2026-08-27_IV_Dr. Stumpf Péter_2_q022: reference erzelmes · compared semleges
  2026-09-07_NRE_Toroczkai László_2_q021: reference erzelmes · compared semleges
  2026-09-14_AV_Dr. Svéd Tamás_2_q007: reference semleges · compared erzelmes
  2026-09-14_IV_Kapitány István_q015: reference erzelmes · compared semleges
  2026-09-14_IV_Kapitány István_q018: reference erzelmes · compared semleges
  2026-09-21_AV_Novák Előd_q012: reference erzelmes · compared semleges
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v1_54_erzelmes.csv
```

## sonnet_v1_54_adj · cap — prompt v1, 54 mondat, egyeztetett kódok (felfelé torzít)

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.870 · Cohen's kappa: 0.848

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
1                    2   0.04   0.40  1.00  0.57  (n < 10: no verdict)
13                   4   0.07   0.80  1.00  0.89  (n < 10: no verdict)
14                   1   0.02    nan  0.00   nan  (n < 10: no verdict)
15                   4   0.07   1.00  0.25  0.40  (n < 10: no verdict)
16                   1   0.02   1.00  1.00  1.00  (n < 10: no verdict)
17                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
19                   2   0.04   1.00  1.00  1.00  (n < 10: no verdict)
2                    1   0.02   1.00  1.00  1.00  (n < 10: no verdict)
20                   7   0.13   0.88  1.00  0.93  (n < 10: no verdict)
3                    2   0.04   1.00  0.50  0.67  (n < 10: no verdict)
5                    2   0.04   1.00  1.00  1.00  (n < 10: no verdict)
6                    4   0.07   1.00  1.00  1.00  (n < 10: no verdict)
7                    1   0.02   1.00  1.00  1.00  (n < 10: no verdict)
8                    4   0.07   1.00  1.00  1.00  (n < 10: no verdict)
9                    1   0.02   1.00  1.00  1.00  (n < 10: no verdict)
999                 18   0.33   1.00  0.89  0.94

confusion matrix (rows = reference, columns = compared):
           1    13    14    15    16    17    19     2    20     3     5     6     7     8     9   999
1          2     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
13         0     4     0     0     0     0     0     0     0     0     0     0     0     0     0     0
14         0     1     0     0     0     0     0     0     0     0     0     0     0     0     0     0
15         1     0     0     1     0     2     0     0     0     0     0     0     0     0     0     0
16         0     0     0     0     1     0     0     0     0     0     0     0     0     0     0     0
17         0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
19         0     0     0     0     0     0     2     0     0     0     0     0     0     0     0     0
2          0     0     0     0     0     0     0     1     0     0     0     0     0     0     0     0
20         0     0     0     0     0     0     0     0     7     0     0     0     0     0     0     0
3          1     0     0     0     0     0     0     0     0     1     0     0     0     0     0     0
5          0     0     0     0     0     0     0     0     0     0     2     0     0     0     0     0
6          0     0     0     0     0     0     0     0     0     0     0     4     0     0     0     0
7          0     0     0     0     0     0     0     0     0     0     0     0     1     0     0     0
8          0     0     0     0     0     0     0     0     0     0     0     0     0     4     0     0
9          0     0     0     0     0     0     0     0     0     0     0     0     0     0     1     0
999        1     0     0     0     0     0     0     0     1     0     0     0     0     0     0    16

mismatches: 7
  2026-06-08_I_Dr. Latorcai Csaba_q011: reference 15 · compared 17
  2026-06-16_NRE_Magyar Péter_4_q010: reference 15 · compared 1
  2026-06-29_NRE_Toroczkai László_1_q044: reference 999 · compared 20
  2026-07-06_A_Takács Péter_q003: reference 3 · compared 1
  2026-08-27_A_Dúró Dóra_q014: reference 15 · compared 17
  2026-09-21_A_Dr. Simicskó István_q022: reference 14 · compared 13
  2026-09-22_NRE_Hortay Olivér_q018: reference 999 · compared 1
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v1_54_adj_cap.csv
```

## sonnet_v1_54_adj · moral — prompt v1, 54 mondat, egyeztetett kódok (felfelé torzít)

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.833 · Cohen's kappa: 0.683

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
11                  32   0.59   0.82  0.97  0.89
3                   13   0.24   1.00  0.92  0.96
5                    3   0.06   0.50  0.67  0.57  (n < 10: no verdict)
6                    1   0.02    nan  0.00   nan  (n < 10: no verdict)
7                    2   0.04    nan  0.00   nan  (n < 10: no verdict)
8                    3   0.06    nan  0.00   nan  (n < 10: no verdict)

confusion matrix (rows = reference, columns = compared):
          11     3     5     6     7     8
11        31     0     1     0     0     0
3          1    12     0     0     0     0
5          1     0     2     0     0     0
6          1     0     0     0     0     0
7          1     0     1     0     0     0
8          3     0     0     0     0     0

mismatches: 9
  2026-05-26_AV_Tarr Zoltán_2_q004: reference 8 · compared 11
  2026-05-26_AV_Toroczkai László_q001: reference 11 · compared 5
  2026-05-26_NRE_Bujdosó Andrea Anna_1_q036: reference 5 · compared 11
  2026-06-15_I_Nacsa Lőrinc_q022: reference 8 · compared 11
  2026-06-30_NRE_Rétvári Bence_q038: reference 3 · compared 11
  2026-07-06_NRE_Dr. Juhász Hajnalka_q034: reference 6 · compared 11
  2026-08-27_IV_Dr. Stumpf Péter_2_q022: reference 8 · compared 11
  2026-08-27_NRE_Toroczkai László_1_q053: reference 7 · compared 5
  2026-09-14_IV_Kapitány István_q018: reference 7 · compared 11
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v1_54_adj_moral.csv
```

## sonnet_v1_54_adj · erzelmes — prompt v1, 54 mondat, egyeztetett kódok (felfelé torzít)

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.852 · Cohen's kappa: 0.680

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
erzelmes            22   0.41   0.94  0.68  0.79
semleges            32   0.59   0.82  0.97  0.89

confusion matrix (rows = reference, columns = compared):
          erzelmes semleges
erzelmes        15        7
semleges         1       31

mismatches: 8
  2026-05-26_AV_Tarr Zoltán_2_q004: reference erzelmes · compared semleges
  2026-05-26_AV_Toroczkai László_q001: reference semleges · compared erzelmes
  2026-05-26_NRE_Bujdosó Andrea Anna_1_q036: reference erzelmes · compared semleges
  2026-06-15_I_Nacsa Lőrinc_q022: reference erzelmes · compared semleges
  2026-06-30_NRE_Rétvári Bence_q038: reference erzelmes · compared semleges
  2026-07-06_NRE_Dr. Juhász Hajnalka_q034: reference erzelmes · compared semleges
  2026-08-27_IV_Dr. Stumpf Péter_2_q022: reference erzelmes · compared semleges
  2026-09-14_IV_Kapitány István_q018: reference erzelmes · compared semleges
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v1_54_adj_erzelmes.csv
```

## llama31_v1_54 · cap — prompt v1, helyi llama3.1, 54 mondat

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.296 · Cohen's kappa: 0.251

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
1                    0   0.00   0.00   nan   nan  (n < 10: no verdict)
12                   2   0.04   0.00  0.00   nan  (n < 10: no verdict)
13                   2   0.04   0.40  1.00  0.57  (n < 10: no verdict)
14                   1   0.02    nan  0.00   nan  (n < 10: no verdict)
15                   3   0.06   0.00  0.00   nan  (n < 10: no verdict)
16                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
17                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
18                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
19                   2   0.04   0.29  1.00  0.44  (n < 10: no verdict)
2                    0   0.00   0.00   nan   nan  (n < 10: no verdict)
20                   7   0.13   0.60  0.43  0.50  (n < 10: no verdict)
3                    3   0.06   1.00  0.33  0.50  (n < 10: no verdict)
5                    2   0.04   0.00  0.00   nan  (n < 10: no verdict)
6                    2   0.04   0.25  1.00  0.40  (n < 10: no verdict)
7                    1   0.02   0.50  1.00  0.67  (n < 10: no verdict)
8                    4   0.07   0.50  0.50  0.50  (n < 10: no verdict)
9                    1   0.02    nan  0.00   nan  (n < 10: no verdict)
999                 24   0.44   1.00  0.12  0.22

confusion matrix (rows = reference, columns = compared):
           1    12    13    14    15    16    17    18    19     2    20     3     5     6     7     8     9   999
1          0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
12         0     0     1     0     0     0     0     0     0     0     1     0     0     0     0     0     0     0
13         0     0     2     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
14         0     0     1     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
15         1     0     0     0     0     0     0     1     0     1     0     0     0     0     0     0     0     0
16         0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
17         0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
18         0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
19         0     0     0     0     0     0     0     0     2     0     0     0     0     0     0     0     0     0
2          0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0     0
20         0     0     0     0     0     0     0     0     1     1     3     0     0     2     0     0     0     0
3          0     0     1     0     1     0     0     0     0     0     0     1     0     0     0     0     0     0
5          0     1     0     0     0     0     0     0     0     0     0     0     0     1     0     0     0     0
6          0     0     0     0     0     0     0     0     0     0     0     0     0     2     0     0     0     0
7          0     0     0     0     0     0     0     0     0     0     0     0     0     0     1     0     0     0
8          1     0     0     0     1     0     0     0     0     0     0     0     0     0     0     2     0     0
9          0     0     0     0     0     0     0     0     1     0     0     0     0     0     0     0     0     0
999        3     0     0     0     0     1     1     0     3     5     1     0     1     3     1     2     0     3

mismatches: 38
  2026-05-26_AV_Toroczkai László_q001: reference 999 · compared 2
  2026-05-26_I_Dr. Máthé Zsuzsa_q008: reference 999 · compared 19
  2026-05-26_NRE_Bujdosó Andrea Anna_1_q036: reference 999 · compared 2
  2026-05-26_NRE_Magyar Péter_6_q008: reference 999 · compared 2
  2026-05-27_NRE_Bencsik János_q030: reference 5 · compared 6
  2026-06-01_AV_Kármán András_1_q011: reference 999 · compared 5
  2026-06-01_NRE_Magyar Péter_2_q067: reference 999 · compared 17
  2026-06-08_I_Dr. Latorcai Csaba_q011: reference 12 · compared 20
  2026-06-08_NRE_Toroczkai László_1_q038: reference 9 · compared 19
  2026-06-15_AV_Dócs Dávid_q008: reference 999 · compared 7
  2026-06-15_I_Nacsa Lőrinc_q022: reference 999 · compared 8
  2026-06-15_I_Novák Előd_q013: reference 999 · compared 16
  2026-06-16_NRE_Magyar Péter_4_q010: reference 15 · compared 1
  2026-06-22_NRE_Magyar Péter_1_q162: reference 20 · compared 2
  2026-06-29_AV_Németh Balázs Lajos_q007: reference 999 · compared 1
  2026-06-29_AV_Tanács Zoltán_4_q003: reference 20 · compared 6
  2026-06-29_IV_Nacsa Lőrinc_q010: reference 999 · compared 2
  2026-06-29_NRE_Magyar Péter_1_q375: reference 999 · compared 6
  2026-06-29_NRE_Toroczkai László_1_q044: reference 999 · compared 2
  2026-06-30_NRE_Toroczkai László_1_q019: reference 999 · compared 20
  2026-07-06_A_Takács Péter_q003: reference 3 · compared 15
  2026-07-06_NRE_Dr. Juhász Hajnalka_q034: reference 12 · compared 13
  2026-07-21_NRE_Magyar Péter_3_q061: reference 8 · compared 15
  2026-07-27_NRE_Rétvári Bence_q050: reference 999 · compared 1
  2026-08-10_AV_Tompa Enikő_1_q016: reference 20 · compared 19
  2026-08-10_IV_Dr. Kátai-Németh Vilmos_q018: reference 999 · compared 6
  2026-08-27_A_Dúró Dóra_q014: reference 15 · compared 18
  2026-08-27_IV_Dr. Stumpf Péter_2_q022: reference 20 · compared 6
  2026-08-27_NRE_Toroczkai László_1_q053: reference 999 · compared 8
  2026-09-07_NRE_Dr. Bóka János_2_q018: reference 999 · compared 6
  2026-09-07_NRE_Magyar Péter_7_q009: reference 5 · compared 12
  2026-09-07_NRE_Toroczkai László_2_q021: reference 999 · compared 19
  2026-09-14_AV_Dr. Svéd Tamás_2_q007: reference 15 · compared 2
  2026-09-14_IV_Dr. Apáti István_q007: reference 3 · compared 13
  2026-09-21_A_Dr. Simicskó István_q022: reference 14 · compared 13
  2026-09-21_NRE_Magyar Péter_4_q215: reference 999 · compared 19
  2026-09-22_NRE_Hortay Olivér_q018: reference 999 · compared 1
  2026-09-28_AV_Rétvári Bence_q010: reference 8 · compared 1
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_llama31_v1_54_cap.csv
```

## llama31_v1_54 · moral — prompt v1, helyi llama3.1, 54 mondat

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.574 · Cohen's kappa: 0.414

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
11                  29   0.54   0.81  0.45  0.58
3                   15   0.28   0.58  0.73  0.65
4                    0   0.00   0.00   nan   nan  (n < 10: no verdict)
5                    3   0.06    nan  0.00   nan  (n < 10: no verdict)
6                    1   0.02   0.50  1.00  0.67  (n < 10: no verdict)
7                    2   0.04   0.20  1.00  0.33  (n < 10: no verdict)
8                    4   0.07   0.67  1.00  0.80  (n < 10: no verdict)

confusion matrix (rows = reference, columns = compared):
          11     3     4     5     6     7     8
11        13     8     0     0     1     6     1
3          2    11     1     0     0     1     0
4          0     0     0     0     0     0     0
5          1     0     0     0     0     1     1
6          0     0     0     0     1     0     0
7          0     0     0     0     0     2     0
8          0     0     0     0     0     0     4

mismatches: 23
  2026-05-26_I_Dr. Máthé Zsuzsa_q008: reference 11 · compared 3
  2026-05-26_NRE_Bujdosó Andrea Anna_1_q036: reference 5 · compared 7
  2026-05-26_NRE_Magyar Péter_6_q008: reference 5 · compared 8
  2026-05-27_NRE_Dr. Juhász Hajnalka_q008: reference 11 · compared 8
  2026-06-01_AV_Dr. Lőrincz Viktória_3_q005: reference 3 · compared 11
  2026-06-01_NRE_Magyar Péter_2_q067: reference 5 · compared 11
  2026-06-08_I_Dr. Latorcai Csaba_q011: reference 11 · compared 3
  2026-06-15_AV_Dócs Dávid_q008: reference 11 · compared 7
  2026-06-15_I_Nacsa Lőrinc_q012: reference 11 · compared 7
  2026-06-16_NRE_Magyar Péter_4_q010: reference 11 · compared 3
  2026-06-29_AV_Németh Balázs Lajos_q007: reference 11 · compared 3
  2026-06-29_NRE_Magyar Péter_1_q375: reference 11 · compared 6
  2026-06-30_NRE_Rétvári Bence_q038: reference 3 · compared 7
  2026-07-06_IV_Németh Balázs Lajos_q011: reference 11 · compared 3
  2026-07-27_NRE_Rétvári Bence_q050: reference 11 · compared 7
  2026-09-14_AV_Dr. Svéd Tamás_2_q007: reference 11 · compared 3
  2026-09-14_A_Dr. Németh Csilla_q011: reference 11 · compared 7
  2026-09-14_IV_Kapitány István_q015: reference 3 · compared 11
  2026-09-21_A_Dr. Simicskó István_q022: reference 11 · compared 7
  2026-09-21_I_Dr. Takács Árpád_q005: reference 11 · compared 7
  2026-09-21_NRE_Magyar Péter_4_q215: reference 3 · compared 4
  2026-09-22_NRE_Hortay Olivér_q018: reference 11 · compared 3
  2026-09-28_AV_Rétvári Bence_q010: reference 11 · compared 3
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_llama31_v1_54_moral.csv
```

## llama31_v1_54 · erzelmes — prompt v1, helyi llama3.1, 54 mondat

```
hand rows: 54 · machine rows: 54 · matched by 'file': 54
matched units: 54 · exact agreement: 0.648 · Cohen's kappa: 0.317

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
erzelmes            25   0.46   0.58  0.88  0.70
semleges            29   0.54   0.81  0.45  0.58

confusion matrix (rows = reference, columns = compared):
          erzelmes semleges
erzelmes        22        3
semleges        16       13

mismatches: 19
  2026-05-26_I_Dr. Máthé Zsuzsa_q008: reference semleges · compared erzelmes
  2026-05-27_NRE_Dr. Juhász Hajnalka_q008: reference semleges · compared erzelmes
  2026-06-01_AV_Dr. Lőrincz Viktória_3_q005: reference erzelmes · compared semleges
  2026-06-01_NRE_Magyar Péter_2_q067: reference erzelmes · compared semleges
  2026-06-08_I_Dr. Latorcai Csaba_q011: reference semleges · compared erzelmes
  2026-06-15_AV_Dócs Dávid_q008: reference semleges · compared erzelmes
  2026-06-15_I_Nacsa Lőrinc_q012: reference semleges · compared erzelmes
  2026-06-16_NRE_Magyar Péter_4_q010: reference semleges · compared erzelmes
  2026-06-29_AV_Németh Balázs Lajos_q007: reference semleges · compared erzelmes
  2026-06-29_NRE_Magyar Péter_1_q375: reference semleges · compared erzelmes
  2026-07-06_IV_Németh Balázs Lajos_q011: reference semleges · compared erzelmes
  2026-07-27_NRE_Rétvári Bence_q050: reference semleges · compared erzelmes
  2026-09-14_AV_Dr. Svéd Tamás_2_q007: reference semleges · compared erzelmes
  2026-09-14_A_Dr. Németh Csilla_q011: reference semleges · compared erzelmes
  2026-09-14_IV_Kapitány István_q015: reference erzelmes · compared semleges
  2026-09-21_A_Dr. Simicskó István_q022: reference semleges · compared erzelmes
  2026-09-21_I_Dr. Takács Árpád_q005: reference semleges · compared erzelmes
  2026-09-22_NRE_Hortay Olivér_q018: reference semleges · compared erzelmes
  2026-09-28_AV_Rétvári Bence_q010: reference semleges · compared erzelmes
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_llama31_v1_54_erzelmes.csv
```

## sonnet_v2_v3 · cap — VÉGSŐ: prompt v2, friss vak minta, 24 mondat

```
hand rows: 24 · machine rows: 24 · matched by 'file': 24
matched units: 24 · exact agreement: 0.750 · Cohen's kappa: 0.720

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
1                    2   0.08   1.00  0.50  0.67  (n < 10: no verdict)
10                   1   0.04   1.00  1.00  1.00  (n < 10: no verdict)
13                   3   0.12   1.00  1.00  1.00  (n < 10: no verdict)
14                   1   0.04   1.00  1.00  1.00  (n < 10: no verdict)
15                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
19                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
2                    1   0.04   0.00  0.00   nan  (n < 10: no verdict)
20                   6   0.25   1.00  0.67  0.80  (n < 10: no verdict)
21                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
3                    3   0.12   1.00  1.00  1.00  (n < 10: no verdict)
6                    3   0.12   1.00  0.67  0.80  (n < 10: no verdict)
7                    2   0.08   1.00  0.50  0.67  (n < 10: no verdict)
999                  2   0.08   0.67  1.00  0.80  (n < 10: no verdict)

confusion matrix (rows = reference, columns = compared):
           1    10    13    14    15    19     2    20    21     3     6     7   999
1          1     0     0     0     1     0     0     0     0     0     0     0     0
10         0     1     0     0     0     0     0     0     0     0     0     0     0
13         0     0     3     0     0     0     0     0     0     0     0     0     0
14         0     0     0     1     0     0     0     0     0     0     0     0     0
15         0     0     0     0     0     0     0     0     0     0     0     0     0
19         0     0     0     0     0     0     0     0     0     0     0     0     0
2          0     0     0     0     0     1     0     0     0     0     0     0     0
20         0     0     0     0     1     0     0     4     0     0     0     0     1
21         0     0     0     0     0     0     0     0     0     0     0     0     0
3          0     0     0     0     0     0     0     0     0     3     0     0     0
6          0     0     0     0     0     0     1     0     0     0     2     0     0
7          0     0     0     0     0     0     0     0     1     0     0     1     0
999        0     0     0     0     0     0     0     0     0     0     0     0     2

mismatches: 6
  2026-06-15_NRE_Magyar Péter_2_q048: reference 2 · compared 19
  2026-07-07_NRE_Dr. Kovács Gyula_q009: reference 7 · compared 21
  2026-07-20_IV_Tarr Zoltán_q021: reference 6 · compared 2
  2026-09-07_A_Dr. Takács Árpád_q008: reference 20 · compared 999
  2026-09-14_AV_Boda Nikoletta_1_q005: reference 1 · compared 15
  2026-09-21_I_Szabadi István_q007: reference 20 · compared 15
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v2_v3_cap.csv
```

## sonnet_v2_v3 · moral — VÉGSŐ: prompt v2, friss vak minta, 24 mondat

```
hand rows: 24 · machine rows: 24 · matched by 'file': 24
matched units: 24 · exact agreement: 0.583 · Cohen's kappa: 0.363

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
11                  12   0.50   0.83  0.83  0.83
3                    5   0.21   0.30  0.60  0.40  (n < 10: no verdict)
4                    1   0.04   0.00  0.00   nan  (n < 10: no verdict)
5                    4   0.17   1.00  0.25  0.40  (n < 10: no verdict)
6                    1   0.04    nan  0.00   nan  (n < 10: no verdict)
8                    1   0.04    nan  0.00   nan  (n < 10: no verdict)

confusion matrix (rows = reference, columns = compared):
          11     3     4     5     6     8
11        10     1     1     0     0     0
3          2     3     0     0     0     0
4          0     1     0     0     0     0
5          0     3     0     1     0     0
6          0     1     0     0     0     0
8          0     1     0     0     0     0

mismatches: 10
  2026-06-15_AV_Kapronczai Balázs_1_q004: reference 3 · compared 11
  2026-06-22_IV_F. Kovács Sándor_q012: reference 4 · compared 3
  2026-07-20_IV_Tarr Zoltán_q021: reference 5 · compared 3
  2026-09-07_A_Dr. Takács Árpád_q008: reference 5 · compared 3
  2026-09-07_NRE_Magyar Péter_7_q003: reference 5 · compared 3
  2026-09-14_AV_Boda Nikoletta_1_q005: reference 6 · compared 3
  2026-09-14_A_Muhari Gergely_q011: reference 3 · compared 11
  2026-09-15_NRE_Kulcsár Krisztián_q021: reference 11 · compared 3
  2026-09-21_AV_Boda Nikoletta_2_q005: reference 8 · compared 3
  2026-09-21_I_Szabadi István_q007: reference 11 · compared 4
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v2_v3_moral.csv
```

## sonnet_v2_v3 · erzelmes — VÉGSŐ: prompt v2, friss vak minta, 24 mondat

```
hand rows: 24 · machine rows: 24 · matched by 'file': 24
matched units: 24 · exact agreement: 0.833 · Cohen's kappa: 0.667

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
erzelmes            12   0.50   0.83  0.83  0.83
semleges            12   0.50   0.83  0.83  0.83

confusion matrix (rows = reference, columns = compared):
          erzelmes semleges
erzelmes        10        2
semleges         2       10

mismatches: 4
  2026-06-15_AV_Kapronczai Balázs_1_q004: reference erzelmes · compared semleges
  2026-09-14_A_Muhari Gergely_q011: reference erzelmes · compared semleges
  2026-09-15_NRE_Kulcsár Krisztián_q021: reference semleges · compared erzelmes
  2026-09-21_I_Szabadi István_q007: reference semleges · compared erzelmes
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_sonnet_v2_v3_erzelmes.csv
```

## haiku_v2_v3 · cap — VÉGSŐ: prompt v2, friss vak minta, 24 mondat (korpuszt kódoló modell)

```
hand rows: 24 · machine rows: 24 · matched by 'file': 24
matched units: 24 · exact agreement: 0.708 · Cohen's kappa: 0.671

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
1                    2   0.08   1.00  0.50  0.67  (n < 10: no verdict)
10                   1   0.04   1.00  1.00  1.00  (n < 10: no verdict)
13                   3   0.12   1.00  1.00  1.00  (n < 10: no verdict)
14                   1   0.04   1.00  1.00  1.00  (n < 10: no verdict)
15                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
19                   0   0.00   0.00   nan   nan  (n < 10: no verdict)
2                    1   0.04   0.00  0.00   nan  (n < 10: no verdict)
20                   6   0.25   0.80  0.67  0.73  (n < 10: no verdict)
3                    3   0.12   1.00  1.00  1.00  (n < 10: no verdict)
6                    3   0.12   1.00  0.33  0.50  (n < 10: no verdict)
7                    2   0.08   1.00  0.50  0.67  (n < 10: no verdict)
999                  2   0.08   0.50  1.00  0.67  (n < 10: no verdict)

confusion matrix (rows = reference, columns = compared):
           1    10    13    14    15    19     2    20     3     6     7   999
1          1     0     0     0     1     0     0     0     0     0     0     0
10         0     1     0     0     0     0     0     0     0     0     0     0
13         0     0     3     0     0     0     0     0     0     0     0     0
14         0     0     0     1     0     0     0     0     0     0     0     0
15         0     0     0     0     0     0     0     0     0     0     0     0
19         0     0     0     0     0     0     0     0     0     0     0     0
2          0     0     0     0     0     1     0     0     0     0     0     0
20         0     0     0     0     0     0     0     4     0     0     0     2
3          0     0     0     0     0     0     0     0     3     0     0     0
6          0     0     0     0     0     0     1     1     0     1     0     0
7          0     0     0     0     1     0     0     0     0     0     1     0
999        0     0     0     0     0     0     0     0     0     0     0     2

mismatches: 7
  2026-06-15_NRE_Magyar Péter_2_q048: reference 2 · compared 19
  2026-07-07_NRE_Dr. Kovács Gyula_q009: reference 7 · compared 15
  2026-07-20_IV_Tarr Zoltán_q021: reference 6 · compared 2
  2026-09-07_A_Dr. Takács Árpád_q008: reference 20 · compared 999
  2026-09-07_NRE_Magyar Péter_7_q003: reference 6 · compared 20
  2026-09-14_AV_Boda Nikoletta_1_q005: reference 1 · compared 15
  2026-09-21_I_Szabadi István_q007: reference 20 · compared 999
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_haiku_v2_v3_cap.csv
```

## haiku_v2_v3 · moral — VÉGSŐ: prompt v2, friss vak minta, 24 mondat (korpuszt kódoló modell)

```
hand rows: 24 · machine rows: 24 · matched by 'file': 24
matched units: 24 · exact agreement: 0.708 · Cohen's kappa: 0.568

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
11                  12   0.50   0.83  0.83  0.83
3                    5   0.21   0.57  0.80  0.67  (n < 10: no verdict)
4                    1   0.04   0.50  1.00  0.67  (n < 10: no verdict)
5                    4   0.17   1.00  0.25  0.40  (n < 10: no verdict)
6                    1   0.04   0.50  1.00  0.67  (n < 10: no verdict)
8                    1   0.04    nan  0.00   nan  (n < 10: no verdict)

confusion matrix (rows = reference, columns = compared):
          11     3     4     5     6     8
11        10     0     1     0     1     0
3          1     4     0     0     0     0
4          0     0     1     0     0     0
5          0     3     0     1     0     0
6          0     0     0     0     1     0
8          1     0     0     0     0     0

mismatches: 7
  2026-06-15_AV_Kapronczai Balázs_1_q004: reference 3 · compared 11
  2026-07-20_IV_Tarr Zoltán_q021: reference 5 · compared 3
  2026-09-07_A_Dr. Takács Árpád_q008: reference 5 · compared 3
  2026-09-07_NRE_Magyar Péter_7_q003: reference 5 · compared 3
  2026-09-14_I_Göröghné Bocskai Éva_q020: reference 11 · compared 6
  2026-09-21_AV_Boda Nikoletta_2_q005: reference 8 · compared 11
  2026-09-21_I_Szabadi István_q007: reference 11 · compared 4
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_haiku_v2_v3_moral.csv
```

## haiku_v2_v3 · erzelmes — VÉGSŐ: prompt v2, friss vak minta, 24 mondat (korpuszt kódoló modell)

```
hand rows: 24 · machine rows: 24 · matched by 'file': 24
matched units: 24 · exact agreement: 0.833 · Cohen's kappa: 0.667

per category (reference = first file / first coder):
code             n_ref   base   prec   rec    F1
erzelmes            12   0.50   0.83  0.83  0.83
semleges            12   0.50   0.83  0.83  0.83

confusion matrix (rows = reference, columns = compared):
          erzelmes semleges
erzelmes        10        2
semleges         2       10

mismatches: 4
  2026-06-15_AV_Kapronczai Balázs_1_q004: reference erzelmes · compared semleges
  2026-09-14_I_Göröghné Bocskai Éva_q020: reference semleges · compared erzelmes
  2026-09-21_AV_Boda Nikoletta_2_q005: reference erzelmes · compared semleges
  2026-09-21_I_Szabadi István_q007: reference semleges · compared erzelmes
written: C:\Users\petra\Documents\antigravity\parlamenti-projekt\gold_standard\mismatches_haiku_v2_v3_erzelmes.csv
```
