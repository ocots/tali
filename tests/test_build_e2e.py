"""`tali build`, bout en bout : `exam.toml` → copies, clés, gabarit (décision `0004`).

Utilise l'examen synthétique d'`examples/` — il sert à la fois d'exemple exécutable et
de fixture, pour ne pas dupliquer une définition d'examen de plus.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from tali.cli import app
from tali.services.build import BuildError, build

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-exam" / "exam.toml"


@pytest.fixture
def exam_dir(tmp_path: Path) -> Path:
    """Une copie de l'examen synthétique, isolée dans un répertoire temporaire — les
    tests n'écrivent jamais dans `examples/` (décision 0004 : le dépôt ne produit rien)."""
    shutil.copy(EXAMPLE, tmp_path / "exam.toml")
    return tmp_path


def test_produit_exactement_n_copies(exam_dir: Path) -> None:
    """220 demandées, 220 produites : attrape la troncature silencieuse, qui ne se
    verrait qu'au moment d'imprimer."""
    result = build(exam_dir)

    assert result.n_copies == 220
    copies = sorted((exam_dir / "build" / "copies").glob("*.pdf"))
    keys = sorted((exam_dir / "build" / "keys").glob("*.json"))
    assert len(copies) == 220
    assert len(keys) == 220
    assert (exam_dir / "build" / "template.json").is_file()


def test_deux_executions_donnent_les_memes_cles(exam_dir: Path) -> None:
    """Le déterminisme permet de régénérer une copie perdue à l'identique. On compare
    les clés, pas les PDF : ceux-ci portent un horodatage, jamais identiques octet à
    octet d'une exécution à l'autre."""
    build(exam_dir)
    first = (exam_dir / "build" / "keys" / "0042.json").read_text()

    shutil.rmtree(exam_dir / "build")
    build(exam_dir)
    second = (exam_dir / "build" / "keys" / "0042.json").read_text()

    assert first == second
    assert json.loads(first)["seed"] != 0


def test_refuse_labsence_dexam_toml(tmp_path: Path) -> None:
    with pytest.raises(BuildError) as err:
        build(tmp_path)
    assert "exam.toml" in str(err.value)


def test_cli_build_utilise_le_dossier_courant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Décision 0004 : jamais un chemin configuré, toujours le dossier courant."""
    shutil.copy(EXAMPLE, tmp_path / "exam.toml")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["build"])

    assert result.exit_code == 0, result.output
    assert "220 copie" in result.output
    assert (tmp_path / "build" / "template.json").is_file()
