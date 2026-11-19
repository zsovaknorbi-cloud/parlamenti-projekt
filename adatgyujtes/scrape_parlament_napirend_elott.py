"""
Országgyűlési napirend előtti felszólalások és hozzászólások scrapelő szkript.
Időszak: 2026-05-26 - mai napig.

Forrás: https://www.parlament.hu/web/guest/felszolalasok-keresese-m
A szkript a parlament.hu modern (Felicitas) háttér API-ját kérdezi le közvetlenül,
amely gyors, stabil és pontos adatokat szolgáltat.
"""

import os
import sys
import json
import time
import re
from datetime import datetime
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

# Windows konzol UTF-8 támogatás
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Konfiguráció
START_DATE = "2026-05-26"
END_DATE = datetime.now().strftime("%Y-%m-%d")

API_BASE = "https://www.parlament.hu/felicitas/api/query/select"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.parlament.hu/web/guest/felszolalasok-keresese-m"
}

def api_post(endpoint: str, query_params: dict, body: dict, retries: int = 3, delay: float = 1.0) -> dict:
    """POST kérés küldése a parlament API felé JSON adattal és query paraméterekkel."""
    qs = "&".join(f"{k}={v}" for k, v in query_params.items()) if query_params else ""
    url = f"{API_BASE}/{endpoint}" + (f"?{qs}" if qs else "")
    data = json.dumps(body).encode("utf-8")
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if attempt == retries - 1:
                print(f"[HIBA] HTTP {e.code} a(z) {url} elérésekor: {e.reason}", file=sys.stderr)
                raise
            time.sleep(delay * (attempt + 1))
        except Exception as e:
            if attempt == retries - 1:
                print(f"[HIBA] Hálózati hiba: {e}", file=sys.stderr)
                raise
            time.sleep(delay * (attempt + 1))
    return {}

def get_sitting_days(start_date: str, end_date: str) -> list:
    """Lekéri az összes ülésnapot a megadott dátumtartományban."""
    print(f">> Ülésnapok lekérése ({start_date} - {end_date})...")
    endpoint = "plenarisulesadatok-plenarisules-registry/plenaris-ules-adatok-query-provider/felszolalasok-keresese-query"
    body = {
        "pMultiIdoszakEleje": start_date,
        "pMultiIdoszakVege": end_date
    }
    
    all_rows = []
    page = 0
    page_size = 50
    
    while True:
        resp = api_post(endpoint, {"page": page, "size": page_size}, body)
        fields = [f.get("name") for f in resp.get("metadata", {}).get("fields", [])]
        rows = resp.get("rows", [])
        if not rows:
            break
            
        for r in rows:
            all_rows.append(dict(zip(fields, r)))
            
        total_size = resp.get("response", {}).get("totalSize", len(all_rows))
        if len(all_rows) >= total_size:
            break
        page += 1
        
    print(f"   Összesen {len(all_rows)} ülésnap található ebben az időszakban.")
    # Időrendi sorrendbe állítás (a legkorábbitól a legfrissebbig)
    all_rows.sort(key=lambda x: x.get("ulesnapDatuma", ""))
    return all_rows

def get_speeches_for_sitting(ulesnap_id: str) -> list:
    """Lekéri egy adott ülésnap összes felszólalását."""
    endpoint = "plenarisulesadatok-plenarisules-registry/plenaris-ules-adatok-query-provider/felszolalasok-keresese-ulesnap-szerint-query"
    body = {"pUlesnap": ulesnap_id}
    
    all_rows = []
    page = 0
    page_size = 100
    
    while True:
        resp = api_post(endpoint, {"page": page, "size": page_size}, body)
        fields = [f.get("name") for f in resp.get("metadata", {}).get("fields", [])]
        rows = resp.get("rows", [])
        if not rows:
            break
            
        for r in rows:
            all_rows.append(dict(zip(fields, r)))
            
        total_size = resp.get("response", {}).get("totalSize", len(all_rows))
        if len(all_rows) >= total_size:
            break
        page += 1
        
    return all_rows

def extract_speech_type(raw_tipus) -> str:
    """Kinyeri a felszólalás típusának nevét a beágyazott JSON struktúrából."""
    if isinstance(raw_tipus, dict):
        rows = raw_tipus.get("rows", [])
        if rows and rows[0]:
            return str(rows[0][0]).strip()
    elif isinstance(raw_tipus, str):
        return raw_tipus.strip()
    return ""

def parse_speaker_and_faction(speaker_raw: str, default_faction: str = None) -> tuple:
    """
    Különválasztja a nevet és a frakciót.
    Például: 'Magyar Péter (TISZA)' -> ('Magyar Péter', 'TISZA')
    Ha nincs zárójel, a megadott tisztég/alapértelmezett értéket használja.
    """
    if not speaker_raw:
        return ("", default_faction or "Ismeretlen")
        
    speaker_raw = speaker_raw.strip()
    m = re.match(r"^(.*?)\s*\((.*?)\)$", speaker_raw)
    if m:
        nev = m.group(1).strip()
        frakcio = m.group(2).strip()
        return (nev, frakcio)
    else:
        return (speaker_raw, default_faction or "Független / Kormányzati tisztségviselő")

def get_speech_detail_and_text(felszolalas_id: str) -> dict:
    """Lekéri a konkrét felszólalás adatait és a teljes szövegét."""
    endpoint = "plenarisulesadatok-plenarisules-registry/plenaris-ules-adatok-query-provider/felszolalas-adatlap-query"
    body = {"pId": felszolalas_id}
    
    resp = api_post(endpoint, {"page": 0, "size": 1}, body)
    fields = [f.get("name") for f in resp.get("metadata", {}).get("fields", [])]
    rows = resp.get("rows", [])
    
    if not rows:
        return {}
        
    d = dict(zip(fields, rows[0]))
    raw_html = d.get("felszolalasSzovege", "") or ""
    
    # HTML tisztítása sima szöveggé
    soup = BeautifulSoup(raw_html, "html.parser")
    clean_text = soup.get_text(separator="\n", strip=True)
    
    d["clean_text"] = clean_text
    return d

def format_duration(seconds: int) -> str:
    """Másodpercek átalakítása 'Xp Ymp' formátumra."""
    if seconds is None:
        return "N/A"
    try:
        sec = int(seconds)
        m, s = divmod(sec, 60)
        return f"{m} perc {s} mp ({sec} mp)"
    except Exception:
        return str(seconds)

def main():
    print("=" * 70)
    print("OR SZÁG GY ŰL ÉS  N A P I R E N D  E L ŐT T I  F E L S Z Ó L A L Á S O K")
    print(f"Időszak: {START_DATE} -> {END_DATE}")
    print("=" * 70)
    
    sitting_days = get_sitting_days(START_DATE, END_DATE)
    if not sitting_days:
        print("[!] Nem található ülésnap a megadott időszakra.")
        return

    collected_speeches = []
    
    for idx, day in enumerate(sitting_days, 1):
        ulesnap_id = day.get("ulesnapId")
        datum = day.get("ulesnapDatuma", "")[:10]
        sorszam = day.get("ulesnapSorszama")
        
        print(f"\n[{idx}/{len(sitting_days)}] Ülésnap vizsgálata: {datum} (Ülésnap sorszám: {sorszam})...")
        speeches = get_speeches_for_sitting(ulesnap_id)
        
        napirend_elotti = []
        for sp in speeches:
            sp_type = extract_speech_type(sp.get("felszolalasTipusa"))
            # Szűrés a "napirend előtti" kulcsszóra (felszólalások és hozzászólások egyaránt)
            if "napirend előtti" in sp_type.lower():
                sp["speech_type_clean"] = sp_type
                napirend_elotti.append(sp)
                
        print(f"    -> Talált napirend előtti felszólalás / hozzászólás: {len(napirend_elotti)} db")
        
        for sp in napirend_elotti:
            sp_id = sp.get("felszolalasId")
            sp_sorszam = sp.get("felszolalasSorszam")
            sp_type = sp.get("speech_type_clean")
            duration_sec = sp.get("videoIdoMasodperc")
            raw_speaker = sp.get("felszolalo", "")
            
            # Részletek és szöveg lekérése
            detail = get_speech_detail_and_text(sp_id)
            clean_text = detail.get("clean_text", "")
            tisztseg = detail.get("tisztseg")
            table_caption = detail.get("tableCaption", "")
            
            nev, frakcio = parse_speaker_and_faction(raw_speaker, default_faction=tisztseg)
            
            speech_record = {
                "id": sp_id,
                "datum": datum,
                "ulesnap_sorszama": sorszam,
                "felszolalas_sorszama": sp_sorszam,
                "fejlec": table_caption,
                "ki_mondja": nev,
                "frakcio": frakcio,
                "tisztseg": tisztseg or "",
                "tipus": sp_type,
                "hossz_masodperc": duration_sec,
                "hossz_formazott": format_duration(duration_sec),
                "szavak_szama": len(clean_text.split()) if clean_text else 0,
                "karakterek_szama": len(clean_text) if clean_text else 0,
                "szoveg": clean_text
            }
            collected_speeches.append(speech_record)
            print(f"       + [{sp_sorszam}] {nev} ({frakcio}) - {format_duration(duration_sec)}")
            
            # Rövid szünet a szerver kímélése érdekében
            time.sleep(0.1)

    print("\n" + "=" * 70)
    print(f"KÉSZ! Összesen {len(collected_speeches)} napirend előtti felszólalás / hozzászólás szövege kinyerve.")
    print("=" * 70)
    
    # 1. Mentés JSON formátumban
    json_filename = "napirend_elotti_felszolalasok_2026.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(collected_speeches, f, ensure_ascii=False, indent=2)
    print(f"[✓] Adatok mentve JSON fájlba: {json_filename}")
    
    # 2. Mentés egyetlen könnyen olvasható szöveges TXT fájlba
    txt_filename = "napirend_elotti_felszolalasok_2026.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(f"ORSZÁGGYŰLÉSI NAPIREND ELŐTTI FELSZÓLALÁSOK ÉS HOZZÁSZÓLÁSOK\n")
        f.write(f"Időszak: {START_DATE} - {END_DATE}\n")
        f.write(f"Kinyerve: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for sp in collected_speeches:
            f.write(f"DÁTUM: {sp['datum']} | ÜLÉSNAP: {sp['ulesnap_sorszama']}. | FELSZÓLALÁS: {sp['felszolalas_sorszama']}.\n")
            f.write(f"FELSZÓLALÓ: {sp['ki_mondja']}\n")
            f.write(f"FRAKCIÓ: {sp['frakcio']}" + (f" ({sp['tisztseg']})" if sp['tisztseg'] else "") + "\n")
            f.write(f"TÍPUS: {sp['tipus']}\n")
            f.write(f"HOSSZ: {sp['hossz_formazott']}\n")
            f.write("-" * 80 + "\n")
            f.write("SZÖVEG:\n")
            f.write(sp['szoveg'] + "\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
    print(f"[✓] Teljes szövegek mentve TXT fájlba: {txt_filename}")

if __name__ == "__main__":
    main()
