"""`exam.toml` : lecture stricte, écriture canonique (cahier des charges §4.3).

Les tests de construction et de validation du domaine sont dans `test_model.py` — ce
fichier ne teste que le format texte, en tirant parti du round-trip pour ne jamais
avoir à énumérer les champs à la main.
"""

from __future__ import annotations

import pytest

from tali.codecs import exam_toml
from tali.domain.exam import ExamError

# Forme canonique : c'est exactement ce que `dumps` doit produire.
CANONICAL = """\
[exam]
id = "ct-2026-01"
title = "Contrôle optimal — Examen final"
seed = 4711
copies = 220

[answer_sheet]
separate = true
pages = 2

[identity]
roster = "roster.csv"

[shuffle]
exercises = true
questions = "within_exercise"
answers = true

[phases]
note = "2026-01-20T18:00"
correction = "2026-01-23T09:00"
claims_deadline = "2026-01-30T23:59"
"""

# Un second examen dont AUCUNE valeur ne coïncide avec le premier. Sans lui, une
# implémentation qui écrirait les valeurs du premier en dur passerait le round-trip
# — c'est le mutant qui a survécu au premier jet de ce test.
VARIANT = (
    CANONICAL.replace('"ct-2026-01"', '"meca-2027-02"')
    .replace("Contrôle optimal — Examen final", "Mécanique — Rattrapage")
    .replace("seed = 4711", "seed = 99")
    .replace("copies = 220", "copies = 37")
    .replace("separate = true", "separate = false")
    .replace("pages = 2", "pages = 5")
    .replace('"roster.csv"', '"inscrits.csv"')
    .replace("exercises = true", "exercises = false")
    .replace('"within_exercise"', '"none"')
    .replace("answers = true", "answers = false")
    .replace("2026-01-20T18:00", "2027-03-01T08:30")
    .replace("2026-01-23T09:00", "2027-03-04T14:00")
    .replace("2026-01-30T23:59", "2027-03-11T23:59")
)


@pytest.mark.parametrize("text", [CANONICAL, VARIANT], ids=["canonical", "variant"])
def test_round_trip_toml(text: str) -> None:
    """Charger puis réécrire rend le même texte, octet pour octet.

    Propriété objective : elle échoue dès qu'un champ est perdu à la lecture ou omis
    à l'écriture, sans qu'on ait à énumérer les champs dans le test.
    """
    assert exam_toml.dumps(exam_toml.loads(text)) == text


def test_les_deux_fixtures_ne_partagent_aucune_valeur() -> None:
    """Garde-fou du garde-fou : si VARIANT dérivait de CANONICAL sans rien changer,
    le round-trip redeviendrait aveugle aux constantes figées."""
    values = lambda t: {l.split(" = ", 1)[1] for l in t.splitlines() if " = " in l}
    assert values(CANONICAL) & values(VARIANT) == set()


def test_round_trip_est_stable_apres_une_seconde_passe() -> None:
    once = exam_toml.dumps(exam_toml.loads(CANONICAL))
    assert exam_toml.dumps(exam_toml.loads(once)) == once


def test_rejette_un_champ_inconnu_en_le_nommant() -> None:
    """Une faute de frappe doit être signalée, jamais ignorée en silence."""
    text = CANONICAL.replace("copies = 220", "copies = 220\ncopyes = 220")
    with pytest.raises(ExamError) as err:
        exam_toml.loads(text)
    assert "exam.copyes" in str(err.value)


# (transformation de CANONICAL, sous-chaîne attendue dans le message d'erreur).
_REJECTIONS = [
    ("table inconnue", CANONICAL + '\n[identiy]\nroster = "r.csv"\n', "identiy"),
    ("champ manquant", CANONICAL.replace('roster = "roster.csv"\n', ""), "identity.roster"),
    # `bool` hérite de `int` en Python : sans garde-fou, `pages = true` passerait.
    ("booléen pour un entier", CANONICAL.replace("pages = 2", "pages = true"), "answer_sheet.pages"),
]


@pytest.mark.parametrize("text, attendu", [(t, a) for _, t, a in _REJECTIONS],
                         ids=[label for label, _, _ in _REJECTIONS])
def test_rejette_en_nommant_le_champ_fautif(text: str, attendu: str) -> None:
    with pytest.raises(ExamError) as err:
        exam_toml.loads(text)
    assert attendu in str(err.value)
