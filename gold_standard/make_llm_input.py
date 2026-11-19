"""
A gépi kódolás bemenete az 54 ellenőrző mondatra: pontosan az a szöveg, amit a kézi kódoló látott,
véletlen sorrendben, kód nélkül.  Kimenet: gold_standard/llm_input_54.csv (id, text)
Futtatás a repó gyökeréből:  python gold_standard/make_llm_input.py
"""
import csv
import random
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
rows = []
with open(ROOT / "hand_coding_sablon.csv", encoding="utf-8-sig") as f:   # a régi 30 kódolólapja
    rows += [(r["file"], r["szoveg"].strip()) for r in csv.DictReader(f)]
ws = load_workbook(ROOT / "gold_standard" / "hand_coding_v2.xlsx", read_only=True)["Kódolás"]
rows += [(r[1], str(r[5]).strip()) for r in ws.iter_rows(min_row=2, values_only=True)]
assert len(rows) == 54 == len({r[0] for r in rows})
random.Random(54).shuffle(rows)
with open(ROOT / "gold_standard" / "llm_input_54.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "text"])
    w.writerows(rows)
print(len(rows), "mondat -> gold_standard/llm_input_54.csv")
