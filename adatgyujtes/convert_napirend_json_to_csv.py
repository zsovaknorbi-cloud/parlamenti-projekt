import json
import csv
import sys

# Windows UTF-8 console output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def convert_to_csv():
    json_path = "napirend_elotti_felszolalasok_2026.json"
    csv_full_path = "napirend_elotti_felszolalasok_2026.csv"
    csv_summary_path = "napirend_elotti_felszolalasok_2026_attekintes.csv"

    print(f"Olvasás: {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Betöltve: {len(data)} db felszólalás.")

    # 1. Teljes CSV (szöveggel együtt)
    fieldnames_full = [
        "datum",
        "ulesnap_sorszama",
        "felszolalas_sorszama",
        "fejlec",
        "ki_mondja",
        "frakcio",
        "tisztseg",
        "tipus",
        "hossz_masodperc",
        "hossz_formazott",
        "szavak_szama",
        "karakterek_szama",
        "id",
        "szoveg"
    ]

    headers_full = [
        "Dátum",
        "Ülésnap sorszáma",
        "Felszólalás sorszáma",
        "Fejléc",
        "Felszólaló",
        "Frakció",
        "Tisztség",
        "Típus",
        "Hossz (másodperc)",
        "Hossz (formázott)",
        "Szavak száma",
        "Karakterek száma",
        "Azonosító (ID)",
        "Szöveg"
    ]

    with open(csv_full_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers_full)
        for item in data:
            writer.writerow([
                item.get("datum", ""),
                item.get("ulesnap_sorszama", ""),
                item.get("felszolalas_sorszama", ""),
                item.get("fejlec", ""),
                item.get("ki_mondja", ""),
                item.get("frakcio", ""),
                item.get("tisztseg", ""),
                item.get("tipus", ""),
                item.get("hossz_masodperc", ""),
                item.get("hossz_formazott", ""),
                item.get("szavak_szama", ""),
                item.get("karakterek_szama", ""),
                item.get("id", ""),
                item.get("szoveg", "")
            ])

    print(f"[✓] Teljes CSV elkészült: {csv_full_path}")

    # 2. Áttekintő CSV (szöveg nélkül, gyors táblázatkezeléshez és diagramokhoz)
    headers_summary = headers_full[:-1]
    with open(csv_summary_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers_summary)
        for item in data:
            writer.writerow([
                item.get("datum", ""),
                item.get("ulesnap_sorszama", ""),
                item.get("felszolalas_sorszama", ""),
                item.get("fejlec", ""),
                item.get("ki_mondja", ""),
                item.get("frakcio", ""),
                item.get("tisztseg", ""),
                item.get("tipus", ""),
                item.get("hossz_masodperc", ""),
                item.get("hossz_formazott", ""),
                item.get("szavak_szama", ""),
                item.get("karakterek_szama", ""),
                item.get("id", "")
            ])

    print(f"[✓] Áttekintő CSV elkészült: {csv_summary_path}")

if __name__ == "__main__":
    convert_to_csv()
