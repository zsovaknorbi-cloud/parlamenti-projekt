# KÓDKÖNYV
# Országgyűlési Felszólalások Korpusza (2026)
*1.0 verzió | 2026. november*

---

## 1. Forrás és lefedettség

Az adatok kizárólag az Országgyűlés honlapjáról ([parlament.hu](https://www.parlament.hu)), annak adatszolgáltatásából (API) és a plenáris jegyzőkönyveiből származnak. A korpusz a 43. ciklus első 30 ülésnapját fedi le (2026. május 26. – szeptember 28.). Minden frakció (TISZA, Fidesz, Mi Hazánk, KDNP), valamint a kormány tagjainak plenáris felszólalása szerepel benne a három felszólalás típus szerint: napirend előtti felszólalások, azonnali kérdések és válaszok, valamint interpellációk. Összesen 1 284 felszólalás, 557 620 szó és kb. 73 órányi adat került a gyűjteménybe (1. táblázat).

### 1. táblázat: A korpusz megoszlása műfaj és frakció szerint (N = 1 284)

| Műfaj | Felszólalás | Frakció / csoport | Felszólalás |
| :--- | :---: | :--- | :---: |
| Azonnali kérdések és válaszok | 543 | TISZA | 656 |
| Napirend előtti felszólalások | 423 | Fidesz | 197 |
| Interpellációk | 318 | Mi Hazánk | 181 |
| – | – | KDNP | 176 |
| – | – | Kormányzati tagok | 74 |
| **Összesen** | **1 284** | **Összesen** | **1 284** |

---

## 2. Feldolgozási napló

A beszédek szövegét és metaadatait (felszólaló, dátum, időtartam, frakció) a portál szerkezetéhez igazított scraperrel töltöttem le. Az interpellációk és azonnali kérdések többfordulós párbeszédek (kérdés, miniszteri válasz, viszonválasz, zárszó) minden megszólalás önálló sor lett. A jegyzőkönyvi fejlécet (`NÉV (PÁRT):` , `NÉV tisztség:`) eltávolítottam a tisztított szövegből, hogy a tartalomelemzést ne torzítsa. Az eredeti szöveg külön oszlopban változatlanul megmaradt, így a lépés visszakövethető. Az adatbázist ezután a CAP témakódokkal és MORES project kódokkal egészítettem ki.

---

## 3. Egyedi azonosítók

Minden megszólalás három elemből álló azonosítót kapott: `DÁTUM_TÍPUS_FELSZÓLALÓ`; ha valaki egy napon belül többször szólt fel, a felszólaló után sorszám áll (`_1`, `_2`), így mind az 1 284 azonosító egyedi (2. táblázat). A `procedure_ID` a hivatalos irományszámot (pl. `I/49`, `A/80`) tartalmazza, és a ParlLawSpeech-hez hasonlóan ez teszi lehetővé a beszéd összekapcsolását az irománnyal és a törvénnyel.

### 2. táblázat: A típuskódok és az egyedi azonosító szerkezete

| Kód | Jelentés | Példa |
| :--- | :--- | :--- |
| **NRE** | napirend előtti felszólalás | `2026-05-26_NRE_Toroczkai László` |
| **I** | interpellációs kérdés | `2026-05-26_I_Bencsik János` |
| **IV** | válasz az interpellációra | `2026-05-26_IV_Kapitány István` |
| **A**, **AV** | azonnali kérdés, illetve az arra adott válasz | `2026-05-26_A_Dr. Takács Árpád` |

---

## 4. Validálás

Az adatvalidálás során két skillt (validálási munkafolyamatot) használtam, amelyeket egy dokumentációs skill egészített ki. A `/datavalidation` a ParlLawSpeech ötlépéses protokollját hajtotta végre a szövegkorpuszon (3. táblázat), a `/data-provenance-checker` pedig a feldolgozott táblát mérte vissza a legelső, nyers parlamenti letöltésekhez.

### 3. táblázat: A /datavalidation és /data-provenance-checker protokoll lépései és eredményei

| Lépés | Mit vizsgáltam? | Eredmény |
| :--- | :--- | :--- |
| **1. Teljesség, duplikáció** | azonosítók egyedisége, hiányzó szöveg | 100% egyedi azonosító, 0 hiányzó szöveg |
| **2. Metaadatok** | dátum, frakció, azonosítók (UUID) | ISO dátumformátum, egységes címkék |
| **3. Kapcsolatok** | összekötés irományszámmal és képviselői névsorral | 861 beszédnél hibátlan kapcsolat |
| **4. Szövegtartalom** | kódolás, fejlécek eltávolítása | 0 kódolási hiba, teljes UTF-8 |
| **5. Felderítő elemzés** | írásjelsűrűség, extrém hosszú beszédek | 2,78 írásjel / 100 karakter |
| **Adat-eredet (Provenance)** | visszavezethetőség a nyers forrásra | 0 sémacsúszás, 0 adatvesztés |

---

## 5. Milyen változók vannak a táblázatban? (Változócsoportok áttekintése)

A táblázat 35 oszlopban rendszerezi a felszólalások adatait, amelyek öt összefüggő tartalmi csoportba sorolhatók:

### Azonosítók és forráslinkek:
A beszéd emberi kulcsa (`egyedi_azonosito`), az irományszám (`procedure_ID`), a belső kód (`felszolalas_id`), valamint a közvetlen internetes hivatkozás a hivatalos parlamenti PDF dokumentumra (`speech_link`).

### Ki beszélt? (Felszólaló adatai):
A képviselő neve (`speaker`), frakciója (`party`), nemzetközi pártkódja (`partyfacts_id`), hivatalos tisztsége (`tisztseg`), valamint hogy kormánytagként (miniszterként vagy államtitkárként) szólt-e fel (`minister`: Igen/Nem).

### Mikor és hogyan? (Időbeli és eljárási adatok):
A beszéd pontos napja (`date`), ülésszaka (`session`), ülésnapi sorszáma (`speechnumber`), az országgyűlési ciklus száma (`legislative_period`: 43), a vita műfaja (`napirendi_mufaj`, `felszolalas_tipusa`), a napirendi pont hivatalos címe (`agenda`), és a válasz elfogadásának eredménye (`dontes_eredmeny`).

### Miről szólt a beszéd? (Közpolitikai és érzelmi tartalom):
* **Közpolitikai tartalom (CAP):** A nemzetközi *Comparative Agendas Project* 20 fő témája alapján meghatározza a felszólalás szakpolitikai területét. Négy oszlop rögzíti: a főtéma magyar megnevezését (`cap_fo_tema_hu`, pl. *Költségvetés*, *Egészségügy*, *Közlekedés*), nemzetközi angol nevét (`cap_fo_tema`), a részletes altémát (`cap_altema`, pl. *Nemzeti költségvetés*, *Árak és infláció*, *Vasúti közlekedés*), valamint a hivatalos numerikus altémakódot (`cap_kod`, pl. *105*, *1005*).
* **Morális és politikai érzelmek (MORES):** A politikai érzelemkódkönyv (TenHouten 2007; Haidt 2003; MORES project) alapján azonosítja a beszéd érzelmi hangnemét. Két oszlop rögzíti: az érzelem nevét (`moral_emotion`) és számkódját (`moral_emotion_code`). Hét lehetséges kategóriát különböztet meg: *Düh és morális felháborodás (3)*, *Félelem és vészhelyzet (4)*, *Undor és megvetés (5)*, *Szomorúság és részvét (6)*, *Öröm és remény (7)*, *Büszkeség és nemzeti helytállás (8)*, illetve a tárgyilagos, érzelemmentes *Semleges (11)*.

### Szövegtartalom és beszédhossz:
A felszólalás hossza másodpercben (`hossz_masodperc`) és formázva (`hossz_formazott`, pl. *3 perc 12 mp*), a szavak és karakterek száma (`szavak_szama`, `karakterek_szama`), a megtisztított beszédtörzs az azonnali elemzéshez (`text`), valamint az eredeti jegyzőkönyvi nyers szöveg a felszólalói fejlécével (`text_raw`).

---

## 6. Kiegészítés — 2.0 verzió (2026. november 19.): kvázi mondatok és gépi kódok

> A fenti 1–5. fejezet a beszédszintű táblát (1 284 felszólalás) írja le. Az ott említett `cap_*` és
> `moral_emotion*` oszlopok **kulcsszavas szabályokból** származnak, validálásuk nem volt független, ezért az elemzés
> **nem** ezeket használja (lásd `NAPLO.md`). A 2.0 elemzés egysége a **tartalmi kvázi mondat**, kódjai a lenti
> táblákban vannak. Pontosítás a 3. fejezethez: az azonosító nem UUID, hanem `DÁTUM_TÍPUS_FELSZÓLALÓ[_sorszám]`.

### 6.1 Kvázi mondat tábla — `parlamenti_kvazi_mondatok_2026_v2.csv`
Előállítja: `clean_quasi_sentences_v2.py` (a `parlamenti_felszolalasok_2026_teljes.sqlite` `kvazi_mondatok`
táblájából). 39 905 sor; ebből 34 593 tartalmi egység. Kódolás: UTF-8, CSV.

| Változó | Leírás |
|---|---|
| `kvazi_mondat_id` | egyedi azonosító: `<beszed_id>_qNNN` (a szétvágott mondatvégeknél `_qNNNb`) |
| `beszed_id` | a felszólalás azonosítója (kapcsolat a beszédszintű táblával) |
| `mondat_sorszam` | a kvázi mondat sorszáma a beszéden belül |
| `speaker`, `party` | felszólaló; eredeti frakciócímke |
| `party_v2` | javított frakció (tisztségnevek helyett frakció; nem képviselő miniszter: „Kormány (nem képviselő)”) |
| `oldal` | `kormany` (miniszter vagy TISZA) / `ellenzek` |
| `minister`, `tisztseg`, `date` | miniszteri státusz (0/1), tisztség, ülésnap (ISO) |
| `napirendi_mufaj`, `felszolalas_tipusa` | műfaj (napirend előtt / interpelláció / azonnali kérdés) és a forduló típusa |
| `szerep` | `kezdemenyezo` / `kormanyzati_valaszado` / `frakcio_hozzaszolo` |
| `fordulo` | `elso` / `viszonvalasz` |
| `egyseg_tipus` | `tartalmi` / `eljarasi` (pl. „Tisztelt Elnök Úr!”) / `kozbeszolas` |
| `mondat_szoveg` | az eredeti kvázi mondat (változatlan, visszakövethetőség) |
| `mondat_szoveg_tiszta` | a kvázi mondat a zárójeles közbeszólások nélkül — ezt kódoljuk |
| `kozbeszolas` | a kiemelt közbeszólás(ok), pl. „(Derültség a Fidesz soraiban.)” |
| `mondat_szoszam`, `tiszta_szoszam` | szószám az eredeti, illetve a tiszta szövegben |
| `javitas` | az egységen végzett javítás (pl. elmaradt mondatvég-vágás) |

### 6.2 Gépi kódok — `coding/labels_full.csv`
A kezdeményező szerepű tartalmi kvázi mondatok mindegyike (15 073), valamint egy 5 000 egységes véletlen minta az
összes szerepből; összesen 17 901 sor. Előállítja: `coding/merge_labels.py` (ellenőrzi, hogy minden adag teljes).

| Változó | Leírás |
|---|---|
| `kvazi_mondat_id` | kapcsolat a 6.1 táblához |
| `n`, `batch` | a gépi kódoláskor használt rövid sorszám (`coding/map.csv`) és az adag neve |
| `cap` | CAP-főtéma: 1–10, 12–21; 999 = nincs szakpolitikai téma (`codebooks/codebook_cap.md`, v2.1) |
| `emotion` | 3 düh, 4 félelem, 5 megvetés, 6 szomorúság, 7 öröm, 8 büszkeség, 11 semleges (`codebook_moral_emotions.md`) |
| `erzelmes` | **fő mérőszám**: 1, ha `emotion` 3–8; 0, ha 11 |
| `reason` | a modell legfeljebb 10 szavas indoklása |
| `model`, `prompt_version` | Claude Haiku (segéd-ügynök), `gold_standard/prompt_v2.md` |

### 6.3 Validálás (2.0)
Vak, friss kézi minta (24 kvázi mondat) vs. Haiku: CAP-főtéma κ = 0,67; érzelmes/semleges κ = 0,67; 7 érzelem
κ = 0,57. Két független gépi futás (250): 0,81 / 0,70 / 0,62. Részletek: `gold_standard/agreement_v2_report.md`,
`coding/reliability/rel_report.md`. Licenc és adatforrás: az Országgyűlés nyilvános jegyzőkönyvei (parlament.hu).
