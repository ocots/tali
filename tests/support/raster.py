"""Rastérisation d'un PDF en image (décision `0002`) — dépendance de test uniquement."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pypdfium2 as pdfium

_POINTS_PER_INCH = 72


def rasterize(pdf_path: Path, *, dpi: int = 200, page: int = 0) -> np.ndarray:
    """Rend une page d'un PDF en niveaux de gris, à `dpi`."""
    document = pdfium.PdfDocument(str(pdf_path))
    bitmap = document[page].render(scale=dpi / _POINTS_PER_INCH)
    return np.array(bitmap.to_pil().convert("L"))
