# Projektnapló — újrafeldolgozás (2026. november)

Cél: a leadott elemzés módszertani hibáinak javítása, és minden lépés rögzítése, hogy a végén a tanulmány,
a kódkönyv (`codebooks/CODEBOOK_PARLAMENTI_KORPUSZ_2026.md`) és a README frissíthető legyen.
Ág: `gold-standard-v2`. A régi fájlokat nem írjuk felül; minden új kimenet verziózott (`_v2`).

Jelölés: **[DOKUMENTÁCIÓBA]** = ezt a tanulmányba / kódkönyvbe át kell vezetni.

---

## 2026-11-18 — Átvilágítás (csak olvasás)

### Mit találtunk
1. **Az osztályozó kulcsszavas regex** (`classify_full_corpus.py`): az első egyező kulcsszó dönt.
   Következmények: „eredmény”, „köszönjük”, „felelősen” → büszkeség; minden ≥6 szavas, kulcsszó nélküli mondat
   → CAP 20 (ezért 64–69% CAP 20 az ellenzéknél).
2. **Az egyezést (κ = 0,73 / 0,75) nem a korpuszt kódoló géppel mérték.** A `gold_standard/labels_*.csv`
   egy Gemini-modell címkéi erre a 30 mondatra; a teljes korpuszt a regex kódolta. A kettő 0/30-ban egyezik.
   A kézi kódokat a ténylegesen használt regex-kódokhoz mérve: CAP főtéma kb. 5/30, érzelem 17/30,
   de a 15 érzelmes mondatból a regex csak 2-t talál meg (érzékenység ≈ 0,13, nem 0,64).
   **[DOKUMENTÁCIÓBA]** a régi validációs számok nem érvényesek a közölt eredményekre.
3. **A régi 30 mondatos minta:** a kézi kódolás vak volt (Excel, gépi címke nélkül) — ez rendben van.
   28 mondat véletlen mintából; **2 mondatot utólag kulcsszavas kereséssel cseréltek be** (`tune_9_30.py`,
   `fix_30.py`): a 9. (Juhász Hajnalka, „keresztény”) és a 30. (Toroczkai László, „föld”). Mindkettő kézi
   érzelemkódja 11 (semleges), tehát a csere nem „ritka érzelmek dúsítása” volt.
4. **Kvázi mondatok** (`build_quasi_sentences.py`, 39 895 egység, medián 11 szó):
   - a „napirend előtt” műfaj 25 447 egységéből 15 535 „napirend előttihez hozzászólás”, ebből 9 611 miniszteri;
     a műfaji összevetés így kormányzati válaszokat hasonlít ellenzéki kérdésekhez;
   - 3 149 eljárási formula („Tisztelt Elnök Úr!”), 5 973 legfeljebb 3 szavas egység a nevezőben;
   - 808 egységben bent maradt zárójeles közbeszólás;
   - 12 mondat a rövidítéslista miatt nem vágódott el („…nap. Tényleg…”);
   - a `party` mezőben néhol tisztség áll („közlekedési és beruházási miniszter”).
5. **Kisebb ellentmondások:** a kutatási terv 33, a kódkönyv és a README 30 ülésnapot ír; a kódkönyv a CAP-ot
   beszédszinten, az elemzés kvázi mondatszinten írja le; a kódkönyvben az azonosító nem UUID.
   **[DOKUMENTÁCIÓBA]**
6. A repóban kb. 100 MB származtatott adat van verziókezelve (sqlite, sql, json, zip, pdf). (Később.)

### Döntések
- A kutatási kérdés, a korpusz és a kézi kódolás megmarad; az osztályozás és a validálás újra készül.
- Módszer: kis vak kézi minta → nyelvi modelles kódolás (`/vclassify`) → egyezés (`/vcoder-agreement`)
  → pontszám szerint rétegzett referencia-minta, több modell kódolja, a vitásakat a kutató dönti el
  (`/vcalibrate`) → korrekció és regresszió.
- A kutató kapacitása kb. 20–30 új mondat kézi kódolása.
- Egy másik MI-asszisztens utólagos „ritka események dúsítása” magyarázatát elvetettük, mert a kódnak és a
  kézi kódoknak ellentmond. A védésen a hibát és a javítást nyíltan vállaljuk.

---

## 2026-11-18 — Aranystandard v2: új vak minta

- Szkript: `gold_standard/sample_v2.py` (seed 20261118), napló: `gold_standard/sample_v2.md`.
- 24 új kvázi mondat, rétegezve: 3 műfaj × 2 szerep (kezdeményező / válaszoló) × 4.
- Keret: 8–30 szó, közbeszólás és eljárási formula nélkül, a korábban kiválasztottak kizárva.
- Első húzásnál egy zárójel nélküli közbeszólás („Lejárt az idő! ‑ Közbeszólás…”) átcsúszott; a szűrőt
  bővítettük és újrahúztunk (még nem kódolt senki).
- Kimenet: `gold_standard/hand_coding_v2.xlsx` (kitöltendő, gépi címke nélkül),
  `gold_standard/sample_v2_manifest.csv` (rétegek).
- Állapot: **a kutató kódolja.** Kitöltés után: 28 véletlen + 2 cserélt + 24 új = 54 kézi kód.
- **[DOKUMENTÁCIÓBA]** a validációs minta leírása (méret, rétegzés, vak kódolás, a 2 cserélt sor kezelése).

---

## 2026-11-18 — Kvázi mondatok tisztítása (v2)

Döntés: **az egységeket nem bontjuk újra** (a kézi kódok ezekre vonatkoznak), csak tisztítjuk és címkézzük.
A vágási szabályokat (mondatvég, pontosvessző, kettőspont, gondolatjel, vessző + kötőszó) a kódkönyvben
leírjuk. **[DOKUMENTÁCIÓBA]**

CAP: mondatszinten kódolunk (mint a kézi kódok), az elemzésben beszédszintre összesítünk
(a beszéd fő témája = a tartalmi mondatai közt leggyakoribb főtéma). **[DOKUMENTÁCIÓBA]**

### Mit csináltunk
Szkript: `clean_quasi_sentences_v2.py` (a régi sqlite-ot csak olvassa). Kimenet:
`parlamenti_kvazi_mondatok_2026_v2.csv` (39 905 egység, 17 MB), jelentés: `output_elemzes/kvazi_mondatok_v2_report.md`.

1. **Közbeszólások kiemelése.** A jegyzőkönyv zárójeles részei (derültség, taps, moraj, elnöki csengő,
   „Pócs János: …” típusú bekiabálás) külön `kozbeszolas` oszlopba kerültek, a `mondat_szoveg_tiszta`-ból kikerültek.
   A zárójelpárokat beszédenként, egységeken át keressük, mert a régi bontó a kettőspontnál a közbeszólásokat is
   kettévágta (pl. „(Magyar Péter” | „Százmilliárdokat… ‑ Az elnök csenget.)”). Kivétel: (sic!), (1). 4 577 egység érintett.
2. **Egységtípus** (`egyseg_tipus`): tartalmi 34 593 (86,7%), eljárási formula 3 917 (9,8%),
   csak közbeszólás 1 395 (3,5%). **Az elemzés nevezője a tartalmi egység.** **[DOKUMENTÁCIÓBA]**
3. **Szerep** (`szerep`, `fordulo`): kezdeményező / kormányzati válaszadó / frakció-hozzászóló, illetve
   első kör / viszonválasz. A „napirend előttihez hozzászólás” a felszólaló miniszter-státusza szerint oszlik.
   Tartalmi egységek: napirend előtt 8 968 kezdeményező, 8 834 kormányzati válasz, 5 123 frakció-hozzászólás;
   interpelláció 2 989 / 2 574; azonnali kérdés 3 116 / 2 989. **[DOKUMENTÁCIÓBA]**
4. **party_v2 és oldal.** A tisztségnevek és a „Kormányzat / Egyéb” értékek helyett: a felszólaló frakciója,
   ha van; különben „Kormány (nem képviselő)” (pl. Vitézy Dávid, Varga Mihály, Ruff Bálint). Az `oldal` (kormány /
   ellenzék) a miniszteri státuszból és a TISZA-tagságból jön. **[DOKUMENTÁCIÓBA]**
5. **10 elmaradt mondatvég-vágás** javítva („Holnap Semmelweis-nap. | Orvosként…”); a második rész azonosítója
   `_qNNNb`. Mind a 10-et kézzel átnéztük: helyesek. Aranystandard-mondatot nem érintett.

### Ellenőrzések (mind rendben)
- Egyedi azonosítók; minden régi azonosító megvan; mind az 54 aranystandard-azonosító megvan.
- A szavak száma változatlan (542 386).
- Szegmentálás vs. egyszerű mondatszámlálás beszédenként (`/datavalidation` 4. lépés): medián 1,24 egység/mondat,
  5–95. percentilis 1,00–1,56. A legnagyobb kiugró (6,75) Magyar Péter névsorolvasása (kivégzett 56-osok nevei,
  pontosvesszővel elválasztva) — valódi szerkezet, nem hiba. **[DOKUMENTÁCIÓBA]** (a bontás leírása + ez az ellenőrzés)

### Nyitott
- A vágási szabályokon (kettőspont, *mert*, *így*) szándékosan nem változtattunk; korlátként leírjuk.
- A régi `split_quasi_sentences.py` és `test_clause_split.py` elavult; a végén archiváljuk.
- A v2 CSV 17 MB — a repó-takarításnál döntjük el, verziókezeljük-e.

---

## 2026-11-18 — Kódkönyvek v2: döntési szabályok

A kódolás előtt átnéztük a két kódkönyvet. A taxonómiák nem változtak, csak döntési szabályokat írtunk hozzájuk.
A régi változat a gitben megvan (`74bc558`).

### CAP (`codebooks/codebook_cap.md`, új „Kódolási szabályok (v2)” fejezet)
- **Szint: főtéma** (1–21, a 11 nincs). Ok: a kutatási kérdés főtémákról szól; 54 kézi mondaton kb. 200 altémára
  nem mérhető egyezés; főtémán a kódolók megbízhatóbban egyeznek. A régi alkódszintű kézi kódokból a főtéma képződik.
  **[DOKUMENTÁCIÓBA]**
- **999 = nincs szakpolitikai téma**: projekt-kiegészítés, mert a hivatalos listában nem volt ilyen kód
  (a régi kézi kódolás már használta). **[DOKUMENTÁCIÓBA]**
- **Csak a mondat számít**, a beszéd témája nem öröklődik (a régi regex örökölte).
- **20 vs. 999**: a 20 csak a kormányzás működéséről szóló mondatoké; a téma nélküli pártcsatározás 999.
  Ez a régi „CAP 20 gyűjtőkategória” hibát szünteti meg. **[DOKUMENTÁCIÓBA]**
- Szabályok a több téma, a gyermek/család, a kultúra/sport/vallás, az EU/külföld és a katasztrófa esetére.
- Talált hibák: a régi osztályozó a kultúrát, a sportot és a vallást 21-esnek kódolta, pedig a 21 a közterületek
  főtéma; a hivatalos listában a 9-es témának csak egy alkódja van (900).

### MORES (`codebooks/codebook_moral_emotions.md`, új 4. fejezet „Projektszabályok”)
- Egység: kvázi mondat, egy kód; küszöb: csak a kifejezett érzelem kap kódot, kétség esetén 11.
- Szabályok a parlamenti esetekre: udvariassági formula → 11; puszta eredményközlés → 11 (a büszkeség, 8, csak
  kollektív önértékelésnél jár — ez a régi „TISZA 31% büszkeség” fő forrása volt); gúnyos „örülök”; irónia;
  retorikai kérdés; idézet; düh vs. megvetés (az 5-ös kód a megvetést is tartalmazza); félelem csak jövőbeli
  fenyegetésre; az „áldozat” szó önmagában nem szomorúság; a „siker” és a „büszkén jelentem” a 8-ba tartozik.
  **[DOKUMENTÁCIÓBA]**
- 17 magyar példamondat a korpuszból, javasolt kóddal. Egyik sincs benne az aranystandardban (szivárgás elkerülése).

### Kódolótábla
- `gold_standard/hand_coding_v2.xlsx`: a CAP oszlop `cap_fotema` lett, lenyíló listával (főtémák + 999); a „Kódok”
  lapon a főtémák magyar nevei, az érzelemkódok és egy 12 pontos rövid szabálylista.
- A minta nem változott: a manifest bájtra azonos (ugyanaz a seed).

---

## 2026-11-18 — Van-e már Gemini-kódolás a korpuszon? (ellenőrzés)

- **Nincs.** Gemini-címke csak a 30 aranystandard-mondatra létezik (`gold_standard/labels_cap.csv`,
  `labels_moral.csv`, indoklással). Ezeket az Antigravity-csevegőben készítették; szkript, prompt és pontos
  modellnév nincs mentve (`models.md`: „Gemini 2.5 Flash / Pro Hybrid Expert”), ezért nem reprodukálhatók.
- A teljes korpusz címkéi (sqlite `kvazi_mondatok.moral_emotion`, `cap_kod`) a regexből jönnek.
- A `calibration/scored_anger.csv` 38 433 „pontszáma” is a regex: 276 db 1.0, és ez pontosan a regex ANGER-címkéi;
  a többi 0.0. Nem valódi pontszám, csak 0/1.
- Ellentmondás: a `calibration/calibration_report.md` szerint az érzékenység 0,90 és a specificitás 0,85, a README
  szerint 0,64 / 1,00; a regexre a kézi kódokkal mért érzékenység ≈ 0,13. **[DOKUMENTÁCIÓBA]** a régi kalibráció
  nem használható.
- Jó hír: a 30 Gemini-címke közel áll a kézi kódokhoz, tehát a nyelvi modelles kódolás ezen a korpuszon működhet.
  A teljes korpuszt szkriptből, rögzített prompttal és modellverzióval kell kódolni, hogy reprodukálható legyen.

---

## 2026-11-18 — Kézi kódolás kész (54 mondat)

- A kutató kitöltötte a `gold_standard/hand_coding_v2.xlsx`-et: 24/24 sor, minden érték érvényes
  (CAP-főtéma 1–21 vagy 999, érzelem 3–8 vagy 11). A mondatok és azonosítók egyeznek a manifesttel.
- A kódoló a mondatot kontextus nélkül látta, gépi címkét nem (ugyanúgy, mint az első 30-nál).
- `gold_standard/build_hand_v2.py` → `hand_v2.csv` (54 sor: 28 régi véletlen, 2 régi cserélt, 24 új) és a
  `/vcoder-agreement` formátumú `hand_cap_v2.csv`, `hand_moral_v2.csv`. A régi alkódokat főtémára alakította
  (pl. 1308 → 13; a 999 marad).
- A gépi kódolás promptját a kézi kódok **megtekintése nélkül** írjuk meg (a kézi kódok eloszlását sem néztük meg),
  hogy a prompt ne igazodjon az ellenőrző mintához. **[DOKUMENTÁCIÓBA]**
- Nyitott kérdés: a gépi kódolás kapjon-e kontextust (előző és következő mondat). A kézi kód kontextus nélkül
  készült, ezért az egyezésmérés első köre kontextus nélkül fut.

---

## 2026-11-18 — Első gépi próba az 54 mondaton (prompt v1)

### Beállítás
- Prompt: `gold_standard/prompt_v1.md` (a két v2 kódkönyvből, a kézi kódok megtekintése nélkül).
- Bemenet: `gold_standard/llm_input_54.csv`, pontosan a kódolónak mutatott szöveg, véletlen sorrendben, kód nélkül.
- Gép 1: vak segéd-ügynök, Claude Sonnet; csak a promptot és a bemenetet olvashatta → `llm_claude_sonnet.csv`.
- Gép 2: helyi llama3.1 8B (ollama, temperature 0, seed 42), `gold_standard/llm_ollama.py` → `llm_llama31.csv`
  (folyamatban).
- Egyezés: `/vcoder-agreement` `agreement.py`; eltérések: `mismatches_sonnet_cap.csv`, `mismatches_sonnet_moral.csv`.

### Eredmény — Claude Sonnet, prompt v1 (n = 54)
| | Pontos egyezés | Cohen κ |
|---|---:|---:|
| CAP-főtéma | 0,59 | 0,51 |
| Érzelem | 0,65 | 0,37 |

- Új 24 / régi 30: CAP κ 0,54 / 0,48; érzelem κ 0,20 / 0,48.
- A gép óvatosabb: a mondatok 30%-át kódolta érzelmesnek, a kutató 46%-át. A 15 kézi „düh” közül 5-öt,
  a 4 kézi „büszkeség” közül mind a 4-et semlegesnek vette.
- Kategóriánkénti verdikt egyiknél sem adható (minden kategória n < 10, kivéve 999, 11 és 3).

### Eredmény — helyi llama3.1 8B, prompt v1 (n = 54, a javítás előtti kézi kódokhoz)
| | Pontos egyezés | Cohen κ |
|---|---:|---:|
| CAP-főtéma | 0,30 | 0,25 |
| Érzelem | 0,57 | 0,41 |

- A llama a 999-et szinte sosem használja; a téma nélküli mondatokat is valamilyen területre sorolja.
- Érzelemből bőkezűbb (az 54-ből 38-at érzelmesnek kódol, a kutató 25-öt); a κ ezért közelebb van a Sonnetéhez,
  mint a pontos egyezés alapján várnánk. A CAP-ra a llama nem használható; a futás kb. 1 óra volt.

### Súlyos lelet: a régi „Gemini-validálás” nem független gépi kódolás
- A `run_vcoder_agreement_analysis.py` beolvassa a kutató kitöltött kódolólapját, majd a „gépi kódokat” kézzel
  beírt listaként tartalmazza (nincs modellhívás, nincs prompt). A címkéket tehát egy MI-asszisztens írta be abban
  a munkamenetben, amely a kézi kódokat is beolvasta; függetlenségük nem igazolható.
- A még korábbi `prepare_agreement_data.py` kifejezetten szimulált: a „gépi címkéket” a (szintén gép által írt)
  „kézi kódokból” másolta, szándékosan beírt 2–3 eltéréssel („valósághű LLM kimenet”).
- Ezért a README κ = 0,728 / 0,753 és a régi kalibráció **nem** gépi kódolás validálása. Ugyanazon a 30 mondaton a
  „Gemini”-címkék CAP κ 0,84, érzelem κ 0,75 értéket adnak, a vakon futtatott Sonnet 0,48 / 0,48-at.
  **[DOKUMENTÁCIÓBA]** az MI-nyilatkozatban és a korlátok között nyíltan közölni kell; a régi számokat nem
  szabad validálásként közölni.
- Korábbi téves állításunk („a 30 Gemini-címke közel áll a kézi kódokhoz, tehát a modell működik”) visszavonva.

### Az eltérések mintázata (verdikt: kódkönyv / gép / kézi kód)
- Büszkeség és düh küszöbe: a v1 prompt „puszta eredményközlés → 11” és „kétség esetén 11” szabálya szigorúbb,
  mint a kutató ítélete. Kódkönyv-döntés kell.
- 20 vs. 999 (5 eset) és a gazdasági témák (1 vs. 15 vs. 20) határa: kódkönyv pontosítása kell.
- A régi 30 mondat a v2 szabályok előtt készült; több eltérésnél a kézi kód ütközik a később elfogadott szabállyal
  (pl. vihar/kárenyhítés → 15, gyermekvédelem → 13). Ezeket a kutató dönti el.

---

## 2026-11-18 — Eltérések egyeztetése, kódkönyv v2.1, prompt v2

A `/vcoder-agreement` 4. lépése szerint a kutató a Sonnet összes eltérését végignézte (22 CAP-, 19 érzelem-eltérés),
és egyenként eldöntötte, a kódkönyv, a gép vagy a kézi kód a hibás.

- **27 kézi kód javítva** (16 CAP, 11 érzelem), indoklással: `gold_standard/hand_corrections_v2.csv`.
  Két érzelem-javítás (E18, E19) a javaslatom szerint került be, mert a kutató nem írt hozzá mást.
  Az eredeti kódok megmaradtak (`hand_v2.csv`); az egyeztetett referencia: `hand_v2_adj.csv`
  (`build_hand_v2.py` állítja elő, ellenőrzi a régi értékeket). **[DOKUMENTÁCIÓBA]**
- Az egyezés az egyeztetett referenciához (prompt v1):

  | | Sonnet CAP | Sonnet érzelem | llama CAP | llama érzelem |
  |---|---:|---:|---:|---:|
  | javítás előtt κ | 0,51 | 0,37 | 0,25 | 0,41 |
  | egyeztetés után κ | **0,85** | **0,68** | 0,30 | 0,41 |

  **Az egyeztetés utáni szám felfelé torzít**: a kutató a gépi kódot látva döntött. Validálásként csak egy friss,
  vak minta egyezése közölhető (`/vcoder-agreement` 5. lépés). **[DOKUMENTÁCIÓBA]**
- A döntésekből szabályok: `codebook_cap.md` E fejezet, `codebook_moral_emotions.md` 14–18. pont (v2.1).
  Főbbek: a parlament működése = 20, az általános vád = 999; költségvetési hiány = 1, kamatstop = 15;
  fogyasztóvédelem = 15; nemzetpolitika: a tárgy dönt; büszkeség az elhivatottságnak tulajdonított siker és a
  nemzeti összetartozás; a kár felelősének megnevezése = düh; a nyomatékosító szó önmagában = 11; a kifejezett
  pozitív értékelés = öröm; bocsánatkérés = szomorúság.
- Új prompt: `gold_standard/prompt_v2.md` (v1 + pontosítások).
- A modellválasztás: a teljes korpuszt Claude-dal kódoljuk; a helyi llama a CAP-ra alkalmatlan (κ 0,30).

---

## 2026-11-18 — Végső ellenőrző minta (v3) kihúzva

- `gold_standard/sample_v2.py --tag v3 --seed 20261119` → `hand_coding_v3.xlsx` (24 mondat, üres),
  `sample_v3_manifest.csv`. Ugyanaz a rétegzés (3 műfaj × 2 szerep × 4), mint a v2-ben.
- Kizárva: a régi 30-as minták, a v2 minta és a kódkönyvekben példaként idézett 20 mondat. Ellenőrizve: 0 átfedés.
- A szkript bővült: `--tag`/`--seed` paraméter; csak a korábbi körök manifestjét zárja ki (a v2 újrafuttatva
  ugyanazt a mintát adja, a manifest változatlan); kitöltött kódolótáblát nem ír felül (kipróbálva).
- A kódolótábla „Kódok” lapján a v2.1 pontosítások rövid összefoglalója is szerepel.
- **Protokoll:** a kutató vakon kódol (gépi kód nélkül), utána fut a prompt v2 a 24 mondaton, és ez az egyezés kerül
  a tanulmányba. Ezen a mintán a promptot és a kódkönyvet már nem módosítjuk. **[DOKUMENTÁCIÓBA]**

---

## 2026-11-18 — VÉGSŐ EGYEZÉS: friss, vak v3 minta, prompt v2 (ez kerül a tanulmányba)

- A kutató vakon kódolta a 24 mondatot (`hand_coding_v3.xlsx`); `build_v3.py` ellenőrizte (24/24 érvényes) és
  előállította a vak gépi bemenetet (`llm_input_v3.csv`).
- Gép: vak segéd-ügynök, Claude Sonnet, `prompt_v2.md` → `llm_claude_sonnet_v3.csv`. Egyezés:
  `/vcoder-agreement` `agreement.py`; eltérések: `mismatches_sonnet_v3_cap.csv`, `..._moral.csv`.
- Ezen a mintán a promptot és a kódkönyvet nem módosítjuk. **[DOKUMENTÁCIÓBA]**

| Mérés (n = 24) | Pontos egyezés | Cohen κ | Konvenció szerint |
|---|---:|---:|---|
| CAP-főtéma | 0,75 | **0,72** | közepes |
| Érzelem, 7 kategória | 0,58 | 0,36 | gyenge |
| Érzelmes vs. semleges* | 0,83 | **0,67** | közepes |
| Negatív / pozitív / semleges* | 0,79 | 0,60 | közepes (határon) |
| Düh+megvetés / egyéb / semleges* | 0,71 | 0,49 | gyenge |

\* Az összevont mérőszámokat az eredmény ismeretében számoltuk (post hoc); így kell közölni. **[DOKUMENTÁCIÓBA]**

- CAP: 6 eltérés, ebből 2 a 20-as és a 15-ös/999-es határán, 1 az 1-es és a 15-ös között.
- Érzelem: a gép és a kutató ugyanannyi (12/24) mondatot tart érzelmesnek, de a negatív érzelmeken belül a gép
  szinte mindent dühnek (3) kódol: a kutató 4 megvetés (5) kódjából 3-at, valamint a félelem, a szomorúság és a
  büszkeség egy-egy esetét is. **A hét kategória közti különbségtétel nem megbízható; az „érzelmes-e” igen.**
- Kategóriánkénti verdikt nem adható (minden kategória n < 10). Az n = 24 kicsi; a κ bizonytalansága nagy.

### Döntés: a fő érzelmi mérőszám
- **Fő mérőszám: érzelmes vs. semleges** (a 3–8 kódok összevonva; κ 0,67). Ez méri a hipotézisekben szereplő
  „érzelmi hőfokot” (a beszéd tartalmi mondatai közül hány százalék érzelmes). A hét kategória csak leíró
  kiegészítés, a gyenge egyezés (κ 0,36) jelzésével. A kutató döntése, 2026-11-18. **[DOKUMENTÁCIÓBA]**
- A gép továbbra is a hét kategóriát kódolja (prompt v2 változatlan); az összevonás az elemzésben történik.

### Modellválasztás a teljes korpuszhoz: Haiku vs. Sonnet ugyanazon a vak v3 mintán
| Modell (prompt v2, n = 24) | CAP κ | Érzelmes/semleges κ | Érzelem-7 κ |
|---|---:|---:|---:|
| Claude Sonnet | 0,72 | 0,67 | 0,36 |
| Claude Haiku | 0,67 | 0,67 | 0,57 |

- Két modell összevetése ugyanazon a vak teszten, hangolás nélkül (nem „tuning on the test”).
- A fő mérőszámban azonosak, CAP-ban a különbség n = 24 mellett a bizonytalanságon belül van. **Döntés: a
  teljes korpuszt a Claude Haiku kódolja** (kisebb keretigény). **[DOKUMENTÁCIÓBA]** a tanulmányban a Haiku
  v3-as számait kell közölni (CAP κ 0,67; érzelmes/semleges κ 0,67).

## 2026-11-18 — Teljes korpusz: előkészítés és próbaadag
- `coding/make_batches.py`: 34 593 tartalmi mondat, véletlen sorrend (seed 20261120), 35 adag × 1000;
  a gép rövid sorszámot lát, a visszafejtés `coding/map.csv`-vel.
- `coding/merge_labels.py`: adagonkénti ellenőrzés (minden sorszám pontosan egyszer, érvényes kódok,
  futásnapló), összefésülés → `coding/labels_full.csv`. Futásnapló: `coding/runs.csv`.
- Próbaadag: batch_001, Haiku segéd-ügynök, prompt v2 (a válasz formátuma CSV, indoklás legfeljebb 10 szó).
  - Eredmény: 1000/1000 sor, 0 hiányzó, 0 duplikált, 0 érvénytelen kód; bekerült a `labels_full.csv`-be.
  - Ráfordítás: kb. 189 ezer token, 5,4 perc. Becslés a maradék 34 adagra: kb. 6,4 millió token, egymás után
    kb. 3 óra, 4 párhuzamos szállal kb. 1 óra.
  - Eloszlás: CAP 999 44%, 20 15%; érzelmes 49% (a vak v3 kézi mintában 50%). A leghosszabb azonos kódsorozat 4,
    tehát a modell nem „ragadt be” egy kódba.
  - 12 véletlen sor szemrevételezése: a kódok és az indoklások a mondathoz illenek; egy határeset
    (hitel-visszafizetés → 1, lehetne 13 vagy 14).
- 1. párhuzamos kör: batch_002–005 (4 Haiku segéd-ügynök egyszerre). Mind a 4 hibátlan → 5000/34 593 kész.
  - Ráfordítás: 170–287 ezer token és 8–12 perc adagonként. A Pro-keret 5 órás ablaka 20% → 36% (+16%, a
    vezérlő beszélgetéssel együtt), a heti keret 10% → 12%. Adagonként kb. 4% az 5 órás és kb. 0,5% a heti
    keretből; a maradék 30 adag kb. 15% heti keret, de több 5 órás ablakra kell osztani.
  - **Figyelmeztető jel:** az érzelmes arány adagonként 0,37 és 0,49 között szór. Mivel az adagok véletlenek,
    1000-es adagnál kb. ±0,03 szórás várható; a különbség nagyobb, ami a futások közti eltérésre (a küszöb
    eltérő alkalmazására) utalhat. Futások közti megbízhatósági ellenőrzés kell. **[DOKUMENTÁCIÓBA]**

## 2026-11-18 — Futások közti megbízhatóság (test-retest)
- `coding/reliability_sample.py`: 5 × 50 véletlen mondat a batch_001–005-ből; egy új, független Haiku-futás
  (250 mondat, két 125-ös fájl) kódolta újra, a régi kód ismerete nélkül. Összevetés:
  `coding/reliability_compare.py` → `coding/reliability/rel_report.md`.

| | n | CAP κ | Érzelmes/semleges κ | Érzelem-7 κ | Érzelmes arány: eredeti → új |
|---|---:|---:|---:|---:|---|
| összesen | 250 | **0,81** | **0,70** | 0,62 | **0,40 → 0,50** |
| adagonként | 50 | 0,73–0,97 | 0,62–0,80 | 0,55–0,70 | mind az 5 adagban nő |

- A CAP futásról futásra stabil. Az érzelmes/semleges besorolás közepesen stabil (κ 0,70, épp a küszöbön).
- **Szintbeli eltolódás:** az új futás mind az 5 adag mintáján több mondatot tart érzelmesnek (átlagosan +10
  százalékpont). A vak v3 mintán a kutató, a Sonnet és a Haiku egyaránt 50%-ot mért; az 1000-es adagok 40%-ot.
  Valószínű ok: a hosszú (1000 mondatos) futásban a modell a végén óvatosabb, semlegesebb. **[DOKUMENTÁCIÓBA]**
- Következmény: az érzelmes mondatok **abszolút aránya** futásfüggő (kb. 40–50%), ezért a tanulmányban nem
  szintet, hanem **különbségeket** (műfaj, szerep, frakció) érdemes állítani. Mivel a mondatok véletlenül kerültek
  az adagokba, az adagok közti eltolódás zaj, nem torzítás a csoportok között; az elemzésben adag-fix hatással
  kontrollálható.

---

## 2026-11-18 este — Szűkített teljes kódolás, elemzés, tanulmány, repó (leadás: 2026-11-19 10:00)

### Döntés a szűkítésről (a kutatóé)
- A Pro-keret 5 órás ablaka nem bírta volna a teljes korpuszt a leadásig. A hipotézisek a **kezdeményező**
  felszólalókra vonatkoznak, ezért csak ezek kódolását folytattuk (`coding/make_initiator_batches.py`,
  batch_101–113); a válaszokat a batch_001–005 véletlen mintájából hasonlítjuk össze. **[DOKUMENTÁCIÓBA]**
- Lefutott: batch_101–108 (8 × 1000, Haiku, prompt v2), mind hibátlan. A 109–113 (4 901 mondat) a keret miatt
  kimaradt. Eredmény: **10 172 / 15 073 kezdeményező egység (67%) kódolva**; mivel a sorrend véletlen, ez
  véletlen részminta. Összesen 13 000 kódolt egység (`coding/labels_full.csv`). A keret 5 órás ablaka kb. 70%-on.

### Elemzés (`analysis/analyze_v2.py` → `output_v2/`)
- Fő mérőszám: érzelmes arány, kezdeményezők; 95%-os klaszter-bootstrap CI beszédek szerint; lineáris valószínűségi
  modell klaszter-robusztus SE-vel (beszéd), műfaj + oldal + viszonválasz + adag-fix hatás.
- Eredmény: napirend előtti 46%, interpelláció 36%, azonnali kérdés 39% érzelmes. A napirend előtti
  +9,6 százalékpont az interpellációhoz képest (CI 5,2–14,0) → **E1 igazolódott**. Az azonnali kérdés +2,7 (CI
  −1,5–6,9) → az **E3 érzelmi része nem igazolódott**; hossz: medián 246 / 334 / 629 szó → **az E3 hosszra
  vonatkozó része igazolódott**. Téma nélküli mondat az interpellációkban a legkevesebb (34%, napirend előtti 43%),
  a leggyakoribb főtéma az interpellációkban az egészségügy, a napirend előttiekben a kormányzati működés → **E2-vel
  összhangban**. Szerepek (véletlen minta): kormányzati válasz 39%, kezdeményező 42%, frakció-hozzászóló 47%.
- Ábrák: `abra1_erzelmes_mufaj_oldal.png`, `abra2_cap_mufaj.png` (a dataviz skill alappalettája, renderelve és
  szemrevételezve).

### Tanulmány és repó
- `build_study_pdf_v2.py` → `elemzes_parlamenti_2026_v2.pdf` (2 oldal): minden szám a `results.json`-ból jön,
  a hipotézisek minősítése a konfidenciaintervallumokból automatikusan. Csak valós, a kódkönyvekben is szereplő
  hivatkozások (CAP: Baumgartner, Breunig és Grossman 2019; Cohen 1960; Haidt 2003; Rozin és mtsai 1999;
  TenHouten 2007). Az „Abszolút filmszínház” fogalomhoz forrást a kutatónak kell adnia, ezért kimaradt.
- `gold_standard/agreement_all.py`: minden egyezésmérés újrafuttatható a repóból (a fő mérőszámra is).
- `reproduce_v2.py`: egy paranccsal újraépíti az 1–8. lépést; **teljes lefutás kipróbálva, hibátlan**.
- `README.md` újraírva (v2), a régi `README_v1_archiv.md`; benne az MI-nyilatkozat és a v1 validálás elvetése.

---

## 2026-11-18 késő este — Kódolás folytatása (a kutató kérésére)
- Előbb a meglévő v2 bekerült a `master` ágba és fel lett töltve a GitHubra (biztonsági változat).
- batch_109–112 (Haiku, prompt v2): mind hibátlan. A batch_113 (901 mondat) a keret miatt (5 órás ablak 88%)
  kimaradt. **Kezdeményező lefedettség: 14 172 / 15 073 (94%)**; összesen 17 000 kódolt egység.
- `reproduce_v2.py` újrafuttatva, hibátlan. A következtetések nem változtak:
  napirend előtti 47%, interpelláció 37%, azonnali kérdés 40% érzelmes; napirend előtti +10,3 százalékpont
  (CI 6,1–14,5) → E1 igazolódott; azonnali kérdés +2,2 (CI −1,7–6,2) → az E3 érzelmi része nem igazolódott;
  téma nélküli mondat: interpelláció 34%, napirend előtti 43%. A PDF ezekkel a számokkal készült újra.
- Két segéd-ügynök jelezte, hogy kilistázta a `coding/out` mappát (fájlt nem nyitott meg); a kódolásra ez nincs
  hatással, mert a kimeneteket a `merge_labels.py` a bemenettel veti össze.

- Utolsó adag (batch_113, 901 mondat) a kutató kérésére lefutott, hibátlan. **Kezdeményező lefedettség:
  15 073 / 15 073 (100%)**, összesen 17 901 kódolt egység. Végső számok: napirend előtti 46%, interpelláció 36%,
  azonnali kérdés 39% érzelmes; napirend előtti +10,2 pp (CI 6,1–14,3); azonnali kérdés +2,8 (CI −1,0–6,5);
  téma nélküli mondat: interpelláció 34%, napirend előtti 43%. A PDF, a README és a korlátok ennek megfelelően
  frissítve. **[DOKUMENTÁCIÓBA]** (kész)

---

## 2026-11-19 reggel — A tanulmány kiegészítése (leadás előtt)
- Új elemzések (`analysis/analyze_v2.py`): szakpolitika × érzelem (`tabla_cap_erzelem.csv`, 3. ábra); frakciók
  Magyar Péterrel és nélküle (`tabla_erzelmes_frakcio.csv`); robusztus modell frakció-fix hatással és Magyar
  Péter-indikátorral (`tabla_regresszio_robusztus.csv`: a napirend előtti hatás +9,6 pp, CI 5,4–13,9 marad, a
  frakciók közti különbség eltűnik); képviselők (n ≥ 100; `tabla_erzelmes_kepviselo.csv`); idősor ülésnaponként:
  érzelmes arány műfajonként és az aszályhoz kötődő témák figyelme (`tabla_idovonal_*.csv`, 4. ábra).
  A napirend előtti felszólalás 15 ülésnapból 14-en a legérzelmesebb műfaj. **[DOKUMENTÁCIÓBA]** (kész)
- PDF (3 oldal): új bekezdések (témák és érzelmek, szereplők, idővonal a megszakított egyensúly óvatos
  értelmezésével — Baumgartner és Jones 1993), 2. táblázat (képviselők), 3–4. ábra, és új fejezet: **eltérések a
  kutatási tervtől és a kódkönyv 1.0-tól** (33 → 30 ülésnap; kvázi mondat; szerep; CAP főtéma + 999; érzelmes/
  semleges fő mérőszám; a kulcsszavas kódok és a nem független validálás cseréje). Mindenhol „kvázi mondat”.
- Kódkönyv: `codebooks/CODEBOOK_PARLAMENTI_KORPUSZ_2026.md` 6. fejezet (2.0): a kvázi mondat tábla és a gépi
  kódok változói, validálás; az UUID-állítás pontosítva.
- `reproduce_v2.py` újrafuttatva: hibátlan, a PDF 3 oldal.
- Idősor a kutató kérésére: szakpolitikai témák heti figyelme összesen és műfajonként (`tabla_tema_het*.csv`,
  `abra5_tema_het.png`, `abra6_tema_het_mufaj.png`; a 8 fő téma + mezőgazdaság és vízügy). A PDF 4. ábrája az
  érzelmes arány műfajonkénti idősora, az 5. ábra a műfajonkénti heti téma-hőtérkép (az aszály-vonal ábra a repóban
  marad: `abra4_idovonal_aszaly.png`). Megfigyelés: a kormányzati működés minden héten jelen van (főleg napirend
  előtt); az ágazati témák rövid, műfajhoz kötött hullámokban jönnek; az aszály hetében (aug. 10.) az azonnali
  kérdésekben a mezőgazdaság és a vízügy ugrik meg, és ettől a héttől az energia figyelme tartósan magasabb
  (≤5% → 6–16%). **[DOKUMENTÁCIÓBA]** (kész)
- Leíró statisztika a `/vdescriptives` szerint: új 2. táblázat (műfajonként és összesen: beszéd, kvázi mondat,
  medián hossz, érzelmes arány CI-vel, düh/megvetés aránya, téma nélküli arány, kormányzati működés súlya,
  ellenzéki arány; `tabla_leiro_mufaj.csv`), a modellváltozók összefoglalója (`tabla_osszefoglalo_valtozok.csv`),
  asszociációk: Cramér-féle V műfaj × főtéma 0,25, főtéma × érzelmes 0,19, műfaj × érzelmes 0,09; beszédszintű
  Spearman ρ (kormányzati téma aránya × érzelmes arány) = 0,38 (CI 0,29–0,45; n = 458). Értelmezés: a műfajok
  inkább témájukban, mint érzelmességükben különböznek. A műfaj × oldal oszlopdiagram kikerült a PDF-ből (a
  táblázat lefedi; a repóban megvan), az ábrák újraszámozva; a PDF 3 oldal.
- A kutató kérésére **szerkeszthető, bővített Word-változat**: `build_study_docx_v2.py` →
  `elemzes_parlamenti_2026_v2_bovitett.docx` (python-docx; 9 oldal Word-ben renderelve, 9 táblázat, 7 ábra):
  minta felépítése, validálás (a prompt v1 próbákkal együtt), leíró és összefoglaló statisztika, asszociációk,
  két regressziós modell egymás mellett, téma × érzelem teljes tábla, frakciók, mind a 26 képviselő, idősorok,
  eltérések, korlátok, MI-nyilatkozat, reprodukciós függelék. A kutató ebből vág. Bekerült a `reproduce_v2.py`-ba.
- A kutató kérésére a PDF és a Word szövege közérthetőbb lett (rövidebb mondatok, a szakkifejezések
  magyarázattal, a technikai részletek a táblák alatti megjegyzésekben); a számok nem változtak.
- **Interaktív prezentáció:** `build_presentation_v2.py` → `prezentacio_v2.html` (egyetlen fájl, internet nélkül
  is fut, az adatok az `output_v2/`-ből beágyazva). Fülek: Műfajok (kormány/ellenzék szűrő, leíró tábla), Témák
  (+ asszociációk), Téma × érzelem (kattintásra érzelem-megoszlás), Szereplők (frakciók, képviselők frakció
  szerinti szűrővel), Idővonal (érzelmi idősor, heti téma-hőtérkép műfaj-választóval), Módszer (folyamat,
  validálás, a régi validálás elvetése). Rámutatásra minden elem mutatja a pontos számot. Világos/sötét mód,
  nyilakkal lapozható. Böngészőben kipróbálva: mind a 6 fül kirajzolódik, nincs konzolhiba, nincs NaN.
- **Repó-takarítás** (a kutató kérésére): a gyökérben csak a v2 folyamat és a leadandók maradtak. 115 fájl
  áthelyezve `git mv`-vel: `archiv_v1/` (régi elemző szkriptek, régi PDF és prezentáció, `calibration/`, a régi
  `output_elemzes/`, `OPPONENSI_SEGEDLET.md` — elavult állításokkal), `adatgyujtes/` (letöltő szkriptek, nyers
  letöltések), `egyeb/` (nem ehhez a kutatáshoz tartozó mellékprojektek; kulcs/jelszó nincs bennük). Törölve a
  forrásadatbázis négy másolata (`.sql`, `.json`, `.zip`, `.csv.xlsx`; az `.sqlite` és a `.csv` megmaradt).
  Minden mappában rövid README; a git-előzményekben minden megmaradt.

---

## Következő lépések
1. A kutató ellenőrzi a kódkönyvek javasolt példakódjait, majd kitölti a `gold_standard/hand_coding_v2.xlsx`-et.
2. A régi 30 kézi kódot főtémára alakítjuk.
3. Nyelvi modelles kódolás a `mondat_szoveg_tiszta` oszlopon (`/vclassify`), ugyanezekkel a kódkönyvekkel,
   először az 54 kézi mondaton.
4. A `codebooks/CODEBOOK_PARLAMENTI_KORPUSZ_2026.md` frissítése (egység, szint, 999, szerep, egységtípus).

- A leadandó PDF tömör változatra átírva (a kutató kérésére): 3 oldal, 5 ábra, 6 táblázat, kevés szöveg; új 3. táblázat az elvárások ellenőrzéséről (Igen/Nem + bizonyíték), 4. táblázat a két regressziós modell egymás mellett, 6. táblázat frakciók és képviselők. A bővített változat a Word-fájlban marad.

- Tömör, szerkeszthető Word-változat a kutató kérésére: build_study_docx_tomor.py -> elemzes_parlamenti_2026_v2.docx (Word-ben 3 oldal, 4 ábra a hőtérképpel, 4 táblázat, rövid szöveg). Bekötve a reproduce_v2.py-ba.

- Végleges, tovább rövidített Word-változat (a kutató kérésére): elemzes_parlamenti_2026_v2_vegleges.docx (3 oldal). Kivéve: a képviselői sorok (önkényes top/bottom kiválasztás, műfaji összetételtől függ), a 4. táblázat téma-oszlopa, a 3. táblázat érzelmes sora (az 1. ábra mutatja), az 1. táblázat test-retest sora. Maradt: 4 táblázat (adat és ellenőrzés, elvárások, műfajok, frakciók) és 4 ábra.

## 2026-11-19 — Leadott változat
- A kutató saját szerkesztésű, végleges PDF-je: `elemzes_parlamenti_2026_leadott.pdf` (3 oldal, cím: „Témák és
  érzelmek három parlamenti műfajban (2026)”). A generált Word-változatból kézzel átírva; két hipotézis (H1, H2)
  maradt, az azonnali kérdésekre vonatkozó elvárás kikerült.
- A számokat összevetettem az `output_v2/results.json`-nal, mind egyezik: 15 073; 78; κ 0,67; +10,2 pp (CI 6,1–14,3);
  34% és 15%; 8 968 / 2 989 / 3 116; 629 / 334 / 246 szó; 43/34/37%; 36/15/22%; 61% és 36%; frakciók
  46/42/42/40/38%; 64%; +9,6 pp.
- A README a leadott fájlra mutat, a végleges hipotézisekkel és eredményekkel.

## 2026-11-19 — A repó szűkítése a kért tartalomra (adat, kód, kódkönyv)
- A kutató kérésére a repóban csak az adat, a kód és a kódkönyv maradt, a README-vel (MI-nyilatkozat) és ezzel a
  naplóval. Kikerült a követésből (helyben megmaradt, `.gitignore`): `egyeb/`, `archiv_v1/`, `.agents/`, `GEMINI.md`,
  a dokumentum- és prezentáció-előállító szkriptek és kimeneteik (PDF, Word, `prezentacio_v2.html`).
- Az egyezésmérő `agreement.py` (a `/vcoder-agreement` skillből) átkerült a `gold_standard/` mappába, így a repó
  önmagában is futtatható. A `reproduce_v2.py` 7 lépésre szűkült; lefutott, hibátlan.
- A régi (v1) változat a szerző gépén lévő teljes git-mentésben (bundle) érhető el.

## 2026-11-19 — Az előzmények megtisztítása (a kutató kérésére)
- A repó nyilvános lett, ezért a GitHubon a régi, nem beadandó anyag (v1, mellékprojektek, adatbázis-másolatok) az
  előzményekben is látszott. A teljes előzményt a gépen mentettem (`parlamenti-projekt_teljes_elozmeny.bundle`, a
  repó mellett), majd a GitHubon a repót egyetlen, tiszta commitra írtam át (force push). A napló ezért a korábbi
  commit-azonosítókra már nem hivatkozik; a lépések leírása itt teljes.

## 2026-11-19 — Prezentáció a 4. blokkra (10 perc)
- `prezentacio_v2.html` (helyben, nem része a repónak): 8 dia a leadott elemzés szerint — cím és H1/H2; adat és
  módszer (felpörgő számok); H1: érzelmes arány műfaj × frakció (a négy frakció külön, CI-vel); H2: témák
  műfajonként (műfaj-kiemelés); téma × érzelem kattintható valódi példamondatokkal (77 kvázi mondat, felszólaló,
  frakció, műfaj, dátum; figyelmeztetés a gépi kódolásra); „Nem a párt, hanem a műfaj” (TISZA Magyar Péterrel és
  nélküle); lejátszható heti hőtérkép az aszály-héttel; összegzés, korlátok, MI-nyilatkozat, reprodukció.
- Animált oszlopok, nyilakkal/szóközzel lapozható, F = teljes képernyő, világos/sötét mód. 1280×720-as nézetben
  kipróbálva: mind a 8 dia kirajzolódik, a lejátszás működik, nincs konzolhiba.
