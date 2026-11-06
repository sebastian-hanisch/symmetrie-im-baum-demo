"""Symmetrien des Zuordnungsproblems: Platzsymmetrien des Rasters, Automorphismen und Zwillinge der Flussmatrix, Zählung der Anordnungen bis auf Symmetrie (Burnside) und der Baum aus Stück 8 mit Orbit-Beschneiden und Zwillingsordnung.
Eigene Herleitung; die Literatur zur Symmetriebrechung in Branch and Bound (Orbit-Fixierung, Lex-Leader, Margot) ist **nicht eingesehen**.

Kosten wie in Stück 1 bis 8: cost(p) = Σ_{i<k} F[i,k] · D[p_i, p_k] (p[i] = Platz des Bauteils i).
**Platzsymmetrie:** g mit D[g a, g b] = D[a, b] macht aus p die Anordnung g∘p mit denselben Kosten. Beim Raster mit Manhattan-Abstand sind das die Symmetrien des Rechtecks (Spiegelungen, Drehung um 180°; beim Quadrat auch Transponieren
und 90°-Drehungen); Test: gleich Aut(D) gegen alle n! Permutationen der Plätze. G wirkt **frei** auf die Anordnungen (g∘p = p nur für g = id): die Zahl der Bahnen ist n!/|G|.
**Bauteilsymmetrie:** h mit F[h a, h b] = F[a, b] macht aus p die Anordnung p∘h. **Zwillinge:** Bauteile i, j mit F[i,k] = F[j,k] für alle k ≠ i, j (Vertauschen ist ein Automorphismus).
**Burnside:** Zahl der Bahnen von G × A auf den Anordnungen (g∘p∘h⁻¹ = p) = (1/|G||A|) Σ_{g,h} #{p : g∘p = p∘h}; #{p : g∘p = p∘h} = ∏_ℓ c_ℓ! ℓ^{c_ℓ} (c_ℓ: Zahl der ℓ-Zykel von g), wenn g und h dieselbe Zykelstruktur haben, sonst 0.
**Baum:** wie Stück 8 (Tiefensuche über Teilzuordnungen, Knotenschranke Gilmore–Lawler), aber beim Verzweigen wird von den freien Plätzen **einer je Bahn** der Symmetrien versucht, die alle schon belegten Plätze einzeln festlassen (an der Wurzel die ganze Gruppe);
Zwillinge einer Klasse werden in aufsteigender Platzreihenfolge gesetzt. Zählung: bewertete Kinder (ohne die Wurzel), wie `syb_tree.solve`."""

from __future__ import annotations

import math
import time
from collections import Counter

import numpy as np

import syb_constants as C
import syb_tree as T


# ----------------------------------------------------------------------------- Platzsymmetrien

def grid_group(rows: int, cols: int) -> list:
    """Platzsymmetrien des rows×cols-Rasters als Permutationen der Plätze (Platz = r·cols + c), ohne Doppelte: bei einer Zeile 2, sonst 4; beim Quadrat 8."""
    idx = lambda r, c: r * cols + c
    maps = [lambda r, c: (r, c), lambda r, c: (r, cols - 1 - c), lambda r, c: (rows - 1 - r, c), lambda r, c: (rows - 1 - r, cols - 1 - c)]
    if rows == cols:
        maps += [lambda r, c: (c, r), lambda r, c: (c, cols - 1 - r), lambda r, c: (cols - 1 - c, r), lambda r, c: (cols - 1 - c, cols - 1 - r)]
    out = []
    for m in maps:
        g = tuple(idx(*m(r, c)) for r in range(rows) for c in range(cols))
        if g not in out:
            out.append(g)
    return out


def is_symmetry(D, g) -> bool:
    """Gilt D[g a, g b] = D[a, b] für alle Plätze?"""
    g = np.asarray(g)
    D = np.asarray(D)
    return bool((D[np.ix_(g, g)] == D).all())


def place_orbits(G: list, n: int) -> list:
    """Bahnen der Plätze unter G, aufsteigend nach dem kleinsten Platz."""
    seen, out = set(), []
    for j in range(n):
        if j not in seen:
            orb = sorted({g[j] for g in G})
            out.append(orb)
            seen |= set(orb)
    return out


def stabilizer_orders(G: list, places) -> list:
    """Ordnung der Gruppe, die die ersten k der Plätze `places` einzeln festlässt, für k = 0 bis len(places)."""
    cur = list(G)
    out = [len(cur)]
    for j in places:
        cur = [g for g in cur if g[j] == j]
        out.append(len(cur))
    return out


def images(perm, G: list) -> list:
    """Die |G| Bilder g∘p einer Anordnung (Platz je Bauteil)."""
    return [tuple(g[int(p)] for p in perm) for g in G]


# ----------------------------------------------------------------------------- Bauteilsymmetrien

def _signatures(F):
    F = np.asarray(F)
    return [tuple(sorted(F[i])) for i in range(len(F))], sorted(range(len(F)), key=lambda i: (-int(F[i].sum()), i))


def aut_count(F, cap: int = C.AUT_CAP) -> tuple:
    """(|Aut(F)|, vollständig?): Zahl der Permutationen h mit F[h a, h b] = F[a, b], durch Rücksetzen; bei mehr als `cap` Automorphismen (cap, False)."""
    F = np.asarray(F)
    n = len(F)
    sig, order = _signatures(F)
    cnt, ok = 0, True
    h, used = [-1] * n, [False] * n

    def rec(k):
        nonlocal cnt, ok
        if cnt >= cap:
            ok = False
            return
        if k == n:
            cnt += 1
            return
        a = order[k]
        for b in range(n):
            if used[b] or sig[b] != sig[a]:
                continue
            if all(F[a, order[t]] == F[b, h[order[t]]] for t in range(k)):
                h[a], used[b] = b, True
                rec(k + 1)
                used[b], h[a] = False, -1
                if not ok:
                    return

    rec(0)
    return cnt, ok


def aut_group(F, cap: int = C.AUT_CAP):
    """Alle Automorphismen von F als Permutationen; None, wenn es mehr als `cap` gibt."""
    F = np.asarray(F)
    n = len(F)
    sig, order = _signatures(F)
    out = []
    h, used = [-1] * n, [False] * n

    def rec(k):
        if len(out) > cap:
            return
        if k == n:
            out.append(tuple(h))
            return
        a = order[k]
        for b in range(n):
            if used[b] or sig[b] != sig[a]:
                continue
            if all(F[a, order[t]] == F[b, h[order[t]]] for t in range(k)):
                h[a], used[b] = b, True
                rec(k + 1)
                used[b], h[a] = False, -1

    rec(0)
    return out if len(out) <= cap else None


def twin_classes(F) -> list:
    """Klassen von Zwillingen (mindestens zwei Bauteile), jede als aufsteigende Liste."""
    F = np.asarray(F)
    n = len(F)
    cls, seen = [], set()
    for i in range(n):
        if i in seen:
            continue
        c = [i] + [j for j in range(i + 1, n) if j not in seen and all(F[i, k] == F[j, k] for k in range(n) if k != i and k != j)]
        if len(c) > 1:
            cls.append(c)
            seen |= set(c)
    return cls


# ----------------------------------------------------------------------------- Zählung

def cycle_type(p) -> tuple:
    n = len(p)
    seen, out = [False] * n, []
    for i in range(n):
        if not seen[i]:
            ln, j = 0, i
            while not seen[j]:
                seen[j] = True
                j = p[j]
                ln += 1
            out.append(ln)
    return tuple(sorted(out))


def fixed_count(t: tuple) -> int:
    """#{p : g∘p = p∘h} für g, h der Zykelstruktur t: ∏_ℓ c_ℓ! ℓ^{c_ℓ}."""
    out = 1
    for ln, c in Counter(t).items():
        out *= math.factorial(c) * ln ** c
    return out


def burnside_orbits(G: list, A: list) -> int:
    """Zahl der Bahnen von G × A auf den Anordnungen (ganzzahlig, exakt)."""
    cg = Counter(cycle_type(g) for g in G)
    ca = Counter(cycle_type(h) for h in A)
    total = sum(m * ca[t] * fixed_count(t) for t, m in cg.items() if t in ca)
    assert total % (len(G) * len(A)) == 0
    return total // (len(G) * len(A))


def orbits_bruteforce(G: list, A: list, n: int) -> int:
    """Gegenprobe: die Bahnen durch Aufzählung aller Anordnungen (n ≤ 8)."""
    import syb_landscape as L

    inv = []
    for h in A:
        x = [0] * n
        for a, b in enumerate(h):
            x[b] = a
        inv.append(x)
    seen, count = set(), 0
    for p in map(tuple, L.all_perms(n).tolist()):
        if p in seen:
            continue
        count += 1
        for g in G:
            for x in inv:
                seen.add(tuple(g[p[x[a]]] for a in range(n)))
    return count


# ----------------------------------------------------------------------------- Baum

def solve(F, D, incumbent=None, order: str = "flow", cap: int | None = C.NODE_CAP, group=None, twins=None) -> dict:
    """Tiefensuche wie `syb_tree.solve` (Gilmore–Lawler-Knotenschranken), mit Orbit-Beschneiden (`group`: Liste der Platzsymmetrien) und Zwillingsordnung (`twins`: Klassen).

    Rückgabe: Knoten (bewertete Kinder), bester Wert, Obergrenze erreicht?, Sekunden, übersprungene Kinder und Knoten je Tiefe."""
    F, D = np.asarray(F), np.asarray(D)
    n = len(F)
    seq = T.branch_order(F, order)
    best = float("inf") if incumbent is None else float(incumbent)
    state = {"nodes": 0, "capped": False, "skipped": 0}
    depth = [0] * n
    start = time.perf_counter()
    G0 = list(group) if group else [tuple(range(n))]
    prev_of = {}
    for c in (twins or []):
        ordered = sorted(c, key=seq.index)
        for a, b in zip(ordered, ordered[1:]):
            prev_of[b] = a                                           # Bauteil b muss auf einen größeren Platz als sein Vorgänger a in der Klasse
    place_of = {}

    def rec(k, fixed, fac, loc, free_l, Gk):
        nonlocal best
        if k == n:
            if fixed < best:
                best = float(fixed)
            return
        i = seq[k]
        free_f = seq[k + 1:]
        reps, done = [], set()
        for j in free_l:                                             # kleinster freier Platz je Bahn der Stabilisatorgruppe
            if j in done:
                continue
            orb = {g[j] for g in Gk}
            done |= orb
            reps.append(j)
            state["skipped"] += len(orb & set(free_l)) - 1
        kids = []
        for j in reps:
            if i in prev_of and not j > place_of[prev_of[i]]:
                state["skipped"] += 1
                continue
            if cap is not None and state["nodes"] >= cap:
                state["capped"] = True
                return
            state["nodes"] += 1
            depth[k] += 1
            fx = fixed + sum(int(F[i, a]) * int(D[j, l]) for a, l in zip(fac, loc))
            rest = [x for x in free_l if x != j]
            b = T.node_bound(C.TREE_ART, F, D, fac + [i], loc + [j], free_f, rest, fx)
            if not T.prunes(b, best):
                kids.append((b, j, fx, rest))
        kids.sort(key=lambda t: (t[0], t[1]))
        for b, j, fx, rest in kids:
            if T.prunes(b, best):
                continue
            place_of[i] = j
            rec(k + 1, fx, fac + [i], loc + [j], rest, [g for g in Gk if g[j] == j])
            place_of.pop(i, None)
            if state["capped"]:
                return

    rec(0, 0, [], [], list(range(n)), G0)
    return {"nodes": state["nodes"], "best": best, "capped": state["capped"], "seconds": time.perf_counter() - start, "skipped": state["skipped"], "depth": tuple(depth)}


# ----------------------------------------------------------------------------- symmetrische Flussmatrizen

def make_flow(kind: str, n: int) -> np.ndarray:
    """Die symmetrischen Familien (alle Flüsse gleich stark): `bipartite`, `ring`, `hub`, `blocks`."""
    F = np.zeros((n, n), dtype=int)
    if kind == "bipartite":
        h = n // 2
        for i in range(n):
            for j in range(n):
                if (i < h) != (j < h):
                    F[i, j] = 1
    elif kind == "ring":
        for i in range(n):
            F[i, (i + 1) % n] = F[(i + 1) % n, i] = 1
    elif kind == "hub":
        F[0, 1:] = 1
        F[1:, 0] = 1
    elif kind == "blocks":
        b = 4 if n == 8 else 3
        for i in range(n):
            for j in range(n):
                if i != j:
                    if i // b == j // b:
                        F[i, j] = 3
                    elif abs(i // b - j // b) == 1:
                        F[i, j] = 1
    else:
        raise ValueError(f"unbekannte symmetrische Familie {kind!r}")
    return F
