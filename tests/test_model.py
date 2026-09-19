"""Les objets du domaine — purs, construits directement, sans passer par un fichier.

Le format `exam.toml` a ses propres tests dans `test_exam_toml.py`. Cette séparation
n'est pas arbitraire : elle reflète la frontière `tali.domain` / `tali.codecs`, et le
dernier test de ce fichier la vérifie.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from tali.domain.exam import (
    AnswerSheet,
    Exam,
    ExamError,
    Identity,
    Phases,
    Shuffle,
)

_T0 = datetime(2026, 1, 20, 18, 0)
_T1 = datetime(2026, 1, 23, 9, 0)
_T2 = datetime(2026, 1, 30, 23, 59)


def make_exam(**overrides: object) -> Exam:
    """Un examen valide, pour ne pas répéter les six sous-objets dans chaque test."""
    fields = {
        "id": "ct-2026-01",
        "title": "Contrôle optimal — Examen final",
        "seed": 4711,
        "copies": 220,
        "answer_sheet": AnswerSheet(separate=True, pages=2),
        "identity": Identity(roster="roster.csv"),
        "shuffle": Shuffle(exercises=True, questions="within_exercise", answers=True),
        "phases": Phases(note=_T0, correction=_T1, claims_deadline=_T2),
    }
    fields.update(overrides)
    return Exam(**fields)  # type: ignore[arg-type]


def test_construit_un_examen_valide() -> None:
    exam = make_exam()
    assert exam.copies == 220
    assert exam.shuffle.questions == "within_exercise"


def test_refuse_une_valeur_de_melange_inconnue() -> None:
    with pytest.raises(ExamError) as err:
        make_exam(shuffle=Shuffle(exercises=True, questions="partout", answers=True))
    assert "shuffle.questions" in str(err.value)


def test_refuse_des_phases_dans_le_desordre() -> None:
    """La note ne peut pas être publiée après la correction."""
    with pytest.raises(ExamError) as err:
        make_exam(phases=Phases(note=_T1, correction=_T0, claims_deadline=_T2))
    assert "phases" in str(err.value)


def test_refuse_moins_dune_copie() -> None:
    with pytest.raises(ExamError) as err:
        make_exam(copies=0)
    assert "exam.copies" in str(err.value)


def test_cle_de_correction_est_par_copie() -> None:
    """Il n'existe pas de clé d'examen : chaque copie a la sienne (§8.3).

    Le mélange n'est pas encore implémenté, mais l'adressage l'est — c'est lui qui
    coûterait cher à rétro-adapter.
    """
    exam = make_exam()
    assert not hasattr(exam, "correction"), "pas de clé globale sur l'examen"

    keys = [exam.correction_key(n) for n in range(1, exam.copies + 1)]
    assert [k.copy_id for k in keys] == list(range(1, exam.copies + 1))
    assert len({k.seed for k in keys}) == exam.copies, "deux copies partagent une graine"


def test_deux_examens_identiques_donnent_les_memes_cles() -> None:
    """Déterminisme entre exécutions : `hash()` ne l'aurait pas donné."""
    assert make_exam().correction_key(7) == make_exam().correction_key(7)


def test_changer_la_graine_change_toutes_les_cles() -> None:
    a, b = make_exam(seed=4711).correction_key(7), make_exam(seed=4712).correction_key(7)
    assert a.seed != b.seed


def test_refuse_un_numero_de_copie_hors_bornes() -> None:
    exam = make_exam()
    for hors in (0, exam.copies + 1):
        with pytest.raises(ExamError) as err:
            exam.correction_key(hors)
        assert "copy_id" in str(err.value)


def test_le_domaine_nimporte_aucun_format() -> None:
    """Règle d'architecture : `tali.domain` ignore TOML, et le vérifie (AGENTS.md).

    Inventaire exact plutôt qu'absence ponctuelle : un import de `json` ou `yaml`
    ajouté demain fera échouer ce test.
    """
    import ast
    import pathlib

    source = pathlib.Path(Exam.__module__.replace(".", "/") + ".py")  # tali/domain/exam.py
    src_root = pathlib.Path(__file__).parents[1] / "src"
    tree = ast.parse((src_root / source).read_text(encoding="utf-8"))
    imported = {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imported == {"__future__", "dataclasses", "datetime", "hashlib"}
