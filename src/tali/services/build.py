"""`tali build` : `exam.toml` → copies PDF, clés, gabarit (décision `0004`).

`build(exam_dir)` est pure quant au chemin : jamais de chemin configuré, `exam_dir` est
toujours passé explicitement — la CLI y met le dossier courant, les tests y mettent un
`tmp_path`. Aucune des deux ne s'écarte de cette règle.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from tali.codecs import exam_toml
from tali.domain.exam import Exam
from tali.render.canvas import Canvas, ReportLabBackend
from tali.render.dimensions import DEFAULT
from tali.render.geometry import mm_to_points
from tali.render.sheet import Template, build_template

# Comptages de contenu : provisoires, en attendant que le sujet réel soit rédigé (#9,
# human-only) et son analyse programmatique implémentée — hors périmètre de novembre
# (AGENTS.md). Suffisant pour prouver la chaîne exam.toml → copies, sans contenu réel.
PLACEHOLDER_QCM_QUESTIONS = 10
PLACEHOLDER_QCM_CHOICES = 4
PLACEHOLDER_OPEN_QUESTIONS = 3


class BuildError(ValueError):
    """`exam.toml` absent ou invalide, ou dossier de sortie inutilisable."""


@dataclass(frozen=True)
class BuildResult:
    n_copies: int
    out_dir: Path


def build(exam_dir: Path) -> BuildResult:
    """Construit toutes les copies d'un examen dans `exam_dir/build/`."""
    exam_path = exam_dir / "exam.toml"
    if not exam_path.is_file():
        raise BuildError(f"{exam_path} introuvable — `tali build` s'exécute dans un dossier d'examen")
    exam = exam_toml.load(exam_path)

    template = build_template(
        n_qcm_questions=PLACEHOLDER_QCM_QUESTIONS,
        n_qcm_choices=PLACEHOLDER_QCM_CHOICES,
        n_open_questions=PLACEHOLDER_OPEN_QUESTIONS,
    )

    out_dir = exam_dir / "build"
    (out_dir / "copies").mkdir(parents=True, exist_ok=True)
    (out_dir / "keys").mkdir(parents=True, exist_ok=True)
    (out_dir / "template.json").write_text(template.to_json(), encoding="utf-8")

    for copy_id in range(1, exam.copies + 1):
        _write_key(exam, copy_id, out_dir / "keys" / f"{copy_id:04d}.json")
        _render_copy(exam, template, copy_id, out_dir / "copies" / f"{copy_id:04d}.pdf")

    return BuildResult(n_copies=exam.copies, out_dir=out_dir)


def _write_key(exam: Exam, copy_id: int, path: Path) -> None:
    key = exam.correction_key(copy_id)
    path.write_text(json.dumps({"copy_id": key.copy_id, "seed": key.seed}), encoding="utf-8")


def _render_copy(exam: Exam, template: Template, copy_id: int, path: Path) -> None:
    """Dessine une page pour cette copie. Une seule page : le gabarit à plusieurs
    pages n'est pas encore couvert (`answer_sheet.pages` non consulté ici)."""
    backend = ReportLabBackend(
        path, mm_to_points(DEFAULT.page_width_mm), mm_to_points(DEFAULT.page_height_mm)
    )
    canvas = Canvas(backend, DEFAULT.page_height_mm)
    for zone in template.zones:
        if zone.type == "marqueur":
            canvas.rect(zone.x_mm, zone.y_mm, zone.width_mm, zone.height_mm, fill=True)
        elif zone.type == "qr":
            payload = f"tali:{exam.id}:{copy_id:04d}:1:{template.version}"
            canvas.qr(zone.x_mm, zone.y_mm, zone.width_mm, payload)
        else:
            canvas.rect(zone.x_mm, zone.y_mm, zone.width_mm, zone.height_mm)
    backend.new_page()
    backend.save()
