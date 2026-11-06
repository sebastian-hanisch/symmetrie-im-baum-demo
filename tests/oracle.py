"""Hilfen für die Tests: künstliche Zeilen der festen Reihen mit bekannten Antworten (ORACLE-PLAYBOOK §5)."""


def run(nodes, best=100.0, capped=False, seconds=0.1, skipped=0):
    return {"nodes": nodes, "best": float(best), "capped": capped, "seconds": seconds, "skipped": skipped, "depth": (nodes,)}


def make_series_row(n, plain, place, g=4, family="cluster", seed=100000, plain0=None, place0=None, aut=1, best=100.0, place_best=None, n_opt=None, orbits=None):
    """Künstliche Zeile von `series_row`: Knoten ohne / mit Orbit-Beschneiden (mit Anfangswert; optional ohne), Gruppengröße `g`."""
    row = {"family": family, "n": n, "seed": seed, "G": g, "aut": aut, "aut_full": True, "orbits_G": 40320 // g, "orbits_GA": None, "ub": int(best), "plain": run(plain, best), "place": run(place, best if place_best is None else place_best)}
    if plain0 is not None:
        row["plain0"], row["place0"] = run(plain0, best), run(place0, best)
    if n_opt is not None:
        row.update({"opt": int(best), "n_opt": n_opt, "n_opt_orbits_G": orbits if orbits is not None else n_opt // g, "n_opt_orbits_GA": None})
    return row


def make_struct_row(kind, n, plain, place, twins, both, caps=(False, False, False, False), g=4, best=50.0):
    row = {"kind": kind, "n": n, "G": g, "aut": 1152, "aut_full": True, "twin_classes": [4, 4], "twin_product": 576, "orbits_G": 10080, "orbits_GA": 17, "ub": int(best)}
    for name, nodes, cap in zip(("plain", "place", "twins", "both"), (plain, place, twins, both), caps):
        row[name] = run(nodes, best, cap)
    return row
