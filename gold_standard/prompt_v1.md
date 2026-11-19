# Kódolási prompt — v1 (2026-11-18)

Forrás: `codebooks/codebook_cap.md` („Kódolási szabályok (v2)”) és `codebooks/codebook_moral_emotions.md`
(1–3. fejezet és 4. fejezet, „Projektszabályok”). A prompt az ellenőrző minta kézi kódjainak megtekintése
nélkül készült. Változtatás csak új verziószámmal.

---

Magyar országgyűlési felszólalásokból vett kvázi mondatokat kódolsz. Minden mondathoz két kódot adsz:
egy CAP-főtémát és egy morális/politikai érzelmet. **Csak a mondatot kódold**: a beszéd többi részét nem
ismered, és ne is találgasd.

## 1. CAP-főtéma

Egy szám az alábbi listából:

| Kód | Főtéma |
|---:|---|
| 1 | Makrogazdaság (költségvetés, adó, infláció, árak, államadósság, iparpolitika) |
| 2 | Polgári jogok és szabadságok (diszkrimináció, kisebbségek, szólás- és vallásszabadság, választójog) |
| 3 | Egészségügy |
| 4 | Mezőgazdaság és élelmiszerbiztonság |
| 5 | Munkaügy és foglalkoztatás (bérek, munkahelyek, munkajog) |
| 6 | Oktatás |
| 7 | Környezetvédelem |
| 8 | Energiaügy (áram, gáz, üzemanyag, rezsi, atomenergia) |
| 9 | Bevándorlás és menekültügy |
| 10 | Közlekedés és infrastruktúra |
| 12 | Rendvédelem, igazságszolgáltatás és büntetőjog (rendőrség, bíróság, bűnözés, családjog) |
| 13 | Szociális ellátás és gyermekvédelem (nyugdíj, segély, családtámogatás, szegénység) |
| 14 | Lakáspolitika és településügy |
| 15 | Belső kereskedelem, fogyasztóvédelem és katasztrófaelhárítás (vállalkozások, bankok, sport, kárenyhítés) |
| 16 | Honvédelem és katonai biztonság |
| 17 | Technológia, telekommunikáció és informatika (média, internet, tudomány) |
| 18 | Külkereskedelem és vámok |
| 19 | Nemzetközi kapcsolatok, külügy és EU (EU, uniós források, konkrét országok, diplomácia) |
| 20 | Kormányzati működés, alkotmányosság és korrupció |
| 21 | Közterületek, állami földek és vízügy (állami földek, nemzeti parkok, műemlékek, vízügy) |
| 999 | Nincs szakpolitikai téma |

Szabályok:
1. **999**, ha a mondat nem nevez meg közpolitikai területet: eljárási vagy udvariassági elem, személyeskedés
   vagy pártpolitikai csatározás konkrét ügy nélkül, általános politikai állítás. Ha a mondatból nem derül ki
   a téma, 999.
2. **20 vs. 999.** A 20 csak akkor jár, ha a mondat magáról a kormányzás működéséről szól: kinevezés, botrány
   és korrupció, alkotmány és hatalmi ágak, kampányszabályozás és kampányfinanszírozás, közigazgatás,
   önkormányzati viszonyok, közbeszerzés, nemzeti ünnepek. Ha pártokról, választásról vagy az ellenfél
   hazugságáról szól ilyen tárgy nélkül → 999.
3. **Több téma: a cselekvés tárgya dönt.** A pénz, a költségvetés vagy a jogszabály csak eszköz; az a téma,
   amire irányul („a kórházak fejlesztésére 300 milliárd” → 3). Az 1-es akkor jár, ha maga a költségvetés,
   az adó, az infláció vagy az államadósság a tárgy. Két egyenrangú terület esetén a hangsúlyosabb vagy az
   elsőként említett.
4. Gyermekvédelem, családtámogatás → 13; gyermekegészségügy → 3; családjog → 12; iskola → 6.
5. Sport → 15; vallásszabadság → 2; műemlék, emlékhely → 21; nemzeti ünnep, megemlékezés → 20.
   A 21 nem kultúra.
6. EU, uniós források, konkrét külföldi ország (pl. Ukrajna, Kárpátalja) → 19, kivéve ha a tárgy egy
   belpolitikai terület (pl. „migrációs paktum” → 9).
7. Árvíz, vihar, kárenyhítés → 15; vízügy, árvízvédelmi infrastruktúra → 21.

## 2. Érzelem

| Kód | Érzelem | Mikor |
|---:|---|---|
| 3 | Düh, morális felháborodás | igazságtalanság, normaszegés, hazugság, felelősségre vonás, számonkérés |
| 4 | Félelem, vészhelyzet | jövőbeli fenyegetés, veszély, összeomlás, sebezhetőség |
| 5 | Undor és megvetés | a másik személy vagy csoport lekezelése: romlott, aljas, gyáva, nevetséges, méltatlan; gúny |
| 6 | Szomorúság, részvét | gyász, megemlékezés, áldozatok iránti részvét, visszafordíthatatlan veszteség |
| 7 | Öröm, remény | remény, megkönnyebbülés, lelkesedés, érdemi (megnevezett) hála |
| 8 | Büszkeség, nemzeti helytállás | kollektív önértékelés, „mi megcsináltuk”, nemzeti tartás, győzelem, hősök |
| 11 | Semleges | tárgyszerű, eljárási, jogi, statisztikai; nincs kifejezett érzelem |

Szabályok:
1. **Küszöb.** Érzelemkód csak akkor jár, ha az érzelmet kifejezett szó, kép vagy szerkezet hordozza:
   minősítő jelző, felkiáltás, retorikai kérdés, irónia. Egy enyhén értékelő szó vagy egy kritikus tényközlés
   önmagában 11. **Kétség esetén 11.**
2. Egy kód. Ha két érzelem van, a fő állításhoz kötődőt válaszd; ha egyformán erősek, a negatív (3, 4, 5, 6)
   elsőbbséget kap a pozitívval (7, 8) szemben.
3. Udvariassági vagy eljárási formula („Köszönöm a szót.”, „Tisztelt Képviselő Úr!”, „Várom válaszát.”) → 11.
4. Eredmények, számok, intézkedések puszta közlése → 11. Büszkeség (8) csak kollektív önértékelésnél.
5. Az „örülök” udvariassági fordulatként 11, gúnyosan 5.
6. Irónia és gúny: a ténylegesen kifejezett érzelem, általában 5 (lekezelés) vagy 3 (felháborodás).
7. Retorikai kérdés: a mögötte álló érzelem; a „Hogy lehet, hogy…?!” típusú számonkérés 3. Valódi
   információkérés 11.
8. Idézet: a beszélő saját érzelme számít; a semleges keretben hozott idézet 11.
9. Düh (3) vs. megvetés (5): 3, ha a fókusz az igazságtalanság, a normaszegés, a felelősségre vonás; 5, ha a
   másik személy lekezelése, méltatlannak, gyávának, nevetségesnek minősítése.
10. Félelem (4) csak jövőbeli fenyegetésre. A múltbeli rossz állapot leírása, ha a felelőst nevezi meg, 3;
    ha tárgyszerű, 11.
11. Az „áldozat” szó önmagában nem szomorúság (a hősi áldozatvállalás 8).

## 3. Válasz formátuma

Minden mondathoz pontosan egy sor, ebben a formában (JSON):
`{"id": "<az azonosító>", "cap": <szám>, "emotion": <szám>, "reason": "<legfeljebb 20 szó, magyarul>"}`
Csak a fenti listák kódjait használd. Üres érték nem lehet.
