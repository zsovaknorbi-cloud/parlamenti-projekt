# Kvázi mondatok v2 — tisztítási jelentés

Szkript: `clean_quasi_sentences_v2.py` · bemenet: `kvazi_mondatok` tábla (39 895 egység) · kimenet: `parlamenti_kvazi_mondatok_2026_v2.csv` (39 905 egység)

## Ellenőrzések

- Egyedi azonosítók: igen (39 905); minden régi azonosító megvan: igen.
- Aranystandard-azonosítók a kimenetben: 54/54.
- Szavak száma a régi és az új egységekben: 542 386 → 542 386 (a szöveg nem veszett el; a közbeszólás külön oszlopba került, de a `mondat_szoveg` változatlan).
- Elmaradt mondatvég-vágás javítva: 10 egység.
- Közbeszólást tartalmazó egység: 4 577.

## Egységtípusok

| Típus | Egység | Arány |
|---|---:|---:|
| tartalmi | 34 593 | 86.7% |
| eljarasi | 3 917 | 9.8% |
| kozbeszolas | 1 395 | 3.5% |

Az elemzés nevezője a **tartalmi** egység; az eljárási formulák és a közbeszólás-egységek kimaradnak.

## Tartalmi egységek műfaj és szerep szerint

| Műfaj | kezdeményező | kormányzati válaszadó | frakció-hozzászóló |
|---|---:|---:|---:|
| napirend előtt | 8 968 | 8 834 | 5 123 |
| interpelláció | 2 989 | 2 574 | 0 |
| azonnali kérdés | 3 116 | 2 989 | 0 |

| Szerep | kormány | ellenzék |
|---|---:|---:|
| kezdemenyezo | 6 286 | 8 787 |
| kormanyzati_valaszado | 14 397 | 0 |
| frakcio_hozzaszolo | 971 | 4 152 |

## party javítások (party → party_v2)

| eredeti party | felszólaló | party_v2 | egység |
|---|---|---|---:|
| Kormányzat / Egyéb | Vitézy Dávid | Kormány (nem képviselő) | 394 |
| közlekedési és beruházási miniszter | Vitézy Dávid | Kormány (nem képviselő) | 211 |
| Kormányzat / Egyéb | Dr. Svéd Tamás | Kormány (nem képviselő) | 198 |
| Kormányzat / Egyéb | Bóna Szabolcs János | Kormány (nem képviselő) | 158 |
| Független / Kormányzati tisztségviselő | Dr. Baka András | Kormány (nem képviselő) | 105 |
| Kormányzat / Egyéb | Dr. Törőcsikné Dr. Görög Márta | Kormány (nem képviselő) | 84 |
| Kormányzat / Egyéb | Varga Mihály | Kormány (nem képviselő) | 63 |
| Miniszterelnökséget vezető miniszter | Dr. Ruff Bálint György | Kormány (nem képviselő) | 55 |
| Kormányzat / Egyéb | Lannert Judit Orsolya | Kormány (nem képviselő) | 52 |
| Kormányzat / Egyéb | Dr. Ruff Bálint György | Kormány (nem képviselő) | 49 |
| Független / Kormányzati tisztségviselő | Holecz Károly | Kormány (nem képviselő) | 36 |
| Független / Kormányzati tisztségviselő | Grexa Liliána | Kormány (nem képviselő) | 34 |
| igazságügyi miniszter | Dr. Törőcsikné Dr. Görög Márta | Kormány (nem képviselő) | 23 |

## Szegmentálás vs. egyszerű mondatszámlálás (beszédenként)

Arány = nem-közbeszólás egységek száma / írásjel alapján számolt mondatok száma. 1 fölött: a bontó a mondatokat tagmondatokra is vágta (ez a szándék).

- medián: 1.24 · 5. percentilis: 1.00 · 95. percentilis: 1.56
- legkisebb arányú beszédek (gyanú: elmaradt vágás):
  - `2026-06-29_IV_Dr. Árvay Nikolett_1`: 2 egység / 3 mondat = 0.67
  - `2026-06-29_IV_Magyar Péter_2`: 2 egység / 3 mondat = 0.67
  - `2026-08-10_NRE_Gyöngyösi István_1`: 5 egység / 6 mondat = 0.83
  - `2026-09-14_NRE_Magyar Péter_6`: 12 egység / 14 mondat = 0.86
  - `2026-06-08_AV_Magyar Péter_5`: 18 egység / 20 mondat = 0.90
- legnagyobb arányú beszédek (gyanú: túlvágás):
  - `2026-09-15_NRE_Kulcsár Krisztián`: 57 egység / 25 mondat = 2.28
  - `2026-05-26_AV_Vitézy Dávid_2`: 10 egység / 4 mondat = 2.50
  - `2026-08-10_IV_Göröghné Bocskai Éva`: 8 egység / 3 mondat = 2.67
  - `2026-05-26_AV_Gajdos László_2`: 10 egység / 3 mondat = 3.33
  - `2026-06-16_NRE_Magyar Péter_6`: 54 egység / 8 mondat = 6.75

## Példák

Szétvágott mondatvégek:
- Holnap Semmelweis-nap. | Orvosként hatalmas megtiszteltetés számomra ezen jeles nap a
- Érdekelne minket, hogy miért csökkent ennyivel ez a szám. | Ennyiben javultak esetleg a szegénységi mutatók a korábban k
- Ez történelmi nap. | Tényleg nagy lehet a verseny a Fidesz-frakcióvezetői pozíció
- Már az is jó hír, hogy már csak körülbelül 130 ezer főről va | Köszönöm, hogy a komplex problémára komplexen néznek rá, és 
- Emlékszik arra, amikor azt mondta, és itt viccelődött, azt m | De most, az augusztus 20-ai ügyben, amely ügyben a Mi Hazánk

Közbeszólás kiemelése (eredeti → tiszta | közbeszólás):
- „(Derültség.) Meggyőződésem, hogy ez fog igazából előrevezetni minket.” → „Meggyőződésem, hogy ez fog igazából előrevezetni minket.” | „(Derültség.)”
- „mert eltérőek a mértékek, és onnantól kezdve (Az elnök a csengő megkocogtatásával jelzi az időkeret leteltét.) meg tudjuk kezdeni a mentesít” → „mert eltérőek a mértékek, és onnantól kezdve meg tudjuk kezdeni a mentesítést, amiben nagy segítsége” | „(Az elnök a csengő megkocogtatásával jelzi az időkeret leteltét.)”
- „(Derültség a kormánypárt soraiban.) Világosan elmondtuk az álláspontunkat ‑ világosan elmondtuk az álláspontunkat! ‑, beszéltem a Bizottság ” → „Világosan elmondtuk az álláspontunkat ‑ világosan elmondtuk az álláspontunkat! ‑, beszéltem a Bizott” | „(Derültség a kormánypárt soraiban.)”
- „Ez a napi egymillió eurós büntetés ‑ helyesen mondta, már majdnem 400 milliárdnál tartunk ‑ (A Fidesz- és a KDNP-frakció felé mutatva” → „Ez a napi egymillió eurós büntetés ‑ helyesen mondta, már majdnem 400 milliárdnál tartunk” | „(A Fidesz- és a KDNP-frakció felé mutatva”
- „) ezeknek az uraknak és hölgyeknek köszönhető.” → „ezeknek az uraknak és hölgyeknek köszönhető.” | „)”
- „Mert vannak jó jogászok, nem Bóka Jánosra gondolok (Derültség a kormánypárt soraiban.)” → „Mert vannak jó jogászok, nem Bóka Jánosra gondolok” | „(Derültség a kormánypárt soraiban.)”
