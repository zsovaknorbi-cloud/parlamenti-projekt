import csv, sqlite3, os, sys

sys.stdout.reconfigure(encoding='utf-8')

CSV_PATH = 'parlamenti_felszolalasok_2026_teljes.csv'
SQLITE_PATH = 'parlamenti_felszolalasok_2026_teljes.sqlite'
SQL_DUMP_PATH = 'parlamenti_felszolalasok_2026_teljes.sql'

if not os.path.exists(CSV_PATH):
    print(f"Hiba: {CSV_PATH} nem található!")
    sys.exit(1)

if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()

# 1. Átgondolt, optimális oszloprend:
# A beszédhossz, szószám és karakterszám ELŐL szerepel a metaadatok között,
# a hatalmas szövegblokkok (text, text_raw) pedig a tábla VÉGÉN,
# így az SQL nézőkben (DBeaver, DB Browser, SQLite Studio) azonnal, görgetés nélkül láthatók!
cursor.execute("""
CREATE TABLE felszolalasok (
    egyedi_azonosito TEXT PRIMARY KEY,
    procedure_ID TEXT,
    partyfacts_id TEXT,
    legislative_period INTEGER,
    session INTEGER,
    speechnumber INTEGER,
    speaker TEXT NOT NULL,
    party TEXT NOT NULL,
    date TEXT NOT NULL,
    agenda TEXT,
    napirendi_mufaj TEXT,
    felszolalas_tipusa TEXT,
    tisztseg TEXT,
    minister BOOLEAN,
    chair BOOLEAN,
    written BOOLEAN,
    
    -- BESZÉDHOSSZ ÉS SZÖVEGMETRIKA (itt elöl, azonnal látható helyen!)
    hossz_masodperc INTEGER,
    hossz_formazott TEXT,
    szavak_szama INTEGER,
    karakterek_szama INTEGER,
    
    -- TARTALMI BESOROLÁSOK
    cap_kod TEXT,
    cap_fo_tema TEXT,
    cap_fo_tema_hu TEXT,
    cap_altema TEXT,
    moral_emotion TEXT,
    moral_emotion_code TEXT,
    
    -- ELJÁRÁSI ÉS FORRÁSADATOK
    iromanyszam TEXT,
    dontes_eredmeny TEXT,
    speech_link TEXT,
    pdf_url TEXT,
    felszolalas_id TEXT UNIQUE,
    datum TEXT,
    ulesnap_sorszama INTEGER,
    felszolalas_sorszama INTEGER,
    felszolalo_nev TEXT,
    frakcio TEXT,
    tema_vagy_fejlec TEXT,
    
    -- HOSSZÚ SZÖVEGEK (A TÁBLA VÉGÉN)
    text TEXT,
    text_raw TEXT
);
""")

cursor.execute("CREATE INDEX idx_felszolalasok_datum ON felszolalasok(date);")
cursor.execute("CREATE INDEX idx_felszolalasok_speaker ON felszolalasok(speaker);")
cursor.execute("CREATE INDEX idx_felszolalasok_party ON felszolalasok(party);")
cursor.execute("CREATE INDEX idx_felszolalasok_mufaj ON felszolalasok(napirendi_mufaj);")
cursor.execute("CREATE INDEX idx_felszolalasok_procedure ON felszolalasok(procedure_ID);")
cursor.execute("CREATE INDEX idx_felszolalasok_cap ON felszolalasok(cap_kod);")

# 2. Adatok beolvasása és beszúrása
with open(CSV_PATH, encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f, delimiter=';')
    rows = list(reader)

cols = [
    'egyedi_azonosito', 'procedure_ID', 'partyfacts_id', 'legislative_period', 'session',
    'speechnumber', 'speaker', 'party', 'date', 'agenda', 'napirendi_mufaj', 'felszolalas_tipusa',
    'tisztseg', 'minister', 'chair', 'written',
    'hossz_masodperc', 'hossz_formazott', 'szavak_szama', 'karakterek_szama',
    'cap_kod', 'cap_fo_tema', 'cap_fo_tema_hu', 'cap_altema',
    'moral_emotion', 'moral_emotion_code',
    'iromanyszam', 'dontes_eredmeny', 'speech_link', 'pdf_url',
    'felszolalas_id', 'datum', 'ulesnap_sorszama', 'felszolalas_sorszama',
    'felszolalo_nev', 'frakcio', 'tema_vagy_fejlec',
    'text', 'text_raw'
]

placeholders = ', '.join(['?'] * len(cols))
sql_insert = f"INSERT INTO felszolalasok ({', '.join(cols)}) VALUES ({placeholders})"

records_to_insert = []
for r in rows:
    record = []
    for c in cols:
        val = r.get(c, '')
        if c in ('legislative_period', 'session', 'speechnumber', 'ulesnap_sorszama', 'felszolalas_sorszama', 'hossz_masodperc', 'szavak_szama', 'karakterek_szama'):
            try:
                val = int(val) if val != '' and val != 'NA' else 0
            except ValueError:
                val = 0
        elif c in ('minister', 'chair', 'written'):
            val = 1 if str(val).strip().upper() in ('TRUE', '1') else 0
        record.append(val)
    records_to_insert.append(record)

cursor.executemany(sql_insert, records_to_insert)
conn.commit()

# 3. Kényelmes elemző nézetek
cursor.execute("""
CREATE VIEW v_felszolalasok_attekintes AS
SELECT 
    egyedi_azonosito,
    procedure_ID,
    date AS datum,
    session AS ulesnap,
    speechnumber AS sorszam,
    speaker AS felszolalo,
    party AS frakcio,
    tisztseg,
    napirendi_mufaj,
    felszolalas_tipusa,
    hossz_masodperc,
    hossz_formazott,
    szavak_szama,
    karakterek_szama,
    agenda AS tema,
    cap_kod,
    cap_fo_tema_hu,
    speech_link
FROM felszolalasok
ORDER BY date, session, speechnumber;
""")

cursor.execute("""
CREATE VIEW v_frakcio_statisztika AS
SELECT 
    party AS frakcio,
    COUNT(*) AS felszolalasok_szama,
    SUM(szavak_szama) AS osszes_szo,
    SUM(karakterek_szama) AS osszes_karakter,
    SUM(hossz_masodperc) AS osszes_masodperc,
    ROUND(SUM(hossz_masodperc) / 3600.0, 2) AS osszes_ora,
    ROUND(AVG(szavak_szama), 1) AS atlag_szoszam,
    ROUND(AVG(karakterek_szama), 1) AS atlag_karakterszam,
    COUNT(DISTINCT speaker) AS aktiv_kepviselok_szama
FROM felszolalasok
GROUP BY party
ORDER BY felszolalasok_szama DESC;
""")

cursor.execute("""
CREATE VIEW v_kepviselo_rangsor AS
SELECT 
    speaker AS kepviselo,
    party AS frakcio,
    COUNT(*) AS osszes_felszolalas,
    SUM(hossz_masodperc) AS osszes_masodperc,
    ROUND(SUM(hossz_masodperc) / 60.0, 1) AS osszes_perc,
    SUM(szavak_szama) AS osszes_szo,
    SUM(karakterek_szama) AS osszes_karakter
FROM felszolalasok
GROUP BY speaker, party
ORDER BY osszes_felszolalas DESC;
""")

conn.commit()

# 4. SQL dump fájl generálása
with open(SQL_DUMP_PATH, 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")

print(f"SQLite adatbázis frissítve: {SQLITE_PATH}")
print(f"SQL dump szkript frissítve: {SQL_DUMP_PATH}")
conn.close()
