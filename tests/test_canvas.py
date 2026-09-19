"""La primitive de dessin — interface étroite au-dessus de ReportLab (décision 0002).

Les tests vérifient des **positions**, jamais une image rendue : la rastérisation est le
travail du corpus synthétique (#7), pas de celui-ci.
"""

from __future__ import annotations

from tali.render.canvas import Canvas
from tali.render.geometry import mm_to_points, to_reportlab

PAGE_HEIGHT_MM = 297.0  # A4


class RecordingBackend:
    """Enregistre les appels au lieu de dessiner — vérifier une position ne demande
    jamais de produire un PDF ni une image."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    def rect(self, x, y, width, height):
        self.calls.append(("rect", (x, y, width, height)))

    def circle(self, x, y, radius):
        self.calls.append(("circle", (x, y, radius)))

    def text(self, x, y, content, size):
        self.calls.append(("text", (x, y, content, size)))

    def qr(self, x, y, size, payload):
        self.calls.append(("qr", (x, y, size, payload)))


def test_origine_en_haut_a_gauche() -> None:
    """`y_mm = 0` doit tomber en haut de la page — le sommet en points, pas la base."""
    backend = RecordingBackend()
    canvas = Canvas(backend, PAGE_HEIGHT_MM)

    canvas.circle(10, 0, 3)  # centre au sommet de la page
    canvas.circle(10, PAGE_HEIGHT_MM, 3)  # centre au bas de la page

    assert backend.calls[0][1][1] == mm_to_points(PAGE_HEIGHT_MM)
    assert backend.calls[1][1][1] == 0


def test_conversion_millimetres_vers_points() -> None:
    """1 pouce = 25.4 mm = 72 points — la conversion que fait `to_reportlab`."""
    assert mm_to_points(25.4) == 72
    x, y = to_reportlab(10, 20, PAGE_HEIGHT_MM)
    assert x == mm_to_points(10)
    assert y == mm_to_points(PAGE_HEIGHT_MM - 20)


def test_qr_pose_a_la_position_demandee() -> None:
    """Le coin haut-gauche demandé arrive au bon endroit, converti pour ReportLab."""
    backend = RecordingBackend()
    Canvas(backend, PAGE_HEIGHT_MM).qr(15, 20, 25, "tali:ct-2026-01:0007:1:1")

    name, (x, y, size, payload) = backend.calls[0]
    assert name == "qr"
    assert (x, y) == to_reportlab(15, 20 + 25, PAGE_HEIGHT_MM)
    assert size == mm_to_points(25)
    assert payload == "tali:ct-2026-01:0007:1:1"


def test_reportlab_nest_importe_que_dans_render() -> None:
    """Test de règle : confiner `reportlab` évite qu'un changement de bibliothèque se
    propage dans tout le projet (décision 0002)."""
    import ast
    import pathlib

    src_root = pathlib.Path(__file__).parents[1] / "src" / "tali"
    offenders = []
    for path in src_root.rglob("*.py"):
        if "render" in path.relative_to(src_root).parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = (
                [(node.module or "").split(".")[0]]
                if isinstance(node, ast.ImportFrom)
                else [a.name.split(".")[0] for a in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            if "reportlab" in names:
                offenders.append(str(path))
    assert offenders == [], f"reportlab importé hors de render/ : {offenders}"
