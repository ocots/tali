"""Détection des marqueurs et homographie (décision `0001` A).

Les marqueurs sont dessinés directement avec `cv2`, jamais via `render/` ni le corpus
synthétique (#7) : ce test doit rester autonome, sans dépendre d'une autre tâche.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from tali.render.dimensions import DEFAULT
from tali.vision.locate import LocateError, locate, marker_positions

PX_PER_MM = 4.0  # résolution arbitraire de test, pas un DPI réel
CANVAS = 2000  # assez grand pour contenir n'importe quelle rotation + translation


def similarity(angle_deg: float, scale: float, tx: float, ty: float):
    """Une transformation mm → pixels : rotation + échelle uniforme + translation."""
    theta = np.radians(angle_deg)

    def apply(x_mm: float, y_mm: float) -> tuple[float, float]:
        x = scale * (x_mm * np.cos(theta) - y_mm * np.sin(theta)) + tx
        y = scale * (x_mm * np.sin(theta) + y_mm * np.cos(theta)) + ty
        return x, y

    return apply


def draw_markers(transform, *, drop: frozenset[str] = frozenset()) -> np.ndarray:
    image = np.full((CANVAS, CANVAS), 255, dtype=np.uint8)
    half = int(DEFAULT.marker_size_mm * PX_PER_MM / 2)
    for name, (x_mm, y_mm) in marker_positions().items():
        if name in drop:
            continue
        x_px, y_px = transform(x_mm, y_mm)
        cv2.rectangle(
            image, (int(x_px - half), int(y_px - half)), (int(x_px + half), int(y_px + half)), 0, -1
        )
    return image


def test_retrouve_une_homographie_connue() -> None:
    """Round-trip, autonome : appliquer une transformation connue, la retrouver à ε
    près — plus informatif que le cas identité, et sans dépendre du corpus synthétique."""
    known = similarity(angle_deg=3.0, scale=PX_PER_MM, tx=100.0, ty=150.0)
    transform = locate(draw_markers(known))

    for x_mm, y_mm in marker_positions().values():
        x_attendu, y_attendu = known(x_mm, y_mm)
        x_obtenu, y_obtenu = transform.to_pixels(x_mm, y_mm)
        assert x_obtenu == pytest.approx(x_attendu, abs=1.0)
        assert y_obtenu == pytest.approx(y_attendu, abs=1.0)


def test_leve_orientation_180_degres_sans_qr() -> None:
    """Une feuille insérée à l'envers reste lisible : le marqueur d'orientation reste
    le voisin du coin haut-gauche du gabarit, où qu'il atterrisse dans l'image."""
    upside_down = similarity(angle_deg=180.0, scale=PX_PER_MM, tx=1000.0, ty=1400.0)
    transform = locate(draw_markers(upside_down))

    x_mm, y_mm = marker_positions()["haut-gauche"]
    x_attendu, y_attendu = upside_down(x_mm, y_mm)
    x_obtenu, y_obtenu = transform.to_pixels(x_mm, y_mm)
    assert x_obtenu == pytest.approx(x_attendu, abs=1.0)
    assert y_obtenu == pytest.approx(y_attendu, abs=1.0)


def test_label_ignore_lordre_de_detection() -> None:
    """La désambiguïsation haut-gauche/orientation dépend de la géométrie, jamais de
    l'ordre dans lequel les marqueurs ont été détectés (contours cv2 non ordonnés)."""
    from tali.vision.locate import _label

    positions = marker_positions()
    dans_l_ordre = [positions[k] for k in ("haut-gauche", "orientation", "haut-droit",
                                            "bas-gauche", "bas-droit")]
    inverse = list(reversed(dans_l_ordre))  # orientation listé avant haut-gauche

    for centers in (dans_l_ordre, inverse):
        labels = _label(centers)
        assert labels["haut-gauche"] == pytest.approx(positions["haut-gauche"])
        assert labels["orientation"] == pytest.approx(positions["orientation"])


def test_refuse_si_moins_de_quatre_marqueurs() -> None:
    """Une homographie complète (décision `0005` A) a besoin de 4 correspondances,
    pas 3 : trois marqueurs ne suffisent plus."""
    identity = similarity(angle_deg=0.0, scale=PX_PER_MM, tx=100.0, ty=100.0)
    image = draw_markers(identity, drop=frozenset({"bas-gauche", "bas-droit"}))
    with pytest.raises(LocateError) as err:
        locate(image)
    assert "moins de quatre" in str(err.value)


def test_refuse_une_page_blanche() -> None:
    with pytest.raises(LocateError):
        locate(np.full((400, 300), 255, dtype=np.uint8))


def test_refuse_si_les_marqueurs_sont_trop_proches_pour_lever_lorientation() -> None:
    """Marqueurs équidistants (+ un quatrième, éloigné, pour atteindre le minimum de la
    décision `0005` A) ne permettent pas d'identifier une paire proche fiable : refuser
    plutôt que deviner une orientation au hasard."""
    image = np.full((CANVAS, CANVAS), 255, dtype=np.uint8)
    half = int(DEFAULT.marker_size_mm * PX_PER_MM / 2)
    for x_px, y_px in ((200, 200), (260, 200), (230, 260), (200, 800)):
        cv2.rectangle(image, (x_px - half, y_px - half), (x_px + half, y_px + half), 0, -1)
    with pytest.raises(LocateError) as err:
        locate(image)
    assert "se distinguent pas assez" in str(err.value)
