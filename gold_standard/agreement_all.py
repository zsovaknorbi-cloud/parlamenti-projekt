"""
Minden ember–gép egyezésmérés újrafuttatása a /vcoder-agreement skill agreement.py-jával.
A gépi kimenetekből (llm_*.csv) előállítja a file,code formátumú címkefájlokat, majd lefuttatja az összevetéseket.
Kimenet: gold_standard/agreement_v2_report.md (a teljes agreement.py kimenet minden párra)
Futtatás a repó gyökeréből:  python gold_standard/agreement_all.py
"""
import csv
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "gold_standard"
AGREEMENT = G / "agreement.py"   # a /vcoder-agreement skill szkriptjének másolata

# (név, gépi kimenet, kézi kód előtag, megjegyzés)
RUNS = [
    ("sonnet_v1_54", "llm_claude_sonnet.csv", "v2", "prompt v1, 54 mondat, javítás előtti kézi kódok"),
    ("sonnet_v1_54_adj", "llm_claude_sonnet.csv", "v2_adj", "prompt v1, 54 mondat, egyeztetett kódok (felfelé torzít)"),
    ("llama31_v1_54", "llm_llama31.csv", "v2", "prompt v1, helyi llama3.1, 54 mondat"),
    ("sonnet_v2_v3", "llm_claude_sonnet_v3.csv", "v3", "VÉGSŐ: prompt v2, friss vak minta, 24 mondat"),
    ("haiku_v2_v3", "llm_claude_haiku_v3.csv", "v3", "VÉGSŐ: prompt v2, friss vak minta, 24 mondat (korpuszt kódoló modell)"),
]


def emo2(code):
    """A fő mérőszám: érzelmes (3–8) vs. semleges (11)."""
    return "semleges" if str(code).strip() == "11" else "erzelmes"


def write(path, pairs):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "code"])
        w.writerows(pairs)


def split(machine, name, hand):
    rows = list(csv.DictReader(open(G / machine, encoding="utf-8")))
    write(G / f"labels_{name}_cap.csv", [(r["file"], r["cap"]) for r in rows])
    write(G / f"labels_{name}_moral.csv", [(r["file"], r["emotion"]) for r in rows])
    write(G / f"labels_{name}_erzelmes.csv", [(r["file"], emo2(r["emotion"])) for r in rows])
    hm = list(csv.DictReader(open(G / f"hand_moral_{hand}.csv", encoding="utf-8")))
    write(G / f"hand_erzelmes_{hand}.csv", [(r["file"], emo2(r["code"])) for r in hm])


out = ["# Ember–gép egyezés (v2) — agreement.py kimenetek", "",
       "Blokkok: cap = CAP-főtéma; moral = 7 érzelemkategória; erzelmes = fő mérőszám (érzelmes vs. semleges).", ""]
for name, machine, hand, note in RUNS:
    split(machine, name, hand)
    for block in ("cap", "moral", "erzelmes"):
        res = subprocess.run([sys.executable, str(AGREEMENT), str(G / f"hand_{block}_{hand}.csv"),
                              str(G / f"labels_{name}_{block}.csv"), "--id", "file", "--code", "code",
                              "--mismatches", str(G / f"mismatches_{name}_{block}.csv")],
                             capture_output=True, text=True, encoding="utf-8")
        out += [f"## {name} · {block} — {note}", "", "```", res.stdout.strip(), "```", ""]
        print(name, block, "|", next((l for l in res.stdout.splitlines() if "kappa" in l), "?"))
(G / "agreement_v2_report.md").write_text("\n".join(out), encoding="utf-8")
print("-> gold_standard/agreement_v2_report.md")
