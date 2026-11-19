"""
v3 (végső ellenőrző) kör: a kitöltött kódolótábla ellenőrzése és szétválasztása.

Kimenet:
  gold_standard/hand_cap_v3.csv, hand_moral_v3.csv   file, code  (/vcoder-agreement formátum)
  gold_standard/llm_input_v3.csv                     id, text    (vak gépi bemenet, kód nélkül, kevert sorrend)
A kézi kódokat nem írja ki a képernyőre, csak az ellenőrzés eredményét.
Futtatás a repó gyökeréből:  python gold_standard/build_v3.py
"""
import csv
import random
import sys
from pathlib import Path

from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
G = Path(__file__).resolve().parent
CAP = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 999}
EM = {3, 4, 5, 6, 7, 8, 11}


def num(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


ws = load_workbook(G / "hand_coding_v3.xlsx", data_only=True)["Kódolás"]
rows = list(ws.iter_rows(min_row=2, values_only=True))
manifest = [r["file"] for r in csv.DictReader(open(G / "sample_v3_manifest.csv", encoding="utf-8"))]
assert [r[1] for r in rows] == manifest, "a tábla sorai eltérnek a manifesttől"
bad = [(r[0], "CAP", r[6]) for r in rows if num(r[6]) not in CAP] + \
      [(r[0], "érzelem", r[7]) for r in rows if num(r[7]) not in EM]
if bad:
    sys.exit(f"hiányzó vagy érvénytelen kód (sorszám, oszlop, érték): {bad}")

for name, col in (("hand_cap_v3.csv", 6), ("hand_moral_v3.csv", 7)):
    with open(G / name, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "code"])
        w.writerows([r[1], num(r[col])] for r in rows)

inp = [(r[1], str(r[5]).strip()) for r in rows]
random.Random(24).shuffle(inp)
with open(G / "llm_input_v3.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "text"])
    w.writerows(inp)
print(f"{len(rows)} sor, minden kód érvényes -> hand_cap_v3.csv, hand_moral_v3.csv, llm_input_v3.csv")
