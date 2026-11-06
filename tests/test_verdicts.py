"""Verdikte: datengetrieben (Art und Text folgen den Zahlen), jeder Zweig an festen Eingaben (DEMO-PLAYBOOK §1b)."""

import copy

import pytest

import syb_constants as C
import syb_evaluation as E
from oracle import make_series_row, make_struct_row, run

S0 = E.Settings()


@pytest.fixture(scope="module")
def v8():
    return E.instance_data(S0)


def test_core_verdict_success_for_the_default_instance(v8):
    kind, text = E.verdict_core(S0, v8)
    assert kind == "success" and "4 Platzsymmetrien" in text and "10 080 Bahnen der Größe 4 (von 40 320)" in text and "keine Symmetrie (nur die Identität)" in text
    assert "139 Knoten gegen 556 ohne Symmetrie (Verhältnis 4,00; Obergrenze der Platzsymmetrie 4)" in text and "**wie ohne Symmetrie**" in text and "Eine Instanz" in text


def test_core_verdict_for_the_other_variants(v8):
    _, plain = E.verdict_core(E.Settings(place=False), v8)
    assert "Baum ohne Symmetrie (Anfangswert beste von 200 Abstiegen): 556 Knoten" in plain and "Mit Orbit-Beschneiden wären es 139 Knoten (Verhältnis 4,00)" in plain
    _, twins = E.verdict_core(E.Settings(place=False, twins=True), v8)
    assert "Zwillinge (Ordnung)" in twins and "Obergrenze der Platzsymmetrie" not in twins
    _, nostart = E.verdict_core(E.Settings(start=False), v8)
    assert "ohne Anfangswert" in nostart


def test_core_verdict_names_a_lost_optimum_and_a_capped_run(v8):
    v = copy.deepcopy(v8)
    v["runs"]["place"]["best"] = 190.0
    kind, text = E.verdict_core(S0, v)
    assert kind == "error" and "**anders als ohne Symmetrie: das Optimum ging verloren!**" in text
    w = copy.deepcopy(v8)
    w["runs"]["plain"]["capped"] = True
    assert "Obergrenze von 400 000 Knoten erreicht: nicht zu Ende gerechnet" in E.verdict_core(S0, w)[1]


def test_core_verdict_with_automorphisms():
    s = E.Settings(family="bipartite", n=9, twins=True)
    v = E.instance_data(s)
    _, text = E.verdict_core(s, v)
    assert "8 Platzsymmetrien" in text and "2 880 Automorphismen" in text and "23 Bahnen unter Plätzen und Bauteilen" in text and "57 Knoten gegen 1 665" in text


def test_group_verdict(v8):
    kind, text = E.verdict_group(S0, v8)
    assert kind == "info" and "**4** Symmetrien der Abstände" in text and "in 2 Bahnen (4, 4 Plätze)" in text and "40 320 sind es roh" in text


def test_count_verdict(v8):
    _, text = E.verdict_count(S0, v8)
    assert "40 320 Anordnungen, 10 080 bis auf die Platzsymmetrie (n!/4)" in text and "10 080 bis auf Plätze und Bauteile (Burnside, 1 Automorphismus der Flüsse); die Aufzählung findet 10 080: gleich" in text
    assert "4 Anordnungen sind optimal (Kosten 183), in 1 Bahn unter den Plätzen und 1 unter Plätzen und Bauteilen" in text
    w = copy.deepcopy(v8)
    w["orbits_brute"] = 1
    assert "**ungleich**" in E.verdict_count(S0, w)[1]
    h = copy.deepcopy(v8)
    h["orbits_GA"], h["orbits_brute"], h["aut"], h["aut_full"], h["twins"], h["twin_product"] = None, None, 50000, False, [[1, 2, 3]], 6
    assert "Burnside nicht gerechnet: mehr als 50 000 Automorphismen" in E.verdict_count(S0, h)[1] and "mindestens 6 Automorphismen" in E.verdict_count(S0, h)[1]


def test_hand_verdict():
    kind, text = E.verdict_hand(E.hand_data())
    assert kind == "info" and "24 Anordnungen, **16** davon kosten 6" in text and "Platzsymmetrien 2" in text and "Automorphismen der Flüsse 8" in text and "unter Plätzen und Bauteilen: **3** (Burnside; die Aufzählung findet 3), davon 2 optimal" in text
    assert "4 Knoten ohne, **2** mit Orbit-Beschneiden, 4 mit Zwillingen, 2 mit beidem; ohne Anfangswert 10 / 8 / 10 / 8" in text


def test_series_verdict_with_and_without_start_value():
    rows = {8: [make_series_row(8, 400, 100, plain0=700, place0=250), make_series_row(8, 240, 60, plain0=300, place0=100)], 9: [make_series_row(9, 8000, 1000, g=8, plain0=900, place0=150)], 12: [make_series_row(12, 8000, 2000)]}
    kind, text = E.verdict_series(rows)
    assert kind == "info" and "n = 8 (2 Instanzen, |G| = 4): Verhältnis im Median 4,00 (kleinstes 4,00, größtes 4,00), Knoten im Median 320 → 80, bester Wert gleich in 2 von 2" in text and "n = 12 (1 Instanzen, |G| = 4)" in text
    assert "keine Symmetrie (|Aut(F)| = 1) in 2 von 2 (n = 8), 1 von 1 (n = 9), 1 von 1 (n = 12)" in text and "kleiner und streut" not in text
    _, nostart = E.verdict_series({m: r for m, r in rows.items() if "plain0" in r[0]}, start=False)
    assert "n = 8 (2 Instanzen, |G| = 4): Verhältnis im Median 2,90" in nostart and "n = 12" not in nostart and "kleiner und streut stärker" in nostart
    bad = {8: [make_series_row(8, 400, 100, place_best=99.0)]}
    assert "bester Wert gleich in 0 von 1" in E.verdict_series(bad)[1]


def test_optimal_verdict():
    rows = {8: [make_series_row(8, 10, 5, n_opt=8), make_series_row(8, 10, 5, n_opt=12, orbits=2)], 12: [make_series_row(12, 10, 5)]}
    kind, text = E.verdict_optimal(rows)
    assert kind == "info" and "n = 8: in 1 von 2 Instanzen ohne Bauteilsymmetrie ist die Zahl der optimalen Anordnungen genau |G| mal die Zahl ihrer Bahnen (Median 10 optimale Anordnungen, größte 12)" in text and "n = 12" not in text and "wirken frei" in text


def test_struct_verdict_marks_capped_runs_and_counts_differences():
    rows = [make_struct_row("bipartite", 12, 400000, 133696, 2120, 1334, caps=(True, False, False, False)), make_struct_row("blocks", 12, 11816, 2966, 1084, 403), make_struct_row("blocks", 9, 300, 50, 90, 20)]
    kind, text = E.verdict_struct(rows)
    assert kind == "info" and "„Zwei Hälften“: 400 000+ / 133 696 / 2 120 / 1 334" in text and "„Blöcke“: 11 816 / 2 966 / 1 084 / 403" in text and "ohne Symmetrie nicht zu Ende gerechnet: 1 Läufe" in text
    assert "verschieden zwischen den Varianten in 0 von 6 Vergleichen (nur zu Ende gerechnete Läufe)" in text
    rows[1]["twins"]["best"] = 49.0
    assert "in 1 von 6 Vergleichen" in E.verdict_struct(rows)[1]


def test_probe_verdict():
    ok = {"total": 300, "bad": {v: 0 for v in C.VARIANTS}, "nodes": dict(zip(C.VARIANTS, (91603, 27921, 60448, 22165)))}
    kind, text = E.verdict_probe(ok)
    assert kind == "success" and "300 zufällige Flussmatrizen" in text and "0 / 0 / 0 / 0" in text and "91 603 / 27 921 / 60 448 / 22 165" in text and "kein Beweis" in text
    kind2, text2 = E.verdict_probe({**ok, "bad": {**ok["bad"], "both": 2}})
    assert kind2 == "error" and "0 / 0 / 0 / 2" in text2 and "ist ungültig" in text2
