"""
Futások közti megbízhatóság: az eredeti adag-kódok (labels_full.csv) vs. az új, független futás
(coding/reliability/rel_out_p*.csv) ugyanazokon a mondatokon. Összesen és adagonként.
Kimenet: a képernyőre, és coding/reliability/rel_report.md
Futtatás:  python coding/reliability_compare.py
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
C = Path(__file__).resolve().parent
orig = {r["n"]: r for r in csv.DictReader(open(C / "labels_full.csv", encoding="utf-8"))}
new = {r["n"]: r for p in sorted((C / "reliability").glob("rel_out_p*.csv"))
       for r in csv.DictReader(open(p, encoding="utf-8"))}
inp = [r["n"] for r in csv.DictReader(open(C / "reliability" / "rel_input.csv", encoding="utf-8"))]
assert sorted(new) == sorted(inp), "az új futás sorai nem egyeznek a mintával"


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] / n * cb[k] / n for k in set(ca) | set(cb))
    return po, ((po - pe) / (1 - pe) if pe < 1 else float("nan"))


def measures(ids):
    em = [(int(orig[i]["emotion"]) != 11, int(new[i]["emotion"]) != 11) for i in ids]
    return {
        "n": len(ids),
        "CAP": kappa([(orig[i]["cap"], new[i]["cap"]) for i in ids]),
        "érzelmes/semleges": kappa(em),
        "érzelem-7": kappa([(orig[i]["emotion"], new[i]["emotion"]) for i in ids]),
        "érzelmes arány (eredeti / új)": (sum(a for a, _ in em) / len(ids), sum(b for _, b in em) / len(ids)),
    }


by_batch = defaultdict(list)
for i in inp:
    by_batch[orig[i]["batch"]].append(i)
lines = ["# Futások közti megbízhatóság (Haiku, prompt v2)", "",
         "| Csoport | n | CAP egyezés / κ | Érzelmes/semleges egyezés / κ | Érzelem-7 egyezés / κ | Érzelmes arány: eredeti → új |",
         "|---|---:|---|---|---|---|"]
for name, ids in [("összesen", inp)] + sorted(by_batch.items()):
    m = measures(ids)
    f = lambda t: f"{t[0]:.2f} / {t[1]:.2f}"
    a, b = m["érzelmes arány (eredeti / új)"]
    lines.append(f"| {name} | {m['n']} | {f(m['CAP'])} | {f(m['érzelmes/semleges'])} | {f(m['érzelem-7'])} | {a:.2f} → {b:.2f} |")
(C / "reliability" / "rel_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
