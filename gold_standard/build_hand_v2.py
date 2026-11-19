"""
Aranystandard v2 — a kézi kódok egy fájlban (54 kvázi mondat).

Források:
  gold_standard/hand_cap.csv, hand_moral.csv  — a régi 30 (alkódszintű CAP) → főtémára alakítva
  gold_standard/hand_coding_v2.xlsx           — az új 24 (főtéma)
Kimenet:
  gold_standard/hand_v2.csv        file, cap, emotion, forras
  gold_standard/hand_cap_v2.csv    file, code   (a /vcoder-agreement agreement.py formátuma)
  gold_standard/hand_moral_v2.csv  file, code
forras: regi_veletlen | regi_csere (utólag kulcsszóval becserélt; tune_9_30.py, fix_30.py) | uj_v2
Mindhárom körben a kódoló csak a mondatot látta (kontextus nélkül), gépi címke nélkül.

Futtatás a repó gyökeréből:  python gold_standard/build_hand_v2.py
"""
import csv
import sys
from pathlib import Path

from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
G = Path(__file__).resolve().parent

SWAPPED = {"2026-05-27_NRE_Dr. Juhász Hajnalka_q008", "2026-06-08_NRE_Toroczkai László_1_q038"}
CAP_MAJOR = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 999}
EMOTIONS = {3, 4, 5, 6, 7, 8, 11}


def to_major(code):
    """CAP alkód → főtéma (105 → 1, 1308 → 13, 2000 → 20); 999 és a főtémák változatlanok."""
    c = int(code)
    if c == 999 or c in CAP_MAJOR:
        return c
    return c // 100


def read_codes(path):
    with open(path, encoding="utf-8-sig") as f:
        return {r["file"]: r["code"] for r in csv.DictReader(f)}


def main():
    old_cap, old_em = read_codes(G / "hand_cap.csv"), read_codes(G / "hand_moral.csv")
    assert old_cap.keys() == old_em.keys()
    rows = []
    for fid in old_cap:
        rows.append({"file": fid, "cap": to_major(old_cap[fid]), "emotion": int(old_em[fid]),
                     "forras": "regi_csere" if fid in SWAPPED else "regi_veletlen"})

    ws = load_workbook(G / "hand_coding_v2.xlsx", data_only=True)["Kódolás"]
    for r in ws.iter_rows(min_row=2, values_only=True):
        rows.append({"file": r[1], "cap": int(str(r[6]).strip()), "emotion": int(str(r[7]).strip()),
                     "forras": "uj_v2"})

    ids = [r["file"] for r in rows]
    assert len(ids) == len(set(ids)) == 54, "duplikált vagy hiányzó sor"
    assert all(r["cap"] in CAP_MAJOR for r in rows), "érvénytelen CAP-főtéma"
    assert all(r["emotion"] in EMOTIONS for r in rows), "érvénytelen érzelemkód"

    with open(G / "hand_v2.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "cap", "emotion", "forras"])
        w.writeheader()
        w.writerows(rows)
    for name, key in (("hand_cap_v2.csv", "cap"), ("hand_moral_v2.csv", "emotion")):
        with open(G / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["file", "code"])
            w.writerows([r["file"], r[key]] for r in rows)

    # Egyeztetett (adjudikált) referencia: a kutató javításai a gépi eltérések átnézése után
    # (gold_standard/hand_corrections_v2.csv). A javítatlan változat is megmarad.
    corr = G / "hand_corrections_v2.csv"
    n_corr = 0
    if corr.exists():
        by_id = {r["file"]: dict(r) for r in rows}
        with open(corr, encoding="utf-8") as f:
            for c in csv.DictReader(f):
                row = by_id[c["file"]]
                assert str(row[c["field"]]) == c["old"], f"eltérő régi érték: {c}"
                row[c["field"]] = int(c["new"])
                n_corr += 1
        adj = list(by_id.values())
        with open(G / "hand_v2_adj.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["file", "cap", "emotion", "forras"])
            w.writeheader()
            w.writerows(adj)
        for name, key in (("hand_cap_v2_adj.csv", "cap"), ("hand_moral_v2_adj.csv", "emotion")):
            with open(G / name, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["file", "code"])
                w.writerows([r["file"], r[key]] for r in adj)

    from collections import Counter
    print("sorok:", len(rows), dict(Counter(r["forras"] for r in rows)), "| javítás:", n_corr)
    print("-> gold_standard/hand_v2.csv (+ _adj), hand_cap_v2.csv, hand_moral_v2.csv (+ _adj)")


if __name__ == "__main__":
    main()
