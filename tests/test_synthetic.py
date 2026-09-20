"""Corpus synthétique — rastérisation, déformations, round-trip (cahier des charges §13.1).

L'actif de test le plus précieux du projet : générer une copie, la rendre en image, la
déformer, vérifier que le pipeline retrouve exactement la vérité terrain connue — ou
refuse plutôt que de se tromper en silence.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tali.render.dimensions import DEFAULT
from tali.services.build import build
from tali.vision.locate import LocateError, locate, marker_positions
from tali.vision.qr import decode_page_qr

from tests.support import deform
from tests.support.raster import rasterize

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-exam" / "exam.toml"
DPI = 200
TOLERANCE_PX = 2.0  # antialiasing + seuillage : « exact » à l'arrondi de rastérisation près


@pytest.fixture(scope="module")
def rendered_page(tmp_path_factory: pytest.TempPathFactory) -> np.ndarray:
    """Une copie construite puis rastérisée, réutilisée par les tests de ce module —
    la reconstruire à chaque test ralentirait sans rien vérifier de plus."""
    exam_dir = tmp_path_factory.mktemp("corpus")
    (exam_dir / "exam.toml").write_text(EXAMPLE.read_text().replace("copies = 220", "copies = 1"))
    result = build(exam_dir)
    return rasterize(result.out_dir / "copies" / "0001.pdf", dpi=DPI)


def test_rend_une_page_a_200_dpi(rendered_page: np.ndarray) -> None:
    """A4 à 200 dpi : 1654 × 2339 px — attrape une conversion mm/points/pixels erronée
    n'importe où dans la chaîne, sans inspection visuelle."""
    largeur = round(DEFAULT.page_width_mm / 25.4 * DPI)
    hauteur = round(DEFAULT.page_height_mm / 25.4 * DPI)
    assert rendered_page.shape == (hauteur, largeur)


def test_round_trip_sans_deformation(rendered_page: np.ndarray) -> None:
    """QR et marqueurs retrouvent exactement ce qui a servi à générer la page."""
    payload = decode_page_qr(rendered_page)
    assert payload.exam_id == "synthetic-2026"
    assert payload.copy_id == 1

    transform = locate(rendered_page)
    px_per_mm = DPI / 25.4
    for x_mm, y_mm in marker_positions().values():
        x_px, y_px = transform.to_pixels(x_mm, y_mm)
        assert x_px == pytest.approx(x_mm * px_per_mm, abs=TOLERANCE_PX)
        assert y_px == pytest.approx(y_mm * px_per_mm, abs=TOLERANCE_PX)


PERSPECTIVE_FOCAL_PX = 40_000.0  # decisions/0006 A : focale longue, marqueurs restent
# détectables (grand-angle par défaut de deform.perspective les sort du cadre à 30°)


def test_round_trip_perspective_30_degres(rendered_page: np.ndarray) -> None:
    """`locate()` retrouve une vraie perspective (décision `0005` A). Focale allongée
    pour rester dans ce que `find_marker_centers` sait détecter (décision `0006` A) :
    le canal photo grand-angle reste hors périmètre de novembre."""
    transform = locate(deform.perspective(rendered_page, degrees=30.0, focal_px=PERSPECTIVE_FOCAL_PX))
    px_per_mm = DPI / 25.4
    for x_mm, y_mm in marker_positions().values():
        x_px, y_px = transform.to_pixels(x_mm, y_mm)
        vraie = deform.perspective_point(
            rendered_page.shape, x_mm * px_per_mm, y_mm * px_per_mm, 30.0, focal_px=PERSPECTIVE_FOCAL_PX
        )
        assert (x_px, y_px) == pytest.approx(vraie, abs=TOLERANCE_PX)


EXTREMES = {
    "rotation-flou-bruit": lambda img: deform.noise(deform.blur(deform.rotate(img, 45.0), 6.0), 60.0),
    "perspective-extreme": lambda img: deform.perspective(img, degrees=60.0),
}


@pytest.mark.parametrize("appliquer", EXTREMES.values(), ids=EXTREMES.keys())
def test_refuse_plutot_que_de_se_tromper_aux_extremes(rendered_page: np.ndarray, appliquer) -> None:
    """Le critère le plus important : un refus explicite, jamais un recalage
    silencieusement faux qui corromprait toute la notation en aval."""
    with pytest.raises(LocateError):
        locate(appliquer(rendered_page))
