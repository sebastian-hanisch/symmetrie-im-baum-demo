"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; Permalink verwirft ungültige Werte."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import syb_constants as C
import syb_evaluation as ev
import syb_presets as PR

APP = str(Path(__file__).resolve().parent.parent / "app.py")
DEFAULT = "Standardfall: Plätze, acht Bauteile"


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(PR.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_control_choices():
    for p in C.PRESETS.values():
        assert p["n"] in C.SIZES and p["family"] in C.ALL_FAMILIES and 0 <= p["seed"] <= C.SEED_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[DEFAULT]) == ev.Settings() and next(iter(C.PRESETS)) == DEFAULT


def test_setting_specs_cover_every_preset_key():
    assert set(PR.PRESET_KEYS.values()) == set(PR.SETTING_SPECS)


def test_the_presets_differ_from_the_default_where_the_help_says_so():
    P = C.PRESETS
    assert P["Quadrat: acht Symmetrien"]["n"] == 9 and P["Zwölf Bauteile"]["n"] == 12 and P["Vier Bauteile"]["n"] == 4 and P["Ohne Anfangswert"]["start"] is False and P[DEFAULT]["start"] is True
    assert P["Zwei Hälften: Zwillinge"]["twins"] is True and P["Zwei Hälften: Zwillinge"]["place"] is False and P["Zwei Hälften: beides"]["twins"] and P["Zwei Hälften: beides"]["place"]
    assert P["Blöcke"]["family"] == "blocks" and P["Zwei Hälften: beides"]["family"] == "bipartite"


def test_permalink_takes_valid_values_and_drops_invalid_ones():
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["family"] = "star"
    at.query_params["n"] = "12"
    at.query_params["seed"] = "7"
    at.run()
    assert not at.exception
    assert at.session_state["family_select"] == "star" and at.session_state["n_select"] == 12 and at.sidebar.number_input(key="seed_input").value == 7
    bad = AppTest.from_file(APP, default_timeout=300)
    bad.query_params["family"] = "gauss"
    bad.query_params["n"] = "7"
    bad.query_params["seed"] = "abc"
    bad.run()
    assert not bad.exception
    assert bad.session_state["family_select"] == C.DEFAULT_FAMILY and bad.session_state["n_select"] == C.DEFAULT_N and bad.session_state["seed_input"] == C.DEFAULT_SEED


def test_the_seed_is_clamped_to_its_bounds():
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["seed"] = "99999999"
    at.run()
    assert at.session_state["seed_input"] == C.SEED_MAX
