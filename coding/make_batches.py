"""
A teljes korpusz gépi kódolásának előkészítése: adagok (batch-ek) a tartalmi kvázi mondatokból.

- Bemenet: parlamenti_kvazi_mondatok_2026_v2.csv (a clean_quasi_sentences_v2.py állítja elő),
  csak az egyseg_tipus == "tartalmi" sorok, a mondat_szoveg_tiszta szöveggel (közbeszólás nélkül).
- A sorrend véletlen (seed 20261120), hogy minden adag a teljes korpusz keresztmetszete legyen.
- A gép rövid sorszámot (n) lát a hosszú azonosító helyett (tokentakarékosság); a visszafejtés a map.csv-vel.
Kimenet:
  coding/map.csv                 n, kvazi_mondat_id
  coding/batches/batch_NNN.csv   n, text   (BATCH_SIZE soronként)
Futtatás a repó gyökeréből:  python coding/make_batches.py
"""
import csv
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "parlamenti_kvazi_mondatok_2026_v2.csv"
OUT = ROOT / "coding"
SEED = 20261120
BATCH_SIZE = 1000

rows = [(r["kvazi_mondat_id"], r["mondat_szoveg_tiszta"].strip())
        for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["egyseg_tipus"] == "tartalmi"]
assert len(rows) == len({r[0] for r in rows})
random.Random(SEED).shuffle(rows)

(OUT / "batches").mkdir(parents=True, exist_ok=True)
with open(OUT / "map.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["n", "kvazi_mondat_id"])
    w.writerows([i, rid] for i, (rid, _) in enumerate(rows, 1))

n_batches = 0
for b in range(0, len(rows), BATCH_SIZE):
    n_batches += 1
    with open(OUT / "batches" / f"batch_{n_batches:03d}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "text"])
        w.writerows([b + i + 1, text] for i, (_, text) in enumerate(rows[b:b + BATCH_SIZE]))
print(f"{len(rows)} tartalmi mondat -> {n_batches} adag (coding/batches/), térkép: coding/map.csv")
