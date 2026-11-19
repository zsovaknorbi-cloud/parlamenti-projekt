"""
Országgyűlési Interpellációk, Azonnali Kérdések és Válaszaik Scrapelő Szkript.
Időszak: 2026-05-26 - 2026-10-12 (43. parlamenti ciklus).

Kinyeri:
1. Az összes interpellációt (I/...) és azonnali kérdést (A/...)
2. A kérdések elhangzott szó szerinti szövegét (kérdező képviselő, párt, hossz)
3. A miniszteri/államtitkári válaszok szó szerinti szövegét (válaszadó neve, tisztsége, hossz)
4. A képviselői viszonválaszokat (elfogadás/elutasítás indoklása és szövege)
5. A miniszteri viszonválaszokat (zárszó szövege)
6. A döntéseket (képviselő és Országgyűlés döntése)
7. A hivatalos iromány metaadatokat (cím, benyújtás dátuma, PDF hivatkozás)
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

START_DATE = "2026-05-26"
END_DATE = "2026-10-12"
CYCLE = 43

API_SELECT = "https://www.parlament.hu/felicitas/api/query/select"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.parlament.hu/web/guest/felszolalasok-keresese-m"
}

def api_post(endpoint: str, query_params: dict, body: dict, retries: int = 3, timeout: int = 30) -> dict:
    """POST kérés küldése a Felicitas API felé."""
    qs = "&".join(f"{k}={v}" for k, v in query_params.items()) if query_params else ""
    url = f"{API_SELECT}/{endpoint}" + (f"?{qs}" if qs else "")
    data = json.dumps(body).encode("utf-8")
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt == retries - 1:
                print(f"[!] Hiba ({url}): {e}", file=sys.stderr)
                return {}
            time.sleep(0.5 * (attempt + 1))
    return {}

def load_or_fetch_iromanyok():
    """Betölti a meglévő irományokat, vagy lekéri őket az iromany-query-ből."""
    json_path = "iromanyok_osszes.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        interp_and_azonnali = {}
        for item in data:
            szam = item.get("iromanyszam", "")
            if szam.startswith("I/") or szam.startswith("A/"):
                interp_and_azonnali[szam] = item
        print(f">> Betöltve {len(interp_and_azonnali)} db I/ és A/ iromány a meglévő adatbázisból.")
        return interp_and_azonnali
    
    print(">> Irományok lekérése a Felicitas API-ról...")
    endpoint = "iromanyadatok-iromany-registry/iromanyok-query-provider/iromany-query"
    body = {"pMultiCiklus": [CYCLE], "pUnios": False, "pNemzetisegi": False, "pIdokeretes": False}
    
    items = {}
    page = 0
    while True:
        resp = api_post(endpoint, {"page": page, "size": 50}, body)
        fields = [f.get("name") for f in resp.get("metadata", {}).get("fields", [])]
        rows = resp.get("rows", [])
        if not rows:
            break
        for r in rows:
            d = dict(zip(fields, r))
            szam = d.get("iromanyszam", "")
            if str(szam).startswith("I/") or str(szam).startswith("A/"):
                items[szam] = {
                    "iromanyszam": szam,
                    "iromany_id": d.get("iromanyId"),
                    "tipus": d.get("iromanytipus"),
                    "cim_osszefoglalo": d.get("cim"),
                    "allapot": d.get("iromanyAllapot"),
                    "benyujtas_datuma": str(d.get("benyujtasDatuma", ""))[:10]
                }
        total_size = resp.get("response", {}).get("totalSize", 0)
        page += 1
        if page * 50 >= total_size:
            break
    print(f">> Letöltve {len(items)} db I/ és A/ iromány.")
    return items

def get_all_sitting_days(start_date: str, end_date: str) -> list:
    """Lekéri az összes ülésnapot a megadott időszakra."""
    print(f">> Ülésnapok lekérése ({start_date} -> {end_date})...")
    endpoint = "plenarisulesadatok-plenarisules-registry/plenaris-ules-adatok-query-provider/felszolalasok-keresese-query"
    body = {"pMultiIdoszakEleje": start_date, "pMultiIdoszakVege": end_date}
    
    all_sittings = []
    page = 0
    while True:
        resp = api_post(endpoint, {"page": page, "size": 50}, body)
        fields = [f.get("name") for f in resp.get("metadata", {}).get("fields", [])]
        rows = resp.get("rows", [])
        if not rows:
            break
        for r in rows:
            all_sittings.append(dict(zip(fields, r)))
        total_size = resp.get("response", {}).get("totalSize", len(all_sittings))
        if len(all_sittings) >= total_size:
            break
        page += 1
        
    all_sittings.sort(key=lambda x: x.get("ulesnapDatuma", ""))
    print(f">> Összesen {len(all_sittings)} ülésnap található ebben az időszakban.")
    return all_sittings

def get_sitting_speeches(ulesnap_id: str) -> list:
    """Lekéri egy ülésnap összes felszólalását."""
    endpoint = "plenarisulesadatok-plenarisules-registry/plenaris-ules-adatok-query-provider/felszolalasok-keresese-ulesnap-szerint-query"
    body = {"pUlesnap": ulesnap_id}
    
    all_speeches = []
    page = 0
    while True:
        resp = api_post(endpoint, {"page": page, "size": 100}, body)
        fields = [f.get("name") for f in resp.get("metadata", {}).get("fields", [])]
        rows = resp.get("rows", [])
        if not rows:
            break
        for r in rows:
            all_speeches.append(dict(zip(fields, r)))
        total_size = resp.get("response", {}).get("totalSize", len(all_speeches))
        if len(all_speeches) >= total_size:
            break
        page += 1
    return all_speeches

def fetch_speech_text(speech_id: str) -> dict:
    """Lekéri egy felszólalás szó szerinti jegyzőkönyvi szövegét."""
    endpoint = "plenarisulesadatok-plenarisules-registry/plenaris-ules-adatok-query-provider/felszolalas-adatlap-query"
    body = {"pId": speech_id}
    resp = api_post(endpoint, {"page": 0, "size": 1}, body, timeout=20)
    fields = [f.get("name") for f in resp.get("metadata", {}).get("fields", [])]
    rows = resp.get("rows", [])
    if not rows:
        return {"szoveg": "", "hossz": 0, "felszolalo": "", "tisztseg": ""}
    
    d = dict(zip(fields, rows[0]))
    raw_html = d.get("felszolalasSzovege", "") or ""
    soup = BeautifulSoup(raw_html, "html.parser")
    clean_text = soup.get_text(separator="\n", strip=True)
    return {
        "szoveg": clean_text,
        "hossz": d.get("videoIdoMasodperc") or 0,
        "felszolalo": d.get("felszolalo") or "",
        "tisztseg": d.get("tisztseg") or ""
    }

def format_duration(seconds: int) -> str:
    if not seconds:
        return "0 mp"
    m, s = divmod(int(seconds), 60)
    if m > 0:
        return f"{m} perc {s} mp"
    return f"{s} mp"

def parse_speaker(speaker_raw: str, default_role: str = ""):
    if not speaker_raw:
        return ("", "Ismeretlen", default_role)
    speaker_raw = speaker_raw.strip()
    m = re.match(r"^(.*?)\s*\((.*?)\)$", speaker_raw)
    if m:
        return (m.group(1).strip(), m.group(2).strip(), default_role)
    return (speaker_raw, "Kormányzat / Egyéb", default_role)

def main():
    print("=" * 80)
    print("OR SZÁG GY ŰL ÉS  I N T E R P E L L Á C I Ó K  É S  A Z O N N A L I  K É R D É S E K")
    print(f"Időszak: {START_DATE} -> {END_DATE}")
    print("=" * 80)

    # 1. Iromány metaadatok
    iromanyok_meta = load_or_fetch_iromanyok()
    
    # 2. Ülésnapok
    sitting_days = get_all_sitting_days(START_DATE, END_DATE)

    # 3. Ülésnapok felszólalásainak összegyűjtése és eseményláncok csoportosítása
    print("\n>> Felszólalások vizsgálata az összes ülésnapon...")
    
    # Strukturált gyűjtő: iromanyszam -> rekord
    grouped_qa = {}
    all_speech_ids_to_fetch = set()

    for idx, s_day in enumerate(sitting_days, 1):
        u_id = s_day.get("ulesnapId")
        datum = s_day.get("ulesnapDatuma", "")[:10]
        sorszam = s_day.get("ulesnapSorszama")
        
        speeches = get_sitting_speeches(u_id)
        
        for sp in speeches:
            sp_id = sp.get("felszolalasId")
            sp_sorszam = sp.get("felszolalasSorszam")
            sp_speaker = sp.get("felszolalo", "")
            sp_duration = sp.get("videoIdoMasodperc") or 0
            
            # Kinyerjük a kapcsolódó irományszámokat és a felszólalás típusát
            tipus_data = sp.get("felszolalasTipusa")
            tipus_name = ""
            associated_ir = []
            
            if isinstance(tipus_data, dict):
                t_rows = tipus_data.get("rows", [])
                if t_rows and t_rows[0]:
                    tipus_name = str(t_rows[0][0]).strip()
                    if len(t_rows[0]) > 1 and isinstance(t_rows[0][1], dict):
                        for ir in t_rows[0][1].get("rows", []):
                            if len(ir) > 2 and ir[2]:
                                associated_ir.append(str(ir[2]).strip())
                                
            # Csak az I/ és A/ típusú eseményekkel foglalkozunk
            for ir_num in associated_ir:
                if ir_num.startswith("I/") or ir_num.startswith("A/"):
                    # Kivesszük az ülésvezetést (elnöki közbeiktatások)
                    if "ülésvezetés" in tipus_name.lower():
                        continue
                        
                    if ir_num not in grouped_qa:
                        meta = iromanyok_meta.get(ir_num, {})
                        grouped_qa[ir_num] = {
                            "iromanyszam": ir_num,
                            "tipus": "interpelláció" if ir_num.startswith("I/") else "azonnali kérdés",
                            "cim": meta.get("cim_osszefoglalo") or meta.get("cim") or "Nincs megadva cím",
                            "allapot": meta.get("allapot", "Ismeretlen"),
                            "benyujtas_datuma": meta.get("benyujtas_datuma", ""),
                            "benyujtok": meta.get("benyujtok", []),
                            "partok": meta.get("partok", []),
                            "pdf_url": meta.get("pdf_url", f"https://www.parlament.hu/irom{CYCLE}/{int(ir_num.split('/')[1]):05d}/{int(ir_num.split('/')[1]):05d}.pdf" if '/' in ir_num and ir_num.split('/')[1].isdigit() else ""),
                            "ulesnap_datuma": datum,
                            "ulesnap_sorszama": sorszam,
                            
                            # Események
                            "kerdes": None,
                            "valasz": None,
                            "kepviseloi_viszonvalasz": None,
                            "miniszteri_viszonvalasz": None,
                            "dontes": None
                        }
                    
                    event_data = {
                        "felszolalas_id": sp_id,
                        "sorszam": sp_sorszam,
                        "tipus_pontos": tipus_name,
                        "felszolalo_raw": sp_speaker,
                        "hossz_mp": sp_duration,
                        "datum": datum
                    }
                    all_speech_ids_to_fetch.add(sp_id)
                    
                    t_low = tipus_name.lower()
                    if "elhangzik az interpelláció" in t_low:
                        grouped_qa[ir_num]["kerdes"] = event_data
                    elif "szóban megválaszolva" in t_low or "kérdés megválaszolva" in t_low:
                        grouped_qa[ir_num]["valasz"] = event_data
                    elif "képviselői viszonválasz" in t_low or "képviselő elfogadta" in t_low or "képviselő elutasította" in t_low:
                        grouped_qa[ir_num]["kepviseloi_viszonvalasz"] = event_data
                    elif "miniszteri viszonválasz" in t_low:
                        grouped_qa[ir_num]["miniszteri_viszonvalasz"] = event_data
                    elif "interpellációs választ elfogadta" in t_low or "választ elutasította" in t_low:
                        grouped_qa[ir_num]["dontes"] = tipus_name
                    elif "bejelentés helyettes válaszadó" in t_low:
                        grouped_qa[ir_num]["dontes"] = tipus_name
                        
        print(f"   [{idx}/{len(sitting_days)}] {datum} ({sorszam}. ülés) feldolgozva.")

    print(f"\n>> Összesen {len(grouped_qa)} db elhangzott interpelláció és azonnali kérdés azonosítva.")
    print(f">> Szükséges szöveges felszólalások száma a párhuzamos letöltéshez: {len(all_speech_ids_to_fetch)} db")

    # 4. Párhuzamos szövegletöltés ThreadPoolExecutor-ral
    print(">> Beszédszövegek letöltése párhuzamos szálakon...")
    speech_texts = {}
    completed_count = 0
    total_to_fetch = len(all_speech_ids_to_fetch)
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {executor.submit(fetch_speech_text, sp_id): sp_id for sp_id in all_speech_ids_to_fetch}
        for future in as_completed(future_to_id):
            sp_id = future_to_id[future]
            try:
                data = future.result()
                speech_texts[sp_id] = data
            except Exception as e:
                speech_texts[sp_id] = {"szoveg": "", "hossz": 0, "felszolalo": "", "tisztseg": ""}
            completed_count += 1
            if completed_count % 50 == 0 or completed_count == total_to_fetch:
                pct = (completed_count / total_to_fetch) * 100
                print(f"   Haladás: {completed_count}/{total_to_fetch} ({pct:.1f}%)")

    elapsed = time.time() - start_time
    print(f"   Szövegek sikeresen letöltve {elapsed:.1f} másodperc alatt!")

    # 5. Eredmények összeállítása
    final_records = []
    
    for ir_num, qa in sorted(grouped_qa.items(), key=lambda x: (x[1].get("ulesnap_datuma", ""), x[0])):
        # Kérdés részletezése
        if qa["kerdes"]:
            q_info = speech_texts.get(qa["kerdes"]["felszolalas_id"], {})
            q_nev, q_frak, q_tiszt = parse_speaker(q_info.get("felszolalo") or qa["kerdes"]["felszolalo_raw"])
            qa["kerdes"]["felszolalo_nev"] = q_nev
            qa["kerdes"]["frakcio"] = q_frak
            qa["kerdes"]["tisztseg"] = q_info.get("tisztseg") or q_tiszt
            qa["kerdes"]["hossz_formazott"] = format_duration(q_info.get("hossz") or qa["kerdes"]["hossz_mp"])
            qa["kerdes"]["szoveg"] = q_info.get("szoveg", "")

        # Válasz részletezése
        if qa["valasz"]:
            a_info = speech_texts.get(qa["valasz"]["felszolalas_id"], {})
            a_nev, a_frak, a_tiszt = parse_speaker(a_info.get("felszolalo") or qa["valasz"]["felszolalo_raw"], default_role=a_info.get("tisztseg"))
            qa["valasz"]["felszolalo_nev"] = a_nev
            qa["valasz"]["frakcio"] = a_frak
            qa["valasz"]["tisztseg"] = a_info.get("tisztseg") or a_tiszt
            qa["valasz"]["hossz_formazott"] = format_duration(a_info.get("hossz") or qa["valasz"]["hossz_mp"])
            qa["valasz"]["szoveg"] = a_info.get("szoveg", "")

        # Képviselői viszonválasz
        if qa["kepviseloi_viszonvalasz"]:
            r_info = speech_texts.get(qa["kepviseloi_viszonvalasz"]["felszolalas_id"], {})
            r_nev, r_frak, r_tiszt = parse_speaker(r_info.get("felszolalo") or qa["kepviseloi_viszonvalasz"]["felszolalo_raw"])
            qa["kepviseloi_viszonvalasz"]["felszolalo_nev"] = r_nev
            qa["kepviseloi_viszonvalasz"]["frakcio"] = r_frak
            qa["kepviseloi_viszonvalasz"]["hossz_formazott"] = format_duration(r_info.get("hossz") or qa["kepviseloi_viszonvalasz"]["hossz_mp"])
            qa["kepviseloi_viszonvalasz"]["szoveg"] = r_info.get("szoveg", "")

        # Miniszteri viszonválasz
        if qa["miniszteri_viszonvalasz"]:
            mr_info = speech_texts.get(qa["miniszteri_viszonvalasz"]["felszolalas_id"], {})
            mr_nev, mr_frak, mr_tiszt = parse_speaker(mr_info.get("felszolalo") or qa["miniszteri_viszonvalasz"]["felszolalo_raw"], default_role=mr_info.get("tisztseg"))
            qa["miniszteri_viszonvalasz"]["felszolalo_nev"] = mr_nev
            qa["miniszteri_viszonvalasz"]["frakcio"] = mr_frak
            qa["miniszteri_viszonvalasz"]["tisztseg"] = mr_info.get("tisztseg") or mr_tiszt
            qa["miniszteri_viszonvalasz"]["hossz_formazott"] = format_duration(mr_info.get("hossz") or qa["miniszteri_viszonvalasz"]["hossz_mp"])
            qa["miniszteri_viszonvalasz"]["szoveg"] = mr_info.get("szoveg", "")

        final_records.append(qa)

    # 6. Mentések
    # A) JSON mentés
    json_path = "interpellaciok_es_azonnali_kerdesek_2026.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(final_records, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] Teljes strukturált adatbázis mentve: {json_path}")

    # B) TXT leirat
    txt_path = "interpellaciok_es_azonnali_kerdesek_2026.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("ORSZÁGGYŰLÉSI INTERPELLÁCIÓK, AZONNALI KÉRDÉSEK ÉS VÁLASZOK\n")
        f.write(f"Időszak: {START_DATE} - {END_DATE}\n")
        f.write(f"Készült: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 90 + "\n\n")

        for r in final_records:
            f.write(f"IROMÁNYSZÁM: {r['iromanyszam']} | TÍPUS: {r['tipus'].upper()} | ÜLÉSNAP: {r['ulesnap_datuma']} ({r['ulesnap_sorszama']}. ülés)\n")
            f.write(f"CÍM / TÉMA: {r['cim']}\n")
            f.write(f"BENYÚJTÁS: {r['benyujtas_datuma']} | ÁLLAPOT: {r['allapot']}\n")
            if r['pdf_url']:
                f.write(f"PDF DOKUMENTUM: {r['pdf_url']}\n")
            f.write("-" * 90 + "\n")

            # Kérdés
            if r['kerdes']:
                k = r['kerdes']
                f.write(f"▶ KÉRDÉS / INTERPELLÁCIÓ ({k.get('felszolalo_nev')} - {k.get('frakcio')} | Idő: {k.get('hossz_formazott')}):\n")
                f.write(k.get('szoveg', '') + "\n\n")
            else:
                f.write("▶ KÉRDÉS: [Nem található szóbeli elmondás a plenáris ülésen / Írásbeli beadvány]\n\n")

            # Válasz
            if r['valasz']:
                v = r['valasz']
                f.write(f"◀ VÁLASZ ({v.get('felszolalo_nev')} - {v.get('tisztseg') or v.get('frakcio')} | Idő: {v.get('hossz_formazott')}):\n")
                f.write(v.get('szoveg', '') + "\n\n")
            else:
                f.write("◀ VÁLASZ: [Nincs szóbeli válasz / Írásbeli válaszra vár]\n\n")

            # Képviselői viszonválasz
            if r['kepviseloi_viszonvalasz']:
                kv = r['kepviseloi_viszonvalasz']
                f.write(f"▶ KÉPVISELŐI VISZONVÁLASZ ({kv.get('felszolalo_nev')} | Idő: {kv.get('hossz_formazott')}):\n")
                f.write(kv.get('szoveg', '') + "\n\n")

            # Miniszteri viszonválasz
            if r['miniszteri_viszonvalasz']:
                mv = r['miniszteri_viszonvalasz']
                f.write(f"◀ MINISZTERI VISZONVÁLASZ ({mv.get('felszolalo_nev')} | Idő: {mv.get('hossz_formazott')}):\n")
                f.write(mv.get('szoveg', '') + "\n\n")

            if r['dontes']:
                f.write(f"DÖNTÉS: {r['dontes']}\n")

            f.write("\n" + "=" * 90 + "\n\n")

    print(f"[✓] Olvasható szöveges leirat mentve: {txt_path}")

    # C) CSV táblázat
    import csv
    csv_path = "interpellaciok_es_azonnali_kerdesek_2026.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Irományszám", "Típus", "Ülésnap Dátuma", "Ülésnap Sorszáma", "Cím / Téma",
            "Kérdező Képviselő", "Kérdező Frakciója", "Kérdés Hossza",
            "Válaszadó Neve", "Válaszadó Tisztsége / Pártja", "Válasz Hossza",
            "Döntés / Eredmény", "PDF Link"
        ])
        for r in final_records:
            k = r.get("kerdes") or {}
            v = r.get("valasz") or {}
            writer.writerow([
                r["iromanyszam"],
                r["tipus"],
                r["ulesnap_datuma"],
                r["ulesnap_sorszama"],
                r["cim"],
                k.get("felszolalo_nev", ""),
                k.get("frakcio", ""),
                k.get("hossz_formazott", ""),
                v.get("felszolalo_nev", ""),
                v.get("tisztseg", "") or v.get("frakcio", ""),
                v.get("hossz_formazott", ""),
                r.get("dontes", "") or r.get("allapot", ""),
                r.get("pdf_url", "")
            ])
    print(f"[✓] Táblázatos összefoglaló mentve: {csv_path}")
    print("=" * 80)
    print("SIKERESEN BEFEJEZŐDÖTT!")

if __name__ == "__main__":
    main()
