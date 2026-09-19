"""Interface étroite au-dessus de ReportLab (décision 0002).

`rect`, `circle`, `text`, `qr` — rien de plus tant que rien de plus n'est utile. Le
confinement à ce module est **vérifié**, pas promis : voir
`test_reportlab_nest_importe_que_dans_render`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.pdfgen.canvas import Canvas as _ReportLabCanvas

from tali.render.geometry import mm_to_points, to_reportlab


class Backend(Protocol):
    """Ce dont `Canvas` a besoin d'un moteur de rendu — en points, origine bas-gauche."""

    def rect(self, x: float, y: float, width: float, height: float) -> None: ...
    def circle(self, x: float, y: float, radius: float) -> None: ...
    def text(self, x: float, y: float, content: str, size: float) -> None: ...
    def qr(self, x: float, y: float, size: float, payload: str) -> None: ...


class ReportLabBackend:
    """Le seul point de contact avec `reportlab` — jamais utilisé directement ailleurs."""

    def __init__(self, path: str | Path, width_pt: float, height_pt: float) -> None:
        self._pdf = _ReportLabCanvas(str(path), pagesize=(width_pt, height_pt))

    def rect(self, x: float, y: float, width: float, height: float) -> None:
        self._pdf.rect(x, y, width, height)

    def circle(self, x: float, y: float, radius: float) -> None:
        self._pdf.circle(x, y, radius)

    def text(self, x: float, y: float, content: str, size: float) -> None:
        self._pdf.setFont("Helvetica", size)
        self._pdf.drawString(x, y, content)

    def qr(self, x: float, y: float, size: float, payload: str) -> None:
        widget = QrCodeWidget(payload)
        x0, y0, x1, y1 = widget.getBounds()
        w, h = x1 - x0, y1 - y0
        drawing = Drawing(size, size, transform=(size / w, 0, 0, size / h, 0, 0))
        drawing.add(widget)
        renderPDF.draw(drawing, self._pdf, x, y)

    def new_page(self) -> None:
        self._pdf.showPage()

    def save(self) -> None:
        self._pdf.save()


class Canvas:
    """Dessine en millimètres, origine en haut à gauche.

    `rect` et `qr` prennent le coin **haut-gauche** de leur boîte ; `circle` prend son
    **centre** ; `text` le point de départ de sa ligne de base — le point naturel de
    chaque primitive dans ReportLab, jamais retraduit ailleurs.
    """

    def __init__(self, backend: Backend, page_height_mm: float) -> None:
        self._backend = backend
        self._page_height_mm = page_height_mm

    def rect(self, x_mm: float, y_mm: float, width_mm: float, height_mm: float) -> None:
        x, y = to_reportlab(x_mm, y_mm + height_mm, self._page_height_mm)
        self._backend.rect(x, y, mm_to_points(width_mm), mm_to_points(height_mm))

    def circle(self, x_mm: float, y_mm: float, radius_mm: float) -> None:
        x, y = to_reportlab(x_mm, y_mm, self._page_height_mm)
        self._backend.circle(x, y, mm_to_points(radius_mm))

    def text(self, x_mm: float, y_mm: float, content: str, *, size_pt: float = 10) -> None:
        x, y = to_reportlab(x_mm, y_mm, self._page_height_mm)
        self._backend.text(x, y, content, size_pt)

    def qr(self, x_mm: float, y_mm: float, size_mm: float, payload: str) -> None:
        x, y = to_reportlab(x_mm, y_mm + size_mm, self._page_height_mm)
        self._backend.qr(x, y, mm_to_points(size_mm), payload)
