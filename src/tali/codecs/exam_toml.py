"""Lecture et écriture d'`exam.toml`.

Le schéma est **fermé** : toute table et toute clé inconnue est refusée, en la nommant.
Un `exam.toml` est écrit à la main, et un champ ignoré en silence est un piège — on
croit avoir configuré quelque chose qui n'a aucun effet.

L'écriture est **canonique** : même ordre, même mise en forme, toujours. C'est ce qui
rend le round-trip textuel vérifiable, et c'est le format que produira `tali init`.
"""

from __future__ import annotations

import tomllib
from datetime import datetime
from pathlib import Path

from tali.domain.exam import (
    AnswerSheet,
    Exam,
    ExamError,
    Identity,
    Phases,
    Shuffle,
)

_SCHEMA: dict[str, dict[str, type]] = {
    "exam": {"id": str, "title": str, "seed": int, "copies": int},
    "answer_sheet": {"separate": bool, "pages": int},
    "identity": {"roster": str},
    "shuffle": {"exercises": bool, "questions": str, "answers": bool},
    "phases": {"note": str, "correction": str, "claims_deadline": str},
}

_PHASE_FORMAT = "%Y-%m-%dT%H:%M"


def _type_name(expected: type) -> str:
    return {str: "une chaîne", int: "un entier", bool: "un booléen"}[expected]


def _check_table(name: str, table: object, fields: dict[str, type]) -> dict[str, object]:
    if not isinstance(table, dict):
        raise ExamError(f"[{name}] doit être une table")
    for key in table:
        if key not in fields:
            raise ExamError(
                f"champ inconnu : {name}.{key} — champs admis : "
                f"{', '.join(sorted(fields))}"
            )
    for key, expected in fields.items():
        if key not in table:
            raise ExamError(f"champ manquant : {name}.{key}")
        value = table[key]
        # bool est une sous-classe de int : sans ce garde-fou, `pages = true` passerait.
        if isinstance(value, bool) != (expected is bool) or not isinstance(value, expected):
            raise ExamError(f"{name}.{key} doit être {_type_name(expected)}, reçu {value!r}")
    return dict(table)


def _phase(raw: dict[str, object], key: str) -> datetime:
    try:
        return datetime.strptime(str(raw[key]), _PHASE_FORMAT)
    except ValueError as exc:
        raise ExamError(
            f"phases.{key} doit être une date de la forme 2026-01-20T18:00, "
            f"reçu {raw[key]!r}"
        ) from exc


def loads(text: str) -> Exam:
    """Construit un `Exam` depuis le contenu d'un `exam.toml`."""
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ExamError(f"exam.toml n'est pas un TOML valide : {exc}") from exc

    for table in data:
        if table not in _SCHEMA:
            raise ExamError(
                f"table inconnue : [{table}] — tables admises : "
                f"{', '.join(_SCHEMA)}"
            )
    for table in _SCHEMA:
        if table not in data:
            raise ExamError(f"table manquante : [{table}]")

    t = {name: _check_table(name, data[name], fields) for name, fields in _SCHEMA.items()}
    return Exam(
        id=t["exam"]["id"],
        title=t["exam"]["title"],
        seed=t["exam"]["seed"],
        copies=t["exam"]["copies"],
        answer_sheet=AnswerSheet(**t["answer_sheet"]),
        identity=Identity(**t["identity"]),
        shuffle=Shuffle(**t["shuffle"]),
        phases=Phases(
            note=_phase(t["phases"], "note"),
            correction=_phase(t["phases"], "correction"),
            claims_deadline=_phase(t["phases"], "claims_deadline"),
        ),
    )


def load(path: Path) -> Exam:
    """Lit `exam.toml`. La seule fonction de ce module qui touche au disque."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ExamError(f"{path} illisible : {exc}") from exc
    return loads(text)


def _scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def dumps(exam: Exam) -> str:
    """Rend l'`exam.toml` canonique de cet examen.

    L'ordre des tables et des clés est celui de `_SCHEMA`, jamais celui du fichier lu :
    deux examens égaux produisent le même texte.
    """
    values: dict[str, dict[str, object]] = {
        "exam": {"id": exam.id, "title": exam.title, "seed": exam.seed, "copies": exam.copies},
        "answer_sheet": {"separate": exam.answer_sheet.separate, "pages": exam.answer_sheet.pages},
        "identity": {"roster": exam.identity.roster},
        "shuffle": {
            "exercises": exam.shuffle.exercises,
            "questions": exam.shuffle.questions,
            "answers": exam.shuffle.answers,
        },
        "phases": {
            key: getattr(exam.phases, key).strftime(_PHASE_FORMAT)
            for key in _SCHEMA["phases"]
        },
    }
    blocks = []
    for table, fields in _SCHEMA.items():
        lines = [f"[{table}]"]
        lines += [f"{key} = {_scalar(values[table][key])}" for key in fields]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"
