"""Symmetrie im Baum - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 13 (gelb) der Reihe „Anordnen: relaxieren und runden“: wie viele Anordnungen sind gleich, und was spart das im Baum? Die Plätze des Rasters haben Symmetrien (Spiegelungen, Drehungen), die Flüsse manchmal auch (gleiche Bauteile).
Eigene Fassung: Gruppen, Zählung bis auf Symmetrie (Burnside) und der Baum aus Stück 8 mit Orbit-Beschneiden und Zwillingsordnung. Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import syb_constants as C
from syb_evaluation import (
    Settings,
    aut_trivial,
    combo_probe,
    count,
    de,
    fam,
    hand_data,
    instance_data,
    node_ratios,
    optimal_orbit_stats,
    plural,
    pooled,
    ratio,
    ratio_stats,
    secs,
    series_sweep,
    struct_row,
    verdict_core,
    verdict_count,
    verdict_group,
    verdict_hand,
    verdict_optimal,
    verdict_probe,
    verdict_series,
    verdict_struct,
)
from syb_layout import dunkles_design, kopf_css
from syb_pdf_export import build_pdf
from syb_presets import bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, sidebar_presets, sync_query_params
from syb_visualization import build_arrangement, build_counts, build_depth, build_images, build_node_bars, build_places, build_ratio_chart, build_struct_bars

st.set_page_config(page_title="Symmetrie im Baum – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Rechne den Baum …")
def _instance(settings: Settings):
    return instance_data(settings)


@st.cache_data(show_spinner=False)
def _hand():
    return hand_data()


@st.cache_data(show_spinner=False)
def _series(family, n):
    return series_sweep(family, n)


@st.cache_data(show_spinner=False)
def _struct(kind, n):
    return struct_row(kind, n)


@st.cache_data(show_spinner=False)
def _probe(per_size):
    return combo_probe(per_size)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


def run_knob(flag, label, info, todo, work):
    """Rechenknopf: `todo` ist eine Liste von Beschriftungen und Aufruf-Argumenten; nach dem Lauf steht `flag` im Session State."""
    if st.session_state.get(flag):
        return True
    st.info(info)
    if st.button(label, key=flag + "_button"):
        bar = st.progress(0.0, text="Rechne …")
        for i, (text, args) in enumerate(todo):
            work(*args)
            bar.progress((i + 1) / len(todo), text=f"{text} fertig")
        st.session_state[flag] = True
        st.rerun()
    return False


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in syb_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🪞 Symmetrie im Baum")
st.markdown(
    """
**Wie viele Anordnungen sind gleich, und was spart das im Baum?** Dieselbe Aufgabe wie in Stück 1 bis 8: `n` Bauteile auf `n` Plätze eines Rasters, Kosten gleich der Summe aus **Fluss mal Abstand**. Spiegelt man das Raster, bleiben alle Abstände gleich:
jede Anordnung hat dann **gleich teure Bilder**, und der Baum aus Stück 8 prüft sie alle. Hier werden die Symmetrien **gezählt** (bis auf Symmetrie bleiben `n!/|G|` Anordnungen) und im Baum **ausgenutzt**: von den freien Plätzen wird nur einer je Bahn versucht.
Gleiche Bauteile („Zwillinge“) lassen sich zusätzlich der Reihe nach setzen. Die Fassung ist **eigen** (die Literatur zur Symmetriebrechung ist nicht eingesehen); die sechs Familien der Flussmatrix und die vier symmetrischen sind **eigene Erfindungen**.
Stück 13 der Reihe „Anordnen: relaxieren und runden“ (gelb, optional).

Weiter unten: **fünf Experimente** (**🔬**), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert es", expanded=True):
    st.markdown(
        """
1. **Platzsymmetrien:** eine Permutation `g` der Plätze mit `D[g a, g b] = D[a, b]`. Beim Raster mit Manhattan-Abstand sind das die Symmetrien des Rechtecks: **4** (zwei Spiegelungen, Drehung um 180°), beim Quadrat **8**. Eine Anordnung `p` und ihr Bild `g∘p` kosten dasselbe; die Gruppe wirkt **frei** (`g∘p = p` nur für `g = id`), also gibt es genau `n!/|G|` Bahnen.
2. **Bauteilsymmetrien:** ein Automorphismus `h` der Flüsse (`F[h a, h b] = F[a, b]`) macht aus `p` die Anordnung `p∘h`. Für den Baum zählen **Zwillinge**: Bauteile mit gleichen Flüssen zu allen anderen. Die Bahnen unter Plätzen und Bauteilen zählt **Burnside** (ganzzahlig, mit der Zykelstruktur der Gruppenelemente); die Aufzählung bis `n = 8` ist die Gegenprobe.
3. **Der Baum** (Stück 8, Gilmore–Lawler-Knotenschranken): **Orbit-Beschneiden** versucht von den freien Plätzen nur den kleinsten je Bahn der Symmetrien, die alle schon belegten Plätze festlassen; **Zwillingsordnung** setzt gleiche Bauteile auf aufsteigende Plätze.
4. **Das Maß:** **Knoten** (bewertete Kinder, ganzzahlig, auf jedem Rechner gleich) und das **Verhältnis** ohne gegen mit Symmetrie. Der **Anfangswert** ist die beste von 200 Abstiegen (Stück 3) oder keiner.
5. **Ohne Verlust?** Der beste Wert muss mit und ohne Symmetrie gleich sein; die App zeigt es für jeden Lauf und prüft die **Kombination** von Plätzen und Zwillingen an 300 Zufallsinstanzen (keine Beweisführung).
6. **Feste Instanzen:** Vergleiche laufen über feste Seeds ab 100000 (`n` = 6, 8, 9, 12 mit 30 / 30 / 18 / 18 Instanzen) und über vier symmetrische Familien, nie über einen einzelnen Lauf.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Die Instanz**")
    family = st.selectbox("Familie der Flussmatrix", C.ALL_FAMILIES, key="family_select", format_func=lambda f: C.ALL_FAMILY_NAMES[f], help="Die sechs Familien der Reihe (zufällig) und vier symmetrische (alle Flüsse gleich stark). Die Beschreibung steht unter dem Regler.")
    st.caption(C.ALL_FAMILY_HELP[family])
    n = st.select_slider("Bauteile n", options=C.SIZES, key="n_select", help=f"Raster von 2×2 bis 3×4. Bis n = 9 wird alles aufgezählt; n = {C.HEAVY_N} läuft nur auf Knopfdruck.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Nur für die sechs Familien der Reihe; die symmetrischen Familien sind deterministisch.")
    st.button("🎲 Neue Instanz", width="stretch", on_click=randomize_seed)
    st.markdown("**Der Baum**")
    place = st.toggle("Platzsymmetrie ausnutzen", key="place_toggle", help="Orbit-Beschneiden: von den freien Plätzen nur einer je Bahn der Stabilisatorgruppe.")
    twins = st.toggle("Zwillinge ordnen", key="twins_toggle", help="Gleiche Bauteile auf aufsteigende Plätze. Zusammen mit der Platzsymmetrie: gemessen gültig, nicht bewiesen.")
    start = st.toggle("Anfangswert", key="start_toggle", help="Die beste von 200 Abstiegen aus Zufallsstarts als Anfangswert des Baums; ohne ihn muss der Baum die erste Lösung selbst finden.")

sync_query_params({"family_select": family, "n_select": int(n), "seed_input": int(seed), "place_toggle": bool(place), "twins_toggle": bool(twins), "start_toggle": bool(start)})
settings = Settings(family, int(n), int(seed), bool(place), bool(twins), bool(start))

v = None
if settings.n < C.HEAVY_N or st.session_state.get("heavy_go") == settings:
    v = _instance(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
if v is None:
    st.info(f"Für n = {settings.n} hat der Baum tausende Knoten; ohne Symmetrie braucht die Rechnung bei manchen Instanzen bis etwa eine halbe Minute (bei symmetrischen Flüssen bis zur Obergrenze von {count(C.NODE_CAP)} Knoten, auf Streamlit Cloud länger). Mit dem Knopf starten:")
    if st.button("⏱️ Baum rechnen", key="heavy_button"):
        st.session_state["heavy_go"] = settings
        st.rerun()
else:
    runs = v["runs"]
    sel = runs[settings.variant]
    plain = runs["plain"]
    m1, m2, m3 = st.columns(3)
    m4, m5 = st.columns(2)
    m1.metric("Platzsymmetrien |G|", f"{len(v['G'])}", help="Symmetrien des Rasters (geprüft an den Abständen).")
    m2.metric("Anordnungen bis auf Plätze", count(v["orbits_G"]), delta=f"von {count(v['arrangements'])}", delta_color="off", help="n!/|G|: die Platzsymmetrie wirkt frei, jede Bahn hat |G| Anordnungen.")
    m3.metric("Knoten mit der gewählten Variante", count(sel["nodes"]) + ("+" if sel["capped"] else ""), delta=f"ohne Symmetrie {count(plain['nodes'])}" + ("+" if plain["capped"] else ""), delta_color="off", help="Bewertete Kinder des Baums; „+“: Obergrenze erreicht, nicht zu Ende gerechnet.")
    m4.metric("Verhältnis ohne gegen mit", de(ratio(plain["nodes"], sel["nodes"]), 2), help="Knoten ohne Symmetrie durch Knoten mit der gewählten Variante; bei der Platzsymmetrie allein höchstens |G|.")
    m5.metric("Bester Wert", f"{sel['best']:.0f}", delta="wie ohne Symmetrie" if sel["best"] == plain["best"] else "ANDERS als ohne Symmetrie", delta_color="off" if sel["best"] == plain["best"] else "inverse", help="Der beste Wert des Baums; mit Symmetrie muss er gleich sein.")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(build_node_bars(runs, settings.variant), width="stretch", key="node_bars")
    with c2:
        st.plotly_chart(build_depth(runs), width="stretch", key="depth_chart")
    if st.button("📄 PDF des aktuellen Ergebnisses erstellen", key="pdf_make"):
        st.session_state["pdf_made"] = (settings, build_pdf(settings, v))
    made = st.session_state.get("pdf_made")
    if made and made[0] == settings:
        st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="symmetrie-im-baum.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viele Anordnungen sind gleich, und was spart das?")
if v is not None:
    verdict(verdict_core(settings, v))

st.markdown("---")

# --- Experiment 1 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Die Gruppe")
st.caption("Das Raster der Plätze, je Bahn der Symmetriegruppe eine Farbe, und eine optimale Anordnung samt ihren gleich teuren Bildern (bis n = 9, wo das Optimum aufgezählt wird). Darunter das Handbeispiel.")
if v is not None:
    st.plotly_chart(build_places(v["inst"], v["G"], v["orbits_places"]), width="stretch", key="places")
    verdict(verdict_group(settings, v))
    if "opt_perm" in v:
        st.plotly_chart(build_images(v["inst"], v["opt_perm"], v["G"]), width="stretch", key="images")
else:
    st.caption("Die Instanz ist noch nicht gerechnet (Knopf oben).")
h = _hand()
verdict(verdict_hand(h))
with st.expander("Handbeispiel zum Nachrechnen"):
    st.markdown(
        f"**Vier Plätze auf einer Zeile** (Stück 3, 5, 8; Abstände 1 bis 3), Fluss A–C, A–D, B–C, B–D je 1. Die Platzgruppe ist `{{id, Spiegelung}}` (`|G| = 2`), es gibt `n! = 24` Anordnungen und `12` Bahnen. "
        f"Die Flüsse bilden einen Vierzyklus A–C–B–D: `|Aut(F)| = 8`, Zwillinge `{{A, B}}` und `{{C, D}}`. **{h['n_opt']} der 24 Anordnungen kosten 6** (das Optimum), die übrigen 8 kosten mehr. "
        f"Burnside: `(1/(2·8)) Σ_(g,h) #{{p : g∘p = p∘h}}` mit `#{{p : g∘p = p∘h}} = ∏ c! ℓ^c` für Paare gleicher Zykelstruktur, sonst 0: **{h['orbits_GA']} Bahnen** (die Aufzählung findet {h['orbits_brute']}), davon {h['n_opt_orbits_GA']} optimal. "
        f"Baum mit Anfangswert 6 (Gilmore–Lawler-Wurzel 5): vier Kinder der Wurzel (eines je Platz); mit Orbit-Beschneiden zwei, denn Platz 4 ist das Spiegelbild von Platz 1 und Platz 3 das von Platz 2."
    )

st.markdown("---")

# --- Experiment 2 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Wie viele Anordnungen sind gleich?")
st.caption("Anordnungen roh, bis auf die Platzsymmetrie (`n!/|G|`) und, wenn die Gruppe der Flüsse klein genug ist, bis auf Plätze und Bauteile (Burnside); bis n = 8 mit der Aufzählung als Gegenprobe. Dazu die optimalen Anordnungen und ihre Bahnen.")
if v is not None:
    st.plotly_chart(build_counts(v), width="stretch", key="counts")
    verdict(verdict_count(settings, v))
    tab = [{"Größe": "Platzsymmetrien |G|", "Wert": len(v["G"])}, {"Größe": "Bahnen der Plätze", "Wert": len(v["orbits_places"])}, {"Größe": "Automorphismen der Flüsse", "Wert": count(v["aut"]) + ("" if v["aut_full"] else " oder mehr")},
           {"Größe": "Zwillingsklassen (Größen)", "Wert": ", ".join(str(len(c)) for c in v["twins"]) or "keine"}, {"Größe": "Anordnungen bis auf Plätze", "Wert": count(v["orbits_G"])},
           {"Größe": "Anordnungen bis auf Plätze und Bauteile (Burnside)", "Wert": count(v["orbits_GA"]) if v["orbits_GA"] is not None else "nicht gerechnet (zu viele Automorphismen)"},
           {"Größe": "Aufzählung der Bahnen (Gegenprobe, n ≤ 8)", "Wert": count(v["orbits_brute"]) if v["orbits_brute"] is not None else "–"}]
    if "opt" in v:
        tab += [{"Größe": "optimale Anordnungen", "Wert": count(v["n_opt"])}, {"Größe": "ihre Bahnen unter den Plätzen", "Wert": count(v["n_opt_orbits_G"])}]
    st.dataframe(pd.DataFrame(tab).astype({"Wert": str}), hide_index=True, width="stretch")
else:
    st.caption("Die Instanz ist noch nicht gerechnet (Knopf oben).")

st.markdown("---")

# --- Experiment 3 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Der Baum")
st.caption("Knoten je Tiefe ohne Symmetrie und mit Orbit-Beschneiden: die Platzsymmetrie spart schon an der Wurzel (von den freien Plätzen bleibt einer je Bahn) und in der Tiefe, wo die Stabilisatorgruppe schrumpft.")
if v is not None:
    runs = v["runs"]
    tab = [{"Variante": C.VARIANT_NAMES[k], "Knoten": count(runs[k]["nodes"]) + ("+" if runs[k]["capped"] else ""), "Verhältnis": de(ratio(runs["plain"]["nodes"], runs[k]["nodes"]), 2), "übersprungene Kinder": count(runs[k]["skipped"]),
           "bester Wert": f"{runs[k]['best']:.0f}", "Zeit": secs(runs[k]["seconds"])} for k in C.VARIANTS]
    st.dataframe(pd.DataFrame(tab), hide_index=True, width="stretch")
    st.plotly_chart(build_depth(runs, "Knoten je Tiefe: ohne gegen Plätze"), width="stretch", key="depth_chart_3")
else:
    st.caption("Die Instanz ist noch nicht gerechnet (Knopf oben).")

st.markdown("---")

# --- Experiment 4 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Über feste Instanzen")
st.caption("Die sechs Familien der Reihe, `n` = 6, 8, 9, 12 (30 / 30 / 18 / 18 Instanzen): das Verhältnis der Knoten ohne gegen mit Orbit-Beschneiden und die Gruppengröße; der beste Wert muss in jeder Instanz gleich sein.")
series_ok = run_knob("series_ok", "⏱️ Feste Instanzen rechnen (n = 6, 8, 9, 12)", "Die Rechnung läuft über 96 Instanzen mit dem Baum ohne und mit Orbit-Beschneiden, mit und ohne Anfangswert, und dauert einige Minuten (bei n = 12 im Median etwa 1,4 s, im größten Fall etwa 45 s je Instanz; auf Streamlit Cloud länger). Mit dem Knopf starten:",
                     [(f"n = {m}, {C.ALL_FAMILY_NAMES[f]}", (f, m)) for m in C.ROW_SIZES for f in C.FAMILIES], lambda f, m: _series(f, m))
rows_by_n = {m: pooled({f: _series(f, m) for f in C.FAMILIES}) for m in C.ROW_SIZES} if series_ok else {}
if series_ok:
    st.plotly_chart(build_ratio_chart(rows_by_n, ratio_stats, node_ratios), width="stretch", key="ratio_chart")
    tab = []
    for m in C.ROW_SIZES:
        rs = rows_by_n[m]
        st_ = ratio_stats(rs)
        row = {"n": m, "Instanzen": len(rs), "|G|": rs[0]["G"], "Anordnungen bis auf Plätze": count(rs[0]["orbits_G"]), "Knoten ohne (Median)": count(st_["median_a"]), "Knoten mit (Median)": count(st_["median_b"]),
               "Verhältnis (Median)": de(st_["median"], 2), "kleinstes bis größtes": f"{de(st_['min'], 2)} bis {de(st_['max'], 2)}", "bester Wert gleich": f"{st_['same_best']} von {len(rs)}", "Flüsse ohne Symmetrie": f"{aut_trivial(rs)} von {len(rs)}"}
        if "plain0" in rs[0]:
            row["Verhältnis ohne Anfangswert (Median)"] = de(ratio_stats(rs, "plain0", "place0")["median"], 2)
        tab.append(row)
    st.dataframe(pd.DataFrame(tab), hide_index=True, width="stretch")
    verdict(verdict_series(rows_by_n))
    verdict(verdict_series({m: r for m, r in rows_by_n.items() if "plain0" in r[0]}, start=False))
    verdict(verdict_optimal(rows_by_n))

st.markdown("---")

# --- Experiment 5 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 5: Symmetrische Flüsse")
st.caption("Vier erfundene Familien mit gleich starken Flüssen (zwei Hälften, Ring, Nabe, Blöcke): Knoten in den vier Varianten, und die Zufallsprobe, ob die Kombination aus Platzsymmetrie und Zwillingen das Optimum behält.")
struct_ok = run_knob("struct_ok", "⏱️ Symmetrische Flüsse rechnen", f"Die Rechnung läuft über 16 Instanzen (vier Familien, n = 6, 8, 9, 12) in vier Varianten; „zwei Hälften“ bei n = 12 ohne Symmetrie erreicht die Obergrenze von {count(C.NODE_CAP)} Knoten (etwa eine bis zwei Minuten, auf Streamlit Cloud länger). Mit dem Knopf starten:",
                     [(f"{C.SYM_FAMILY_NAMES[k]}, n = {m}", (k, m)) for k in C.SYM_FAMILIES for m in C.STRUCT_SIZES], lambda k, m: _struct(k, m))
if struct_ok:
    srows = [_struct(k, m) for k in C.SYM_FAMILIES for m in C.STRUCT_SIZES]
    st.plotly_chart(build_struct_bars(srows), width="stretch", key="struct_bars")
    tab = [{"Familie": fam(r["kind"]), "n": r["n"], "|G|": r["G"], "Automorphismen": count(r["aut"]) + ("" if r["aut_full"] else " oder mehr"), "Zwillingsklassen": ", ".join(map(str, r["twin_classes"])) or "–",
            "Bahnen bis auf Plätze": count(r["orbits_G"]), "Bahnen bis auf Plätze und Bauteile": count(r["orbits_GA"]) if r["orbits_GA"] is not None else "–",
            **{C.VARIANT_SHORT[k]: count(r[k]["nodes"]) + ("+" if r[k]["capped"] else "") for k in C.VARIANTS}} for r in srows]
    st.dataframe(pd.DataFrame(tab), hide_index=True, width="stretch")
    verdict(verdict_struct(srows))
probe_ok = run_knob("probe_ok", "⏱️ Zufallsprobe rechnen (300 Instanzen)", "Die Zufallsprobe rechnet 300 zufällige Flussmatrizen mit erzwungenen Zwillingen (n = 6 und 8) in vier Varianten gegen die Aufzählung und dauert etwa eine halbe Minute (auf Streamlit Cloud länger). Mit dem Knopf starten:",
                    [("Zufallsprobe", (C.PROBE_COUNT,))], lambda c: _probe(c))
if probe_ok:
    verdict(verdict_probe(_probe(C.PROBE_COUNT)))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der Gewinn ist klein** | Die Platzsymmetrie spart höchstens den Faktor der Gruppengröße (4 oder 8); gegen eine schärfere Schranke (Stück 5, 7) ist das ein kleiner, fester Faktor. Der große Gewinn steht an erfundenen symmetrischen Flüssen (Zwillinge), nicht an der Platine. | Stück 5, 7 |
| **Eigene Fassung** | Orbit-Beschneiden mit der Stabilisatorkette und die Zwillingsordnung sind eigene Herleitungen; die Literatur zur Symmetriebrechung (Orbit-Fixierung, Lex-Leader, Margot) ist **nicht eingesehen**. | Abzählen-Linie (Burnside) |
| **Kombination nicht bewiesen** | Platzsymmetrie und Zwillingsordnung zusammen verloren in 300 Zufallsinstanzen und den strukturierten Familien nie das Optimum; ein Beweis ist das nicht (allgemein verlangt man eine lexikographische Bedingung für das Produkt der Gruppen). Ein Fehler wäre still. | – |
| **Nur Rechteck-Raster** | Die Gruppe der Plätze sind die Symmetrien des Rechtecks (geprüft an `D` gegen alle `n!` Permutationen bis `n = 9`); andere Anordnungen der Plätze (Ringe, Hallen) sind nicht gebaut. | Stück 1 |
| **Bauteilsymmetrie nur über Zwillinge** | Allgemeine Automorphismen der Flüsse werden gezählt (Burnside), im Baum aber nur als Zwillinge genutzt; bei mehr als 50 000 Automorphismen wird nicht gezählt. | – |
| **Nur Gilmore–Lawler im Baum** | Mit der linearen oder der SDP-Schranke am Knoten ist der Gewinn nicht gemessen. | Stück 7, 8 |
| **Ohne Anfangswert kleiner** | Der Baum muss zuerst eine Lösung finden; der Gewinn ist kleiner und streut (Median etwa 2,3 bis 6,5 gegen 4 bis 8, kleinstes etwa 1,2). | – |
| **Die Familien sind erfunden** | Echte Platinen haben andere Flüsse; die vier symmetrischen Familien sind eigens so gebaut, dass Zwillinge entstehen. | Stück 2 |
| **Wenige Instanzen und kleine Größen** | n = 6, 8: 30 Instanzen, n = 9, 12: 18; keine QAPLIB, keine Raster über 3×4 im Baum. | – |
| **Zeit ist implementierungsabhängig** | Python-Fassung; Zeiten schwanken um das Doppelte, in Tests stehen nie Zeiten. Die Knotenzahlen sind ganzzahlig und rechnerunabhängig. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Die Aufgabe.** Flüsse $F$, Abstände $D$ (Manhattan auf dem Raster), Anordnung $p$ (Platz $p_i$ des Bauteils $i$): $\mathrm{cost}(p) = \sum_{i<k} F_{ik} D_{p_i p_k}$.

**Platzsymmetrie.** $G = \{g \in S_n : D_{g(a) g(b)} = D_{ab}\ \forall a, b\}$. Dann $\mathrm{cost}(g \circ p) = \mathrm{cost}(p)$. $G$ wirkt **frei** auf die Anordnungen: $g \circ p = p$ heißt $g(p_i) = p_i$ für alle $i$, also $g = \mathrm{id}$, weil $p$ bijektiv ist. Jede Bahn hat $|G|$ Elemente, es gibt $n!/|G|$ Bahnen.

**Bauteilsymmetrie.** $A = \{h \in S_n : F_{h(a) h(b)} = F_{ab}\}$, $\mathrm{cost}(p \circ h) = \mathrm{cost}(p)$. **Zwillinge:** $F_{ik} = F_{jk}$ für alle $k \ne i, j$; dann ist die Vertauschung von $i$ und $j$ in $A$.

**Burnside.** Die Gruppe $G \times A$ wirkt durch $(g, h) \cdot p = g \circ p \circ h^{-1}$. Zahl der Bahnen $= \frac{1}{|G||A|} \sum_{(g,h)} |\{p : g \circ p = p \circ h\}|$. Für feste $g, h$ ist $g \circ p = p \circ h$ genau dann lösbar, wenn $g$ und $h$ dieselbe Zykelstruktur haben; dann gibt es $\prod_{\ell} c_\ell!\, \ell^{c_\ell}$ Lösungen ($c_\ell$: Zahl der $\ell$-Zykel).

**Orbit-Beschneiden.** In einem Knoten sind die Plätze $S$ belegt, $G_S = \{g \in G : g(j) = j\ \forall j \in S\}$. Von den freien Plätzen wird je Bahn von $G_S$ nur der kleinste verzweigt. Jede Anordnung ist durch ein Element von $G_S$ äquivalent zu einer, die dem Pfad folgt; die Kosten und die Schranken der Kinder in einer Bahn sind gleich (die Schranke hängt nur von $D$ und $F$ ab, die von $g$ erhalten werden).

**Zwillingsordnung.** Für eine Klasse $\{i_1, \dots, i_m\}$ (in der Reihenfolge der Verzweigung) verlangt man $p_{i_1} < p_{i_2} < \dots < p_{i_m}$. Durch Vertauschen der Zwillinge erreicht man diese Ordnung ohne Kostenänderung.

**Kombination.** Beide Bedingungen zusammen sind in den Messungen gültig; ein Beweis steht aus (die Platzbedingung „kleinster Platz je Bahn“ und die Zwillingsbedingung „aufsteigende Plätze“ sind nicht gemeinsam lexikographisch geführt).

**Verhältnis.** $\text{Knoten ohne} / \text{Knoten mit}$; für die Platzsymmetrie allein höchstens $|G|$ bei Anfangswert gleich dem Optimum.

**Literatur.** Symmetriebrechung im Branch and Bound (Orbit-Fixierung, Lex-Leader-Bedingungen, Margot u. a.) und die Berechnung von Automorphismengruppen von Graphen kenne ich nur als Namen aus der Fachliteratur: **nicht nachgelesen**. Die Fassung hier ist eigen und wird durch Tests geprüft
(Aufzählung aller Permutationen der Plätze, Burnside gegen Aufzählung der Bahnen, Baum gegen Aufzählung). Die Zahlen sind eigene Rechnungen an eigenen, erfundenen Familien.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
