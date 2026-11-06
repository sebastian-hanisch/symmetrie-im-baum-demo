"""Symmetrien, Zählung (Burnside) und Baum: Handwerte, Eigenschaften und Orakel (Aufzählung aller Permutationen; ORACLE-PLAYBOOK §5)."""

import itertools
import math

import numpy as np
import pytest

import syb_bounds as B
import syb_constants as C
import syb_landscape as L
import syb_symmetry as S
import syb_tree as T
from syb_instance import make_instance
from syb_evaluation import make_flow_instance


def opt_of(F, D):
    n = len(F)
    return int(L.costs_of(L.all_perms(n), F, D).min())


# ----------------------------------------------------------------------------- Platzgruppen

@pytest.mark.parametrize("rows,cols,order", [(1, 4, 2), (2, 2, 8), (2, 3, 4), (2, 4, 4), (3, 3, 8), (3, 4, 4), (4, 4, 8)])
def test_grid_group_sizes_closure_and_identity(rows, cols, order):
    G = S.grid_group(rows, cols)
    n = rows * cols
    assert len(G) == order == len(set(G)) and tuple(range(n)) in G
    for g in G:
        for h in G:
            assert tuple(g[h[a]] for a in range(n)) in G                              # abgeschlossen unter Verkettung
        inv = [0] * n
        for a, b in enumerate(g):
            inv[b] = a
        assert tuple(inv) in G


@pytest.mark.parametrize("n", (6, 8))
def test_the_group_is_exactly_the_automorphism_group_of_the_distances(n):
    """Gegen alle n! Permutationen der Plätze (Aufzählung): genau die Symmetrien des Rechtecks lassen D invariant."""
    inst = make_instance("uniform", n, 100000)
    D = inst.D.astype(int)
    G = S.grid_group(inst.rows, inst.cols)
    assert all(S.is_symmetry(D, g) for g in G)
    found = [s for s in itertools.permutations(range(n)) if S.is_symmetry(D, s)]
    assert sorted(found) == sorted(G)


def test_the_group_of_the_square_has_eight_elements_by_enumeration():
    inst = make_instance("uniform", 9, 100000)
    D = inst.D.astype(int)
    assert sum(S.is_symmetry(D, s) for s in itertools.permutations(range(9))) == 8 == len(S.grid_group(3, 3))
    assert not S.is_symmetry(D, (1, 0, 2, 3, 4, 5, 6, 7, 8))


def test_place_orbits_and_stabilizers():
    G = S.grid_group(3, 3)
    assert S.place_orbits(G, 9) == [[0, 2, 6, 8], [1, 3, 5, 7], [4]]
    assert S.stabilizer_orders(G, [4]) == [8, 8] and S.stabilizer_orders(G, [0, 4]) == [8, 2, 2] and S.stabilizer_orders(G, [1, 3]) == [8, 2, 1]
    G24 = S.grid_group(2, 4)
    assert S.place_orbits(G24, 8) == [[0, 3, 4, 7], [1, 2, 5, 6]] and S.stabilizer_orders(G24, [0]) == [4, 1]


def test_images_have_the_same_cost_and_the_action_is_free():
    inst = make_instance("uniform", 8, 100003)
    F, D = inst.F.astype(int), inst.D.astype(int)
    G = S.grid_group(2, 4)
    rng = np.random.default_rng(1)
    for _ in range(20):
        p = [int(x) for x in rng.permutation(8)]
        imgs = S.images(p, G)
        costs = {int(L.costs_of(np.array([q]), F, D)[0]) for q in imgs}
        assert len(costs) == 1 and len(set(imgs)) == len(G)                              # gleich teuer, paarweise verschieden (freie Wirkung)


# ----------------------------------------------------------------------------- Bauteilgruppen

@pytest.mark.parametrize("family", C.ALL_FAMILIES)
def test_aut_count_and_group_agree_with_the_brute_force_count(family):
    inst = make_flow_instance(family, 6, 100000)
    F = inst.F.astype(int)
    brute = sum(1 for h in itertools.permutations(range(6)) if (F[np.ix_(h, h)] == F).all())
    cnt, full = S.aut_count(F)
    A = S.aut_group(F)
    assert cnt == brute == len(A) and full and all((F[np.ix_(h, h)] == F).all() for h in A)


def test_the_symmetric_families_have_their_known_groups():
    h = lambda k, n: S.aut_count(S.make_flow(k, n), cap=3_000_000)[0]
    assert [h("ring", n) for n in (6, 8, 9)] == [12, 16, 18]
    assert [h("hub", n) for n in (6, 8, 9)] == [120, 5040, 40320]
    assert [h("bipartite", n) for n in (6, 8, 9)] == [2 * 36, 2 * 576, 24 * 120]            # n = 9: Hälften 4 und 5, keine Vertauschung der Hälften
    assert [h("blocks", n) for n in (6, 8, 9)] == [2 * 36, 2 * 576, 6 ** 3 * 2]
    assert S.aut_count(S.make_flow("hub", 12), cap=1000) == (1000, False) and S.aut_group(S.make_flow("hub", 9), cap=1000) is None


def test_twin_classes_are_automorphisms_and_cover_the_known_classes():
    assert S.twin_classes(S.make_flow("bipartite", 8)) == [[0, 1, 2, 3], [4, 5, 6, 7]] and S.twin_classes(S.make_flow("hub", 6)) == [[1, 2, 3, 4, 5]]
    assert S.twin_classes(S.make_flow("blocks", 9)) == [[0, 1, 2], [3, 4, 5], [6, 7, 8]] and S.twin_classes(S.make_flow("ring", 8)) == []
    for fam in C.ALL_FAMILIES:
        F = make_flow_instance(fam, 8, 100001).F.astype(int)
        for c in S.twin_classes(F):
            for i, j in itertools.combinations(c, 2):
                p = list(range(8))
                p[i], p[j] = j, i
                assert (F[np.ix_(p, p)] == F).all()


def test_make_flow_rejects_unknown_kinds():
    with pytest.raises(ValueError):
        S.make_flow("gauss", 6)


# ----------------------------------------------------------------------------- Burnside

def test_cycle_types_and_fixed_counts_by_hand():
    assert S.cycle_type((0, 1, 2, 3)) == (1, 1, 1, 1) and S.cycle_type((1, 0, 3, 2)) == (2, 2) and S.cycle_type((1, 2, 0, 3)) == (1, 3)
    assert S.fixed_count((1, 1, 1, 1)) == 24 and S.fixed_count((2, 2)) == 8
    assert S.fixed_count((4,)) == 4 and S.fixed_count((1, 3)) == 3 and S.fixed_count((1, 1, 2)) == 2 * 2


def test_hand_example_burnside_equals_the_enumeration(hand_gap):
    F = hand_gap.F.astype(int)
    G, A = S.grid_group(1, 4), S.aut_group(F)
    assert len(G) == 2 and len(A) == 8 and S.twin_classes(F) == [[0, 1], [2, 3]]
    assert S.burnside_orbits(G, A) == S.orbits_bruteforce(G, A, 4) == 3
    assert S.burnside_orbits(G, [tuple(range(4))]) == 12 == 24 // 2


@pytest.mark.parametrize("family", C.ALL_FAMILIES)
@pytest.mark.parametrize("n", (6, 8))
def test_burnside_equals_the_enumerated_orbits(family, n):
    inst = make_flow_instance(family, n, 100002)
    F = inst.F.astype(int)
    G = S.grid_group(inst.rows, inst.cols)
    A = S.aut_group(F)
    if A is None or n == 8 and len(A) * len(G) > 6000:
        pytest.skip("Gegenprobe durch Aufzählung zu groß")
    b = S.burnside_orbits(G, A)
    assert b == S.orbits_bruteforce(G, A, n) and b <= math.factorial(n) // len(G)
    if len(A) == 1:
        assert b == math.factorial(n) // len(G)


# ----------------------------------------------------------------------------- Baum

@pytest.mark.parametrize("family", C.ALL_FAMILIES)
@pytest.mark.parametrize("start", (True, False))
def test_every_variant_finds_the_enumerated_optimum(family, start):
    inst = make_flow_instance(family, 8, 100004)
    F, D = inst.F.astype(int), inst.D.astype(int)
    G, tw = S.grid_group(inst.rows, inst.cols), S.twin_classes(F)
    opt = opt_of(F, D)
    ub = int(B.best_found(F, D, 100004, 200)[0]) if start else None
    nodes = {}
    for name, kw in (("plain", {}), ("place", {"group": G}), ("twins", {"twins": tw}), ("both", {"group": G, "twins": tw})):
        r = S.solve(F, D, incumbent=ub, **kw)
        assert r["best"] == opt and not r["capped"] and sum(r["depth"]) == r["nodes"], (family, name)
        nodes[name] = r["nodes"]
    assert nodes["place"] <= nodes["plain"] and nodes["twins"] <= nodes["plain"] and nodes["both"] <= nodes["plain"]


def test_without_symmetry_the_tree_is_the_tree_of_stueck_8():
    inst = make_instance("cluster", 8, 100005)
    F, D = inst.F.astype(int), inst.D.astype(int)
    ub = int(B.best_found(F, D, 100005, 200)[0])
    a = S.solve(F, D, incumbent=ub)
    b = T.solve(F, D, "glb", incumbent=ub)
    assert a["nodes"] == b.nodes and a["best"] == b.best and a["depth"] == b.depth


def test_the_gain_of_the_place_group_is_at_most_its_order_with_the_optimum_as_start_value():
    for fam in C.FAMILIES:
        inst = make_instance(fam, 8, 100006)
        F, D = inst.F.astype(int), inst.D.astype(int)
        opt = opt_of(F, D)
        plain = S.solve(F, D, incumbent=opt)
        sym = S.solve(F, D, incumbent=opt, group=S.grid_group(2, 4))
        assert sym["nodes"] * 4 >= plain["nodes"] and sym["nodes"] <= plain["nodes"]


def test_hand_example_nodes(hand_gap):
    F, D = hand_gap.F.astype(int), hand_gap.D.astype(int)
    G, tw = S.grid_group(1, 4), S.twin_classes(F)
    got = {inc: [S.solve(F, D, incumbent=inc, **kw)["nodes"] for kw in ({}, {"group": G}, {"twins": tw}, {"group": G, "twins": tw})] for inc in (6, None)}
    assert got == {6: [4, 2, 4, 2], None: [10, 8, 10, 8]}
    assert all(S.solve(F, D, incumbent=None, **kw)["best"] == 6 for kw in ({}, {"group": G}, {"twins": tw}))


def test_the_node_cap_stops_the_search_and_says_so():
    F = S.make_flow("bipartite", 12)
    D = make_instance("uniform", 12, 1).D.astype(int)
    r = S.solve(F, D, incumbent=78, cap=500)
    assert r["capped"] and r["nodes"] <= 500


def test_twin_order_cuts_a_lot_on_symmetric_flows_and_keeps_the_value():
    inst = make_flow_instance("bipartite", 8, 1)
    F, D = inst.F.astype(int), inst.D.astype(int)
    ub = int(B.best_found(F, D, 1, 200)[0])
    plain = S.solve(F, D, incumbent=ub)
    twins = S.solve(F, D, incumbent=ub, twins=S.twin_classes(F))
    both = S.solve(F, D, incumbent=ub, group=S.grid_group(2, 4), twins=S.twin_classes(F))
    assert (plain["nodes"], twins["nodes"], both["nodes"]) == (880, 111, 60) and plain["best"] == twins["best"] == both["best"] == 28
