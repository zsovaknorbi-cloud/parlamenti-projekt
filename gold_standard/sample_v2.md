# Aranystandard v2 — mintavételi napló

## A régi 30 mondat (`hand_coding_sablon.csv`, `gold_standard/hand_*.csv`)
- A kézi kódolás **vak** volt: a kódoló csak a mondatokat kapta meg Excelben, gépi címkét nem látott.
- 28 mondat véletlen mintából származik (`generate_fresh_hand_coding_csv.py`, `ORDER BY RANDOM()`, seed nélkül,
  8–28 szó, frakciókvótával).
- **2 mondatot utólag, kulcsszavas kereséssel cseréltek be** (`tune_9_30.py`, `fix_30.py`); ezek nem véletlen minta:
  - 9. sor: `2026-05-27_NRE_Dr. Juhász Hajnalka_q008` (KDNP, `LIKE '%keresztény%'`)
  - 30. sor: `2026-06-08_NRE_Toroczkai László_1_q038` (Mi Hazánk, `LIKE '%föld%'`)

  Az egyezésszámításban ezeket külön jelöljük (érzékenységvizsgálat: velük és nélkülük).

## Az új 24 mondat (`hand_coding_v2.xlsx`)
- Szkript: `gold_standard/sample_v2.py`, seed = 20261118, újrafuttatva ugyanazt adja.
- Rétegzett véletlen minta: 3 műfaj × 2 szerep (kezdeményező / válaszoló), rétegenként 4 mondat.
- Keret: 8–30 szavas kvázi mondatok, zárójeles vagy zárójel nélküli közbeszólás és eljárási formula nélkül;
  a korábban kiválasztott mondatok kizárva.
- A tábla sorrendje véletlen; a rétegek a `sample_v2_manifest.csv`-ben vannak, a kódolónak nem kell látnia.
- Vak kódolás: a táblában nincs gépi címke.

Együtt: 28 véletlen + 2 cserélt + 24 új = 54 kézzel kódolt mondat.
