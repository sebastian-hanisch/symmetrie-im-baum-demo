"""PDF-Export des aktuellen Ergebnisses (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import syb_constants as C
from syb_evaluation import Settings, count, fam, num, ratio, secs

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "×": "x", "Δ": "Delta", "↔": "<->", "„": '"', "“": '"', "²": "2", "³": "3", "⁻": "-", "¹": "1", "½": "1/2", "⁴": "4", "∘": "o", "≈": "~"}


def _s(text) -> str:
    out = str(text).replace("**", "").replace("`", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings, v: dict) -> bytes:
    """`v`: das Ergebnis von `instance_data`."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Symmetrie im Baum"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    inst = v["inst"]
    start = "Anfangswert beste von 200 Abstiegen" if s.start else "ohne Anfangswert"
    pdf.multi_cell(0, 5, _s(f"Familie {fam(s.family)}, {s.n} Bauteile, {inst.rows}x{inst.cols}-Raster, Seed {s.seed}; Variante {C.VARIANT_NAMES[s.variant]}; {start}. Eine Instanz, kein Befund über die Familie. Erfundene Familien, eigene Fassung der Symmetriebrechung. "
                            "Knoten sind bewertete Kinder des Baums (Gilmore-Lawler); Zeiten sind Messungen dieser Fassung. Alles simuliert."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.multi_cell(0, 5, _s(f"Platzsymmetrien: {len(v['G'])}; Anordnungen: {count(v['arrangements'])} roh, {count(v['orbits_G'])} bis auf die Platzsymmetrie"
                            + (f", {count(v['orbits_GA'])} bis auf Plätze und Bauteile (Burnside)" if v["orbits_GA"] is not None else "") + f". Automorphismen der Flüsse: {count(v['aut'])}{'' if v['aut_full'] else ' oder mehr'}; Zwillingsklassen: "
                            + (", ".join(str(len(c)) for c in v["twins"]) or "keine") + "."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    for w, h in ((70, "Variante"), (35, "Knoten"), (35, "Verhältnis"), (30, "bester Wert")):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    plain = v["runs"]["plain"]
    for k in C.VARIANTS:
        r = v["runs"][k]
        pdf.cell(70, 5.5, _s(C.VARIANT_NAMES[k]), border=1)
        pdf.cell(35, 5.5, _s(count(r["nodes"]) + ("+" if r["capped"] else "")), border=1)
        pdf.cell(35, 5.5, _s(f"{ratio(plain['nodes'], r['nodes']):.2f}".replace(".", ",")), border=1)
        pdf.cell(30, 5.5, _s(num(r["best"])), border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: symmetrie-im-baum-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
