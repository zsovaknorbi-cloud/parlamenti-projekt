"""
Gépi kódolás helyi modellel (ollama), rögzített prompttal.

Használat:  python gold_standard/llm_ollama.py <bemenet.csv> <kimenet.csv> [--model llama3.1:latest]
Bemenet: id, text.  Kimenet: file, cap, emotion, reason, model, prompt_version, raw
Beállítások: temperature 0, seed 42, JSON kimenet. Ha a válasz érvénytelen, egyszer újrapróbálja;
ha akkor sem jó, a sor cap=999, emotion=11 kódot kap "SET-ASIDE" indoklással (nem marad üres).
Futás közben minden sort azonnal kiír, így megszakítás után folytatható (a kész azonosítókat kihagyja).
"""
import argparse
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
PROMPT_FILE = HERE / "prompt_v1.md"
PROMPT_VERSION = "v1"
CAP = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 999}
EM = {3, 4, 5, 6, 7, 8, 11}
FIELDS = ["file", "cap", "emotion", "reason", "model", "prompt_version", "raw"]


def system_prompt():
    text = PROMPT_FILE.read_text(encoding="utf-8")
    return text.split("---", 1)[1].strip()   # a fejléc (forrás, verzió) nem része a promptnak


def ask(model, system, sid, sentence):
    body = {
        "model": model, "stream": False, "format": "json",
        "options": {"temperature": 0, "seed": 42, "num_ctx": 8192},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f'Azonosító: {sid}\nMondat: "{sentence}"\n\nVálasz egyetlen JSON-objektumként.'},
        ],
    }
    req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["message"]["content"]


def parse(raw):
    d = json.loads(raw)
    cap, em = int(d["cap"]), int(d["emotion"])
    if cap not in CAP or em not in EM:
        raise ValueError(f"érvénytelen kód: {cap}, {em}")
    return cap, em, str(d.get("reason", "")).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--model", default="llama3.1:latest")
    a = ap.parse_args()
    system = system_prompt()
    rows = list(csv.DictReader(open(a.inp, encoding="utf-8")))
    out = Path(a.out)
    done = set()
    if out.exists():
        done = {r["file"] for r in csv.DictReader(open(out, encoding="utf-8"))}
    new = not out.exists()
    with open(out, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        t0 = time.time()
        for i, r in enumerate(rows, 1):
            if r["id"] in done:
                continue
            raw = ""
            for attempt in range(2):
                try:
                    raw = ask(a.model, system, r["id"], r["text"])
                    cap, em, reason = parse(raw)
                    break
                except Exception as e:  # noqa: BLE001
                    cap, em, reason = 999, 11, f"SET-ASIDE: {e}"[:200]
            w.writerow({"file": r["id"], "cap": cap, "emotion": em, "reason": reason, "model": a.model,
                        "prompt_version": PROMPT_VERSION, "raw": raw.replace("\n", " ")[:500]})
            f.flush()
            print(f"{i}/{len(rows)}  {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
