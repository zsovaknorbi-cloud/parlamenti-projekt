"""
A gépi kódolás adagjainak összefésülése és ellenőrzése (a /vclassify számlálási ellenőrzése szerint).

Bemenet:  coding/out/batch_NNN_pK.csv   n, cap, emotion, reason   (a segéd-ügynökök írják)
          coding/batches/batch_NNN.csv  (ebből tudjuk, mely n-eknek kell meglenniük)
          coding/map.csv                n → kvazi_mondat_id
          coding/runs.csv               batch, model, prompt_version, datum  (adagonként egy sor)
Kimenet:  coding/labels_full.csv        kvazi_mondat_id, n, batch, cap, emotion, erzelmes, reason, model, prompt_version
Ellenőrzés adagonként: minden n pontosan egyszer szerepel, nincs idegen n, minden kód érvényes.
Hibás vagy hiányos adag nem kerül be (a jelentés megnevezi); a többi igen.
Futtatás a repó gyökeréből:  python coding/merge_labels.py
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
C = Path(__file__).resolve().parent
CAP = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 999}
EM = {3, 4, 5, 6, 7, 8, 11}

idmap = {int(r["n"]): r["kvazi_mondat_id"] for r in csv.DictReader(open(C / "map.csv", encoding="utf-8"))}
runs = {r["batch"]: r for r in csv.DictReader(open(C / "runs.csv", encoding="utf-8"))} if (C / "runs.csv").exists() else {}

parts = defaultdict(list)
for p in sorted((C / "out").glob("batch_*_p*.csv")):
    parts[re.match(r"(batch_\d+)_p\d+\.csv", p.name).group(1)].append(p)

out, report = [], []
for batch, files in sorted(parts.items()):
    expected = {int(r["n"]) for r in csv.DictReader(open(C / "batches" / f"{batch}.csv", encoding="utf-8"))}
    rows = [r for p in files for r in csv.DictReader(open(p, encoding="utf-8"))]
    cnt = Counter(int(r["n"]) for r in rows)
    missing, dup, extra = expected - set(cnt), [n for n, k in cnt.items() if k > 1], set(cnt) - expected
    invalid = [r["n"] for r in rows if int(r["cap"]) not in CAP or int(r["emotion"]) not in EM]
    ok = not (missing or dup or extra or invalid) and batch in runs
    report.append(f"{batch}: {len(rows)}/{len(expected)} sor | hiányzó {len(missing)} | duplikált {len(dup)} | "
                  f"idegen {len(extra)} | érvénytelen kód {len(invalid)} | futásnapló {'van' if batch in runs else 'NINCS'}"
                  f" -> {'BEKERÜL' if ok else 'KIMARAD'}")
    if ok:
        run = runs[batch]
        for r in sorted(rows, key=lambda r: int(r["n"])):
            em = int(r["emotion"])
            out.append({"kvazi_mondat_id": idmap[int(r["n"])], "n": int(r["n"]), "batch": batch,
                        "cap": int(r["cap"]), "emotion": em, "erzelmes": int(em != 11),
                        "reason": r.get("reason", "").strip(), "model": run["model"],
                        "prompt_version": run["prompt_version"]})

with open(C / "labels_full.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["kvazi_mondat_id", "n", "batch", "cap", "emotion", "erzelmes", "reason",
                                      "model", "prompt_version"])
    w.writeheader()
    w.writerows(out)
print("\n".join(report))
print(f"\nösszesen bekerült: {len(out)} / {len(idmap)} tartalmi mondat -> coding/labels_full.csv")
