"""Toutes les dimensions du gabarit, en un seul endroit (décision `0001` D).

Valeurs de départ, à imprimer et mesurer — le spike S2 les ajustera. Elles ne sont
gravées que dans ce fichier : les ajuster ne doit jamais toucher `sheet.py`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dimensions:
    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    marker_size_mm: float = 8.0
    marker_margin_mm: float = 10.0
    qr_size_mm: float = 18.0
    bubble_diameter_mm: float = 5.0
    bubble_pitch_mm: float = 8.0
    letter_cell_mm: float = 8.0  # même bulle que le QCM (décision 0001 D)
    open_frame_line_height_mm: float = 8.0


DEFAULT = Dimensions()
