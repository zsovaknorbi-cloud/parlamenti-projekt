"""
Aranystandard v2 — új, vak kézi kódolási minta (24 kvázi mondat).

Rétegzett véletlen minta: 3 műfaj × 2 szerep (kezdeményező / válaszoló), rétegenként 4 mondat.
Fix seed, így a minta újra előállítható. Kizárja a korábban már kiválasztott mondatokat.
Gépi címkét NEM tesz a táblába (vak kódolás).

Futtatás a repó gyökeréből:
  python gold_standard/sample_v2.py                               # v2 kör (seed 20261118)
  python gold_standard/sample_v2.py --tag v3 --seed 20261119      # v3: friss, végső ellenőrző kör
Kimenet:
  gold_standard/hand_coding_<tag>.xlsx       — a kitöltendő tábla
  gold_standard/sample_<tag>_manifest.csv    — a minta azonosítói és rétegei
Kizárja: a régi 30-as mintákat, minden más kör manifestjét, és a kódkönyvekben példaként idézett mondatokat.
"""
import argparse
import csv
import random
import re
import sqlite3
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

sys.stdout.reconfigure(encoding="utf-8")

_ap = argparse.ArgumentParser()
_ap.add_argument("--tag", default="v2")
_ap.add_argument("--seed", type=int, default=20261118)
_args = _ap.parse_args()
TAG = _args.tag

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "parlamenti_felszolalasok_2026_teljes.sqlite"
OUT_XLSX = ROOT / "gold_standard" / f"hand_coding_{TAG}.xlsx"
OUT_MANIFEST = ROOT / "gold_standard" / f"sample_{TAG}_manifest.csv"
SEED = _args.seed
PER_STRATUM = 4

# Korábban már kiválasztott mondatok (ne ismétlődjenek): a régi minták + a többi kör manifestje
def _tag_of(p):
    return p.name[len("sample_"):-len("_manifest.csv")]


def _tag_key(t):
    return int(t[1:]) if t[1:].isdigit() else 0


# csak a KORÁBBI körök manifestjei, hogy egy régi kör újrafuttatása ugyanazt a mintát adja
PREVIOUS = [ROOT / "hand_coding_sablon.csv", ROOT / "gold_standard_30_sentences.csv"] + [
    p for p in sorted((ROOT / "gold_standard").glob("sample_*_manifest.csv"))
    if _tag_key(_tag_of(p)) < _tag_key(TAG)]
# A kódkönyvekben példaként idézett mondatok (a v2 kör óta kerültek be; a v2 húzását nem érintették)
CODEBOOKS = [ROOT / "codebooks" / "codebook_cap.md", ROOT / "codebooks" / "codebook_moral_emotions.md"]
EXAMPLE_ID = re.compile(r"`(2026-\d\d-\d\d_[A-Z]+_[^`]+_q\d+b?)`")

ROLE = {
    "napirend előtti felszólalás": "kezdeményező",
    "interpelláció - kérdés": "kezdeményező",
    "azonnali kérdés - kérdés": "kezdeményező",
    "interpelláció - képviselői viszonválasz": "kezdeményező",
    "azonnali kérdés - képviselői viszonválasz": "kezdeményező",
    "napirend előttihez hozzászólás": "válaszoló",
    "interpelláció - miniszteri válasz": "válaszoló",
    "azonnali kérdés - miniszteri válasz": "válaszoló",
    "azonnali kérdés - miniszteri viszonválasz": "válaszoló",
}
PROCEDURAL = ("tisztelt elnök", "köszönöm a szót", "köszönöm szépen", "parancsoljon", "elnök úr", "elnök asszony")
# Zárójel nélkül bent maradt közbeszólások / elnöki jelzések
STAGE = ("közbeszólás", "lejárt az idő", "taps", "derültség", "moraj", "csenget")

CAP_MAJOR = [
    (1, "Makrogazdaság"), (2, "Polgári jogok és szabadságok"), (3, "Egészségügy"),
    (4, "Mezőgazdaság és élelmiszerbiztonság"), (5, "Munkaügy és foglalkoztatás"), (6, "Oktatás"),
    (7, "Környezetvédelem"), (8, "Energiaügy"), (9, "Bevándorlás és menekültügy"),
    (10, "Közlekedés és infrastruktúra"), (12, "Rendvédelem, igazságszolgáltatás és büntetőjog"),
    (13, "Szociális ellátás és gyermekvédelem"), (14, "Lakáspolitika és településügy"),
    (15, "Belső kereskedelem, fogyasztóvédelem és katasztrófaelhárítás"), (16, "Honvédelem és katonai biztonság"),
    (17, "Technológia, telekommunikáció és informatika"), (18, "Külkereskedelem és vámok"),
    (19, "Nemzetközi kapcsolatok, külügy és EU"), (20, "Kormányzati működés, alkotmányosság és korrupció"),
    (21, "Közterületek, állami földek és vízügy"), (999, "Nincs szakpolitikai téma"),
]

RULES = [
    ("Egység", "Csak a mondatot kódold. Ha a mondatból nem derül ki a téma: 999 (akkor is, ha a beszéd másról szól)."),
    ("CAP szint", "Főtéma: egy szám a fenti listából (1–21, a 11 nincs; vagy 999)."),
    ("20 vs. 999", "20 csak akkor, ha a mondat a kormányzás működéséről szól (kinevezés, korrupció, alkotmány, "
                   "kampányfinanszírozás, közigazgatás). Pártcsatározás konkrét ügy nélkül: 999."),
    ("Több téma", "A cselekvés tárgya dönt: a kórházak költségvetése → 3, nem 1."),
    ("Érzelem küszöb", "Csak kifejezett érzelem kap kódot. Kétség esetén 11."),
    ("Formulák", "„Köszönöm a szót”, „Tisztelt Képviselő Úr!” → 11. Érdemi, megnevezett hála → 7."),
    ("Eredmények", "Puszta tényközlés („a családok megkapták a támogatást”) → 11. Büszkeség (8) csak kollektív "
                   "önértékelésnél, „mi megcsináltuk” jellegű győzelemnél."),
    ("Irónia, gúny", "A ténylegesen kifejezett érzelem: általában 5 (lekezelés) vagy 3 (felháborodás)."),
    ("Retorikai kérdés", "A mögötte álló érzelem: a „Hogy lehet, hogy…?!” számonkérés → 3."),
    ("Idézet", "A beszélő saját érzelme számít, nem az idézetté."),
    ("3 vs. 5", "3: igazságtalanság, normaszegés, felelősségre vonás. 5: a másik személy lekezelése "
                "(gyáva, nevetséges, méltatlan)."),
    ("v2.1: parlament", "A parlament és a jogalkotás működése (alaptörvény, ügyrend, bizottság) → 20; "
                        "általános politikai vád, vállalások teljesítése → 999."),
    ("v2.1: gazdaság", "Költségvetési hiány → 1; kamatstop → 15; fogyasztóvédelem → 15; "
                       "nemzetpolitika: a tárgy dönt (kettős állampolgárság → 2, diákprogram → 6)."),
    ("v2.1: érzelmek", "Elhivatottságnak tulajdonított siker, nemzeti összetartozás → 8; a kár felelősének "
                       "megnevezése, követelés, felkiáltásos szlogen → 3; nyomatékosító szó önmagában → 11; "
                       "kifejezett pozitív értékelés → 7; bocsánatkérés → 6."),
    ("Bővebben", "codebooks/codebook_cap.md („Kódolási szabályok (v2)”, E rész) és "
                 "codebooks/codebook_moral_emotions.md (4. fejezet, 14–18. pont)."),
]

EMOTIONS = [
    (3, "Düh és morális felháborodás"),
    (4, "Félelem és vészhelyzet"),
    (5, "Undor és megvetés"),
    (6, "Szomorúság és részvét"),
    (7, "Öröm és remény"),
    (8, "Büszkeség és nemzeti helytállás"),
    (11, "Semleges"),
]


def previous_ids():
    ids = set()
    for p in PREVIOUS:
        if p.exists():
            with open(p, encoding="utf-8-sig") as f:
                ids |= {r["file"] for r in csv.DictReader(f)}
    if TAG != "v2":  # a v2 húzásakor a kódkönyvekben még nem voltak példamondatok
        for p in CODEBOOKS:
            ids |= set(EXAMPLE_ID.findall(p.read_text(encoding="utf-8")))
    return ids


def eligible(row):
    text = row["mondat_szoveg"].strip()
    low = text.lower()
    return (
        8 <= row["mondat_szoszam"] <= 30
        and "(" not in text and ")" not in text
        and not low.startswith(PROCEDURAL)
        and not any(s in low for s in STAGE)
        and row["felszolalas_tipusa"] in ROLE
    )


def already_filled():
    """True, ha a kimeneti Excelben már van beírt kód — ezt soha nem írjuk felül."""
    if not OUT_XLSX.exists():
        return False
    from openpyxl import load_workbook
    ws = load_workbook(OUT_XLSX, read_only=True)["Kódolás"]
    return any(r[6] not in (None, "") or r[7] not in (None, "") for r in ws.iter_rows(min_row=2, values_only=True))


def main():
    if already_filled():
        sys.exit(f"{OUT_XLSX.name} már ki van töltve — nem írom felül. Új körhöz adj meg új --tag-et.")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT kvazi_mondat_id, speaker, party, napirendi_mufaj, felszolalas_tipusa, "
        "mondat_szoveg, mondat_szoszam FROM kvazi_mondatok ORDER BY kvazi_mondat_id"
    ).fetchall()
    con.close()

    skip = previous_ids()
    strata = {}
    for r in rows:
        if r["kvazi_mondat_id"] in skip or not eligible(r):
            continue
        key = (r["napirendi_mufaj"], ROLE[r["felszolalas_tipusa"]])
        strata.setdefault(key, []).append(r)

    rng = random.Random(SEED)
    sample = []
    for key in sorted(strata):
        pool = strata[key]
        picked = rng.sample(pool, PER_STRATUM)
        print(f"{key[0]:16} | {key[1]:12} | keret: {len(pool):5} | kiválasztva: {len(picked)}")
        sample += [(key, r) for r in picked]
    rng.shuffle(sample)  # a sorrend ne árulja el a réteget

    # Manifest (rétegekkel, a kódoló táblában ez nem szerepel)
    with open(OUT_MANIFEST, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sorszam", "file", "mufaj", "szerep", "felszolalas_tipusa", "seed"])
        for i, (key, r) in enumerate(sample, 1):
            w.writerow([i, r["kvazi_mondat_id"], key[0], key[1], r["felszolalas_tipusa"], SEED])

    # Kitöltendő Excel — ugyanaz a szerkezet, mint a hand_coding_sablon.csv
    wb = Workbook()
    ws = wb.active
    ws.title = "Kódolás"
    header = ["sorszam", "file", "speaker", "party", "mufaj", "szoveg", "cap_fotema", "moral_emotion_kod"]
    ws.append(header)
    for i, (key, r) in enumerate(sample, 1):
        ws.append([i, r["kvazi_mondat_id"], r["speaker"], r["party"], r["napirendi_mufaj"],
                   r["mondat_szoveg"].strip(), None, None])

    bold = Font(bold=True)
    fill = PatternFill("solid", fgColor="FFF2CC")
    for c in ws[1]:
        c.font = bold
    for col, width in zip("ABCDEFGH", (8, 34, 20, 12, 16, 80, 12, 18)):
        ws.column_dimensions[col].width = width
    last = len(sample) + 1
    for row in ws.iter_rows(min_row=2, max_row=last):
        row[5].alignment = Alignment(wrap_text=True, vertical="top")
        for c in row[:5]:
            c.alignment = Alignment(vertical="top")
        row[6].fill = fill
        row[7].fill = fill
    ws.freeze_panes = "A2"

    dv_em = DataValidation(type="list", formula1='"3,4,5,6,7,8,11"', allow_blank=True,
                           error="Érzelemkód: 3, 4, 5, 6, 7, 8 vagy 11", showErrorMessage=True)
    cap_list = ",".join(str(c) for c, _ in CAP_MAJOR)
    dv_cap = DataValidation(type="list", formula1=f'"{cap_list}"', allow_blank=True,
                            error="CAP főtéma: 1–21 (a 11 nincs) vagy 999 (nincs szakpolitikai téma)",
                            showErrorMessage=True)
    ws.add_data_validation(dv_em)
    ws.add_data_validation(dv_cap)
    dv_em.add(f"H2:H{last}")
    dv_cap.add(f"G2:G{last}")

    help_ws = wb.create_sheet("Kódok")
    help_ws.append(["CAP főtéma", "Megnevezés"])
    head_rows = [1]
    for code, label in CAP_MAJOR:
        help_ws.append([code, label])
    help_ws.append([])
    help_ws.append(["Érzelemkód", "Jelentés"])
    head_rows.append(help_ws.max_row)
    for code, label in EMOTIONS:
        help_ws.append([code, label])
    help_ws.append([])
    help_ws.append(["Szabály", "Röviden (kódkönyv v2, 2026-11-18)"])
    head_rows.append(help_ws.max_row)
    for k, v in RULES:
        help_ws.append([k, v])
    for r in head_rows:
        for c in help_ws[r]:
            c.font = bold
    for row in help_ws.iter_rows():
        row[1].alignment = Alignment(wrap_text=True, vertical="top")
    help_ws.column_dimensions["A"].width = 18
    help_ws.column_dimensions["B"].width = 100

    wb.save(OUT_XLSX)
    print(f"\n{len(sample)} mondat -> {OUT_XLSX.relative_to(ROOT)}")
    print(f"manifest -> {OUT_MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
