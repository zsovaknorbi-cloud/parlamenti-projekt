"""
Adatbázisok Összefésülése:
1. data/tisza_kepviselok.sqlite (Képviselői törzsadatok: kepviselo_id, mandatum_tipusa, bizottsagok)
2. data/tisza_es_miniszter_felszolalasok.sqlite (Felszólalások szűrése és tisztítása)

Eredmény:
- Egyetlen konszolidált SQLite adatbázis: data/tisza_kepviselok.sqlite
- Külső közjogi méltóságok, eskütevők és vendégek kizárva (csak TISZA képviselők és kormányzati válaszadó miniszterek)
- Tisztség mezők standardizálása (országgyűlési képviselő vs miniszteri tisztségek)
- Kapcsolt nézetek (v_felszolalasok_reszletes, v_kepviselo_statisztika)
- Exportálás: data/tisza_felszolalasok_osszefesulve.csv és .json
"""

import os
import sys
import json
import csv
import sqlite3

# Windows UTF-8 konzol támogatás
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA_DIR = "data"
KEPVISELOK_DB = os.path.join(DATA_DIR, "tisza_kepviselok.sqlite")
FELSZOLALASOK_DB = os.path.join(DATA_DIR, "tisza_es_miniszter_felszolalasok.sqlite")

OUT_CSV = os.path.join(DATA_DIR, "tisza_felszolalasok_osszefesulve.csv")
OUT_JSON = os.path.join(DATA_DIR, "tisza_felszolalasok_osszefesulve.json")

# Kiszűrendő külső közjogi méltóságok, eskütevők, nemzetiségi szószólók és meghívottak
EXCLUDED_EXTERNAL_PERSONS = {
    # Közjogi eskütevők (nem képviselők, hatósági/testületi tagok)
    "Bálint Viktor",
    "Dr. Bayer Judit",
    "Dr. Bencsik Márta",
    "Dr. Ligeti Miklós",
    "Dr. Polyák Gábor",
    "Dr. Sonnevend Pál",
    "Dr. Tasnády Katalin",
    "Unger Anna Róza",
    # Külső közjogi méltóságok
    "Dr. Baka András",           # Köztársasági elnök
    "Varga Mihály",             # Magyar Nemzeti Bank elnöke
    "Horváth Gábor",            # Költségvetési Tanács elnöke
    # Meghívott vendég
    "Dr. Gerzsenyi Gabriella",  # EP-képviselő
    # Nemzetiségi szószólók
    "Gallai Gergely",
    "Grexa Liliána",
    "Holecz Károly",
    "Paulik Antal",
    "Varga Szimeon",
}

def merge():
    print("=" * 75)
    print("ADATBÁZISOK ÖSSZEFÉSÜLÉSE ÉS ADATTISZTÍTÁSA (DATA VALIDATION & RECORD LINKAGE)")
    print("=" * 75)

    if not os.path.exists(KEPVISELOK_DB):
        raise FileNotFoundError(f"Nem található: {KEPVISELOK_DB}")
    if not os.path.exists(FELSZOLALASOK_DB):
        raise FileNotFoundError(f"Nem található: {FELSZOLALASOK_DB}")

    # 1. Felszólalások beolvasása a forrásból
    src_conn = sqlite3.connect(FELSZOLALASOK_DB)
    src_conn.row_factory = sqlite3.Row
    src_cur = src_conn.cursor()
    src_cur.execute("SELECT * FROM felszolalasok")
    raw_speeches = [dict(row) for row in src_cur.fetchall()]
    src_conn.close()

    print(f">> [1/4] Beolvasva {len(raw_speeches)} db nyers felszólalás a(z) {FELSZOLALASOK_DB}-ból.")

    # Szűrés: külső közjogi méltóságok, eskütevők és meghívottak eltávolítása
    speeches = [sp for sp in raw_speeches if sp.get("kepviselo_nev", "").strip() not in EXCLUDED_EXTERNAL_PERSONS]
    excluded_count = len(raw_speeches) - len(speeches)
    print(f">> [Szűrés] Eltávolítva {excluded_count} db felszólalás (külső eskütevők, közjogi méltóságok, szószólók: {len(EXCLUDED_EXTERNAL_PERSONS)} fő).")
    print(f">>         Megmaradt: {len(speeches)} db felszólalás (TISZA képviselők és kormánytagok).")

    # 2. Cél SQLite megnyitása (tisza_kepviselok.sqlite)
    tgt_conn = sqlite3.connect(KEPVISELOK_DB)
    tgt_conn.row_factory = sqlite3.Row
    tgt_cur = tgt_conn.cursor()

    # Képviselői alapadatok ellenőrzése
    tgt_cur.execute("SELECT * FROM tisza_kepviselok")
    mps = [dict(row) for row in tgt_cur.fetchall()]
    print(f">> [2/4] Cél adatbázis ({KEPVISELOK_DB}) ellenőrizve: {len(mps)} TISZA képviselői törzsrekord.")

    # 3. Felszólalások tábla újratöltése a képviselői adatbázisban
    tgt_cur.execute("""
        CREATE TABLE IF NOT EXISTS felszolalasok (
            felszolalas_id TEXT PRIMARY KEY,
            kepviselo_nev TEXT,
            kepviselo_id TEXT,
            frakcio TEXT,
            datum TEXT,
            ulesnap_sorszama INTEGER,
            felszolalas_sorszama INTEGER,
            hossz_masodperc INTEGER,
            hossz_formazott TEXT,
            tisztseg TEXT,
            bizottsag TEXT,
            ok TEXT,
            teljes_szoveg TEXT,
            FOREIGN KEY (kepviselo_id) REFERENCES tisza_kepviselok (kepviselo_id)
        )
    """)
    tgt_cur.execute("DELETE FROM felszolalasok")

    # Képviselő ID-k kiegészítése a név alapján, ha hiányozna
    name_to_id = {m["kepviselo_nev"]: m["kepviselo_id"] for m in mps}

    for sp in speeches:
        kid = sp.get("kepviselo_id") or ""
        nev = sp.get("kepviselo_nev") or ""
        if not kid and nev in name_to_id:
            kid = name_to_id[nev]
            sp["kepviselo_id"] = kid

        tgt_cur.execute("""
            INSERT INTO felszolalasok (
                felszolalas_id, kepviselo_nev, kepviselo_id, frakcio, datum,
                ulesnap_sorszama, felszolalas_sorszama, hossz_masodperc,
                hossz_formazott, tisztseg, bizottsag, ok, teljes_szoveg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sp["felszolalas_id"],
            nev,
            kid,
            sp["frakcio"],
            sp["datum"],
            sp["ulesnap_sorszama"],
            sp["felszolalas_sorszama"],
            sp["hossz_masodperc"],
            sp["hossz_formazott"],
            sp["tisztseg"],
            sp["bizottsag"],
            sp["ok"],
            sp["teljes_szoveg"]
        ))
    tgt_conn.commit()

    # 4. Részletes kapcsolt NÉZET létrehozása (VIEW)
    # Tisztség normalizálása: ha a parlamenti forrásban nincs kormányzati tisztség megadva,
    # akkor a képviselőnél 'országgyűlési képviselő', kormánytagoknál pedig a miniszteri rang.
    tgt_cur.execute("DROP VIEW IF EXISTS v_felszolalasok_reszletes")
    tgt_cur.execute("""
        CREATE VIEW v_felszolalasok_reszletes AS
        SELECT 
            f.felszolalas_id,
            f.datum,
            f.ulesnap_sorszama,
            f.felszolalas_sorszama,
            f.hossz_masodperc,
            f.hossz_formazott,
            COALESCE(k.kepviselo_nev, f.kepviselo_nev) AS kepviselo_nev,
            COALESCE(k.kepviselo_id, f.kepviselo_id) AS kepviselo_id,
            COALESCE(k.frakcio, f.frakcio) AS frakcio,
            COALESCE(k.mandatum_tipusa, 'Miniszter (nem képviselő)') AS mandatum_tipusa,
            k.bizottsag_1,
            k.bizottsag_2,
            CASE 
                WHEN f.tisztseg IS NOT NULL AND TRIM(f.tisztseg) != '' THEN TRIM(f.tisztseg)
                WHEN k.kepviselo_nev IS NOT NULL THEN 'országgyűlési képviselő'
                ELSE 'Kormányzati tisztségviselő'
            END AS tisztseg,
            f.bizottsag AS felszolalas_bizottsaga,
            f.ok,
            f.teljes_szoveg
        FROM felszolalasok f
        LEFT JOIN tisza_kepviselok k 
            ON (f.kepviselo_id = k.kepviselo_id AND f.kepviselo_id != '')
            OR (f.kepviselo_nev = k.kepviselo_nev)
        ORDER BY kepviselo_nev, datum, felszolalas_sorszama;
    """)

    # 5. Képviselői statisztika NÉZET létrehozása
    tgt_cur.execute("DROP VIEW IF EXISTS v_kepviselo_statisztika")
    tgt_cur.execute("""
        CREATE VIEW v_kepviselo_statisztika AS
        SELECT 
            k.kepviselo_nev,
            k.kepviselo_id,
            k.frakcio,
            k.mandatum_tipusa,
            k.bizottsag_1,
            k.bizottsag_2,
            COUNT(f.felszolalas_id) AS felszolalasok_szama,
            COALESCE(SUM(f.hossz_masodperc), 0) AS osszes_hossz_masodperc,
            ROUND(COALESCE(SUM(f.hossz_masodperc), 0) / 60.0, 1) AS osszes_hossz_perc,
            MIN(f.datum) AS elso_felszolalas_datuma,
            MAX(f.datum) AS utolso_felszolalas_datuma
        FROM tisza_kepviselok k
        LEFT JOIN felszolalasok f 
            ON (k.kepviselo_id = f.kepviselo_id AND k.kepviselo_id != '')
            OR (k.kepviselo_nev = f.kepviselo_nev)
        GROUP BY k.kepviselo_id
        ORDER BY felszolalasok_szama DESC;
    """)
    tgt_conn.commit()

    print(">> [3/4] Táblák és nézetek (v_felszolalasok_reszletes, v_kepviselo_statisztika) frissítve.")

    # 6. Összefésült adatok kinyerése és exportálása
    tgt_cur.execute("SELECT * FROM v_felszolalasok_reszletes")
    merged_rows = [dict(r) for r in tgt_cur.fetchall()]

    # A) CSV Export
    if merged_rows:
        fieldnames = list(merged_rows[0].keys())
        with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(merged_rows)

    # B) JSON Export
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged_rows, f, indent=2, ensure_ascii=False)

    print(f">> [4/4] Export sikeres:")
    print(f"   - CSV:  {OUT_CSV}")
    print(f"   - JSON: {OUT_JSON}")

    # Statisztika
    matched_mps = sum(1 for r in merged_rows if r["mandatum_tipusa"] != "Miniszter (nem képviselő)")
    minister_speeches = sum(1 for r in merged_rows if r["mandatum_tipusa"] == "Miniszter (nem képviselő)")
    missing_tisztseg = sum(1 for r in merged_rows if not r.get("tisztseg") or not r["tisztseg"].strip())

    print("\n" + "=" * 75)
    print("FRISSÍTETT ADATBÁZIS EREDMÉNYE:")
    print(f"  Összes felszólalás:                {len(merged_rows)} db")
    print(f"  - TISZA képviselői felszólalás:   {matched_mps} db")
    print(f"  - Kormányzati miniszteri válasz:  {minister_speeches} db")
    print(f"  - Hiányzó tisztségű rekord:       {missing_tisztseg} db (0 db, mind javítva!)")
    print(f"  Integrált SQLite adatbázis:        {KEPVISELOK_DB}")
    print("=" * 75)

    tgt_conn.close()

if __name__ == "__main__":
    merge()
