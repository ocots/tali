"""Détection des marqueurs et homographie (décision `0001` A).

Modèle géométrique : **affine** (rotation, échelle, translation, cisaillement), pas
une homographie projective complète — suffisant pour un scanner à plat. Le canal
photo, qui introduirait une vraie perspective, est explicitement hors du périmètre de
novembre (AGENTS.md).
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from tali.render.dimensions import DEFAULT, Dimensions


class LocateError(ValueError):
    """Moins de trois marqueurs trouvés, ou géométrie trop ambiguë pour être fiable."""


def marker_positions(dims: Dimensions = DEFAULT) -> dict[str, tuple[float, float]]:
    """Position (mm) des cinq marqueurs du gabarit (décision `0001` A).

    Dupliqué depuis la disposition de `render.sheet` plutôt qu'importé : `sheet.py` a
    besoin des comptages de questions d'un examen réel, `locate.py` n'en a jamais
    besoin — ce sont deux consommateurs différents de la même géométrie de coin.
    """
    m, s = dims.marker_margin_mm, dims.marker_size_mm
    c = s / 2
    return {
        "haut-gauche": (m + c, m + c),
        "orientation": (m + 2 * s + c, m + c),
        "haut-droit": (dims.page_width_mm - m - c, m + c),
        "bas-gauche": (m + c, dims.page_height_mm - m - c),
        "bas-droit": (dims.page_width_mm - m - c, dims.page_height_mm - m - c),
    }


@dataclass(frozen=True)
class Transform:
    """Une transformation affine millimètres → pixels, et son inverse."""

    matrix: np.ndarray  # 2×3, comme OpenCV

    def to_pixels(self, x_mm: float, y_mm: float) -> tuple[float, float]:
        x, y = self.matrix @ np.array([x_mm, y_mm, 1.0])
        return float(x), float(y)

    def to_mm(self, x_px: float, y_px: float) -> tuple[float, float]:
        inverse = cv2.invertAffineTransform(self.matrix)
        x, y = inverse @ np.array([x_px, y_px, 1.0])
        return float(x), float(y)


def find_marker_centers(image: np.ndarray) -> list[tuple[float, float]]:
    """Détecte des carrés noirs pleins par seuillage puis filtrage sur la forme."""
    _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers: list[tuple[float, float]] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 20:  # bruit de seuillage
            continue
        x, y, w, h = cv2.boundingRect(contour)
        squareness = min(w, h) / max(w, h)
        fill_ratio = area / (w * h)
        if squareness > 0.8 and fill_ratio > 0.7:
            centers.append((x + w / 2, y + h / 2))
    return centers


def _label(centers: list[tuple[float, float]]) -> dict[str, tuple[float, float]]:
    """Identifie chaque marqueur détecté par son rôle, **sans supposer d'orientation**.

    Le marqueur d'orientation n'est jamais qu'à ~2 tailles de marqueur du coin
    haut-gauche du gabarit (décision `0001` A) — bien plus proche que deux vrais
    coins, qui sont séparés par des dizaines à des centaines de millimètres. Cette
    paire la plus proche identifie le coin haut-gauche **quelle que soit la rotation
    de la page dans l'image** : c'est une relation rigide, elle survit à la rotation.
    """
    if len(centers) < 3:
        raise LocateError(f"moins de trois marqueurs détectés ({len(centers)})")

    pts = np.array(centers, dtype=np.float64)
    n = len(pts)
    pairs = sorted(
        ((float(np.linalg.norm(pts[i] - pts[j])), i, j) for i in range(n) for j in range(i + 1, n))
    )
    if len(pairs) > 1 and pairs[1][0] < pairs[0][0] * 3:
        raise LocateError("les marqueurs ne se distinguent pas assez pour lever l'orientation")

    _, i, j = pairs[0]
    remaining = [pts[k] for k in range(n) if k not in (i, j)]

    # Lequel de {i, j} est le marqueur d'orientation ? Dans le gabarit, il est décalé
    # vers le reste du bord haut (décision 0001 A), donc systématiquement plus proche
    # de n'importe quel autre coin que ne l'est le vrai coin haut-gauche — une relation
    # de distances relatives, préservée par n'importe quelle rotation/mise à l'échelle
    # uniforme. Voter sur les marqueurs restants tranche, même avec un seul restant.
    votes_j_est_orientation = sum(
        1 for r in remaining if np.linalg.norm(pts[j] - r) < np.linalg.norm(pts[i] - r)
    )
    anchor_idx, extra_idx = (i, j) if votes_j_est_orientation * 2 >= len(remaining) else (j, i)
    labels: dict[str, tuple[float, float]] = {
        "haut-gauche": tuple(pts[anchor_idx]),
        "orientation": tuple(pts[extra_idx]),
    }
    if remaining:
        expected = marker_positions()
        anchor = pts[anchor_idx]
        w_mm = np.linalg.norm(np.subtract(expected["haut-droit"], expected["haut-gauche"]))
        h_mm = np.linalg.norm(np.subtract(expected["bas-gauche"], expected["haut-gauche"]))
        near, far = ("haut-droit", "bas-gauche") if w_mm < h_mm else ("bas-gauche", "haut-droit")
        order = [near, far, "bas-droit"]
        by_distance = sorted(remaining, key=lambda p: np.linalg.norm(p - anchor))
        for label, point in zip(order, by_distance):
            labels[label] = tuple(point)
    return labels


def locate(image: np.ndarray, dims: Dimensions = DEFAULT) -> Transform:
    """Détecte les marqueurs d'une page et produit sa transformation mm → pixels."""
    labels = _label(find_marker_centers(image))
    expected = marker_positions(dims)

    src = np.array([expected[k] for k in labels], dtype=np.float32)
    dst = np.array([labels[k] for k in labels], dtype=np.float32)
    matrix, _ = cv2.estimateAffine2D(src, dst)
    if matrix is None:
        raise LocateError("transformation non trouvée à partir des marqueurs détectés")
    return Transform(matrix=matrix)
