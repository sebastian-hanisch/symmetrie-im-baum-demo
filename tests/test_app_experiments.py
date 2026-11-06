"""Pfade der App, die der Rauchtest nicht erreicht: die Experimente im Seiteninhalt, PDF, jede Familie, die Schalter, n = 12, die Rechenknöpfe (DEMO-PLAYBOOK §1d)."""

from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import syb_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
KIND = {"family_select": "selectbox", "n_select": "select_slider", "seed_input": "number_input", "place_toggle": "toggle", "twins_toggle": "toggle", "start_toggle": "toggle"}
LABELS = {"Platzsymmetrien |G|", "Anordnungen bis auf Plätze", "Knoten mit der gewählten Variante", "Verhältnis ohne gegen mit", "Bester Wert"}


@pytest.fixture(autouse=True)
def _clear_caches():
    """st.cache_data gilt im ganzen Prozess: Tests, die Konstanten ändern, dürfen keine Ergebnisse an andere weitergeben."""
    st.cache_data.clear()
    yield
    st.cache_data.clear()


def _app(**state) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    for key, value in state.items():
        getattr(at.sidebar, KIND[key])(key=key).set_value(value)
    if state:
        at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return " ".join(str(e.value) for e in list(at.success) + list(at.info) + list(at.warning) + list(at.error) + list(at.markdown) + list(at.caption))


def _metrics(at):
    return {m.label: m for m in at.metric}


def test_default_page_shows_the_metrics_and_the_verdicts():
    at = _app()
    m = _metrics(at)
    assert set(m) == LABELS and m["Platzsymmetrien |G|"].value == "4" and m["Anordnungen bis auf Plätze"].value == "10 080" and m["Knoten mit der gewählten Variante"].value == "139" and m["Knoten mit der gewählten Variante"].delta == "ohne Symmetrie 556"
    assert m["Verhältnis ohne gegen mit"].value == "4,00" and m["Bester Wert"].value == "183" and m["Bester Wert"].delta == "wie ohne Symmetrie"
    text = _texts(at)
    for part in ("Familie **Zwei Cluster**, 8 Bauteile, Raster 2×4, Seed 48", "139 Knoten gegen 556 ohne Symmetrie", "**4** Symmetrien der Abstände", "Platzsymmetrien 2 (Spiegelung)", "fünf Experimente"):
        assert part in text, part
    assert len(at.get("plotly_chart")) == 6


def test_the_experiments_the_hand_example_the_limits_table_and_the_formulation_are_on_the_page():
    at = _app()
    headings = [s.value for s in at.subheader]
    assert [h.split(":")[0] for h in headings if h.startswith("🔬 Experiment")] == [f"🔬 Experiment {i}" for i in (1, 2, 3, 4, 5)] and "🚧 Wo die Annahmen enden" in headings
    assert [e.label for e in at.expander] == ["So funktioniert es", "Handbeispiel zum Nachrechnen", "📐 Mathematische Formulierung"]
    assert not at.error
    assert any("`n! = 24` Anordnungen und `12` Bahnen" in str(m.value) and "**16 der 24 Anordnungen kosten 6**" in str(m.value) and "**3 Bahnen**" in str(m.value) for m in at.markdown)
    assert [b.label for b in at.button if "⏱️" in b.label] == ["⏱️ Feste Instanzen rechnen (n = 6, 8, 9, 12)", "⏱️ Symmetrische Flüsse rechnen", "⏱️ Zufallsprobe rechnen (300 Instanzen)"]


def test_the_square_has_eight_symmetries_and_the_tree_shrinks_by_about_that_factor():
    at = _app(n_select=9)
    m = _metrics(at)
    assert m["Platzsymmetrien |G|"].value == "8" and m["Anordnungen bis auf Plätze"].value == "45 360" and float(m["Verhältnis ohne gegen mit"].value.replace(",", ".")) > 5


def test_switches_change_the_selected_variant():
    base = _metrics(_app())["Knoten mit der gewählten Variante"].value
    plain = _app(place_toggle=False)
    assert _metrics(plain)["Knoten mit der gewählten Variante"].value == "556" and _metrics(plain)["Verhältnis ohne gegen mit"].value == "1,00"
    both = _app(family_select="bipartite", n_select=9, twins_toggle=True)
    assert _metrics(both)["Knoten mit der gewählten Variante"].value == "57" and base == "139"
    nostart = _app(start_toggle=False)
    assert "ohne Anfangswert" in _texts(nostart) and int(_metrics(nostart)["Knoten mit der gewählten Variante"].delta.replace("ohne Symmetrie ", "").replace(" ", "")) > 556


def test_every_family_and_size_renders():
    for fam in C.ALL_FAMILIES:
        at = _app(family_select=fam, n_select=6)
        assert fam and set(_metrics(at)) == LABELS and not at.exception
    for n in (4, 9):
        at = _app(n_select=n)
        assert f"{n} Bauteile" in _texts(at) and len(at.get("plotly_chart")) == 6


def test_twelve_waits_for_its_button():
    at = _app(n_select=12)
    assert "⏱️ Baum rechnen" in [b.label for b in at.button] and not at.metric and "Mit dem Knopf starten" in _texts(at)
    at.button(key="heavy_button").click().run()
    assert not at.exception and set(_metrics(at)) == LABELS and _metrics(at)["Platzsymmetrien |G|"].value == "4"


def test_the_pdf_button_makes_a_download():
    at = _app(n_select=6)
    at.button(key="pdf_make").click().run()
    assert not at.exception and any(d.proto.label == "⬇️ PDF herunterladen" for d in at.get("download_button"))


def test_the_comparison_buttons_fill_their_sections(monkeypatch):
    monkeypatch.setattr(C, "ROW_SIZES", (6, 8))                                      # nur für die Geschwindigkeit des Tests: die echten Reihen stehen in test_claims.py
    monkeypatch.setattr(C, "SEEDS", {6: 1, 8: 1, 9: 1, 12: 1})
    monkeypatch.setattr(C, "STRUCT_SIZES", (6, 8))
    monkeypatch.setattr(C, "PROBE_COUNT", 3)
    at = _app()
    at.button(key="series_ok_button").click().run()
    text = _texts(at)
    assert not at.exception and "n = 6 (6 Instanzen, |G| = 4)" in text and "n = 8 (6 Instanzen, |G| = 4)" in text and "bester Wert gleich in 6 von 6" in text and len(at.get("plotly_chart")) == 6 + 1
    at.button(key="struct_ok_button").click().run()
    text = _texts(at)
    assert not at.exception and "„Zwei Hälften“" in text and "Gilmore–Lawler ist bei „Ring“ und „Nabe“ so scharf" in text and len(at.get("plotly_chart")) == 6 + 1 + 1
    at.button(key="probe_ok_button").click().run()
    text = _texts(at)
    assert not at.exception and "6 zufällige Flussmatrizen mit erzwungenen Zwillingspaaren" in text and "0 / 0 / 0 / 0" in text
