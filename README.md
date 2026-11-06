# Symmetrie im Baum – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-symmetrie-im-baum-demo.streamlit.app/)** -->

Stück 13 von 15 (gelb, optional) der **Konzepte-Reihe „Anordnen: relaxieren und runden“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Konzepte-Seite der Reihe gibt es noch nicht). Der Baum stammt aus Stück [8, Branch and Bound](https://github.com/sebastian-hanisch/schranke-im-baum-demo), die Schranke aus Stück [3, Gilmore–Lawler](https://github.com/sebastian-hanisch/gilmore-lawler-demo); Stück [1](https://github.com/sebastian-hanisch/quadratische-zuordnung-demo) zählt Spiegelbilder noch „roh“. Burnside und Pólya allgemein stehen in der Abzählen-Linie ([Burnside und Pólya](https://github.com/sebastian-hanisch/burnside-polya-demo), [Isomorphieausschluss](https://github.com/sebastian-hanisch/isomorphieausschluss-demo)); hier ist es eine **Anwendung im Baum**.

## Warum dieses Problem

Spiegelt man ein Raster von Plätzen, bleiben alle Abstände gleich: jede Anordnung hat **gleich teure Bilder**, und der Baum aus Stück 8 prüft sie alle. Wie viele Anordnungen sind also „gleich“, und was spart es, nur eine je Klasse zu prüfen? Die Plätze haben Symmetrien (Spiegelungen, Drehungen), die Flüsse manchmal auch (gleiche Bauteile, „Zwillinge“). Das Stück **zählt** die Anordnungen bis auf Symmetrie (Burnside) und **nutzt** die Symmetrie im Baum (Orbit-Beschneiden, Zwillingsordnung).

Die Antwort dieser Messung: **Der Baum schrumpft um die Größe der Platzgruppe, ohne Verlust** (4, bei 3×3 8), mehr nicht. Bei den sechs Familien der Reihe haben die Flüsse fast nie Symmetrie; **Bauteil-Zwillinge sparen Größenordnungen, aber nur an erfundenen symmetrischen Flüssen.**

## Modell

- **Aufgabe** (wie in Stück 1 bis 8): `n` Bauteile auf `n` Plätze eines Rasters (Manhattan-Abstand), Fluss `F`; `cost(p) = Σ_{i<k} F[i,k] · D[p_i, p_k]` (`p[i]` = Platz des Bauteils `i`). Raster 2×2 bis 3×4; zehn Familien der Flussmatrix: die sechs der Reihe (Netzliste, gleichverteilt, dünn besetzt, zwei Cluster, Stern, wenige starke Flüsse) und vier **symmetrische, erfundene** (zwei Hälften, Ring, Nabe, Blöcke; alle Flüsse gleich stark).
- **Platzsymmetrie** (`syb_symmetry.py`, eigene Herleitung; die Literatur zur Symmetriebrechung (Orbit-Fixierung, Lex-Leader, Margot) ist **nicht eingesehen**): `g` mit `D[g a, g b] = D[a, b]` macht aus `p` die Anordnung `g∘p` mit denselben Kosten. Beim Raster sind es die Symmetrien des Rechtecks: **4** (zwei Spiegelungen, Drehung um 180°), beim Quadrat **8**, bei einer Zeile 2. Die Gruppe ist **genau** `Aut(D)`: gegen alle `n!` Permutationen der Plätze geprüft (`n` = 6, 8, 9). `G` wirkt **frei** auf die Anordnungen (`g∘p = p` nur für `g = id`): `n!/|G|` Bahnen.
- **Bauteilsymmetrie:** `h` mit `F[h a, h b] = F[a, b]` macht aus `p` die Anordnung `p∘h`. **Zwillinge:** `F[i,k] = F[j,k]` für alle `k ≠ i, j` (Vertauschen ist ein Automorphismus). `|Aut(F)|` wird gezählt (Zählgrenze 50 000).
- **Burnside:** Bahnen von `G × A` = `(1/|G||A|) Σ_{g,h} #{p : g∘p = p∘h}`, und `#{p : g∘p = p∘h} = ∏_ℓ c_ℓ! ℓ^{c_ℓ}` für gleiche Zykelstruktur, sonst 0 (ganzzahlig, exakt). Gegenprobe: die Bahnen durch Aufzählung (bis `n = 8`).
- **Baum** (Stück 8, Gilmore–Lawler-Knotenschranken): **Orbit-Beschneiden** versucht von den freien Plätzen nur den kleinsten je Bahn der Gruppe der Symmetrien, die alle belegten Plätze einzeln festlassen (Stabilisatorkette); **Zwillingsordnung** setzt gleiche Bauteile auf aufsteigende Plätze. **Knoten** = bewertete Kinder (ganzzahlig, auf jedem Rechner gleich); **Verhältnis** = Knoten ohne / mit; **Anfangswert** = die beste von 200 Abstiegen (Stück 3) oder keiner; Obergrenze 400 000 Knoten.
- **Instanzen:** feste Seeds ab 100000: `n` = 6 / 8 mit 30, `n` = 9 / 12 mit 18 Instanzen (die Instanzen der Beweisseite von Stück 15); vier symmetrische Familien je Größe `n` = 6, 8, 9, 12 (16 Instanzen, ohne Zufall); eine **Zufallsprobe** der Kombination mit 300 Instanzen.
- **Experimente:** (1) die Gruppe (Raster mit Bahnen, Bilder einer optimalen Anordnung, Handbeispiel); (2) wie viele Anordnungen sind gleich; (3) der Baum (Knoten je Tiefe); (4) über feste Instanzen; (5) symmetrische Flüsse und die Zufallsprobe. Formeln im 📐-Expander der App.

## Methodik

Der Abschnitt „Ergebnis“ und die Experimente 1 bis 3 rechnen **eine** Instanz (Familie, `n` = 4, 6, 8, 9, 12, Seed, drei Schalter: Platzsymmetrie, Zwillinge, Anfangswert; `n = 12` nur auf Knopfdruck). Die Experimente 4 und 5 laufen auf Knopfdruck über feste Instanzen (einige Minuten, auf Streamlit Cloud länger). Standard: Zwei Cluster, `n = 8`, Seed 48, Platzsymmetrie mit Anfangswert. Der Baum läuft in allen vier Varianten (ohne, Plätze, Zwillinge, beides). Zeiten sind Sekunden dieser Python-Fassung und schwanken um das Doppelte; **Zeiten stehen in Anzeigen, nie in Tests.**

## Befunde (gemessen, keine Behauptungen)

Alles Messung an den sechs erfundenen Familien der Reihe und den vier erfundenen symmetrischen Familien. Die Knotenzahlen sind ganzzahlig und rechnerunabhängig.

1. **Der Baum schrumpft um die Größe der Platzgruppe, ohne Verlust.** Knoten ohne gegen mit Orbit-Beschneiden (Anfangswert die beste von 200 Abstiegen): Verhältnis im Median **3,58 / 4,00 / 7,38 / 3,98** bei `n` = 6 / 8 / 9 / 12 (`|G|` = 4 / 4 / **8** / 4; kleinstes und größtes 3,00 und 3,94 / 4,00 und 4,00 / 6,20 und 7,92 / 3,79 und 4,00). Bei `n = 8` ist es in **allen 30** Instanzen genau 4,00 (`8 980 → 2 245` Knoten insgesamt). Bei `n = 12`: Median 7 990 → 2 007 Knoten, Summe 839 720 → 210 140. Der beste Wert ist mit und ohne Beschneiden **gleich in 96 von 96** Instanzen, und das Verhältnis liegt nie über `|G|`.
2. **Ohne Anfangswert ist der Gewinn kleiner:** Verhältnis im Median 2,31 / 3,14 / 6,50 bei `n` = 6 / 8 / 9 (kleinstes 1,24 / 1,20 / 3,60), weil der Baum zuerst eine Lösung finden muss; der Wert bleibt gleich in 78 von 78.
3. **Alle optimalen Anordnungen kommen in ganzen Bahnen:** ihre Zahl ist genau `|G|` mal die Zahl ihrer Bahnen in **26 von 26, 28 von 28 und 16 von 16** Instanzen ohne Bauteilsymmetrie (`n` = 6 / 8 / 9); Median 4 / 4 / 8 optimale Anordnungen, größte 48 / 32 / 64.
4. **Die Flüsse der sechs Familien haben fast nie Symmetrie.** `|Aut(F)| = 1` in 26 von 30, 28 von 30, 16 von 18 und 16 von 18 Instanzen; größer nur bei „Netzliste“ (2, 2, 6, 4, 2, 4), „dünn besetzt“ (2, 2, 2) und einmal „Stern“ (2). Die Zahl der Bahnen von `G × A` sinkt dadurch höchstens auf ein Sechstel von `n!/|G|`. **Burnside = Aufzählung** in allen geprüften Fällen (zehn Familien, `n` = 6 und 8).
5. **Bei symmetrischen Flüssen sind die Zwillinge entscheidend.** Knoten ohne / Plätze / Zwillinge / beides: „zwei Hälften“ bei `n = 12`: **über 400 000 (Obergrenze erreicht) / 133 696 / 2 120 / 1 334**; bei `n = 9`: 1 665 / 216 / 181 / 57 (Aut 2 880 Automorphismen, 23 Bahnen gegen `n!/|G|` = 45 360); „Blöcke“ bei `n = 12`: 11 816 / 2 966 / 1 084 / 403. Bei „Ring“ und „Nabe“ ist der Baum schon ohne Symmetrie klein (Gilmore–Lawler ist dort scharf): 12 Knoten bei `n = 12`, mit Plätzen 4.
6. **Platzgruppe und Zwillinge zusammen sind in den Messungen gültig, aber nicht bewiesen.** In **300** Zufallsinstanzen (`n` = 6 und 8, Flüsse zufällig mit erzwungenen Zwillingspaaren, Baum ohne Anfangswert, Optimum aus der Aufzählung) verfehlte keine der vier Varianten das Optimum; Knoten insgesamt 90 801 / 27 134 / 60 216 / 21 252. Dass die einfache Kombination (kleinster Platz je Bahn, aufsteigende Zwillingsplätze) allgemein gültig ist, ist **nicht** gezeigt.

**Handbeispiel** (Stück 3, 5, 8): vier Plätze auf einer Zeile, Fluss A–C, A–D, B–C, B–D je 1. `n! = 24` Anordnungen, Platzgruppe `{id, Spiegelung}`, `|Aut(F)| = 8` (Vierzyklus A–C–B–D), Zwillinge {A, B} und {C, D}. **16 der 24 Anordnungen kosten 6** (das Optimum); Bahnen unter den Plätzen 12, unter Plätzen und Bauteilen **3** (Burnside = Aufzählung), davon 2 optimal. Baum (Anfangswert 6): 4 Knoten ohne, **2** mit Orbit-Beschneiden, 4 mit Zwillingen, 2 mit beidem; ohne Anfangswert 10 / 8 / 10 / 8.

### Sechs Familien der Reihe (mit Anfangswert)

| | n = 6 | 8 | 9 | 12 |
|---|---|---|---|---|
| Instanzen | 30 | 30 | 18 | 18 |
| Platzgruppe `\|G\|` | 4 | 4 | 8 | 4 |
| Flüsse ohne Symmetrie | 26 von 30 | 28 von 30 | 16 von 18 | 16 von 18 |
| Anordnungen bis auf Plätze `n!/\|G\|` | 180 | 10 080 | 45 360 | 119 750 400 |
| Knoten ohne / mit, Median | 34 / 9,5 | 240 / 60 | 675 / 91 | 7 990 / 2 007 |
| Verhältnis, Median (kleinstes bis größtes) | 3,58 (3,00 bis 3,94) | 4,00 (4,00 bis 4,00) | 7,38 (6,20 bis 7,92) | 3,98 (3,79 bis 4,00) |
| Verhältnis ohne Anfangswert, Median | 2,31 | 3,14 | 6,50 | – |
| bester Wert gleich | 30 von 30 | 30 von 30 | 18 von 18 | 18 von 18 |

Die Knotenzahlen und Verhältnisse stehen mit ihren genauen Werten in `tests/test_claims.py`; die Zeiten stehen in keinem Test.

## Ehrliche Grenzen

- **Der Gewinn ist klein:** die Platzsymmetrie spart höchstens `|G|` (4 oder 8); gegen eine schärfere Schranke (Stück 5, 7) ist das ein kleiner, fester Faktor. Der große Gewinn (Zwillinge) steht an erfundenen Flüssen, nicht an der Platine.
- **Eigene Fassung:** Orbit-Beschneiden mit der Stabilisatorkette und die Zwillingsordnung sind eigene Herleitungen; die Literatur ist **nicht nachgelesen**, Selbstangaben werden nicht übernommen.
- **Kombination nicht bewiesen:** 0 verfehlte Optima in 300 Zufallsinstanzen und 16 strukturierten Instanzen sind kein Beweis; allgemein verlangt man eine lexikographische Bedingung für das Produkt der Gruppen. Ein Fehler wäre still, deshalb der Orakel-Test.
- **Nur Rechteck-Raster:** die Gruppe der Plätze sind die Symmetrien des Rechtecks (geprüft an `D`); Raster bis 3×4 im Baum (Ein-Zeilen-Raster und Quadrate bis 4×4 nur in der Gruppenprüfung).
- **Bauteilsymmetrie nur über Zwillinge** im Baum; allgemeine Automorphismen werden gezählt (bis 50 000), nicht genutzt. „Zwei Hälften“ und „Nabe“ bei `n = 12` liegen über der Zählgrenze (nur die Zwillingsklassen).
- **Nur Gilmore–Lawler im Baum:** mit der linearen oder der SDP-Schranke am Knoten ist der Gewinn nicht gemessen.
- **Ohne Anfangswert** ist der Gewinn kleiner und streut (1,2 bis 3,9 bei `n = 8`).
- **Familien erfunden, wenige Instanzen:** die vier symmetrischen Familien sind eigens so gebaut, dass Zwillinge entstehen; `n` = 6, 8: 30 Instanzen, `n` = 9, 12: 18; keine QAPLIB.
- **Zeit ist implementierungsabhängig:** Python-Fassung; Zeiten schwanken um das Doppelte, in Tests stehen nie Zeiten. Die Knotenzahlen sind ganzzahlig und rechnerunabhängig.

## Verifikation

- **Tests** (`pytest tests/`): **300 Tests** (299 bestanden, einer übersprungen: die Gegenprobe durch Aufzählung ist für ein großes Paar aus Gruppen zu groß), rund sieben Minuten (Windows, Python 3.14; die festen Instanzen der Zahlen-Tests rechnen parallel). Handwerte (Handbeispiel: 24 / 16 / 12 / 3 / 2 Anordnungen und Bahnen, Knoten 4 / 2 / 4 / 2 und 10 / 8 / 10 / 8; Gruppengrößen je Raster; Zykelstruktur und `∏ c! ℓ^c` von Hand), Eigenschaften (die Gruppe ist abgeschlossen und enthält die Identität, die Wirkung ist frei, Bilder kosten dasselbe, Zwillinge sind Automorphismen, Knoten mit Beschneiden höchstens ohne, Verhältnis höchstens `|G|` bei Anfangswert gleich dem Optimum), Orakel (die Aufzählung aller Permutationen der Plätze: `G = Aut(D)`; **Burnside gegen die aufgezählten Bahnen** für zehn Familien; der Baum mit jedem Schalter gleich dem aufgezählten Optimum; der Baum ohne Symmetrie gleich dem Baum aus Stück 8), Verdikte (Art und Text folgen den Zahlen, jeder Zweig an festen Eingaben), AppTest (alle Regler und Schalter an ihren Grenzen, alle Rechenknöpfe mit verkleinerten Reihen, PDF), und die **Zahlen der README** an den festen Instanzen (`tests/test_claims.py`, parallel gerechnet; ganzzahlige Knotenzahlen genau).
- **Kopie:** die Kerne (Instanzen, Zuordnung, Aufzählung, Gilmore–Lawler, Baum) sind Kopien aus Stück 1 bis 8; Tests vergleichen die Familien mit denen von Stück 1 bis 12, sofern die Schwester-Repos nebenan liegen.
- **Nicht getestet:** Zeiten; kein Mutationstest; Linux-CI: noch nicht gelaufen (die Knotenzahlen sind ganzzahlig und rechnerunabhängig); die Zahlen der Tabellen stammen aus dem Windows-Lauf.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, fünf Experimente, Grenzen, Formulierung |
| `syb_symmetry.py` | Platzgruppe, Automorphismen und Zwillinge, Burnside, der Baum mit Orbit-Beschneiden und Zwillingsordnung, die symmetrischen Flussmatrizen |
| `syb_evaluation.py` | Eine Instanz, Zeilen der Vergleiche, Zufallsprobe, Kennzahlen, Verdikte |
| `syb_rng.py`, `syb_cost.py`, `syb_landscape.py` | SplitMix64, Kosten, Aufzählung (Kopien aus Stück 1 und 2) |
| `syb_instance.py` | Sechs Familien der Flussmatrix, Raster, Handbeispiele |
| `syb_assignment.py` | Ungarische Methode (Kopie aus Stück 8) |
| `syb_bounds.py` | Gilmore–Lawler, Dual Ascent, Abstiege aus Zufall (Kopien aus Stück 3 und 5) |
| `syb_tree.py` | Branch and Bound (Kopie aus Stück 8) |
| `syb_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `syb_pdf_export.py` | PDF-Export des Ergebnisses |
| `syb_constants.py` | Größen, Familien, Varianten, feste Reihen, Farben, Presets |
| `syb_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Button |
| `syb_layout.py` | Fester Kopf (Stylesheet) |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (nur für die Orakel der Kernkopien) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt; kein `scipy` zur Laufzeit) |
| `tests/` | Symmetrien, Zählung, Baum, Auswertung, Verdikte, Kerne, Abbildungen, Presets, Layout, AppTest, Zahlen der README (`test_claims.py`, `rows.py`), Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Allgemeine Graphautomorphismen** (nauty o. Ä.) und ein **Beweis der Kombination** (Lex-Leader für das Produkt der Gruppen).
- **Symmetrie in den Schranken selbst** (die Schranke eines Knotens ist bei symmetrischen Plätzen gleich; das ist der Grund des Gewinns, kein eigenes Verfahren).
- **Andere Anordnungen der Plätze** als Rechteck-Raster, **QAPLIB**, Raster über 3×4 im Baum.
- **Zeiten in Tests.**

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version in den App-Einstellungen prüfen (lokal Python 3.14, CI Python 3.12); der Code verwendet nur Merkmale, die in Python 3.12 laufen. <!-- lint-ok: dezimalpunkt -->

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy, pandas und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
