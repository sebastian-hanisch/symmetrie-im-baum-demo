"""Symmetrien, Zählung und Baum auf einer Instanz, Vergleiche über feste Instanzen, Zufallsprobe und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text).

Alle Aussagen gelten für die gerechneten Instanzen, die sechs erfundenen Familien der Reihe und die vier erfundenen symmetrischen Familien. **Knoten** sind die bewerteten Kinder des Baums (Gilmore–Lawler-Knotenschranken, Stück 8);
sie sind ganzzahlig und auf jedem Rechner gleich. **Verhältnis** = Knoten ohne / Knoten mit. Zeiten sind Sekunden dieser Python-Fassung auf diesem Rechner (schwanken von Lauf zu Lauf um das Doppelte) und stehen nie in Tests.
Der **Anfangswert** ist die beste von 200 Abstiegen aus Zufallsstarts (Stück 3), oder keiner."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, replace

import numpy as np

import syb_bounds as B
import syb_constants as C
import syb_landscape as L
import syb_symmetry as S
from syb_instance import hand_instance, make_instance
from syb_rng import SplitMix64


@dataclass(frozen=True)
class Settings:
    family: str = C.DEFAULT_FAMILY
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    place: bool = C.DEFAULT_PLACE
    twins: bool = C.DEFAULT_TWINS
    start: bool = C.DEFAULT_START

    @property
    def variant(self) -> str:
        return "both" if self.place and self.twins else "place" if self.place else "twins" if self.twins else "plain"


# ----------------------------------------------------------------------------- Formatierung

def de(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma und typografischem Minuszeichen."""
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def pct(x: float, digits: int = 0) -> str:
    return de(x, digits) + " %"


def fam(name: str) -> str:
    return C.ALL_FAMILY_NAMES.get(name, name)


def num(x: float) -> str:
    """Ganze Zahl ohne Nachkommastelle, sonst eine Stelle: 27 / 27,5 / −12,1."""
    return str(int(round(x))) if abs(x - round(x)) < 1e-9 else de(x, 1)


def count(x: float) -> str:
    """Anzahl mit Leerzeichen als Tausendertrenner: 1200 → „1 200“."""
    return C.n_text(int(round(x)))


def secs(x: float) -> str:
    """Sekunden mit sinnvoller Stellenzahl: 0,016 s / 0,42 s / 5,1 s / 31 s."""
    if x < 0.1:
        return de(x, 3) + " s"
    if x < 10:
        return de(x, 2 if x < 1 else 1) + " s"
    return de(x, 0) + " s"


def ratio(a: float, b: float) -> float:
    """a / b (Knoten ohne durch Knoten mit); 1 bei 0 / 0."""
    return a / b if b else (1.0 if not a else float("inf"))


# ----------------------------------------------------------------------------- Instanzen

def make_flow_instance(family: str, n: int, seed: int):
    """Instanz einer der zehn Familien: die sechs der Reihe nach Seed, die vier symmetrischen deterministisch (das Raster der Größe n; der Seed zählt nicht)."""
    inst = make_instance("uniform" if family in C.SYM_FAMILIES else family, n, seed)
    if family in C.SYM_FAMILIES:
        return replace(inst, F=S.make_flow(family, n).astype(inst.F.dtype), family=family, nets=())
    return inst


def optimal_set(F, D, G: list, A, n: int) -> dict:
    """Optimum, Zahl der optimalen Anordnungen und ihrer Bahnen unter G (und unter G × A, wenn die Rechnung klein genug bleibt); nur n ≤ 9."""
    P = L.all_perms(n)
    c = L.costs_of(P, F, D)
    opt = int(c.min())
    O = P[c == opt].tolist()
    seen, orbits_G = set(), 0
    for p in map(tuple, O):
        if p in seen:
            continue
        orbits_G += 1
        seen |= {tuple(g[a] for a in p) for g in G}
    out = {"opt": opt, "n_opt": len(O), "n_opt_orbits_G": orbits_G, "n_opt_orbits_GA": None}
    if A is not None and len(O) * len(G) * len(A) <= 2_000_000:
        inv = []
        for h in A:
            x = [0] * n
            for a, b in enumerate(h):
                x[b] = a
            inv.append(x)
        seen, k = set(), 0
        for p in map(tuple, O):
            if p in seen:
                continue
            k += 1
            for g in G:
                for x in inv:
                    seen.add(tuple(g[p[x[a]]] for a in range(n)))
        out["n_opt_orbits_GA"] = k
    return out


def symmetry_data(inst) -> dict:
    """Platzgruppe (geprüft an D), Bauteil-Automorphismen (gezählt, bei kleiner Zahl als Liste), Zwillinge und die Zahl der Anordnungen bis auf Symmetrie."""
    F, D = inst.F.astype(int), inst.D.astype(int)
    n = inst.n
    G = S.grid_group(inst.rows, inst.cols)
    assert all(S.is_symmetry(D, g) for g in G)
    cnt, full = S.aut_count(F)
    A = S.aut_group(F) if full else None
    tw = S.twin_classes(F)
    return {"G": G, "orbits_places": S.place_orbits(G, n), "aut": cnt, "aut_full": full, "A": A, "twins": tw, "twin_product": int(np.prod([math.factorial(len(c)) for c in tw])) if tw else 1,
            "arrangements": math.factorial(n), "orbits_G": math.factorial(n) // len(G), "orbits_GA": S.burnside_orbits(G, A) if A is not None else None,
            "orbits_brute": S.orbits_bruteforce(G, A, n) if (A is not None and n <= C.BRUTE_MAX_N) else None}


def tree_runs(inst, sym: dict, start: bool, variants=C.VARIANTS) -> tuple:
    """Der Baum in den gewählten Varianten; Anfangswert die beste von 200 Abstiegen (oder keiner). Rückgabe: (Läufe je Variante, Anfangswert)."""
    F, D = inst.F.astype(int), inst.D.astype(int)
    ub = int(B.best_found(F, D, 0, C.STARTS)[0]) if start else None
    runs = {}
    for v in variants:
        runs[v] = S.solve(F, D, incumbent=ub, group=sym["G"] if v in ("place", "both") else None, twins=sym["twins"] if v in ("twins", "both") else None)
    return runs, ub


def instance_data(s: Settings) -> dict:
    """Alles zu einer Instanz: Symmetrien, Zählung, optimale Anordnungen (n ≤ 9) und der Baum in allen vier Varianten."""
    inst = make_flow_instance(s.family, s.n, s.seed)
    F, D = inst.F.astype(int), inst.D.astype(int)
    sym = symmetry_data(inst)
    v = {"inst": inst, **sym}
    if s.n in C.EXACT_SIZES:
        v.update(optimal_set(F, D, sym["G"], sym["A"], s.n))
        v["opt_perm"] = [int(x) for x in L.all_perms(s.n)[int(np.argmin(L.costs_of(L.all_perms(s.n), F, D)))]]
    ub = int(B.best_found(F, D, s.seed, C.STARTS)[0])
    v["ub"] = ub
    runs = {}
    for var in C.VARIANTS:
        runs[var] = S.solve(F, D, incumbent=ub if s.start else None, group=sym["G"] if var in ("place", "both") else None, twins=sym["twins"] if var in ("twins", "both") else None)
    v["runs"] = runs
    return v


def hand_data() -> dict:
    """Vier Plätze auf einer Zeile (Stück 3, 5, 8): Gruppen, Bahnen, optimale Anordnungen und Baum in allen vier Varianten, mit und ohne Anfangswert 6."""
    inst = hand_instance(C.HAND_GAP_FLOWS, *C.HAND_GAP_GRID)
    F, D = inst.F.astype(int), inst.D.astype(int)
    G, A, tw = S.grid_group(1, 4), S.aut_group(F), S.twin_classes(F)
    opt = optimal_set(F, D, G, A, 4)
    P = L.all_perms(4)
    out = {"inst": inst, "G": G, "A": A, "twins": tw, "arrangements": 24, "orbits_G": 12, "orbits_GA": S.burnside_orbits(G, A), "orbits_brute": S.orbits_bruteforce(G, A, 4), **opt,
           "opt_perm": [int(x) for x in P[int(np.argmin(L.costs_of(P, F, D)))]]}
    for inc, key in ((6, "with"), (None, "without")):
        out[key] = {v: S.solve(F, D, incumbent=inc, group=G if v in ("place", "both") else None, twins=tw if v in ("twins", "both") else None)["nodes"] for v in C.VARIANTS}
    return out


# ----------------------------------------------------------------------------- Zeilen der Vergleiche

def series_row(family: str, n: int, seed: int) -> dict:
    """Eine Instanz der Reihe: Gruppen, Zählung, optimale Anordnungen (n ≤ 9) und der Baum ohne und mit Orbit-Beschneiden, mit und ohne Anfangswert (ohne nur n ≤ 9)."""
    inst = make_flow_instance(family, n, seed)
    F, D = inst.F.astype(int), inst.D.astype(int)
    sym = symmetry_data(inst)
    ub = int(B.best_found(F, D, seed, C.STARTS)[0])
    row = {"family": family, "n": n, "seed": seed, "G": len(sym["G"]), "aut": sym["aut"], "aut_full": sym["aut_full"], "orbits_G": sym["orbits_G"], "orbits_GA": sym["orbits_GA"], "ub": ub,
           "plain": S.solve(F, D, incumbent=ub), "place": S.solve(F, D, incumbent=ub, group=sym["G"])}
    if n <= 9:
        row["plain0"] = S.solve(F, D, incumbent=None)
        row["place0"] = S.solve(F, D, incumbent=None, group=sym["G"])
        row.update(optimal_set(F, D, sym["G"], sym["A"], n))
    return row


def series_jobs(n: int) -> list:
    return [(f, n, s) for f in C.FAMILIES for s in range(C.FIXED_SEED0, C.FIXED_SEED0 + C.SEEDS[n])]


def series_sweep(family: str, n: int) -> list:
    return [series_row(*job) for job in series_jobs(n) if job[0] == family]


def pooled(by_family: dict) -> list:
    return [r for f in C.FAMILIES if f in by_family for r in by_family[f]]


def struct_row(kind: str, n: int) -> dict:
    """Eine Instanz einer symmetrischen Familie: Gruppen, Zwillingsklassen, Burnside (wenn die Gruppe klein genug ist) und der Baum in allen vier Varianten (Anfangswert: beste von 200 Abstiegen)."""
    inst = make_flow_instance(kind, n, C.FIXED_SEED0)
    F, D = inst.F.astype(int), inst.D.astype(int)
    sym = symmetry_data(inst)
    ub = int(B.best_found(F, D, C.FIXED_SEED0, C.STARTS)[0])
    row = {"kind": kind, "n": n, "G": len(sym["G"]), "aut": sym["aut"], "aut_full": sym["aut_full"], "twin_classes": [len(c) for c in sym["twins"]], "twin_product": sym["twin_product"],
           "orbits_G": sym["orbits_G"], "orbits_GA": sym["orbits_GA"], "ub": ub}
    for v in C.VARIANTS:
        row[v] = S.solve(F, D, incumbent=ub, group=sym["G"] if v in ("place", "both") else None, twins=sym["twins"] if v in ("twins", "both") else None)
    return row


def combo_probe(count_per_size: int = C.PROBE_COUNT) -> dict:
    """Zufallsprobe der Kombination: zufällige Flussmatrizen mit erzwungenen Zwillingspaaren (n = 6 und 8, abwechselnd zwei und ein Paar), Optimum aus der Aufzählung, Baum **ohne** Anfangswert in allen vier Varianten.
    Rückgabe: Zahl der Instanzen, je Variante die Zahl der verfehlten Optima und die Knoten insgesamt."""
    rng = SplitMix64(C.PROBE_SEED)
    total = 0
    bad = {v: 0 for v in C.VARIANTS}
    nodes = {v: 0 for v in C.VARIANTS}
    for n in C.PROBE_SIZES:
        rows, cols = C.GRID[n]
        G = S.grid_group(rows, cols)
        D = make_instance("uniform", n, 1).D.astype(int)
        P = L.all_perms(n)
        for t in range(count_per_size):
            F = np.zeros((n, n), dtype=int)
            for i in range(n):
                for j in range(i + 1, n):
                    F[i, j] = F[j, i] = rng.below(6)
            for i, j in C.PROBE_PAIRS[t % 2]:
                for k in range(n):
                    if k not in (i, j):
                        F[j, k] = F[k, j] = F[i, k]
            tw = S.twin_classes(F)
            opt = int(L.costs_of(P, F, D).min())
            total += 1
            for v in C.VARIANTS:
                r = S.solve(F, D, incumbent=None, group=G if v in ("place", "both") else None, twins=tw if v in ("twins", "both") else None)
                nodes[v] += r["nodes"]
                bad[v] += r["best"] != opt
    return {"total": total, "bad": bad, "nodes": nodes}


# ----------------------------------------------------------------------------- Auswertungen

def node_ratios(rows: list, a: str = "plain", b: str = "place") -> list:
    return [ratio(r[a]["nodes"], r[b]["nodes"]) for r in rows]


def ratio_stats(rows: list, a: str = "plain", b: str = "place") -> dict:
    rs = node_ratios(rows, a, b)
    return {"count": len(rows), "median": float(np.median(rs)), "min": float(min(rs)), "max": float(max(rs)), "nodes_a": sum(r[a]["nodes"] for r in rows), "nodes_b": sum(r[b]["nodes"] for r in rows),
            "median_a": float(np.median([r[a]["nodes"] for r in rows])), "median_b": float(np.median([r[b]["nodes"] for r in rows])), "same_best": sum(r[a]["best"] == r[b]["best"] for r in rows)}


def aut_trivial(rows: list) -> int:
    return sum(r["aut"] == 1 for r in rows)


def optimal_orbit_stats(rows: list) -> dict:
    """Zeilen mit bekanntem Optimum und trivialer Bauteilgruppe: in wie vielen ist die Zahl der optimalen Anordnungen gleich |G| mal der Zahl ihrer Bahnen?"""
    rs = [r for r in rows if "n_opt" in r and r["aut"] == 1]
    return {"count": len(rs), "exact": sum(r["n_opt"] == r["G"] * r["n_opt_orbits_G"] for r in rs), "median": float(np.median([r["n_opt"] for r in rs])) if rs else float("nan"), "max": max((r["n_opt"] for r in rs), default=0)}


# ----------------------------------------------------------------------------- Verdikte

def _head(s: Settings, v: dict) -> str:
    inst = v["inst"]
    return f"Familie **{fam(s.family)}**, {s.n} Bauteile, Raster {inst.rows}×{inst.cols}, Seed {s.seed}"


def plural(k: int, one: str, many: str) -> str:
    """„1 Bahn“ / „4 Bahnen“."""
    return f"{count(k)} {one if k == 1 else many}"


def _start(s: Settings) -> str:
    return "Anfangswert beste von 200 Abstiegen" if s.start else "ohne Anfangswert"


def verdict_core(s: Settings, v: dict):
    """Die Kernfrage: wie viele Anordnungen sind gleich, und was spart das im Baum?"""
    runs = v["runs"]
    plain, sel = runs["plain"], runs[s.variant]
    g = len(v["G"])
    same = plain["best"] == sel["best"]
    r = ratio(plain["nodes"], sel["nodes"])
    kind = "success" if same else "error"
    parts = [f"{_head(s, v)}: {g} Platzsymmetrien, die Anordnungen fallen in {count(v['orbits_G'])} Bahnen der Größe {g} (von {count(v['arrangements'])})"]
    if v["aut"] > 1:
        parts.append(f"die Flüsse haben {count(v['aut'])}{'' if v['aut_full'] else ' oder mehr'} Automorphismen" + (f", {count(v['orbits_GA'])} Bahnen unter Plätzen und Bauteilen" if v["orbits_GA"] is not None else ""))
    else:
        parts.append("die Flüsse haben keine Symmetrie (nur die Identität)")
    if s.variant == "plain":
        tree = f"Baum ohne Symmetrie ({_start(s)}): {count(plain['nodes'])} Knoten, bester Wert {num(plain['best'])}. Mit Orbit-Beschneiden wären es {count(runs['place']['nodes'])} Knoten (Verhältnis {de(ratio(plain['nodes'], runs['place']['nodes']), 2)})."
    else:
        tree = (f"Baum ({C.VARIANT_NAMES[s.variant]}, {_start(s)}): {count(sel['nodes'])} Knoten gegen {count(plain['nodes'])} ohne Symmetrie (Verhältnis {de(r, 2)}{'; Obergrenze der Platzsymmetrie ' + str(g) if s.variant == 'place' else ''}), "
                f"{count(sel['skipped'])} Kinder übersprungen; bester Wert {num(sel['best'])} " + ("**wie ohne Symmetrie**." if same else "**anders als ohne Symmetrie: das Optimum ging verloren!**") + ("" if not (plain['capped'] or sel['capped']) else f" Obergrenze von {count(C.NODE_CAP)} Knoten erreicht: nicht zu Ende gerechnet."))
    return kind, "; ".join(parts) + ". " + tree + " Eine Instanz, kein Befund über die Familie."


def verdict_group(s: Settings, v: dict):
    g = v["G"]
    orbs = v["orbits_places"]
    return "info", (f"{_head(s, v)}: Das {v['inst'].rows}×{v['inst'].cols}-Raster hat **{len(g)}** Symmetrien der Abstände (geprüft an D); die {s.n} Plätze fallen in {len(orbs)} Bahnen ({', '.join(str(len(o)) for o in orbs)} Plätze). "
                    f"Eine Anordnung hat {len(g)} gleich teure Bilder; {count(v['orbits_G'])} Anordnungen bleiben übrig, {count(v['arrangements'])} sind es roh (Spiegelbilder zählen mit, wie in Stück 1).")


def verdict_count(s: Settings, v: dict):
    parts = [f"{_head(s, v)}: {count(v['arrangements'])} Anordnungen, {count(v['orbits_G'])} bis auf die Platzsymmetrie (n!/{len(v['G'])})"]
    if v["orbits_GA"] is not None:
        parts.append(f"{count(v['orbits_GA'])} bis auf Plätze und Bauteile (Burnside, {plural(v['aut'], 'Automorphismus', 'Automorphismen')} der Flüsse)" + (f"; die Aufzählung findet {count(v['orbits_brute'])}: " + ("gleich" if v["orbits_brute"] == v["orbits_GA"] else "**ungleich**") if v["orbits_brute"] is not None else ""))
    else:
        parts.append(f"Burnside nicht gerechnet: mehr als {count(C.AUT_CAP)} Automorphismen der Flüsse (Zählgrenze); Zwillingsklassen {', '.join(str(len(c)) for c in v['twins']) or 'keine'}, mindestens {count(v['twin_product'])} Automorphismen")
    if "opt" in v:
        parts.append(f"{count(v['n_opt'])} Anordnungen sind optimal (Kosten {num(v['opt'])}), in {plural(v['n_opt_orbits_G'], 'Bahn', 'Bahnen')} unter den Plätzen" + (f" und {count(v['n_opt_orbits_GA'])} unter Plätzen und Bauteilen" if v["n_opt_orbits_GA"] is not None else ""))
    return "info", "; ".join(parts) + "."


def verdict_hand(h: dict):
    w, wo = h["with"], h["without"]
    return "info", (f"Vier Plätze auf einer Zeile (Abstände 1 bis 3), Fluss A–C, A–D, B–C, B–D je 1: {h['arrangements']} Anordnungen, **{h['n_opt']}** davon kosten {h['opt']} (das Optimum). Platzsymmetrien {len(h['G'])} (Spiegelung), Automorphismen der Flüsse {len(h['A'])} (die Symmetrien des Vierzyklus), "
                    f"Zwillinge {{A, B}} und {{C, D}}. Bahnen unter den Plätzen: {h['orbits_G']}, unter Plätzen und Bauteilen: **{h['orbits_GA']}** (Burnside; die Aufzählung findet {h['orbits_brute']}), davon {h['n_opt_orbits_GA']} optimal. "
                    f"Baum mit Anfangswert 6: {w['plain']} Knoten ohne, **{w['place']}** mit Orbit-Beschneiden, {w['twins']} mit Zwillingen, {w['both']} mit beidem; ohne Anfangswert {wo['plain']} / {wo['place']} / {wo['twins']} / {wo['both']}.")


def verdict_series(rows_by_n: dict, start: bool = True):
    parts = []
    for n in sorted(rows_by_n):
        rs = rows_by_n[n]
        a, b = ("plain", "place") if start else ("plain0", "place0")
        if a not in rs[0]:
            continue
        st = ratio_stats(rs, a, b)
        parts.append(f"n = {n} ({len(rs)} Instanzen, |G| = {rs[0]['G']}): Verhältnis im Median {de(st['median'], 2)} (kleinstes {de(st['min'], 2)}, größtes {de(st['max'], 2)}), Knoten im Median {count(st['median_a'])} → {count(st['median_b'])}, bester Wert gleich in {st['same_best']} von {len(rs)}")
    triv = {n: f"{aut_trivial(rows_by_n[n])} von {len(rows_by_n[n])}" for n in sorted(rows_by_n)}
    return "info", ("; ".join(parts) + f". Die Flüsse haben keine Symmetrie (|Aut(F)| = 1) in {', '.join(f'{v} (n = {n})' for n, v in triv.items())}." + ("" if start else " Ohne Anfangswert ist der Gewinn kleiner und streut stärker, weil der Baum zuerst eine Lösung finden muss."))


def verdict_optimal(rows_by_n: dict):
    parts = []
    for n in sorted(rows_by_n):
        o = optimal_orbit_stats(rows_by_n[n])
        if o["count"]:
            parts.append(f"n = {n}: in {o['exact']} von {o['count']} Instanzen ohne Bauteilsymmetrie ist die Zahl der optimalen Anordnungen genau |G| mal die Zahl ihrer Bahnen (Median {num(o['median'])} optimale Anordnungen, größte {o['max']})")
    return "info", "; ".join(parts) + ". Die Platzsymmetrien wirken frei auf die Anordnungen: jede Bahn hat genau |G| Anordnungen."


def verdict_struct(rows: list):
    out = []
    for r in rows:
        if r["n"] == max(x["n"] for x in rows):
            cells = " / ".join(f"{count(r[v]['nodes'])}{'+' if r[v]['capped'] else ''}" for v in C.VARIANTS)
            out.append(f"„{fam(r['kind'])}“: {cells}")
    n = max(r["n"] for r in rows)
    pairs = [(r, v) for r in rows for v in C.VARIANTS[1:] if not (r["plain"]["capped"] or r[v]["capped"])]
    wrong = sum(r[v]["best"] != r["plain"]["best"] for r, v in pairs)
    capped = sum(r["plain"]["capped"] for r in rows)
    return "info", (f"Knoten bei n = {n} (ohne / Plätze / Zwillinge / beides; „+“: Obergrenze von {count(C.NODE_CAP)} Knoten erreicht, nicht zu Ende gerechnet): " + "; ".join(out) + f". Bester Wert verschieden zwischen den Varianten in {wrong} von {len(pairs)} Vergleichen (nur zu Ende gerechnete Läufe); ohne Symmetrie nicht zu Ende gerechnet: {capped} Läufe. "
                    "Gilmore–Lawler ist bei „Ring“ und „Nabe“ so scharf, dass der Baum schon ohne Symmetrie klein bleibt.")


def verdict_probe(p: dict):
    bad = sum(p["bad"].values())
    nodes = " / ".join(count(p["nodes"][v]) for v in C.VARIANTS)
    kind = "success" if bad == 0 else "error"
    return kind, (f"{count(p['total'])} zufällige Flussmatrizen mit erzwungenen Zwillingspaaren (n = {', '.join(map(str, C.PROBE_SIZES))}), Baum ohne Anfangswert, Optimum aus der Aufzählung: verfehlte Optima ohne / Plätze / Zwillinge / beides: "
                  + " / ".join(str(p["bad"][v]) for v in C.VARIANTS) + f"; Knoten insgesamt {nodes}. " + ("Keine Variante verfehlt das Optimum; das ist **kein Beweis**, dass die einfache Kombination (kleinster Platz je Bahn, aufsteigende Zwillingsplätze) allgemein gültig ist." if bad == 0 else "**Mindestens eine Variante verfehlt das Optimum: diese Kombination ist ungültig.**"))
