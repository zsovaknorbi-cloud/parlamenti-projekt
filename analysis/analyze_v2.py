"""
Elemzés v2 — a gépi kódolás (coding/labels_full.csv) és a kvázi mondat metaadatok alapján.

Fő minta: a KEZDEMÉNYEZŐ szerepű tartalmi mondatok (napirend előtti felszólaló, interpelláló, kérdező;
viszonválasszal). Kiegészítő minta: a batch_001–005 véletlen adagjai (a korpusz 14%-a), minden szereppel.
Fő érzelmi mérőszám: érzelmes (3–8) vs. semleges (11). CAP: főtéma, a 999 (nincs szakpolitikai téma) nélkül.

Kimenet: output_v2/ (ábrák PNG, táblák CSV és MD, results.json)
Futtatás a repó gyökeréből:  python analysis/analyze_v2.py
Csak standard könyvtár + numpy, pandas, matplotlib.
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output_v2"
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(20261118)
N_BOOT = 2000

GENRES = ["napirend előtt", "interpelláció", "azonnali kérdés"]
GENRE_LABEL = {"napirend előtt": "Napirend előtti", "interpelláció": "Interpelláció", "azonnali kérdés": "Azonnali kérdés"}
SIDE_LABEL = {"kormany": "Kormányoldal", "ellenzek": "Ellenzék"}
ROLE_LABEL = {"kezdemenyezo": "Kezdeményező", "kormanyzati_valaszado": "Kormányzati válaszadó",
              "frakcio_hozzaszolo": "Frakció-hozzászóló"}
CAP_HU = {1: "Makrogazdaság", 2: "Polgári jogok", 3: "Egészségügy", 4: "Mezőgazdaság", 5: "Munkaügy",
          6: "Oktatás", 7: "Környezetvédelem", 8: "Energia", 9: "Bevándorlás", 10: "Közlekedés",
          12: "Rendvédelem, igazságügy", 13: "Szociális ellátás", 14: "Lakhatás", 15: "Kereskedelem, fogyasztóvéd.",
          16: "Honvédelem", 17: "Technológia, média", 18: "Külkereskedelem", 19: "Külügy, EU",
          20: "Kormányzati működés", 21: "Közterületek, vízügy"}
# Kategorikus színek a dataviz skill validált alappalettájából, rögzített sorrendben (1: kék, 2: narancs, 3: aqua)
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e3e2de"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 200})


def load():
    lab = pd.read_csv(ROOT / "coding" / "labels_full.csv", encoding="utf-8")
    meta = pd.read_csv(ROOT / "parlamenti_kvazi_mondatok_2026_v2.csv", encoding="utf-8",
                       usecols=["kvazi_mondat_id", "beszed_id", "speaker", "party_v2", "oldal", "date",
                                "napirendi_mufaj", "felszolalas_tipusa", "szerep", "fordulo", "egyseg_tipus",
                                "tiszta_szoszam"])
    df = lab.merge(meta, on="kvazi_mondat_id", how="left", validate="one_to_one")
    assert df["beszed_id"].notna().all(), "címke metaadat nélkül"
    return df, meta


def boot_share(d, col, cluster="beszed_id"):
    """Arány és 95%-os klaszter-bootstrap CI (beszédek újramintavételezése)."""
    g = d.groupby(cluster)[col].agg(["sum", "count"]).to_numpy()
    est = g[:, 0].sum() / g[:, 1].sum()
    idx = RNG.integers(0, len(g), size=(N_BOOT, len(g)))
    s = g[idx]
    boots = s[..., 0].sum(1) / s[..., 1].sum(1)
    return est, np.percentile(boots, 2.5), np.percentile(boots, 97.5), len(d), len(g)


def ols_cluster(y, X, groups):
    """OLS (lineáris valószínűségi modell) klaszter-robusztus (CR1) standard hibával."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    meat = np.zeros((X.shape[1], X.shape[1]))
    codes, uniq = pd.factorize(pd.Series(groups))
    for g in range(len(uniq)):
        m = codes == g
        sg = X[m].T @ u[m]
        meat += np.outer(sg, sg)
    n, k, G = X.shape[0], X.shape[1], len(uniq)
    V = XtX_inv @ meat @ XtX_inv * (G / (G - 1)) * ((n - 1) / (n - k))
    return beta, np.sqrt(np.diag(V)), G


def main():
    df, meta = load()
    res = {"n_kodolt": int(len(df))}
    ini = df[df["szerep"] == "kezdemenyezo"].copy()
    n_ini_total = int(((meta["szerep"] == "kezdemenyezo") & (meta["egyseg_tipus"] == "tartalmi")).sum())
    res["kezdemenyezo_kodolt"] = int(len(ini))
    res["kezdemenyezo_osszes"] = n_ini_total
    print(f"kódolt: {len(df)} | kezdeményező: {len(ini)} / {n_ini_total}")

    # --- 1. Érzelmes arány műfaj × oldal (kezdeményezők) ---------------------------------------
    rows = []
    for g in GENRES:
        for side in ["kormany", "ellenzek", None]:
            d = ini[(ini["napirendi_mufaj"] == g) & ((ini["oldal"] == side) if side else True)]
            if len(d) == 0:
                continue
            est, lo, hi, n, nb = boot_share(d, "erzelmes")
            rows.append({"mufaj": g, "oldal": side or "mind", "erzelmes_arany": est, "ci_also": lo, "ci_felso": hi,
                         "mondat": n, "beszed": nb})
    t1 = pd.DataFrame(rows)
    t1.to_csv(OUT / "tabla_erzelmes_mufaj_oldal.csv", index=False, encoding="utf-8")
    res["erzelmes_mufaj_oldal"] = t1.to_dict("records")

    # --- 2. Lineáris valószínűségi modell: érzelmes ~ műfaj + oldal + viszonválasz + adag-FE --------
    X = pd.DataFrame({"const": 1.0,
                      "napirend_elott": (ini["napirendi_mufaj"] == "napirend előtt").astype(float),
                      "azonnali_kerdes": (ini["napirendi_mufaj"] == "azonnali kérdés").astype(float),
                      "ellenzek": (ini["oldal"] == "ellenzek").astype(float),
                      "viszonvalasz": (ini["fordulo"] == "viszonvalasz").astype(float)})
    for b in sorted(ini["batch"].unique())[1:]:
        X[f"adag_{b}"] = (ini["batch"] == b).astype(float)
    beta, se, G = ols_cluster(ini["erzelmes"], X, ini["beszed_id"])
    keep = ["const", "napirend_elott", "azonnali_kerdes", "ellenzek", "viszonvalasz"]
    reg = pd.DataFrame({"valtozo": X.columns, "b": beta, "se": se})
    reg = reg[reg["valtozo"].isin(keep)].assign(ci_also=lambda r: r.b - 1.96 * r.se, ci_felso=lambda r: r.b + 1.96 * r.se)
    reg.to_csv(OUT / "tabla_regresszio_erzelmes.csv", index=False, encoding="utf-8")
    res["regresszio"] = {"n": int(len(ini)), "klaszter_beszed": int(G), "egyutthatok": reg.to_dict("records"),
                         "referencia": "interpelláció, kormányoldal, első kör; adag-fix hatással"}

    # --- 3. Beszédhossz műfajonként (kezdeményező beszédek, tartalmi szavak) ------------------------
    sp = meta[(meta["szerep"] == "kezdemenyezo") & (meta["egyseg_tipus"] == "tartalmi") & (meta["fordulo"] == "elso")]
    words = sp.groupby(["beszed_id", "napirendi_mufaj"])["tiszta_szoszam"].sum().reset_index()
    t3 = words.groupby("napirendi_mufaj")["tiszta_szoszam"].agg(["count", "median", "mean"]).reindex(GENRES)
    t3.to_csv(OUT / "tabla_beszedhossz.csv", encoding="utf-8")
    res["beszedhossz"] = t3.reset_index().to_dict("records")

    # --- 4. CAP főtémák műfajonként (kezdeményezők, 999 nélkül) ------------------------------------
    cap = ini[ini["cap"] != 999]
    share999 = ini.groupby("napirendi_mufaj")["cap"].apply(lambda s: (s == 999).mean()).reindex(GENRES)
    ct = pd.crosstab(cap["cap"], cap["napirendi_mufaj"], normalize="columns").reindex(columns=GENRES).fillna(0)
    top = ct.mean(axis=1).sort_values(ascending=False).head(8).index
    ct.to_csv(OUT / "tabla_cap_mufaj.csv", encoding="utf-8")
    res["cap_999_arany"] = share999.to_dict()
    res["cap_top"] = {CAP_HU[int(c)]: ct.loc[c].round(3).to_dict() for c in top}

    # --- 5. Kiegészítő: szerepek összevetése a véletlen mintán (batch_001–005) ----------------------
    rnd = df[df["batch"].isin([f"batch_00{i}" for i in range(1, 6)])]
    rows = []
    for r in ROLE_LABEL:
        d = rnd[rnd["szerep"] == r]
        if len(d):
            est, lo, hi, n, nb = boot_share(d, "erzelmes")
            rows.append({"szerep": r, "erzelmes_arany": est, "ci_also": lo, "ci_felso": hi, "mondat": n, "beszed": nb})
    t5 = pd.DataFrame(rows)
    t5.to_csv(OUT / "tabla_erzelmes_szerep_veletlen.csv", index=False, encoding="utf-8")
    res["erzelmes_szerep_veletlen"] = t5.to_dict("records")

    # --- 6. Szakpolitika × érzelem (kezdeményezők, 999 nélkül) ------------------------------------
    # Fő mérőszám: az érzelmes mondatok aránya témánként (κ 0,67). Az érzelemtípusok megoszlása az érzelmes
    # mondatokon belül csak leíró (a 7 kategória egyezése gyengébb: Haiku κ 0,57).
    EMO = {3: "düh", 4: "félelem", 5: "megvetés", 6: "szomorúság", 7: "öröm", 8: "büszkeség"}
    rows = []
    for c, d in cap.groupby("cap"):
        if len(d) < 100:
            continue
        est, lo, hi, n, nb = boot_share(d, "erzelmes")
        emo = d[d["erzelmes"] == 1]["emotion"].value_counts(normalize=True)
        row = {"cap": int(c), "tema": CAP_HU[int(c)], "mondat": n, "erzelmes_arany": est, "ci_also": lo,
               "ci_felso": hi, "negativ_az_erzelmesbol": float(emo.reindex([3, 4, 5, 6]).fillna(0).sum())}
        row.update({f"{EMO[k]}": float(emo.get(k, 0.0)) for k in EMO})
        rows.append(row)
    t6 = pd.DataFrame(rows).sort_values("erzelmes_arany", ascending=False)
    t6.to_csv(OUT / "tabla_cap_erzelem.csv", index=False, encoding="utf-8")
    res["cap_erzelem"] = t6.to_dict("records")

    # --- 7. Szereplők: frakciók (Magyar Péterrel és nélküle) és képviselők -----------------------
    MP = "Magyar Péter"
    rows = []
    for p, d in ini.groupby("party_v2"):
        est, lo, hi, n, nb = boot_share(d, "erzelmes")
        rows.append({"frakcio": p, "erzelmes_arany": est, "ci_also": lo, "ci_felso": hi, "mondat": n, "beszed": nb})
    d = ini[(ini["party_v2"] == "TISZA") & (ini["speaker"] != MP)]
    est, lo, hi, n, nb = boot_share(d, "erzelmes")
    rows.append({"frakcio": "TISZA Magyar Péter nélkül", "erzelmes_arany": est, "ci_also": lo, "ci_felso": hi,
                 "mondat": n, "beszed": nb})
    t7 = pd.DataFrame(rows)
    t7.to_csv(OUT / "tabla_erzelmes_frakcio.csv", index=False, encoding="utf-8")
    res["erzelmes_frakcio"] = t7.to_dict("records")
    res["magyar_peter_arany_tisza"] = float((ini[ini["party_v2"] == "TISZA"]["speaker"] == MP).mean())

    # Robusztusság: a műfaji hatás frakció-fix hatással és Magyar Péter-dummyval is
    X2 = X.copy()
    for p in ["Fidesz", "KDNP", "Mi Hazánk", "Kormány (nem képviselő)"]:
        X2[f"frakcio_{p}"] = (ini["party_v2"] == p).astype(float)
    X2 = X2.drop(columns=["ellenzek"])
    X2["magyar_peter"] = (ini["speaker"] == MP).astype(float)
    b2, se2, _ = ols_cluster(ini["erzelmes"], X2, ini["beszed_id"])
    reg2 = pd.DataFrame({"valtozo": X2.columns, "b": b2, "se": se2})
    reg2 = reg2[~reg2["valtozo"].str.startswith("adag_")].assign(ci_also=lambda r: r.b - 1.96 * r.se,
                                                                 ci_felso=lambda r: r.b + 1.96 * r.se)
    reg2.to_csv(OUT / "tabla_regresszio_robusztus.csv", index=False, encoding="utf-8")
    res["regresszio_robusztus"] = reg2.to_dict("records")

    rows = []
    for (s, p), d in ini.groupby(["speaker", "party_v2"]):
        if len(d) < 100:
            continue
        est, lo, hi, n, nb = boot_share(d, "erzelmes")
        topc = d.loc[d["cap"] != 999, "cap"]
        rows.append({"kepviselo": s, "frakcio": p, "mondat": n, "beszed": nb, "erzelmes_arany": est, "ci_also": lo,
                     "ci_felso": hi, "fotema": CAP_HU[int(topc.mode().iloc[0])] if len(topc) else "-"})
    t8 = pd.DataFrame(rows).sort_values("erzelmes_arany", ascending=False)
    t8.to_csv(OUT / "tabla_erzelmes_kepviselo.csv", index=False, encoding="utf-8")
    res["erzelmes_kepviselo"] = t8.to_dict("records")

    # --- 8. Idővonal: a mezőgazdaság + vízügy + környezetvédelem figyelme ülésnaponként ------------
    DROUGHT_TOPICS = [4, 7, 21]
    kw = r"aszál|vízhiány|csapadékhiány|vízszint|öntöz|szárazság"
    txt = pd.read_csv(ROOT / "parlamenti_kvazi_mondatok_2026_v2.csv", encoding="utf-8",
                      usecols=["kvazi_mondat_id", "mondat_szoveg_tiszta"])
    tl = ini.merge(txt, on="kvazi_mondat_id")
    tl["aszaly_szo"] = tl["mondat_szoveg_tiszta"].str.contains(kw, case=False, regex=True)
    t9 = tl.groupby("date").agg(mondat=("cap", "size"),
                                figyelem=("cap", lambda s: s.isin(DROUGHT_TOPICS).mean()),
                                aszaly_mondat=("aszaly_szo", "sum")).reset_index()
    t9["fo_tema_aznap"] = [
        CAP_HU.get(int(tl[(tl["date"] == dt) & tl["cap"].isin(DROUGHT_TOPICS)]["cap"].mode().iloc[0]), "-")
        if (tl[(tl["date"] == dt) & tl["cap"].isin(DROUGHT_TOPICS)].shape[0]) else "-" for dt in t9["date"]]
    t9.to_csv(OUT / "tabla_idovonal_aszaly.csv", index=False, encoding="utf-8")
    res["idovonal"] = t9.to_dict("records")
    res["idovonal_median"] = float(t9["figyelem"].median())

    # --- 9. Szakpolitikai témák figyelme hetente, összesen és műfajonként ------------------------------
    # Hét = az ülésnapok hete (hétfő–kedd párok); arány a szakpolitikai tartalmú (999 nélküli) kvázi mondatokon belül.
    wk = cap.copy()
    wk["het"] = pd.to_datetime(wk["date"]).dt.to_period("W-SUN").dt.start_time
    # a 8 leggyakoribb főtéma + a mezőgazdaság és a vízügy (az aszály-kérdés miatt), gyakoriság szerint
    top_topics = wk["cap"].value_counts().head(8).index.tolist()
    top_topics += [c for c in (4, 21) if c not in top_topics]
    def weekly(d):
        t = pd.crosstab(d["cap"], d["het"], normalize="columns").reindex(top_topics).fillna(0)
        return t
    W_all = weekly(wk)
    W_all.to_csv(OUT / "tabla_tema_het.csv", encoding="utf-8")
    W_g = {g: weekly(wk[wk["napirendi_mufaj"] == g]) for g in GENRES}
    pd.concat(W_g, names=["mufaj"]).to_csv(OUT / "tabla_tema_het_mufaj.csv", encoding="utf-8")
    n_week = wk.groupby("het").size()
    res["tema_het_n"] = {str(k.date()): int(v) for k, v in n_week.items()}

    def heat(ax, W, title, show_y=True):
        im = ax.imshow(W.to_numpy() * 100, aspect="auto", cmap="Blues", vmin=0, vmax=50)
        ax.set_yticks(range(len(W.index)), [CAP_HU[int(c)] for c in W.index] if show_y else [""] * len(W.index),
                      fontsize=7)
        ax.set_xticks(range(len(W.columns)), [f"{c:%m.%d}" for c in W.columns], fontsize=6, rotation=90)
        ax.set_title(title, fontsize=8, loc="left", color=INK)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        return im

    # Ábra 5: összesített hőtérkép (a PDF-be)
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    im = heat(ax, W_all, "")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.01)
    cb.set_label("%", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(OUT / "abra5_tema_het.png")
    plt.close(fig)

    # Ábra 6: műfajonkénti hőtérképek (repó, prezentáció)
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.2), sharey=True)
    for k, (g, ax) in enumerate(zip(GENRES, axes)):
        im = heat(ax, W_g[g], GENRE_LABEL[g], show_y=(k == 0))
    axes[0].set_yticks(range(len(top_topics)), [CAP_HU[int(c)] for c in top_topics], fontsize=7)
    axes[0].tick_params(labelleft=True)
    cb = fig.colorbar(im, ax=axes, fraction=0.02, pad=0.01)
    cb.set_label("% a szakpolitikai kvázi mondatokon belül", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    fig.savefig(OUT / "abra6_tema_het_mufaj.png", bbox_inches="tight")
    plt.close(fig)

    # --- 10. Leíró statisztika (vdescriptives) és asszociációs mérőszámok ----------------------------
    def cramers_v(a, b):
        ct = pd.crosstab(a, b).to_numpy().astype(float)
        n = ct.sum()
        exp = ct.sum(1, keepdims=True) @ ct.sum(0, keepdims=True) / n
        chi2 = ((ct - exp) ** 2 / exp).sum()
        k = min(ct.shape) - 1
        return float(np.sqrt(chi2 / (n * k))), float(chi2), int((ct.shape[0] - 1) * (ct.shape[1] - 1))

    desc = []
    for g in GENRES + ["összesen"]:
        d = ini if g == "összesen" else ini[ini["napirendi_mufaj"] == g]
        est, lo, hi, n, nb = boot_share(d, "erzelmes")
        emo = d[d["erzelmes"] == 1]["emotion"]
        sub = d[d["cap"] != 999]["cap"]
        w = words if g == "összesen" else words[words["napirendi_mufaj"] == g]
        desc.append({"mufaj": g, "beszed": nb, "kvazi_mondat": n,
                     "szo_median": float(w["tiszta_szoszam"].median()),
                     "erzelmes": est, "erzelmes_ci_also": lo, "erzelmes_ci_felso": hi,
                     "duh_megvetes_az_erzelmesbol": float(emo.isin([3, 5]).mean()),
                     "tema_nelkul": float((d["cap"] == 999).mean()),
                     "fotema": CAP_HU[int(sub.mode().iloc[0])], "fotema_arany": float((sub == sub.mode().iloc[0]).mean()),
                     "ellenzeki_arany": float((d["oldal"] == "ellenzek").mean())})
    t10 = pd.DataFrame(desc)
    t10.to_csv(OUT / "tabla_leiro_mufaj.csv", index=False, encoding="utf-8")
    res["leiro_mufaj"] = t10.to_dict("records")

    # A modellváltozók összefoglaló statisztikája (N, átlag, SD, min, max)
    summ = X[["napirend_elott", "azonnali_kerdes", "ellenzek", "viszonvalasz"]].assign(erzelmes=ini["erzelmes"].values)
    t11 = summ.agg(["count", "mean", "std", "min", "max"]).T
    t11.to_csv(OUT / "tabla_osszefoglalo_valtozok.csv", encoding="utf-8")
    res["osszefoglalo_valtozok"] = {k: {s: float(v) for s, v in r.items()} for k, r in t11.iterrows()}

    # Asszociációk: Cramér-féle V (kvázi mondat szint) és beszédszintű Spearman-korreláció
    assoc = {}
    assoc["mufaj_x_erzelmes"] = cramers_v(ini["napirendi_mufaj"], ini["erzelmes"])
    assoc["fotema_x_erzelmes"] = cramers_v(cap["cap"], cap["erzelmes"])
    assoc["mufaj_x_fotema"] = cramers_v(cap["napirendi_mufaj"], cap["cap"])
    sp = ini.groupby("beszed_id").agg(n=("erzelmes", "size"), erz=("erzelmes", "mean"),
                                      korm=("cap", lambda s: (s == 20).mean()),
                                      tema_nelkul=("cap", lambda s: (s == 999).mean()))
    sp = sp[sp["n"] >= 10]

    def spearman(a, b):
        return float(pd.Series(a).rank().corr(pd.Series(b).rank()))
    rho = spearman(sp["korm"].values, sp["erz"].values)
    boots = []
    for _ in range(N_BOOT):
        i = RNG.integers(0, len(sp), len(sp))
        boots.append(spearman(sp["korm"].values[i], sp["erz"].values[i]))
    assoc["beszed_kormanyzati_tema_x_erzelmes_spearman"] = (rho, float(np.percentile(boots, 2.5)),
                                                           float(np.percentile(boots, 97.5)), int(len(sp)))
    res["asszociaciok"] = assoc

    # --- Ábra 3: témák érzelmi hőfoka -----------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    t6s = t6.sort_values("erzelmes_arany")
    y = np.arange(len(t6s))
    ax.barh(y, t6s["erzelmes_arany"] * 100, height=0.7, color=C1, zorder=2)
    ax.errorbar(t6s["erzelmes_arany"] * 100, y, xerr=[(t6s["erzelmes_arany"] - t6s["ci_also"]) * 100,
                                                      (t6s["ci_felso"] - t6s["erzelmes_arany"]) * 100],
                fmt="none", ecolor=INK2, elinewidth=0.8, capsize=2, zorder=3)
    ax.set_yticks(y, [f"{t} (n={n})" for t, n in zip(t6s["tema"], t6s["mondat"])], fontsize=7.5)
    ax.set_xlabel("Érzelmes kvázi mondatok aránya (%), kezdeményezők")
    ax.axvline(ini["erzelmes"].mean() * 100, color=INK2, linestyle="--", linewidth=0.8, zorder=1)
    ax.text(ini["erzelmes"].mean() * 100 + 0.5, len(t6s) - 0.6, "átlag", color=INK2, fontsize=7)
    ax.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)
    fig.tight_layout()
    fig.savefig(OUT / "abra3_tema_erzelem.png")
    plt.close(fig)

    # --- Ábra 4: idővonal -----------------------------------------------------------------------
    # felső panel: érzelmes arány ülésnaponként, műfajonként (csak a legalább 40 kvázi mondatos nap-műfaj párok)
    em_day = (ini.groupby(["date", "napirendi_mufaj"])["erzelmes"].agg(["mean", "size"]).reset_index())
    em_day = em_day[em_day["size"] >= 40]
    em_day.to_csv(OUT / "tabla_idovonal_erzelmes.csv", index=False, encoding="utf-8")
    fig, (ax0, ax) = plt.subplots(2, 1, figsize=(6.2, 3.9), sharex=True, gridspec_kw={"height_ratios": [1.15, 1]})
    for g, col in zip(GENRES, [C1, C2, C3]):
        s = em_day[em_day["napirendi_mufaj"] == g]
        ax0.plot(pd.to_datetime(s["date"]), s["mean"] * 100, color=col, linewidth=1.6, marker="o", markersize=3,
                 label=GENRE_LABEL[g], zorder=3)
    ax0.set_ylabel("Érzelmes (%)")
    ax0.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    ax0.legend(frameon=False, ncols=3, fontsize=7, loc="lower right", bbox_to_anchor=(1.0, 0.98),
               handlelength=1.4, columnspacing=1.0)
    ax0.set_title("a) Érzelmes arány", fontsize=8, loc="left", color=INK, pad=6)
    ax.set_title("b) Mezőgazdaság + vízügy + környezetvédelem figyelme", fontsize=8, loc="left", color=INK)
    x = pd.to_datetime(t9["date"])
    ax.plot(x, t9["figyelem"] * 100, color=C1, linewidth=2, marker="o", markersize=3.5, zorder=3)
    ax.axhline(res["idovonal_median"] * 100, color=INK2, linestyle="--", linewidth=0.8)
    peak = t9.loc[t9["aszaly_mondat"].idxmax()]
    ax.annotate(f"{pd.to_datetime(peak['date']):%m. %d.}: {int(peak['aszaly_mondat'])} aszály-említés",
                (pd.to_datetime(peak["date"]), peak["figyelem"] * 100), xytext=(10, 18), textcoords="offset points",
                fontsize=7.5, color=INK, arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.8})
    ax.set_ylabel("Figyelem (%)")
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m. %d."))
    fig.tight_layout()
    fig.savefig(OUT / "abra4_idovonal_aszaly.png")
    plt.close(fig)

    # Ábra 4a önállóan (a PDF-be): érzelmes arány ülésnaponként, műfajonként
    fig, ax0 = plt.subplots(figsize=(6.2, 2.0))
    for g, col in zip(GENRES, [C1, C2, C3]):
        s = em_day[em_day["napirendi_mufaj"] == g]
        ax0.plot(pd.to_datetime(s["date"]), s["mean"] * 100, color=col, linewidth=1.6, marker="o", markersize=3,
                 label=GENRE_LABEL[g], zorder=3)
    ax0.set_ylabel("Érzelmes (%)")
    ax0.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    ax0.legend(frameon=False, ncols=3, fontsize=7, loc="lower right", bbox_to_anchor=(1.0, 0.98),
               handlelength=1.4, columnspacing=1.0)
    ax0.xaxis.set_major_formatter(mdates.DateFormatter("%m. %d."))
    fig.tight_layout()
    fig.savefig(OUT / "abra4a_idovonal_erzelmes.png")
    plt.close(fig)

    # --- Ábra 1: érzelmes arány műfaj × oldal ---------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    x = np.arange(len(GENRES))
    w = 0.36
    for j, (side, col) in enumerate([("kormany", C1), ("ellenzek", C2)]):
        d = t1[t1["oldal"] == side].set_index("mufaj").reindex(GENRES)
        pos = x + (j - 0.5) * w
        ax.bar(pos, d["erzelmes_arany"] * 100, width=w - 0.03, color=col, label=SIDE_LABEL[side], zorder=2)
        ax.errorbar(pos, d["erzelmes_arany"] * 100,
                    yerr=[(d["erzelmes_arany"] - d["ci_also"]) * 100, (d["ci_felso"] - d["erzelmes_arany"]) * 100],
                    fmt="none", ecolor=INK2, elinewidth=1, capsize=3, zorder=3)
        for p, v in zip(pos, d["erzelmes_arany"]):
            ax.text(p, 1.5, f"{v * 100:.0f}%", ha="center", va="bottom", color="white", fontsize=8, zorder=4)
    ax.set_xticks(x, [GENRE_LABEL[g] for g in GENRES])
    ax.set_ylabel("Érzelmes kvázi mondatok aránya (%)")
    ax.set_ylim(0, max(70, float(t1["ci_felso"].max() * 100) + 5))
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    ax.legend(frameon=False, loc="upper right", ncols=2)
    fig.tight_layout()
    fig.savefig(OUT / "abra1_erzelmes_mufaj_oldal.png")
    plt.close(fig)

    # --- Ábra 2: CAP főtémák műfajonként --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    labels = [CAP_HU[int(c)] for c in top][::-1]
    y = np.arange(len(top))
    h = 0.27
    for j, (g, col) in enumerate(zip(GENRES, [C1, C2, C3])):
        vals = ct.loc[top, g].to_numpy()[::-1] * 100
        ax.barh(y + (1 - j) * h, vals, height=h - 0.02, color=col, label=GENRE_LABEL[g], zorder=2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("A szakpolitikai tartalmú kvázi mondatok aránya (%), műfajonként")
    ax.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "abra2_cap_mufaj.png")
    plt.close(fig)

    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print(t1.round(3).to_string(index=False))
    print(reg.round(3).to_string(index=False))
    print(t3.round(1).to_string())
    print("999 arány:", share999.round(3).to_dict())
    print(t5.round(3).to_string(index=False))
    print(t6.drop(columns=["cap"]).round(2).to_string(index=False))
    print("-> output_v2/")


if __name__ == "__main__":
    main()
