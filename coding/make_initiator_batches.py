"""
Szűkített teljes kódolás (2026-11-18 döntés): a KEZDEMÉNYEZŐ szerepű tartalmi mondatok közül azok,
amelyek még nincsenek kódolva (labels_full.csv), új adagokba (batch_101, batch_102, ...).
A sorszám (n) ugyanaz marad, mint a coding/map.csv-ben, így az összefésülés változatlan.
Futtatás a repó gyökeréből:  python coding/make_initiator_batches.py
"""
import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "coding"
BATCH_SIZE = 1000
FIRST = 101

units = {r["kvazi_mondat_id"]: r for r in csv.DictReader(open(ROOT / "parlamenti_kvazi_mondatok_2026_v2.csv", encoding="utf-8"))}
done = {r["kvazi_mondat_id"] for r in csv.DictReader(open(C / "labels_full.csv", encoding="utf-8"))}
todo = []
for r in csv.DictReader(open(C / "map.csv", encoding="utf-8")):        # a map sorrendje már véletlen
    u = units[r["kvazi_mondat_id"]]
    if u["szerep"] == "kezdemenyezo" and r["kvazi_mondat_id"] not in done:
        todo.append((r["n"], u["mondat_szoveg_tiszta"].strip()))

made = []
for i in range(0, len(todo), BATCH_SIZE):
    name = f"batch_{FIRST + len(made):03d}"
    with open(C / "batches" / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "text"])
        w.writerows(todo[i:i + BATCH_SIZE])
    made.append((name, len(todo[i:i + BATCH_SIZE])))
print(f"{len(todo)} még kódolatlan kezdeményező mondat -> {len(made)} adag: " + ", ".join(f"{n} ({k})" for n, k in made))
