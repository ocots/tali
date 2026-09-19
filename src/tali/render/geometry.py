"""Conversion millimètres ↔ points, origine haut-gauche ↔ bas-gauche.

Fonctions pures, sans dépendance à ReportLab : c'est ce qui les rend testables sans
rendre de PDF, et c'est cette conversion qui isole toute la moitié « génération » d'un
changement de bibliothèque (décision 0002).
"""

from __future__ import annotations

# 1 point = 1/72 pouce, 1 pouce = 25.4 mm — le facteur que ReportLab utilise en interne
# (`reportlab.lib.units.mm`), reproduit ici pour que ce module reste libre de reportlab.
POINTS_PER_MM = 72 / 25.4


def mm_to_points(value_mm: float) -> float:
    return value_mm * POINTS_PER_MM


def to_reportlab(x_mm: float, y_mm: float, page_height_mm: float) -> tuple[float, float]:
    """(x, y) en mm, origine en haut à gauche → (x, y) en points, origine en bas à gauche.

    La seule fonction qui sait que ReportLab compte depuis le bas : l'appeler ici une
    fois évite de refaire — et de rater — cette conversion à chaque appel de dessin.
    """
    return mm_to_points(x_mm), mm_to_points(page_height_mm - y_mm)
