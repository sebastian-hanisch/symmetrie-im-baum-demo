"""Plotly-Abbildungen. Alle 2D-Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import syb_constants as C



def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=380, legend_below=True):
    legend = dict(orientation="h", yanchor="top", y=-0.22, x=0) if legend_below else dict(orientation="h", yanchor="bottom", y=1.02, x=0)
    fig.update_layout(height=height + (40 if legend_below else 0), margin=dict(l=10, r=10, t=50, b=10), legend=legend, plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_arrangement(inst, perm, title: str) -> go.Figure:
    """Die gerundete Anordnung: Bauteile auf den Plätzen, Verbindungen mit Fluss als Linien."""
    fig = go.Figure()
    xs, ys = inst.xy[:, 0].astype(float), -inst.xy[:, 1].astype(float)
    pos = [(xs[int(perm[i])], ys[int(perm[i])]) for i in range(inst.n)]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(symbol="square", size=36, color="rgba(150,150,150,0.18)", line=dict(width=1, color="rgba(150,150,150,0.5)")), hoverinfo="skip", showlegend=False))
    lx, ly = [], []
    for a in range(inst.n):
        for b in range(a + 1, inst.n):
            if inst.F[a, b]:
                lx += [pos[a][0], pos[b][0], None]
                ly += [pos[a][1], pos[b][1], None]
    fig.add_trace(go.Scatter(x=lx, y=ly, mode="lines", line=dict(width=1.5, color="rgba(76,120,168,0.35)"), hoverinfo="skip", name="Fluss"))
    fig.add_trace(go.Scatter(x=[q[0] for q in pos], y=[q[1] for q in pos], mode="markers+text", text=list(inst.names), textposition="middle center", showlegend=False, marker=dict(size=26, color=C.COLORS["best"]), textfont=dict(color="white", size=10)))
    fig.update_layout(title=title)
    fig.update_xaxes(visible=False, range=[xs.min() - 0.7, xs.max() + 0.7], scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, range=[ys.min() - 0.7, ys.max() + 0.7])
    return _base(fig, height=300)


def build_places(inst, G: list, orbits: list, title: str = "Plätze und ihre Bahnen") -> go.Figure:
    """Das Raster der Plätze (Nummer im Feld), je Bahn der Symmetriegruppe eine Farbe."""
    xy = inst.xy.astype(float)
    color_of = {}
    for k, orb in enumerate(orbits):
        for j in orb:
            color_of[j] = C.COLORS["orbit"][k % len(C.COLORS["orbit"])]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xy[:, 0], y=-xy[:, 1], mode="markers+text", text=[str(j + 1) for j in range(inst.n)], textposition="middle center", textfont=dict(color="white", size=12),
                             marker=dict(symbol="square", size=44, color=[color_of[j] for j in range(inst.n)]), hovertemplate="Platz %{text}<extra></extra>", showlegend=False))
    fig.update_xaxes(visible=False, range=[xy[:, 0].min() - 0.7, xy[:, 0].max() + 0.7], scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, range=[-xy[:, 1].max() - 0.7, -xy[:, 1].min() + 0.7])
    fig.update_layout(title=f"{title}: {len(G)} Symmetrien, {len(orbits)} Bahnen")
    return _base(fig, height=300)


def build_images(inst, perm, G: list, title: str = "Eine Anordnung und ihre gleich teuren Bilder") -> go.Figure:
    """Die |G| Bilder g∘p einer Anordnung (kleine Raster mit den Bauteilnamen); alle haben dieselben Kosten."""
    from syb_symmetry import images

    imgs = images(perm, G)
    k = len(imgs)
    cols = min(4, k)
    rows = -(-k // cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=["Original" if i == 0 else f"Bild {i}" for i in range(k)], horizontal_spacing=0.04, vertical_spacing=0.18)
    xy = inst.xy.astype(float)
    for idx, img in enumerate(imgs):
        r, c = divmod(idx, cols)
        fig.add_trace(go.Scatter(x=xy[:, 0], y=-xy[:, 1], mode="markers", marker=dict(symbol="square", size=26, color="rgba(150,150,150,0.18)", line=dict(width=1, color="rgba(150,150,150,0.5)")), hoverinfo="skip", showlegend=False), row=r + 1, col=c + 1)
        fig.add_trace(go.Scatter(x=[xy[img[i], 0] for i in range(inst.n)], y=[-xy[img[i], 1] for i in range(inst.n)], mode="markers+text", text=list(inst.names), textposition="middle center",
                                 marker=dict(size=20, color=C.COLORS["best"] if idx == 0 else C.COLORS["place"]), textfont=dict(color="white", size=9), hoverinfo="skip", showlegend=False), row=r + 1, col=c + 1)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(title=title)
    return _base(fig, height=170 * rows + 80)


def build_node_bars(runs: dict, selected: str, title: str = "Knoten des Baums") -> go.Figure:
    """Knoten je Variante (ohne, Plätze, Zwillinge, beides); die gewählte Variante ist umrandet."""
    ks = list(C.VARIANTS)
    fig = go.Figure(go.Bar(x=[C.VARIANT_NAMES[k] for k in ks], y=[runs[k]["nodes"] for k in ks], marker_color=[C.COLORS[k] for k in ks], marker_line=dict(width=[3 if k == selected else 0 for k in ks], color="#c0504d"),
                           text=[f"{runs[k]['nodes']:,}".replace(",", " ") + ("+" if runs[k]["capped"] else "") for k in ks], textposition="outside"))
    fig.update_layout(title=title, showlegend=False)
    fig.update_yaxes(title="bewertete Knoten", rangemode="tozero")
    return _base(fig, height=340, legend_below=False)


def build_depth(runs: dict, title: str = "Knoten je Tiefe des Baums") -> go.Figure:
    """Knoten je Tiefe (Zahl der schon gesetzten Bauteile) für ohne Symmetrie und mit Plätzen."""
    fig = go.Figure()
    for k in ("plain", "place"):
        d = runs[k]["depth"]
        fig.add_trace(go.Bar(x=[str(i + 1) for i in range(len(d))], y=list(d), name=C.VARIANT_NAMES[k], marker_color=C.COLORS[k]))
    fig.update_layout(title=title, barmode="group")
    fig.update_xaxes(title="gesetzte Bauteile")
    fig.update_yaxes(title="bewertete Knoten")
    return _base(fig, height=320)


def build_ratio_chart(rows_by_n: dict, ratio_stats, node_ratios, start: bool = True, title: str = "Verhältnis der Knoten ohne gegen mit Orbit-Beschneiden") -> go.Figure:
    """Je Größe die Verhältnisse aller Instanzen (Kästen) und die Gruppengröße (Linie)."""
    a, b = ("plain", "place") if start else ("plain0", "place0")
    fig = go.Figure()
    ns = [n for n in sorted(rows_by_n) if a in rows_by_n[n][0]]
    for n in ns:
        fig.add_trace(go.Box(y=node_ratios(rows_by_n[n], a, b), name=f"n = {n}", boxpoints="all", jitter=0.4, pointpos=0, marker_color=C.COLORS["place"], showlegend=False))
    fig.add_trace(go.Scatter(x=[f"n = {n}" for n in ns], y=[rows_by_n[n][0]["G"] for n in ns], mode="markers+lines", name="Gruppengröße |G|", line=dict(color="#c0504d", dash="dot"), marker=dict(symbol="diamond", size=12)))
    fig.update_layout(title=title)
    fig.update_yaxes(title="Verhältnis der Knoten", rangemode="tozero")
    return _base(fig, height=380)


def build_struct_bars(rows: list, title: str = "Knoten bei symmetrischen Flüssen") -> go.Figure:
    """Knoten je Familie und Größe in den vier Varianten (logarithmisch); „+“ heißt Obergrenze erreicht."""
    fig = go.Figure()
    labels = [f"{C.SYM_FAMILY_NAMES[r['kind']]}, n = {r['n']}" for r in rows]
    for v in C.VARIANTS:
        fig.add_trace(go.Bar(x=labels, y=[max(r[v]["nodes"], 1) for r in rows], name=C.VARIANT_NAMES[v], marker_color=C.COLORS[v]))
    fig.update_layout(title=title, barmode="group")
    fig.update_yaxes(type="log", title="bewertete Knoten (logarithmisch)")
    fig.update_xaxes(tickangle=-40)
    return _base(fig, height=460)


def build_counts(v: dict, title: str = "Anordnungen bis auf Symmetrie") -> go.Figure:
    """Zahl der Anordnungen roh, bis auf die Platzsymmetrie und (wenn gerechnet) bis auf Plätze und Bauteile; logarithmisch."""
    names = ["roh (n!)", f"bis auf Plätze (n!/{len(v['G'])})"]
    vals = [v["arrangements"], v["orbits_G"]]
    if v["orbits_GA"] is not None:
        names.append("bis auf Plätze und Bauteile")
        vals.append(v["orbits_GA"])
    fig = go.Figure(go.Bar(x=names, y=vals, marker_color=["#9aa0a6", C.COLORS["place"], C.COLORS["both"]][: len(vals)], text=[f"{x:,}".replace(",", " ") for x in vals], textposition="outside"))
    fig.update_layout(title=title, showlegend=False)
    fig.update_yaxes(type="log", title="Zahl der Anordnungen (logarithmisch)")
    return _base(fig, height=320, legend_below=False)
