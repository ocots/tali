"""Gabarit de la feuille de réponses (décision `0001`) : marqueurs, QR, grilles
d'identité, bulles QCM, cadres de réponse ouverte — et rien d'autre."""

from __future__ import annotations

import pytest

from tali.render.dimensions import DEFAULT
from tali.render.sheet import SheetError, Template, ZONE_TYPES, build_template


def make_template(**overrides) -> Template:
    fields = {"n_qcm_questions": 3, "n_qcm_choices": 4, "n_open_questions": 2}
    fields.update(overrides)
    return build_template(**fields)


def test_cinq_marqueurs_dont_un_asymetrique() -> None:
    """Décision `0001` A : quatre coins identiques sont indiscernables à 180°."""
    markers = [z for z in make_template().zones if z.type == "marqueur"]
    assert len(markers) == 5

    centers = {(z.x_mm + z.width_mm / 2, z.y_mm + z.height_mm / 2) for z in markers}
    rotated = {(DEFAULT.page_width_mm - x, DEFAULT.page_height_mm - y) for x, y in centers}
    assert rotated != centers, "marqueurs symétriques à 180° : orientation ambiguë sans QR"


def test_template_json_donne_toute_zone_par_identifiant() -> None:
    template = make_template()
    reloaded = Template.from_json(template.to_json())

    assert reloaded.version == template.version
    for zone in template.zones:
        assert reloaded.zone(zone.id) == zone
    with pytest.raises(KeyError):
        reloaded.zone("n-existe-pas")


def test_inventaire_exact_des_zones() -> None:
    """Test de règle : rend `decisions/0003` exécutable. Une grille de chiffres ajoutée
    sans avoir relu la décision fait échouer ce test, pas seulement une revue de code."""
    assert make_template().types() == ZONE_TYPES
    assert ZONE_TYPES == {"marqueur", "qr", "grille_lettres", "bulle_qcm", "cadre_ouvert"}


def test_refuse_un_type_de_zone_inconnu() -> None:
    from tali.render.sheet import Zone

    with pytest.raises(SheetError) as err:
        Zone("x", "grille_chiffres", 0, 0, 1, 1)
    assert "grille_chiffres" in str(err.value)


def test_refuse_des_identifiants_de_zone_en_double() -> None:
    from tali.render.sheet import Zone

    with pytest.raises(SheetError) as err:
        Template(version="1", zones=(Zone("a", "qr", 0, 0, 1, 1), Zone("a", "qr", 1, 1, 1, 1)))
    assert "a" in str(err.value)


def test_une_seule_case_par_lettre() -> None:
    """Décision `0003` C : une lettre isolée par case, pas une signature libre."""
    template = make_template()
    lettres = [z for z in template.zones if z.type == "grille_lettres"]
    assert all(z.width_mm == z.height_mm for z in lettres), "les cases doivent être carrées"


def test_les_dimensions_viennent_dun_seul_endroit() -> None:
    """Changer `dimensions.py` seul doit suffire à redimensionner tout le gabarit."""
    from tali.render.dimensions import Dimensions

    grand = build_template(n_qcm_questions=1, n_qcm_choices=1, n_open_questions=1,
                            dims=Dimensions(qr_size_mm=30.0))
    assert grand.zone("qr").width_mm == 30.0
