"""Abbildungen: sie entstehen für jede Eingabe, Achsen sind gesperrt, Daten stimmen mit den Werten überein; PDF-Export."""

import pytest

import syb_constants as C
import syb_evaluation as E
import syb_instance as I
import syb_symmetry as S
import syb_visualization as V
from oracle import make_series_row, make_struct_row, run
from syb_pdf_export import build_pdf


def _locked(fig):
    return fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


@pytest.fixture(scope="module")
def v8():
    return E.instance_data(E.Settings())


def test_arrangement_for_every_family_and_size():
    for fam in C.ALL_FAMILIES:
        for n in (4, 6, 9, 12):
            inst = E.make_flow_instance(fam, n, 3)
            fig = V.build_arrangement(inst, list(range(n)), fam)
            assert len(fig.data[-1].x) == n and _locked(fig)


def test_places_chart_colors_by_orbit(v8):
    fig = V.build_places(v8["inst"], v8["G"], v8["orbits_places"])
    colors = list(fig.data[0].marker.color)
    assert len(colors) == 8 and len(set(colors)) == 2 and colors[0] == colors[3] == colors[4] == colors[7] != colors[1] and "4 Symmetrien, 2 Bahnen" in fig.layout.title.text and _locked(fig)


def test_images_chart_has_one_panel_per_symmetry(v8):
    fig = V.build_images(v8["inst"], v8["opt_perm"], v8["G"])
    assert len(fig.data) == 2 * len(v8["G"]) and fig.layout.annotations[0].text == "Original" and fig.layout.annotations[3].text == "Bild 3"
    sq = E.instance_data(E.Settings(n=9))
    assert len(V.build_images(sq["inst"], sq["opt_perm"], sq["G"]).data) == 16


def test_node_and_depth_charts(v8):
    fig = V.build_node_bars(v8["runs"], "place")
    assert list(fig.data[0].y) == [v8["runs"][k]["nodes"] for k in C.VARIANTS] and list(fig.data[0].marker.line.width) == [0, 3, 0, 0] and _locked(fig)
    d = V.build_depth(v8["runs"])
    assert [t.name for t in d.data] == [C.VARIANT_NAMES["plain"], C.VARIANT_NAMES["place"]] and list(d.data[0].y) == list(v8["runs"]["plain"]["depth"]) and _locked(d)
    capped = {k: run(10, capped=(k == "plain")) for k in C.VARIANTS}
    assert V.build_node_bars(capped, "plain").data[0].text[0] == "10+"


def test_ratio_chart_shows_the_group_size_line():
    rows = {8: [make_series_row(8, 400, 100, plain0=700, place0=250), make_series_row(8, 240, 60, plain0=300, place0=100)], 9: [make_series_row(9, 8000, 1000, g=8)]}
    fig = V.build_ratio_chart(rows, E.ratio_stats, E.node_ratios)
    boxes = [t for t in fig.data if t.type == "box"]
    assert [list(b.y) for b in boxes] == [[4.0, 4.0], [8.0]] and list(fig.data[-1].y) == [4, 8] and fig.data[-1].name == "Gruppengröße |G|"
    assert len([t for t in V.build_ratio_chart(rows, E.ratio_stats, E.node_ratios, start=False).data if t.type == "box"]) == 1


def test_struct_and_counts_charts(v8):
    rows = [make_struct_row("bipartite", 12, 400000, 133696, 2120, 1334), make_struct_row("blocks", 9, 300, 50, 90, 20)]
    fig = V.build_struct_bars(rows)
    assert [t.name for t in fig.data] == [C.VARIANT_NAMES[v] for v in C.VARIANTS] and list(fig.data[0].x) == ["Zwei Hälften, n = 12", "Blöcke, n = 9"] and list(fig.data[3].y) == [1334, 20] and fig.layout.yaxis.type == "log"
    c = V.build_counts(v8)
    assert list(c.data[0].y) == [40320, 10080, 10080] and len(c.data[0].x) == 3 and _locked(c)
    big = E.instance_data(E.Settings(family="hub", n=12, place=False))
    assert len(V.build_counts(big).data[0].y) == 2


def test_pdf_export(v8):
    pdf = build_pdf(E.Settings(), v8)
    assert pdf[:4] == b"%PDF" and len(pdf) > 1500
    s = E.Settings(family="bipartite", n=6, twins=True, start=False)
    assert build_pdf(s, E.instance_data(s))[:4] == b"%PDF"
