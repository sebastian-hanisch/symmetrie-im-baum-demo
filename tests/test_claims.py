"""Die Zahlen der README und der Verdikte, an den festen Instanzen und der Zufallsprobe nachgerechnet (Messung, nicht Satz).

Knotenzahlen, Gruppengrößen und Bahnzahlen sind **ganzzahlig und auf jedem Rechner gleich** (keine Gleitkomma-Entscheidung im Baum, feste Seeds, SplitMix64 für die Zufallsprobe): sie werden **genau** geprüft, Verhältnisse auf drei Stellen.
Zeiten stehen hier nie."""

import numpy as np
import pytest

import rows as RW
import syb_constants as C
import syb_evaluation as E

# n: (Instanzen, |G|, Instanzen ohne Bauteilsymmetrie, Verhältnis Median / kleinstes / größtes, Knoten ohne / mit (Summe), Knoten ohne / mit (Median))
SERIES = {
    6: (30, 4, 26, (3.578, 3.000, 3.941), (1706, 454), (34, 9.5)),
    8: (30, 4, 28, (4.000, 4.000, 4.000), (8980, 2245), (240, 60)),
    9: (18, 8, 16, (7.378, 6.200, 7.919), (27078, 3496), (675, 91)),
    12: (18, 4, 16, (3.978, 3.785, 3.999), (839720, 210140), (7990, 2007)),
}
NO_START = {6: ((2.308, 1.235, 3.703), (2006, 750)), 8: ((3.142, 1.200, 3.924), (9895, 3133)), 9: ((6.504, 3.600, 7.778), (28151, 3976))}   # ohne Anfangswert (n ≤ 9)
OPTIMAL = {6: (26, 4.0, 48), 8: (28, 4.0, 32), 9: (16, 8.0, 64)}                # Instanzen ohne Bauteilsymmetrie, Median und größte Zahl optimaler Anordnungen
AUT_BIGGER = {6: [("netlist", 2), ("netlist", 2), ("sparse", 2), ("star", 2)], 8: [("netlist", 6), ("sparse", 2)], 9: [("netlist", 4), ("sparse", 2)], 12: [("netlist", 2), ("netlist", 4)]}
# symmetrische Familien: (|G|, |Aut(F)|, vollständig gezählt, Zwillingsklassen, Bahnen G × A, Knoten ohne / Plätze / Zwillinge / beides, ohne Symmetrie bei der Obergrenze)
STRUCT = {
    ("bipartite", 6): (4, 72, True, [3, 3], 5, (36, 10, 21, 9), False), ("bipartite", 8): (4, 1152, True, [4, 4], 17, (880, 220, 111, 60), False),
    ("bipartite", 9): (8, 2880, True, [4, 5], 23, (1665, 216, 181, 57), False), ("bipartite", 12): (4, 50000, False, [6, 6], None, (400000, 133696, 2120, 1334), True),
    ("ring", 6): (4, 12, True, [], 24, (6, 2, 6, 2), False), ("ring", 8): (4, 16, True, [], 720, (8, 2, 8, 2), False),
    ("ring", 9): (8, 18, True, [], 2544, (401, 55, 401, 55), False), ("ring", 12): (4, 24, True, [], 4996320, (12, 4, 12, 4), False),
    ("hub", 6): (4, 120, True, [5], 2, (6, 2, 6, 2), False), ("hub", 8): (4, 5040, True, [7], 2, (8, 2, 8, 2), False),
    ("hub", 9): (8, 40320, True, [8], 3, (9, 3, 9, 3), False), ("hub", 12): (4, 50000, False, [11], None, (12, 4, 12, 4), False),
    ("blocks", 6): (4, 72, True, [3, 3], 5, (84, 22, 31, 15), False), ("blocks", 8): (4, 1152, True, [4, 4], 17, (304, 76, 62, 34), False),
    ("blocks", 9): (8, 432, True, [3, 3, 3], 118, (305, 45, 91, 23), False), ("blocks", 12): (4, 2592, True, [3, 3, 3, 3], 46592, (11816, 2966, 1084, 403), False),
}
PROBE = {"total": 300, "bad": {v: 0 for v in C.VARIANTS}, "nodes": dict(zip(C.VARIANTS, (90801, 27134, 60216, 21252)))}


@pytest.mark.parametrize("n", C.ROW_SIZES)
def test_the_tree_shrinks_by_the_group_size_without_loss(n):
    count, g, triv, (med, lo, hi), (sa, sb), (ma, mb) = SERIES[n]
    rows = RW.series_rows(n)
    st = E.ratio_stats(rows)
    assert len(rows) == count and all(r["G"] == g for r in rows) and E.aut_trivial(rows) == triv
    assert (st["nodes_a"], st["nodes_b"], st["median_a"], st["median_b"]) == (sa, sb, ma, mb)
    assert (st["median"], st["min"], st["max"]) == pytest.approx((med, lo, hi), abs=1e-3)
    assert st["same_best"] == count and not any(r["plain"]["capped"] or r["place"]["capped"] for r in rows)
    assert 1.0 <= st["min"] and st["max"] <= g + 1e-9                          # nie mehr als die Gruppengröße gespart (mit Anfangswert)
    assert sorted((r["family"], r["aut"]) for r in rows if r["aut"] > 1) == AUT_BIGGER[n]


def test_at_eight_places_the_ratio_is_exactly_the_group_order_in_every_instance():
    rows = RW.series_rows(8)
    assert all(r["plain"]["nodes"] == 4 * r["place"]["nodes"] for r in rows)


@pytest.mark.parametrize("n", (6, 8, 9))
def test_without_a_start_value_the_gain_is_smaller_and_still_lossless(n):
    (med, lo, hi), (sa, sb) = NO_START[n]
    rows = RW.series_rows(n)
    st = E.ratio_stats(rows, "plain0", "place0")
    assert (st["nodes_a"], st["nodes_b"]) == (sa, sb) and (st["median"], st["min"], st["max"]) == pytest.approx((med, lo, hi), abs=1e-3) and st["same_best"] == len(rows)
    assert st["median"] < E.ratio_stats(rows)["median"] and st["max"] <= rows[0]["G"] + 1e-9


@pytest.mark.parametrize("n", (6, 8, 9))
def test_optimal_arrangements_come_in_whole_orbits(n):
    count, med, big = OPTIMAL[n]
    o = E.optimal_orbit_stats(RW.series_rows(n))
    assert (o["count"], o["exact"], o["median"], o["max"]) == (count, count, med, big)


@pytest.mark.parametrize("n", C.ROW_SIZES)
def test_counts_up_to_symmetry(n):
    import math

    rows = RW.series_rows(n)
    for r in rows:
        assert r["orbits_G"] == math.factorial(n) // r["G"]
        if r["orbits_GA"] is not None:
            assert r["orbits_GA"] <= r["orbits_G"] and (r["aut"] > 1 or r["orbits_GA"] == r["orbits_G"])
    assert min(r["orbits_GA"] / r["orbits_G"] for r in rows if r["orbits_GA"]) == pytest.approx({6: 0.5, 8: 1 / 6, 9: 0.2507936507936508, 12: 0.25}[n])


@pytest.mark.parametrize("key", list(STRUCT))
def test_symmetric_families(key):
    kind, n = key
    g, aut, full, twins, ga, nodes, capped = STRUCT[key]
    r = next(x for x in RW.struct_rows() if (x["kind"], x["n"]) == key)
    assert (r["G"], r["aut"], r["aut_full"], r["twin_classes"], r["orbits_GA"]) == (g, aut, full, twins, ga)
    assert tuple(r[v]["nodes"] for v in C.VARIANTS) == nodes and r["plain"]["capped"] == capped
    assert not any(r[v]["capped"] for v in C.VARIANTS[1:])
    assert len({r[v]["best"] for v in C.VARIANTS}) == 1                          # in allen vier Varianten derselbe beste Wert


def test_twins_beat_the_place_group_on_the_symmetric_families():
    rows = {(r["kind"], r["n"]): r for r in RW.struct_rows()}
    assert rows[("bipartite", 12)]["plain"]["capped"] and rows[("bipartite", 12)]["both"]["nodes"] == 1334 and rows[("bipartite", 12)]["twins"]["nodes"] < rows[("bipartite", 12)]["place"]["nodes"] // 50
    for key in (("bipartite", 9), ("bipartite", 8), ("blocks", 12)):
        r = rows[key]
        assert r["both"]["nodes"] < r["twins"]["nodes"] < r["plain"]["nodes"] and r["both"]["nodes"] < r["place"]["nodes"] < r["plain"]["nodes"]


def test_the_random_probe_of_the_combination():
    """300 zufällige Flussmatrizen mit erzwungenen Zwillingen, Baum ohne Anfangswert, Optimum aus der Aufzählung: keine Variante verfehlt es (kein Beweis); Knoten genau."""
    p = E.combo_probe()
    assert p == PROBE
