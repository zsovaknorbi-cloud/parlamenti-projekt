"""
Kvázi mondatok tisztítása és címkézése (v2).

NEM bontja újra a szöveget: a kvázi mondat egységek és azonosítóik megmaradnak (a kézi kódok ezekre vonatkoznak).
Egyetlen kivétel: a 12 körüli eset, ahol a rövidítéslista miatt egy mondatvég nem vágódott el
(„… nap. Tényleg …”); ezek két egységre válnak, a második azonosítója `_qNNNb`.

Hozzáadott oszlopok:
  mondat_szoveg_tiszta  a mondat közbeszólások nélkül (ezt kódoljuk)
  kozbeszolas           a mondatból kiemelt zárójeles közbeszólás(ok), pl. „Derültség a Fidesz soraiban.”
  egyseg_tipus          tartalmi | eljarasi | kozbeszolas
  szerep                kezdemenyezo | kormanyzati_valaszado | frakcio_hozzaszolo
  fordulo               elso | viszonvalasz
  party_v2              frakció (tisztségnevek helyett), ill. „Kormány (nem képviselő)”
  oldal                 kormany | ellenzek
  tiszta_szoszam        szavak száma a tiszta szövegben
  javitas               mi történt az egységgel (üres, ha semmi)

Bemenet:  parlamenti_felszolalasok_2026_teljes.sqlite (csak olvasás; kvazi_mondatok és felszolalasok tábla)
Kimenet:  parlamenti_kvazi_mondatok_2026_v2.csv
          output_elemzes/kvazi_mondatok_v2_report.md
Futtatás: python clean_quasi_sentences_v2.py
"""
import csv
import re
import sqlite3
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DB = ROOT / "parlamenti_felszolalasok_2026_teljes.sqlite"
OUT_CSV = ROOT / "parlamenti_kvazi_mondatok_2026_v2.csv"
OUT_REPORT = ROOT / "output_elemzes" / "kvazi_mondatok_v2_report.md"
GOLD_FILES = [ROOT / "hand_coding_sablon.csv", ROOT / "gold_standard" / "sample_v2_manifest.csv"]

FRAKCIOK = {"TISZA", "Fidesz", "KDNP", "Mi Hazánk"}
KORMANYOLDAL = {"TISZA"}

# --- 1. Rövidítés miatt össze nem vágott mondatvégek -------------------------------------------
# Csak valódi köznevek, amelyek tévesen kerültek a rövidítéslistára.
MISSED_SPLIT = re.compile(r"\b(nap|szám|cikk|hat|rendelet)\. (?=[A-ZÁÉÍÓÖŐÚÜŰ„])")

# --- 2. Közbeszólások ----------------------------------------------------------------------------
# A jegyzőkönyvben minden zárójeles rész közbeszólás vagy elnöki jelzés, kivéve a (sic!) és a (1) típusú
# számozást. A zárójeles rész a kvázi mondat határain is átnyúlhat (a bontó a kettőspontnál vágott),
# ezért beszédenként, a teljes egységsoron keressük a párokat.
NOT_INTERJECTION = re.compile(r"^\(\s*(sic!?|\d{1,2}|[a-h])\s*\)$", re.IGNORECASE)
MAX_SPAN = 800  # ennél hosszabb „zárójel” valószínűleg páratlan zárójel, nem közbeszólás

# --- 3. Eljárási formulák ------------------------------------------------------------------------
PROC_WORDS = {
    "tisztelt", "kedves", "elnök", "úr", "asszony", "ház", "országgyűlés", "képviselőtársaim", "képviselőtársam",
    "képviselőtársak", "miniszter", "államtitkár", "képviselő", "miniszterelnök", "honfitársaim", "hölgyeim",
    "uraim", "és", "köszönöm", "köszönjük", "szépen", "a", "az", "szót", "figyelmet", "figyelmüket", "figyelmükat",
    "megtisztelő", "hogy", "meghallgattak", "várom", "válaszát", "választ", "parancsoljon", "nagyon", "önöknek",
    "elnökasszony", "elnökúr", "házelnök", "alelnök", "jó", "napot", "kívánok", "mindenkinek",
}
TOKEN = re.compile(r"[a-záéíóöőúüű]+", re.IGNORECASE)

# --- 4. Szerep -----------------------------------------------------------------------------------
def szerep_fordulo(tipus, minister):
    fordulo = "viszonvalasz" if "viszonválasz" in tipus else "elso"
    if tipus in ("napirend előtti felszólalás", "interpelláció - kérdés", "azonnali kérdés - kérdés") \
            or "képviselői viszonválasz" in tipus:
        return "kezdemenyezo", fordulo
    if "miniszteri" in tipus:
        return "kormanyzati_valaszado", fordulo
    if tipus == "napirend előttihez hozzászólás":
        return ("kormanyzati_valaszado" if minister else "frakcio_hozzaszolo"), fordulo
    raise ValueError(f"ismeretlen felszólalás-típus: {tipus}")


def clean_ws(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?…])", r"\1", s)
    s = re.sub(r"^[\s,;:‑–—-]+", "", s)        # bal oldalon maradt írásjel / gondolatjel
    s = re.sub(r"[\s,;:‑–—-]+$", "", s) if not re.search(r"[.!?…]$", s) else s
    return s.strip()


def is_procedural(text):
    toks = TOKEN.findall(text.lower())
    return 0 < len(toks) <= 12 and all(t in PROC_WORDS for t in toks)


def gold_ids():
    ids = set()
    for p in GOLD_FILES:
        if p.exists():
            with open(p, encoding="utf-8-sig") as f:
                ids |= {r["file"] for r in csv.DictReader(f)}
    return ids


def interjection_mask(stream):
    """Visszaad egy bool listát: True, ha a karakter közbeszólás (zárójeles rész) része."""
    mask = [False] * len(stream)
    i = 0
    while i < len(stream):
        if stream[i] == "(":
            depth, j = 0, i
            while j < len(stream) and j - i <= MAX_SPAN:
                if stream[j] == "(":
                    depth += 1
                elif stream[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j < len(stream) and depth == 0 and j - i <= MAX_SPAN:
                span = stream[i:j + 1].replace("\x00", " ")
                if not NOT_INTERJECTION.match(span):
                    for k in range(i, j + 1):
                        if stream[k] != "\x00":
                            mask[k] = True
                i = j + 1
                continue
        i += 1
    return mask


def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    units = con.execute("""
        SELECT kvazi_mondat_id, beszed_id, mondat_sorszam, speaker, party, date, napirendi_mufaj,
               felszolalas_tipusa, tisztseg, minister, mondat_szoveg, mondat_szoszam
        FROM kvazi_mondatok ORDER BY beszed_id, mondat_sorszam""").fetchall()
    speeches = {r["egyedi_azonosito"]: r for r in con.execute(
        "SELECT egyedi_azonosito, text, szavak_szama FROM felszolalasok")}
    con.close()
    n_in = len(units)
    protected = gold_ids()

    # Felszólalónkénti frakció a hibás party-értékek javításához
    speaker_party = defaultdict(Counter)
    for u in units:
        if u["party"] in FRAKCIOK:
            speaker_party[u["speaker"]][u["party"]] += 1

    by_speech = defaultdict(list)
    for u in units:
        by_speech[u["beszed_id"]].append(dict(u))

    out, log = [], Counter()
    split_examples, party_fixes, interj_examples = [], Counter(), []

    for sid, us in by_speech.items():
        # 1. elmaradt mondatvég-vágások
        expanded = []
        for u in us:
            parts = MISSED_SPLIT.split(u["mondat_szoveg"])
            if len(parts) > 1 and u["kvazi_mondat_id"] not in protected:
                # a split a csoportot is visszaadja: [elő, szó, után, szó, után…] -> újraragasztás
                pieces, cur = [], parts[0]
                for k in range(1, len(parts), 2):
                    pieces.append(cur + parts[k] + ".")
                    cur = parts[k + 1]
                pieces.append(cur)
                for n, p in enumerate(pieces):
                    v = dict(u)
                    v["kvazi_mondat_id"] = u["kvazi_mondat_id"] + ("" if n == 0 else "b" * n)
                    v["mondat_szoveg"] = p.strip()
                    v["javitas"] = "mondatvég szétvágva (rövidítéslista-hiba)"
                    expanded.append(v)
                log["szétvágott egység"] += 1
                split_examples.append(" | ".join(x.strip()[:60] for x in pieces))
            else:
                u["javitas"] = "" if len(parts) == 1 else "mondatvég-hiba, de aranystandard: nem vágva"
                expanded.append(u)

        # 2. közbeszólások a teljes beszéden
        stream = "\x00".join(u["mondat_szoveg"] for u in expanded)
        mask = interjection_mask(stream)
        pos = 0
        for u in expanded:
            txt = u["mondat_szoveg"]
            m = mask[pos:pos + len(txt)]
            pos += len(txt) + 1
            clean = "".join(c for c, x in zip(txt, m) if not x)
            inter = "".join(c if x else " " for c, x in zip(txt, m))
            inter = " | ".join(clean_ws(p) for p in re.split(r"\s{2,}", inter) if clean_ws(p))
            clean = clean_ws(clean)
            if inter:
                log["közbeszólást tartalmazó egység"] += 1
                if len(interj_examples) < 6 and clean:
                    interj_examples.append((txt[:140], clean[:100], inter[:80]))

            # 3. egységtípus
            if not TOKEN.search(clean):
                tipus = "kozbeszolas"
            elif is_procedural(clean):
                tipus = "eljarasi"
            else:
                tipus = "tartalmi"

            # 4. szerep, frakció, oldal
            minister = str(u["minister"]) in ("1", "True", "true")
            szerep, fordulo = szerep_fordulo(u["felszolalas_tipusa"], minister)
            party = u["party"]
            if party in FRAKCIOK:
                party_v2 = party
            elif speaker_party[u["speaker"]]:
                party_v2 = speaker_party[u["speaker"]].most_common(1)[0][0]
                party_fixes[(party, u["speaker"], party_v2)] += 1
            else:
                party_v2 = "Kormány (nem képviselő)"
                party_fixes[(party, u["speaker"], party_v2)] += 1
            oldal = "kormany" if (minister or party_v2 in KORMANYOLDAL or party_v2.startswith("Kormány")) else "ellenzek"

            out.append({
                "kvazi_mondat_id": u["kvazi_mondat_id"], "beszed_id": sid, "mondat_sorszam": u["mondat_sorszam"],
                "speaker": u["speaker"], "party": party, "party_v2": party_v2, "oldal": oldal,
                "minister": int(minister), "tisztseg": u["tisztseg"], "date": u["date"],
                "napirendi_mufaj": u["napirendi_mufaj"], "felszolalas_tipusa": u["felszolalas_tipusa"],
                "szerep": szerep, "fordulo": fordulo, "egyseg_tipus": tipus,
                "mondat_szoveg": u["mondat_szoveg"], "mondat_szoveg_tiszta": clean, "kozbeszolas": inter,
                "mondat_szoszam": len(u["mondat_szoveg"].split()), "tiszta_szoszam": len(clean.split()),
                "javitas": u.get("javitas", ""),
            })

    # --- Ellenőrzések ----------------------------------------------------------------------------
    ids = [r["kvazi_mondat_id"] for r in out]
    assert len(ids) == len(set(ids)), "nem egyedi azonosító!"
    old_ids = {u["kvazi_mondat_id"] for u in units}
    assert old_ids <= set(ids), "elveszett egység!"
    missing_gold = protected - set(ids)
    # minden régi egység szövege megvan (a szétvágottaké darabokban)
    words_old = sum(len(u["mondat_szoveg"].split()) for u in units)
    words_new = sum(r["mondat_szoszam"] for r in out)

    # Szegmentálás vs. egyszerű mondatszámlálás (beszédenként), /datavalidation 4. lépés
    ratios = []
    for sid, us in by_speech.items():
        t = speeches[sid]["text"] or ""
        t = re.sub(r"\([^()]{0,800}\)", " ", t)
        n_sent = len(re.findall(r"[.!?…]+(?=\s+[A-ZÁÉÍÓÖŐÚÜŰ„(]|\s*$)", t)) or 1
        ratios.append((sid, n_sent))
    units_per_speech = Counter(r["beszed_id"] for r in out if r["egyseg_tipus"] != "kozbeszolas")
    rr = sorted((units_per_speech[sid] / n, sid, units_per_speech[sid], n) for sid, n in ratios)
    ratio_vals = [x[0] for x in rr]

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    # --- Jelentés --------------------------------------------------------------------------------
    t_cnt = Counter(r["egyseg_tipus"] for r in out)
    cross = Counter((r["napirendi_mufaj"], r["szerep"]) for r in out if r["egyseg_tipus"] == "tartalmi")
    side = Counter((r["szerep"], r["oldal"]) for r in out if r["egyseg_tipus"] == "tartalmi")
    q = statistics.quantiles(ratio_vals, n=20)
    L = []
    L.append("# Kvázi mondatok v2 — tisztítási jelentés\n")
    L.append(f"Szkript: `clean_quasi_sentences_v2.py` · bemenet: `kvazi_mondatok` tábla ({n_in:,} egység) · "
             f"kimenet: `{OUT_CSV.name}` ({len(out):,} egység)\n".replace(",", " "))
    L.append("## Ellenőrzések\n")
    L.append(f"- Egyedi azonosítók: igen ({len(ids):,}); minden régi azonosító megvan: igen.".replace(",", " "))
    L.append(f"- Aranystandard-azonosítók a kimenetben: {len(protected) - len(missing_gold)}/{len(protected)}.")
    L.append(f"- Szavak száma a régi és az új egységekben: {words_old:,} → {words_new:,}".replace(",", " ")
             + " (a szöveg nem veszett el; a közbeszólás külön oszlopba került, de a `mondat_szoveg` változatlan).")
    L.append(f"- Elmaradt mondatvég-vágás javítva: {log['szétvágott egység']} egység.")
    L.append(f"- Közbeszólást tartalmazó egység: {log['közbeszólást tartalmazó egység']:,}.\n".replace(",", " "))
    L.append("## Egységtípusok\n")
    L.append("| Típus | Egység | Arány |\n|---|---:|---:|")
    for k in ("tartalmi", "eljarasi", "kozbeszolas"):
        L.append(f"| {k} | {t_cnt[k]:,} | {t_cnt[k] / len(out):.1%} |".replace(",", " "))
    L.append("\nAz elemzés nevezője a **tartalmi** egység; az eljárási formulák és a közbeszólás-egységek kimaradnak.\n")
    L.append("## Tartalmi egységek műfaj és szerep szerint\n")
    L.append("| Műfaj | kezdeményező | kormányzati válaszadó | frakció-hozzászóló |\n|---|---:|---:|---:|")
    for m in ("napirend előtt", "interpelláció", "azonnali kérdés"):
        L.append(f"| {m} | {cross[(m, 'kezdemenyezo')]:,} | {cross[(m, 'kormanyzati_valaszado')]:,} | "
                 f"{cross[(m, 'frakcio_hozzaszolo')]:,} |".replace(",", " "))
    L.append("\n| Szerep | kormány | ellenzék |\n|---|---:|---:|")
    for s in ("kezdemenyezo", "kormanyzati_valaszado", "frakcio_hozzaszolo"):
        L.append(f"| {s} | {side[(s, 'kormany')]:,} | {side[(s, 'ellenzek')]:,} |".replace(",", " "))
    L.append("\n## party javítások (party → party_v2)\n")
    L.append("| eredeti party | felszólaló | party_v2 | egység |\n|---|---|---|---:|")
    for (p, s, p2), n in sorted(party_fixes.items(), key=lambda x: -x[1]):
        L.append(f"| {p} | {s} | {p2} | {n} |")
    L.append("\n## Szegmentálás vs. egyszerű mondatszámlálás (beszédenként)\n")
    L.append("Arány = nem-közbeszólás egységek száma / írásjel alapján számolt mondatok száma. "
             "1 fölött: a bontó a mondatokat tagmondatokra is vágta (ez a szándék).\n")
    L.append(f"- medián: {statistics.median(ratio_vals):.2f} · 5. percentilis: {q[0]:.2f} · "
             f"95. percentilis: {q[-1]:.2f}")
    L.append("- legkisebb arányú beszédek (gyanú: elmaradt vágás):")
    for r in rr[:5]:
        L.append(f"  - `{r[1]}`: {r[2]} egység / {r[3]} mondat = {r[0]:.2f}")
    L.append("- legnagyobb arányú beszédek (gyanú: túlvágás):")
    for r in rr[-5:]:
        L.append(f"  - `{r[1]}`: {r[2]} egység / {r[3]} mondat = {r[0]:.2f}")
    L.append("\n## Példák\n")
    L.append("Szétvágott mondatvégek:")
    L += [f"- {x}" for x in split_examples[:5]]
    L.append("\nKözbeszólás kiemelése (eredeti → tiszta | közbeszólás):")
    L += [f"- „{a}” → „{b}” | „{c}”" for a, b, c in interj_examples]
    OUT_REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")

    print("\n".join(L))


if __name__ == "__main__":
    main()
