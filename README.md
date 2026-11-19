# Témák és érzelmek három parlamenti műfajban (2026) — adat, kód, kódkönyv

Zsovák Norbert · Bibó István Szakkollégium · Mesterséges intelligencia a társadalom- és politikatudományi kutatásban ·
2026. ősz

A repó a tanulmány reprodukciós csomagja: **adat, kód és kódkönyv**. A tanulmány (PDF) külön került leadásra.

## Kérdés és hipotézisek
Miről és mennyire érzelmesen beszélnek a képviselők a napirend előtti felszólalásokban, az interpellációkban és az
azonnali kérdésekben a 43. ciklus első 30 ülésnapján (2026. május 26. – szeptember 28.)?
- **H1** — a napirend előtti felszólalás a legérzelmesebb: **igazolódott** (+10,2 százalékpont az interpellációhoz
  képest, 95% CI 6,1–14,3; pártokra és Magyar Péterre kontrollálva +9,6).
- **H2** — az interpelláció a legkonkrétabb: **igazolódott** (itt a legkevesebb a téma nélküli, 34%, és az általános
  kormányzati, 15%, kvázi mondat).

## Reprodukció egy paranccsal
```bash
pip install pandas numpy matplotlib openpyxl
python reproduce_v2.py
```
Az eredmények (táblák, ábrák, `results.json`) az `output_v2/` mappába kerülnek; a repóban lévő változattal
összevethetők.

## Tartalom
| | Fájl / mappa | Tartalom |
|---|---|---|
| **Adat** | `parlamenti_felszolalasok_2026_teljes.sqlite`, `.csv` | 1 284 felszólalás szövege és metaadatai (parlament.hu) |
| | `adatgyujtes/` | a letöltő és összefésülő szkriptek, nyers letöltések |
| | `coding/` | a gépi kódolás bemenete (`batches/`), kimenete (`out/`), ellenőrzött összesítése (`labels_full.csv`) |
| | `gold_standard/` | vak kézi kódolás, mintavétel, egyeztetés, egyezésmérés |
| **Kód** | `reproduce_v2.py` | a teljes elemzés egy paranccsal |
| | `clean_quasi_sentences_v2.py` | kvázi mondatok, szerep (kezdeményező/válaszoló), közbeszólások |
| | `analysis/analyze_v2.py` | statisztikák, táblák, ábrák → `output_v2/` |
| **Kódkönyv** | `codebooks/CODEBOOK_PARLAMENTI_KORPUSZ_2026.md` | a korpusz és minden változó leírása (6. fejezet: v2) |
| | `codebooks/codebook_cap.md` | CAP-főtémák, döntési szabályok (v2.1) |
| | `codebooks/codebook_moral_emotions.md` | morális érzelmek, döntési szabályok (v2.1) |
| | `gold_standard/prompt_v2.md` | a nyelvi modell rögzített kódolási utasítása |
| Napló | `NAPLO.md` | minden lépés és döntés időrendben |

## Validálás
| Ellenőrzés | n | Téma κ | Érzelmes/semleges κ |
|---|---:|---:|---:|
| Vak kézi minta vs. a korpuszt kódoló modell (Claude Haiku) | 24 | 0,67 | 0,67 |
| Két független gépi futás | 250 | 0,81 | 0,70 |

κ = Cohen-féle kappa (0 = véletlen egyezés, 1 = tökéletes). A projekt egy korábbi változatának egyezési értékei nem
független gépi kódolásból származtak, ezért elvetettem őket (részletek: `NAPLO.md`). A repó a beadandó anyagot
tartalmazza; a korábbi munkaváltozatok teljes előzménye a szerzőnél, git-mentésben (bundle) megvan, kérésre átadható.

## MI-nyilatkozat
- **Eszköz:** Claude Code (Claude Opus; a kódoláshoz Claude Haiku és Sonnet), korábban Google Antigravity (Gemini).
- **Mit végzett:** a letöltő és elemző kódot, a 15 073 kezdeményező kvázi mondat téma- és érzelemkódolását, a
  statisztikákat és az ábrákat.
- **Hogyan ellenőriztem:** 78 kvázi mondat vak kézi kódolása és az eltérések egyenkénti eldöntése; a végleges gépi
  kódolás mérése friss, vak mintán (κ = 0,67); két független gépi futás összevetése (κ = 0,70–0,81); adagonkénti
  teljességi ellenőrzés (`coding/merge_labels.py`); a teljes folyamat újrafuttatása (`reproduce_v2.py`); a korábbi,
  nem független validálás feltárása és elvetése.
- **Fennmaradó kockázat:** a kézi ellenőrző minta kicsi; az érzelemtípusok gépi megkülönböztetése csak közepes
  (κ = 0,57), ezért a fő mérőszám az érzelmes/semleges besorolás; az érzelmes arány szintje futásonként kissé eltér,
  ezért a műfajok közti különbségek megbízhatóbbak a szinteknél; az eredmények leíró jellegűek.
