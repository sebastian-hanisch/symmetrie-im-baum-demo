"""Kennzahlen, feste Instanzen, Zeilen der Vergleiche und Formatierung: an künstlichen Zeilen mit bekannten Antworten und an kleinen echten Instanzen (ORACLE-PLAYBOOK §5)."""

import math

import pytest

import syb_constants as C
import syb_evaluation as E
from oracle import make_series_row, make_struct_row


def test_formatting():
    assert E.de(-1.5, 1) == "−1,5" and E.pct(12.34, 1) == "12,3 %" and E.num(27) == "27" and E.num(27.5) == "27,5" and E.count(1200) == "1 200"
    assert E.secs(0.0164) == "0,016 s" and E.secs(0.42) == "0,42 s" and E.secs(5.13) == "5,1 s" and E.secs(31.4) == "31 s"
    assert E.plural(1, "Bahn", "Bahnen") == "1 Bahn" and E.plural(12, "Bahn", "Bahnen") == "12 Bahnen" and E.plural(0, "Bahn", "Bahnen") == "0 Bahnen"


def test_ratio_handles_zero_nodes():
    assert E.ratio(100, 25) == 4.0 and E.ratio(0, 0) == 1.0 and E.ratio(5, 0) == float("inf")


def test_settings_variant():
    assert E.Settings(place=True, twins=False).variant == "place" and E.Settings(place=True, twins=True).variant == "both"
    assert E.Settings(place=False, twins=True).variant == "twins" and E.Settings(place=False, twins=False).variant == "plain"


def test_fixed_instances():
    assert {n: len(E.series_jobs(n)) for n in C.ROW_SIZES} == {6: 30, 8: 30, 9: 18, 12: 18}
    jobs = E.series_jobs(8)
    assert [j[2] for j in jobs if j[0] == "star"] == list(range(C.FIXED_SEED0, C.FIXED_SEED0 + 5)) and {j[0] for j in jobs} == set(C.FAMILIES) and len(set(jobs)) == len(jobs)


def test_flow_instances_of_all_ten_families():
    for f in C.ALL_FAMILIES:
        inst = E.make_flow_instance(f, 8, 100000)
        assert inst.F.shape == (8, 8) and (inst.F == inst.F.T).all() and (inst.F.diagonal() == 0).all() and inst.family == f
    a, b = E.make_flow_instance("bipartite", 8, 1), E.make_flow_instance("bipartite", 8, 999)
    assert (a.F == b.F).all()                                                          # die symmetrischen Familien sind deterministisch


def test_symmetry_data_for_the_default_instance():
    inst = E.make_flow_instance("cluster", 8, 48)
    d = E.symmetry_data(inst)
    assert len(d["G"]) == 4 and d["aut"] == 1 and d["aut_full"] and d["orbits_G"] == 10080 == d["orbits_GA"] == d["orbits_brute"] and d["arrangements"] == 40320 and d["twins"] == [] and d["twin_product"] == 1
    assert d["orbits_places"] == [[0, 3, 4, 7], [1, 2, 5, 6]]
    big = E.symmetry_data(E.make_flow_instance("hub", 12, 1))
    assert not big["aut_full"] and big["A"] is None and big["orbits_GA"] is None and big["orbits_brute"] is None and big["twin_product"] == math.factorial(11)


def test_optimal_set_for_a_known_instance():
    inst = E.make_flow_instance("cluster", 8, 48)
    d = E.symmetry_data(inst)
    o = E.optimal_set(inst.F.astype(int), inst.D.astype(int), d["G"], d["A"], 8)
    assert o["opt"] == 183 and o["n_opt"] == 4 and o["n_opt_orbits_G"] == 1 and o["n_opt_orbits_GA"] == 1


def test_instance_data_for_the_default_settings():
    s = E.Settings()
    v = E.instance_data(s)
    assert set(v["runs"]) == set(C.VARIANTS) and v["opt"] == 183 and v["ub"] >= 183 and sorted(v["opt_perm"]) == list(range(8))
    assert v["runs"]["plain"]["nodes"] == 556 and v["runs"]["place"]["nodes"] == 139 and all(r["best"] == 183 for r in v["runs"].values())
    free = E.instance_data(E.Settings(start=False))
    assert free["runs"]["plain"]["nodes"] > v["runs"]["plain"]["nodes"] and all(r["best"] == 183 for r in free["runs"].values())
    big = E.instance_data(E.Settings(family="bipartite", n=9, twins=True))
    assert (big["runs"]["plain"]["nodes"], big["runs"]["place"]["nodes"], big["runs"]["twins"]["nodes"], big["runs"]["both"]["nodes"]) == (1665, 216, 181, 57) and big["n_opt"] == 14400


def test_hand_data():
    h = E.hand_data()
    assert (h["arrangements"], h["orbits_G"], h["orbits_GA"], h["orbits_brute"], h["n_opt"], h["n_opt_orbits_GA"], h["opt"]) == (24, 12, 3, 3, 16, 2, 6) and len(h["G"]) == 2 and len(h["A"]) == 8
    assert h["with"] == {"plain": 4, "place": 2, "twins": 4, "both": 2} and h["without"] == {"plain": 10, "place": 8, "twins": 10, "both": 8}


def test_series_row_on_a_small_instance():
    r = E.series_row("cluster", 6, 100000)
    assert r["G"] == 4 and r["aut"] == 1 and r["orbits_G"] == 180 and r["place"]["best"] == r["plain"]["best"] == r["opt"] and r["n_opt"] == 4 * r["n_opt_orbits_G"]
    assert r["place"]["nodes"] <= r["plain"]["nodes"] and r["place0"]["nodes"] <= r["plain0"]["nodes"] and len(E.series_sweep("cluster", 6)) == C.SEEDS[6]


def test_struct_row_on_a_small_instance():
    r = E.struct_row("bipartite", 8)
    assert (r["G"], r["aut"], r["twin_classes"], r["orbits_GA"]) == (4, 1152, [4, 4], 17) and (r["plain"]["nodes"], r["place"]["nodes"], r["twins"]["nodes"], r["both"]["nodes"]) == (880, 220, 111, 60)
    assert len({r[v]["best"] for v in C.VARIANTS}) == 1


def test_combo_probe_counts(monkeypatch):
    p = E.combo_probe(6)
    assert p["total"] == 12 and p["bad"] == {v: 0 for v in C.VARIANTS} and p["nodes"]["both"] <= p["nodes"]["plain"] and p == E.combo_probe(6)


def test_ratio_stats_and_counts_on_known_rows():
    rows = [make_series_row(8, 400, 100, plain0=700, place0=250), make_series_row(8, 240, 60, plain0=300, place0=100), make_series_row(8, 40, 10, aut=2, plain0=60, place0=15, place_best=99.0)]
    st = E.ratio_stats(rows)
    assert st["count"] == 3 and st["median"] == 4.0 and st["min"] == 4.0 and st["max"] == 4.0 and st["nodes_a"] == 680 and st["nodes_b"] == 170 and st["median_a"] == 240 and st["median_b"] == 60 and st["same_best"] == 2
    assert E.node_ratios(rows, "plain0", "place0") == [2.8, 3.0, 4.0] and E.ratio_stats(rows, "plain0", "place0")["median"] == 3.0
    assert E.aut_trivial(rows) == 2


def test_optimal_orbit_stats():
    rows = [make_series_row(8, 10, 5, n_opt=8), make_series_row(8, 10, 5, n_opt=12, orbits=2), make_series_row(8, 10, 5, n_opt=4, aut=2), make_series_row(8, 10, 5)]
    o = E.optimal_orbit_stats(rows)
    assert o == {"count": 2, "exact": 1, "median": 10.0, "max": 12}
    assert E.optimal_orbit_stats([make_series_row(8, 10, 5)])["count"] == 0


def test_struct_rows_helper_shapes():
    r = make_struct_row("bipartite", 12, 400000, 133696, 2120, 1334, caps=(True, False, False, False))
    assert r["plain"]["capped"] and not r["both"]["capped"] and r["both"]["nodes"] == 1334
