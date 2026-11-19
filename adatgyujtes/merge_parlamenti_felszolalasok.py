"""
Parlamenti felszólalások (napirend előtt + interpellációk és azonnali kérdések) egységes korpusz-építő szkript.
Létrehozza a teljes, felszólalás-szintű 2026-os parlamenti beszéltárat.
"""

import csv
import json
import os
import sys

# Windows konzol UTF-8 támogatás
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def build_unified_corpus():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    napirend_path = os.path.join(base_dir, 'napirend_elotti_felszolalasok_2026.json')
    inter_path = os.path.join(base_dir, 'interpellaciok_es_azonnali_kerdesek_2026.json')
    
    if not os.path.exists(napirend_path) or not os.path.exists(inter_path):
        raise FileNotFoundError("A forrásfájlok nem találhatók a projekt gyökerében!")
        
    with open(napirend_path, 'r', encoding='utf-8') as f:
        napirend_data = json.load(f)
        
    with open(inter_path, 'r', encoding='utf-8') as f:
        inter_data = json.load(f)
        
    unified_records = []
    
    # 1. Napirend előtti felszólalások feldolgozása
    for item in napirend_data:
        szoveg = (item.get('szoveg') or '').strip()
        words = len(szoveg.split())
        chars = len(szoveg)
        
        unified_records.append({
            'felszolalas_id': item.get('id', ''),
            'datum': item.get('datum', ''),
            'ulesnap_sorszama': int(item.get('ulesnap_sorszama', 0)),
            'felszolalas_sorszama': int(item.get('felszolalas_sorszama', 0)),
            'napirendi_mufaj': 'napirend előtt',
            'felszolalas_tipusa': item.get('tipus', ''),
            'felszolalo_nev': item.get('ki_mondja', '').strip(),
            'frakcio': item.get('frakcio', '').strip(),
            'tisztseg': item.get('tisztseg', '').strip(),
            'tema_vagy_fejlec': item.get('fejlec', '').strip(),
            'iromanyszam': '',
            'hossz_masodperc': int(item.get('hossz_masodperc', 0)),
            'hossz_formazott': item.get('hossz_formazott', ''),
            'szavak_szama': int(item.get('szavak_szama') or words),
            'karakterek_szama': int(item.get('karakterek_szama') or chars),
            'dontes_eredmeny': '',
            'pdf_url': '',
            'szoveg': szoveg
        })
        
    # 2. Interpellációk és azonnali kérdések felszólalásainak feldolgozása
    for item in inter_data:
        iromanyszam = item.get('iromanyszam', '').strip()
        top_tipus = item.get('tipus', '').strip()
        cim = item.get('cim', '').strip()
        dontes = (item.get('dontes') or '').strip()
        pdf_url = item.get('pdf_url', '').strip()
        ulesnap_sorszama = int(item.get('ulesnap_sorszama', 0))
        datum = item.get('ulesnap_datuma', '').strip()
        
        parts = [
            ('kerdes', f"{top_tipus} - kérdés"),
            ('valasz', f"{top_tipus} - miniszteri válasz"),
            ('kepviseloi_viszonvalasz', f"{top_tipus} - képviselői viszonválasz"),
            ('miniszteri_viszonvalasz', f"{top_tipus} - miniszteri viszonválasz")
        ]
        
        for part_key, tipus_nev in parts:
            sp = item.get(part_key)
            if not sp or not isinstance(sp, dict):
                continue
                
            szoveg = (sp.get('szoveg') or '').strip()
            words = len(szoveg.split())
            chars = len(szoveg)
            hossz_mp = int(sp.get('hossz_mp', 0) or 0)
            hossz_formazott = sp.get('hossz_formazott', '')
            if not hossz_formazott and hossz_mp:
                perc = hossz_mp // 60
                mp = hossz_mp % 60
                hossz_formazott = f"{perc} perc {mp} mp" if perc > 0 else f"{mp} mp"
                
            sorszam = sp.get('sorszam')
            sorszam_int = int(sorszam) if sorszam is not None else 0
            
            unified_records.append({
                'felszolalas_id': sp.get('felszolalas_id', ''),
                'datum': sp.get('datum', datum) or datum,
                'ulesnap_sorszama': ulesnap_sorszama,
                'felszolalas_sorszama': sorszam_int,
                'napirendi_mufaj': top_tipus,
                'felszolalas_tipusa': tipus_nev,
                'felszolalo_nev': (sp.get('felszolalo_nev') or '').strip(),
                'frakcio': (sp.get('frakcio') or '').strip(),
                'tisztseg': (sp.get('tisztseg') or '').strip(),
                'tema_vagy_fejlec': cim,
                'iromanyszam': iromanyszam,
                'hossz_masodperc': hossz_mp,
                'hossz_formazott': hossz_formazott,
                'szavak_szama': words,
                'karakterek_szama': chars,
                'dontes_eredmeny': dontes,
                'pdf_url': pdf_url,
                'szoveg': szoveg
            })

    # Időrendi sorrendbe állítás: Dátum -> Ülésnap -> Felszólalás sorszáma
    unified_records.sort(key=lambda r: (r['datum'], r['ulesnap_sorszama'], r['felszolalas_sorszama']))

    # ParlLawSpeech (PLS v1.0) változók és egyedi azonosítók generálása
    from collections import Counter
    import re

    # 1. PartyFacts ID adatbázis-kapcsolat (Döring & Regel 2019 / partyfacts.org)
    PARTYFACTS_MAP = {
        'Fidesz': '1691',
        'KDNP': '1412',
        'Mi Hazánk': '34805',
        'TISZA': 'NA', # Új párt (2021), a PartyFacts korábbi törzsében még nem szerepel
    }

    # Regex a felszólaló nevének és pártjának/tisztségének levágásához a tisztított szöveghez (text)
    # pl. 'MAGYAR PÉTER miniszterelnök: ...' vagy 'TOROCZKAI LÁSZLÓ (Mi Hazánk): ...'
    header_regex = re.compile(r'^[A-ZÁÉÍÓÖŐÚÜŰ\.\s\-]{3,}(?:\([^\)]+\))?(?:\s+[a-záéíóöőúüűA-ZÁÉÍÓÖŐÚÜŰ\s\,\.\-]+)?\s*:\s*')

    # CAP (Comparative Agendas Project) meglévő kódok betöltése a korábbi harmonizált táblából
    cap_source_path = os.path.join(base_dir, 'data', 'tisza_felszolalasok_osszefesulve.csv')
    cap_lookup = {}
    if os.path.exists(cap_source_path):
        with open(cap_source_path, encoding='utf-8-sig', errors='replace') as f:
            c_reader = csv.DictReader(f, delimiter=';')
            for row in c_reader:
                fid = row.get('felszolalas_id', '').strip()
                if fid:
                    cap_lookup[fid] = {
                        'cap_kod': row.get('cap_kod', '').strip() or 'NA',
                        'cap_fo_tema': row.get('cap_fo_tema', '').strip() or 'NA',
                        'cap_fo_tema_hu': row.get('cap_fo_tema_hu', '').strip() or 'NA',
                        'cap_altema': row.get('cap_altema', '').strip() or 'NA'
                    }

    # 2. Egyedi azonosító számláló
    seen_counter = Counter()
    for r in unified_records:
        t = r['felszolalas_tipusa'].lower()
        if 'interpelláció' in t:
            code = 'IV' if 'válasz' in t else 'I'
        elif 'azonnali kérdés' in t:
            code = 'AV' if 'válasz' in t else 'A'
        elif 'napirend' in t:
            code = 'NRE'
        else:
            code = 'EGYEB'
        base_id = f"{r['datum']}_{code}_{r['felszolalo_nev']}"
        seen_counter[base_id] += 1

    # 3. Változók beépítése rekord szinten
    running_counter = Counter()
    for r in unified_records:
        t = r['felszolalas_tipusa'].lower()
        if 'interpelláció' in t:
            code = 'IV' if 'válasz' in t else 'I'
        elif 'azonnali kérdés' in t:
            code = 'AV' if 'válasz' in t else 'A'
        elif 'napirend' in t:
            code = 'NRE'
        else:
            code = 'EGYEB'
        base_id = f"{r['datum']}_{code}_{r['felszolalo_nev']}"
        total = seen_counter[base_id]
        running_counter[base_id] += 1
        idx = running_counter[base_id]

        # Felhasználói egyedi azonosító
        r['egyedi_azonosito'] = f"{base_id}_{idx}" if total > 1 else base_id

        # ParlLawSpeech CORE VARIABLES (Table 2)
        # procedure_ID: Eljárás/iromány azonosító a beszédek, törvényjavaslatok és törvények összekötéséhez
        r['procedure_ID'] = r.get('iromanyszam', '').strip() or 'NA'
        r['speaker'] = r.get('felszolalo_nev', '').strip()
        r['party'] = r.get('frakcio', '').strip()
        r['date'] = r.get('datum', '').strip()
        r['agenda'] = r.get('tema_vagy_fejlec', '').strip()
        r['speechnumber'] = r.get('felszolalas_sorszama', 0)
        r['partyfacts_id'] = PARTYFACTS_MAP.get(r['party'], 'NA')

        # ParlLawSpeech ADDITIONAL VARIABLES (Section 3.1.2)
        # legislative_period: Magyarország 43. parlamenti ciklusa
        r['legislative_period'] = 43
        # session: ülésszak / ülésnap sorszáma
        r['session'] = r.get('ulesnap_sorszama', 0)
        # chair: levezető elnök-e (plenáris érdemi vitákban FALSE)
        r['chair'] = False
        # minister: kormánytag (miniszter / államtitkár)-e
        tisztseg = r.get('tisztseg', '').lower()
        frakcio_l = r['party'].lower()
        is_min = ('miniszter' in tisztseg or 'államtitkár' in tisztseg or
                  'kormányzat' in frakcio_l or 'miniszter' in frakcio_l)
        r['minister'] = is_min
        # written: írásbeli felszólalás-e (az elhangzott beszédek mind False)
        r['written'] = False
        # speech_link: közvetlen hivatalos hivatkozás
        r['speech_link'] = r.get('pdf_url', '').strip() or 'NA'

        # Szövegek: text_raw (eredeti) és text (fejléctől megtisztított beszédtörzs)
        raw_text = r.get('szoveg', '').strip()
        r['text_raw'] = raw_text
        r['text'] = header_regex.sub('', raw_text).strip()

        # Morális és politikai érzelem változók (TenHouten 2007 / Haidt 2003 alapján)
        # Kódok: 3 (Anger), 4 (Fear), 5 (Disgust), 6 (Sadness), 7 (Joy), 8 (Pride), 11 (None)
        r['moral_emotion'] = r.get('moral_emotion', '').strip() or 'NA'
        r['moral_emotion_code'] = r.get('moral_emotion_code', '').strip() or 'NA'

        # CAP (Comparative Agendas Project) tématartalmi kódok csatolása
        fid = r.get('felszolalas_id', '').strip()
        if fid in cap_lookup:
            r['cap_kod'] = cap_lookup[fid]['cap_kod']
            r['cap_fo_tema'] = cap_lookup[fid]['cap_fo_tema']
            r['cap_fo_tema_hu'] = cap_lookup[fid]['cap_fo_tema_hu']
            r['cap_altema'] = cap_lookup[fid]['cap_altema']
        else:
            r['cap_kod'] = 'NA'
            r['cap_fo_tema'] = 'NA'
            r['cap_fo_tema_hu'] = 'NA'
            r['cap_altema'] = 'NA'

    # Oszlopstruktúra a ParlLawSpeech és a magyar mezők optimális elrendezésével
    fieldnames = [
        'egyedi_azonosito',
        'procedure_ID',
        'partyfacts_id',
        'legislative_period',
        'session',
        'speechnumber',
        'speaker',
        'party',
        'date',
        'agenda',
        # CAP témabesorolási változók
        'cap_kod',
        'cap_fo_tema',
        'cap_fo_tema_hu',
        'cap_altema',
        'minister',
        'chair',
        'written',
        'speech_link',
        'moral_emotion',
        'moral_emotion_code',
        'text',
        'text_raw',
        # Eredeti részletes mezők
        'felszolalas_id',
        'datum',
        'ulesnap_sorszama',
        'felszolalas_sorszama',
        'napirendi_mufaj',
        'felszolalas_tipusa',
        'felszolalo_nev',
        'frakcio',
        'tisztseg',
        'tema_vagy_fejlec',
        'iromanyszam',
        'hossz_masodperc',
        'hossz_formazott',
        'szavak_szama',
        'karakterek_szama',
        'dontes_eredmeny',
        'pdf_url'
    ]

    # Mentések
    # 1. Teljes JSON
    json_out_path = os.path.join(base_dir, 'parlamenti_felszolalasok_2026_teljes.json')
    with open(json_out_path, 'w', encoding='utf-8') as f:
        json.dump(unified_records, f, ensure_ascii=False, indent=2)

    # 2. Teljes CSV (szöveggel)
    csv_out_path = os.path.join(base_dir, 'parlamenti_felszolalasok_2026_teljes.csv')
    with open(csv_out_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(unified_records)

    # 3. Áttekintő CSV (szöveg nélkül, gyors táblázatos áttekintésre és elemzésre)
    overview_fields = [f for f in fieldnames if f not in ('text', 'text_raw', 'szoveg')]
    csv_overview_path = os.path.join(base_dir, 'parlamenti_felszolalasok_2026_attekintes.csv')
    with open(csv_overview_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=overview_fields, delimiter=';', extrasaction='ignore')
        writer.writeheader()
        for r in unified_records:
            row_copy = {k: r[k] for k in overview_fields}
            writer.writerow(row_copy)

    # Statisztika és validáció
    total_speeches = len(unified_records)
    total_words = sum(r['szavak_szama'] for r in unified_records)
    total_seconds = sum(r['hossz_masodperc'] for r in unified_records)
    total_hours = total_seconds / 3600
    dates = sorted(set(r['datum'] for r in unified_records))
    
    print("=" * 60)
    print("PARLAMENTI FELSZÓLALÁSOK (2026) EGYSÉGESÍTÉS SIKERES!")
    print("=" * 60)
    print(f"Összes mentett felszólalás: {total_speeches:,} db")
    print(f"Időintervallum: {dates[0]} - {dates[-1]} ({len(dates)} különböző ülésnap)")
    print(f"Összes szó: {total_words:,} szó")
    print(f"Összes felszólalási idő: {total_seconds:,} másodperc (~{total_hours:.1f} óra)")
    print("-" * 60)
    print("Létrehozott állományok:")
    print(f"  1. {os.path.basename(json_out_path)} ({os.path.getsize(json_out_path):,} bájt)")
    print(f"  2. {os.path.basename(csv_out_path)} ({os.path.getsize(csv_out_path):,} bájt)")
    print(f"  3. {os.path.basename(csv_overview_path)} ({os.path.getsize(csv_overview_path):,} bájt)")
    print("=" * 60)


if __name__ == '__main__':
    build_unified_corpus()
