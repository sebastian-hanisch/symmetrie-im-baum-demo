"""Konstanten: Größen, Raster, Familien der Flussmatrix (sechs der Reihe und vier symmetrische), Symmetrien und Baum, feste Reihen der Experimente, Farben und Presets."""

SIZES = (4, 6, 8, 9, 12)                              # Regler „Bauteile“ (n = 4: Raster 2×2; das Handbeispiel „vier Plätze auf einer Zeile“ steht fest in Experiment 1)
EXACT_SIZES = (4, 6, 8, 9)                            # alle n! Anordnungen werden aufgezählt
BRUTE_MAX_N = 8                                       # Bahnen durch Aufzählung (Gegenprobe zu Burnside) nur bis hierher live
HEAVY_N = 12                                          # ab hier läuft die Rechnung nur auf Knopfdruck (ohne Beschneiden bis etwa 45 s)
DEFAULT_N = 8
GRID = {4: (2, 2), 6: (2, 3), 8: (2, 4), 9: (3, 3), 12: (3, 4), 16: (4, 4)}   # Plätze als Raster (Zeilen, Spalten), Abstand = Manhattan
SEED_MAX, DEFAULT_SEED = 999999, 48
FIXED_SEED0 = 100000                                  # feste Instanzen: Seeds ab 100000 (nie ein einzelner Seed als Befund)
SEEDS = {6: 5, 8: 5, 9: 3, 12: 3}                     # Seeds je Familie der Reihe: 30 / 30 / 18 / 18 Instanzen
ROW_SIZES = (6, 8, 9, 12)                             # Größen der festen Reihen
STRUCT_SIZES = (6, 8, 9, 12)                          # Größen der symmetrischen Familien (je Familie und Größe eine Instanz)
NODE_CAP = 400_000                                    # Obergrenze der Knoten des Baums
STARTS = 200                                          # Abstiege aus Zufallsstarts (Anfangswert des Baums)
AUT_CAP = 50_000                                      # Zählgrenze von |Aut(F)| (und größte Gruppe, die als Liste gehalten wird)
PROBE_SIZES = (6, 8)                                  # Größen der Zufallsprobe der Kombination
PROBE_COUNT = 150                                     # Zufallsinstanzen je Größe (insgesamt 300)
PROBE_SEED = 7
PROBE_PAIRS = (((0, 1), (2, 3)), ((0, 1),))           # erzwungene Zwillingspaare, abwechselnd

# --- Symmetrien und Baum --------------------------------------------------------------------------------------------------------------------------
TREE_ART = "glb"                                      # Knotenschranke: Gilmore–Lawler (Stück 3)
VARIANTS = ("plain", "place", "twins", "both")
VARIANT_NAMES = {"plain": "ohne Symmetrie", "place": "Plätze (Orbit-Beschneiden)", "twins": "Zwillinge (Ordnung)", "both": "Plätze und Zwillinge"}
VARIANT_SHORT = {"plain": "ohne", "place": "Plätze", "twins": "Zwillinge", "both": "beides"}
DEFAULT_PLACE = True
DEFAULT_TWINS = False
DEFAULT_START = True                                  # Anfangswert = beste von 200 Abstiegen
SYM_FAMILIES = ("bipartite", "ring", "hub", "blocks")
SYM_FAMILY_NAMES = {"bipartite": "Zwei Hälften", "ring": "Ring", "hub": "Nabe", "blocks": "Blöcke"}
SYM_FAMILY_HELP = {
    "bipartite": "Alle Flüsse 1 zwischen der ersten und der zweiten Hälfte der Bauteile, sonst keine: viele gleiche Bauteile (Zwillinge).",
    "ring": "Fluss 1 zwischen Nachbarn auf einem Ring: die Automorphismen sind Drehungen und Spiegelungen des Rings.",
    "hub": "Ein Bauteil (die Nabe) hat Fluss 1 zu allen anderen: alle übrigen sind Zwillinge.",
    "blocks": "Blöcke zu je 3 (n = 8: 4) Bauteilen, Fluss 3 im Block und 1 zwischen aufeinanderfolgenden Blöcken: Zwillinge im Block.",
}
ALL_FAMILIES = ("netlist", "uniform", "sparse", "cluster", "star", "skewed") + SYM_FAMILIES

FAMILIES = ("netlist", "uniform", "sparse", "cluster", "star", "skewed")
DEFAULT_FAMILY = "cluster"
FAMILY_NAMES = {"netlist": "Netzliste", "uniform": "Gleichverteilt", "sparse": "Dünn besetzt", "cluster": "Zwei Cluster", "star": "Stern", "skewed": "Wenige starke Flüsse"}
FAMILY_HELP = {
    "netlist": "Netzliste aus Dreiergruppen (IC, Kondensator, Widerstand), jedes Paar in einem Netz zählt Fluss 1: die Familie aus Stück 1.",
    "uniform": "Jedes Paar von Bauteilen hat einen zufälligen Fluss von 0 bis 9, gleichverteilt: dichte Matrix ohne Struktur.",
    "sparse": "Nur drei von zehn Paaren haben Fluss (1 bis 9), die übrigen keinen: dünn besetzt ohne weitere Struktur.",
    "cluster": "Zwei Gruppen von Bauteilen: innerhalb einer Gruppe starker Fluss (8 bis 10), zwischen den Gruppen schwacher (0 bis 2).",
    "star": "Ein Bauteil (die Nabe) hat starken Fluss (1 bis 9) zu allen anderen; zwischen den übrigen höchstens 1.",
    "skewed": "Die Flüsse sind schief verteilt: viele Paare ohne oder mit kleinem Fluss, wenige mit sehr großem (bis 60).",
}

# Netzliste (wie in Stück 1 bis 5)
N_NETS_PER_COMPONENT = 1.5
NET_SIZES = (2, 3, 4)
NET_WEIGHTS = (5, 3, 2)
LOCAL_NET_PERCENT = 70
GROUP = 3
# Dünn besetzt, Cluster, Stern, schief (wie in Stück 2)
SPARSE_PERCENT = 30
UNIFORM_MAX = 9
CLUSTER_STRONG, CLUSTER_WEAK_MAX = 8, 2
SKEW_VALUES = (0, 1, 2, 4, 8, 16, 32, 60)
SKEW_WEIGHTS = (45, 22, 13, 8, 6, 3, 2, 1)           # ganzzahlige Gewichte (Summe 100), schweres Ende

HAND_FLOWS = ((0, 1, 5), (1, 2, 1))                   # Handbeispiel 1: drei Bauteile auf einer Zeile, Fluss A–B 5, B–C 1
HAND_GRID = (1, 3)
HAND_GAP_FLOWS = ((0, 2, 1), (0, 3, 1), (1, 2, 1), (1, 3, 1))   # Handbeispiel 3: vier Bauteile auf einer Zeile, A und B gegen C und D
HAND_GAP_GRID = (1, 4)
HAND_GRID_FLOWS = ((0, 1, 3), (0, 2, 1), (1, 3, 2), (2, 3, 4))  # Handbeispiel 2 (aus Stück 1): Raster 2×2
HAND_GRID_GRID = (2, 2)

ALL_FAMILY_NAMES = {**FAMILY_NAMES, **SYM_FAMILY_NAMES}
ALL_FAMILY_HELP = {**FAMILY_HELP, **SYM_FAMILY_HELP}
COLORS = {"best": "#2F6B65", "plain": "#9aa0a6", "place": "#4c78a8", "twins": "#b08a2e", "both": "#2F6B65", "bad": "#b34a4a", "line": "#4c78a8", "ok": "#2F6B65", "warn": "#b08a2e",
          "orbit": ["#4c78a8", "#b08a2e", "#2F6B65", "#8e6bb0", "#c0504d", "#9c755f"]}

_BASE = {"family": DEFAULT_FAMILY, "n": DEFAULT_N, "seed": DEFAULT_SEED, "place": DEFAULT_PLACE, "twins": DEFAULT_TWINS, "start": DEFAULT_START}
PRESETS = {
    "Standardfall: Plätze, acht Bauteile": dict(_BASE),
    "Quadrat: acht Symmetrien": dict(_BASE, n=9),
    "Zwölf Bauteile": dict(_BASE, n=12),
    "Ohne Anfangswert": dict(_BASE, start=False),
    "Zwei Hälften: Zwillinge": dict(_BASE, family="bipartite", n=9, twins=True, place=False),
    "Zwei Hälften: beides": dict(_BASE, family="bipartite", n=9, twins=True),
    "Blöcke": dict(_BASE, family="blocks", n=9, twins=True),
    "Vier Bauteile": dict(_BASE, n=4, family="uniform"),
}
PRESET_HELP = {
    "Standardfall: Plätze, acht Bauteile": "Acht Bauteile auf dem 2×4-Raster (vier Platzsymmetrien): der Baum wird mit Orbit-Beschneiden etwa auf ein Viertel verkleinert, der beste Wert bleibt gleich.",
    "Quadrat: acht Symmetrien": "Das 3×3-Raster hat acht Symmetrien: der Baum schrumpft etwa um den Faktor acht; die Plätze der Mitte und am Rand haben verschiedene Bahnen.",
    "Zwölf Bauteile": "Zwölf Bauteile auf dem 3×4-Raster: der Baum hat tausende Knoten; die Rechnung läuft nur auf Knopfdruck.",
    "Ohne Anfangswert": "Der Baum muss die erste Lösung selbst finden: der Gewinn durch Symmetrie ist kleiner und streut stärker.",
    "Zwei Hälften: Zwillinge": "Alle Bauteile einer Hälfte sind Zwillinge: die Ordnung der Zwillingsplätze spart hier mehr als die Platzsymmetrie.",
    "Zwei Hälften: beides": "Platzsymmetrie und Zwillingsordnung zusammen: die kleinste Zahl Knoten; die Kombination ist gemessen gültig, nicht bewiesen.",
    "Blöcke": "Drei Blöcke gleicher Bauteile: Zwillinge im Block, dazu die Spiegelung der Blockfolge.",
    "Vier Bauteile": "Vier Bauteile auf dem 2×2-Raster (acht Symmetrien): die ganze Aufzählung (24 Anordnungen) passt auf einen Bildschirm.",
}


def n_text(n: int) -> str:
    """Anzahl mit Leerzeichen als Tausendertrenner: 362880 → „362 880“."""
    return f"{n:,}".replace(",", " ")


assert set(PRESETS) == set(PRESET_HELP) and set(ALL_FAMILY_NAMES) == set(ALL_FAMILIES) == set(ALL_FAMILY_HELP) and set(VARIANT_NAMES) == set(VARIANTS) == set(VARIANT_SHORT)
assert all(p["n"] in SIZES and p["family"] in ALL_FAMILIES and 0 <= p["seed"] <= SEED_MAX for p in PRESETS.values())
assert all(r * c == n for n, (r, c) in GRID.items()) and sum(SKEW_WEIGHTS) == 100 and set(SIZES) <= set(GRID) and set(SEEDS) == set(ROW_SIZES)
