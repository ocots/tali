# Tâche #2 — Primitive de dessin — interface étroite au-dessus de ReportLab

- **rôle** : `feature`
- **critère de complétion** : `.venv/bin/python -m pytest -q tests/test_canvas.py::test_origine_en_haut_a_gauche tests/test_canvas.py::test_conversion_millimetres_vers_points tests/test_canvas.py::test_qr_pose_a_la_position_demandee tests/test_canvas.py::test_reportlab_nest_importe_que_dans_render`
- **périmètre** : `src/tali/render/**`, `tests/test_canvas.py`
- **budget** : 1 session

## Plan

- [x] `geometry.py` — conversion mm/points pure, sans dépendance à reportlab
- [x] `canvas.py` — `Canvas` + `Backend` (Protocol) + `ReportLabBackend`
- [x] `tests/test_canvas.py` — positions, jamais d'image rendue
- [x] Ajouter `reportlab` à `pyproject.toml`

## Journal

**`pyproject.toml` n'était couvert par aucun périmètre de rôle** — ajouter une
dépendance y est pourtant nécessaire pour cette tâche (et pour toute tâche future qui en
introduit une). Corrigé sur `main`, hors de cette PR (voir le commit sur `.crank.toml`).

**Position vs image, résolu par inversion de dépendance.** « Les tests vérifient des
positions, sans rendre d'image » ne se fait pas en inspectant un PDF généré — ReportLab
n'expose pas ce qu'il a dessiné. `Canvas` ne parle qu'à un `Backend` (Protocol) ; les
tests lui donnent un `RecordingBackend` qui note les appels reçus, en points. Un seul
`ReportLabBackend` réel, qui concentre tout le contact avec `reportlab`.

**Convention de point d'ancrage par primitive**, pour éviter d'en inventer une uniforme
qui trahirait l'une d'elles : `rect`/`qr` prennent leur coin haut-gauche (le point
naturel pour poser une boîte), `circle` son centre, `text` le départ de sa ligne de
base — chacun le paramètre natif de l'appel ReportLab correspondant.

Les quatre tests du contrat mutation-testés (signe de conversion inversé, mauvais
facteur mm→pt, QR non recalé sur son coin bas, import `reportlab` glissé hors de
`render/`) : les quatre mutants sont tués.

## Bilan

`geometry.to_reportlab`/`mm_to_points` : conversion pure, testée seule. `Canvas` (`rect`,
`circle`, `text`, `qr`) au-dessus d'un `Backend` injectable ; `ReportLabBackend` est le
seul point de contact avec `reportlab`, vérifié par un test AST, pas seulement documenté.

## Points d'incertitude

- Le rendu réel (production d'un vrai PDF) n'est pas testé ici — volontairement : c'est
  le rôle du corpus synthétique (#7), qui rastérise et vérifie le round-trip.
- `ReportLabBackend` n'est pas appelé par les tests : sa correction dépend de la
  bibliothèque elle-même, pas de notre logique. À couvrir par le round-trip de #7.
