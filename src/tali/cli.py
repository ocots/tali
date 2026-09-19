"""L'interface en ligne de commande de `tali`.

Chaque commande s'exécute dans le dossier courant — jamais sur un chemin configuré
(décision `0004`). `tali` ne connaît aucun chemin de données, comme `git` ne connaît
aucun dépôt avant qu'on `cd` dedans.
"""

from __future__ import annotations

from pathlib import Path

import click

from tali.services.build import BuildError, build


@click.group()
def app() -> None:
    """tali — aide à la correction de copies d'examen scannées."""


@app.command()
def build_() -> None:
    """Génère les copies de l'examen du dossier courant."""
    try:
        result = build(Path.cwd())
    except BuildError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"{result.n_copies} copie(s) générée(s) dans {result.out_dir}")


app.add_command(build_, name="build")
