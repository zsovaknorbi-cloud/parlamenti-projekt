"""
Reprodukció — egy paranccsal újraépíti a tanulmány minden számát, tábláját és ábráját a repóban lévő adatokból:
    python reproduce_v2.py

Lépések:
  1. clean_quasi_sentences_v2.py     kvázi mondatok tisztítása, szerep, egységtípus → parlamenti_kvazi_mondatok_2026_v2.csv
  2. gold_standard/build_hand_v2.py  kézi kódok (54) + egyeztetés → gold_standard/hand_v2*.csv
  3. gold_standard/build_v3.py       végső vak ellenőrző minta (24) → hand_*_v3.csv
  4. gold_standard/agreement_all.py  ember–gép egyezés (Cohen-féle kappa) → gold_standard/agreement_v2_report.md
  5. coding/merge_labels.py          a gépi kódolás adagjainak ellenőrzése és összefésülése → coding/labels_full.csv
  6. coding/reliability_compare.py   két független gépi futás összevetése → coding/reliability/rel_report.md
  7. analysis/analyze_v2.py          elemzés → output_v2/ (ábrák, táblák, results.json)

A nyelvi modelles kódolást nem futtatja újra: bemenete (coding/batches/), rögzített utasítása
(gold_standard/prompt_v2.md) és kimenete (coding/out/) a repóban van, így az eredmény ellenőrizhető.
Függőségek: Python 3.10+, pandas, numpy, matplotlib, openpyxl.
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    "clean_quasi_sentences_v2.py",
    "gold_standard/build_hand_v2.py",
    "gold_standard/build_v3.py",
    "gold_standard/agreement_all.py",
    "coding/merge_labels.py",
    "coding/reliability_compare.py",
    "analysis/analyze_v2.py",
]

for i, step in enumerate(STEPS, 1):
    t0 = time.time()
    print(f"\n[{i}/{len(STEPS)}] {step}", flush=True)
    r = subprocess.run([sys.executable, str(ROOT / step)], cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"HIBA: {step} (kilépési kód {r.returncode})")
    print(f"    kész, {time.time() - t0:.1f} s", flush=True)
print("\nA reprodukció kész: az eredmények az output_v2/ mappában vannak.")
