"""
Futások közti megbízhatóság (test-retest): ugyanazokat a mondatokat egy új, független Haiku-futás is kódolja.

Mintavétel: a megadott kész adagok mindegyikéből 50 véletlen mondat (seed 20261121), kevert sorrendben.
Kimenet: coding/reliability/rel_input.csv  (n, text) — a gép ugyanazt a rövid sorszámot látja, a régi kód nélkül.
Futtatás:  python coding/reliability_sample.py batch_001 batch_002 batch_003 batch_004 batch_005
"""
import csv
import random
import sys
from pathlib import Path

C = Path(__file__).resolve().parent
PER_BATCH = 50
rng = random.Random(20261121)
rows = []
for b in sys.argv[1:]:
    batch = list(csv.DictReader(open(C / "batches" / f"{b}.csv", encoding="utf-8")))
    rows += [(r["n"], r["text"]) for r in rng.sample(batch, PER_BATCH)]
rng.shuffle(rows)
(C / "reliability").mkdir(exist_ok=True)
with open(C / "reliability" / "rel_input.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["n", "text"])
    w.writerows(rows)
print(len(rows), "mondat -> coding/reliability/rel_input.csv")
