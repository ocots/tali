#!/usr/bin/env python3
"""Crée les issues de M0. À lancer UNE FOIS, après le premier push sur GitHub.

    python3 tools/bootstrap-m0.py --dry-run    # voir ce qui serait créé
    python3 tools/bootstrap-m0.py

Ce n'est pas une file d'attente parallèle : c'est un amorçage. Une fois lancé, la
seule source de vérité est GitHub, et ce fichier peut être supprimé.

⚠️  Relis les critères `done` avant de lancer. C'est le champ qui décide de tout
    (AGENTS.md) : un `done` mal formulé produit du volume, pas du progrès. Si l'un
    d'eux te paraît vague ou invérifiable, corrige-le ici d'abord.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class Issue:
    title: str
    context: str
    role: str = "feature"
    done: str = ""
    touche: tuple[str, ...] = ()
    budget: str = "1 session"
    labels: tuple[str, ...] = ()
    attendu: tuple[str, ...] = field(default_factory=tuple)

    def body(self) -> str:
        parts = [self.context.strip(), ""]
        if self.attendu:
            parts += ["**Attendu :**", ""]
            parts += [f"- {a}" for a in self.attendu]
            parts += [""]
        if self.done:
            parts += ["```crank", f"role: {self.role}", f"done: {self.done}"]
            if self.touche:
                parts += ["touche:"] + [f"  - {t}" for t in self.touche]
            parts += [f"budget: {self.budget}", "```"]
        return "\n".join(parts)


P = "src/tali"
T = "tests"

ISSUES: list[Issue] = [
    # ── Socle : formats et domaine ────────────────────────────────────────────
    Issue(
        title="Modèle d'examen — lire et valider exam.toml",
        context=(
            "Le dossier d'examen est autodescriptif et `exam.toml` en est le marqueur "
            "(`decisions/0004`). Première brique : le lire et produire les objets du "
            "domaine. Aucun rendu, aucune E/S au-delà de la lecture du fichier."
        ),
        done=f"pytest {T}/test_model.py -q",
        touche=(f"{P}/domain/**", f"{P}/codecs/**", f"{T}/test_model.py"),
        attendu=(
            "modèles purs : `Exam`, `Exercise`, `Question`, `Zone`, `Sheet`",
            "validation aux frontières avec des messages d'erreur utilisables — "
            "le fichier est écrit à la main, les fautes de frappe sont la norme",
            "**la clé de correction est par copie dès maintenant**, même sans mélange "
            "(cahier des charges §8.3) — rétro-adapter coûterait cher",
        ),
    ),
    Issue(
        title="Primitive de dessin — interface étroite au-dessus de ReportLab",
        context=(
            "ReportLab est acté (`decisions/0002`), mais il ne doit pas s'infiltrer "
            "partout : une interface étroite permet d'en changer sans toucher au reste."
        ),
        done=f"pytest {T}/test_canvas.py -q",
        touche=(f"{P}/render/**", f"{T}/test_canvas.py"),
        attendu=(
            "`rect`, `circle`, `text`, `qr`, et rien de plus tant que rien de plus n'est utile",
            "**coordonnées en millimètres, origine en haut à gauche** — ReportLab compte "
            "en points depuis le bas ; faire la conversion une fois ici évite de la refaire "
            "partout et de s'y tromper",
            "les tests vérifient des positions, sans rendre d'image",
        ),
    ),
    # ── Génération ────────────────────────────────────────────────────────────
    Issue(
        title="Gabarit de la feuille de réponses",
        context=(
            "Compose la feuille décrite par `decisions/0001` et produit `template.json`, "
            "qui donne les coordonnées de chaque zone. C'est le chemin critique du "
            "23 novembre : la feuille est imprimée une fois."
        ),
        done=f"pytest {T}/test_sheet.py -q",
        touche=(f"{P}/render/**", f"{T}/test_sheet.py"),
        attendu=(
            "4 carrés pleins aux coins **plus un 5e** près du haut-gauche pour l'orientation",
            "QR par page : `tali:<exam>:<copie>:<page>:<version>`",
            "grilles `NOM` / `PRÉNOM`, une lettre par case (`decisions/0003`)",
            "bulles QCM et cadres de réponse ouverte",
            "**aucune grille de chiffres** — décision 0003",
            "`template.json` : toute zone doit être retrouvable par son identifiant",
        ),
    ),
    Issue(
        title="tali build — générer les copies d'un dossier d'examen",
        context=(
            "Bout en bout : `exam.toml` → `build/copies/NNNN.pdf` + `build/keys/NNNN.json` "
            "+ `build/template.json`. Sans mélange pour l'instant (il viendra en M3)."
        ),
        done=f"pytest {T}/test_build_e2e.py -q",
        touche=(f"{P}/cli.py", f"{P}/services/**", f"{T}/test_build_e2e.py", "examples/**"),
        budget="1 à 2 sessions",
        labels=("blocked",),
        attendu=(
            "un examen d'exemple **synthétique** dans `examples/` — il sert aussi de fixture",
            "la commande s'exécute dans le dossier courant, jamais sur un chemin configuré",
            "⚠️ `blocked` : retirer le label quand le modèle et le gabarit sont fusionnés",
        ),
    ),
    # ── Lecture ───────────────────────────────────────────────────────────────
    Issue(
        title="Rastérisation d'un PDF pour les tests",
        context=(
            "pypdfium2 (`decisions/0002`) : rendre une page en image à un dpi donné. "
            "Dépendance **de test uniquement**, pas d'exécution.\n\n"
            "Petite brique, mais c'est elle qui porte tout le corpus synthétique : sans "
            "elle, impossible de tester le round-trip sans imprimante."
        ),
        done=f"pytest {T}/test_raster.py -q",
        touche=(f"{T}/support/**", f"{T}/test_raster.py"),
        budget="½ session",
    ),
    Issue(
        title="Lecture du QR d'une page",
        context=(
            "Décoder `tali:<exam>:<copie>:<page>:<version>` depuis une image de page.\n\n"
            "Doit **refuser proprement** une version de gabarit inconnue plutôt que de "
            "lire de travers une feuille d'une autre session."
        ),
        done=f"pytest {T}/test_qr.py -q",
        touche=(f"{P}/vision/**", f"{T}/test_qr.py"),
        budget="½ session",
    ),
    Issue(
        title="Détection des marqueurs et homographie",
        context=(
            "Le cœur du recalage : depuis une image quelconque, retrouver les 4 marqueurs "
            "de coin, lever l'orientation avec le 5e, et produire l'homographie "
            "millimètres ↔ pixels qui permet de découper n'importe quelle zone du gabarit."
        ),
        done=f"pytest {T}/test_locate.py -q",
        touche=(f"{P}/vision/**", f"{T}/test_locate.py"),
        budget="1 à 2 sessions",
        attendu=(
            "fonction **pure** image → homographie, testable sans dépôt ni réseau",
            "l'orientation doit être levée **sans le QR** : si le QR est abîmé, la "
            "géométrie doit rester récupérable seule",
            "refuser plutôt que deviner quand moins de 3 marqueurs sont trouvés",
        ),
    ),
    Issue(
        title="Corpus synthétique et courbe de dégradation",
        context=(
            "L'actif de test le plus précieux du projet (cahier des charges §13.1) : "
            "générer une feuille, la rendre en image, la déformer, et vérifier que le "
            "pipeline retrouve exactement la vérité terrain connue.\n\n"
            "Reproductible, sans aucune donnée personnelle, et couvre à volonté les cas "
            "rares qu'on ne verra jamais assez souvent en vrai."
        ),
        done=f"pytest {T}/test_synthetic.py -q",
        touche=(f"{T}/support/**", f"{T}/test_synthetic.py"),
        budget="1 à 2 sessions",
        labels=("blocked",),
        attendu=(
            "déformations paramétrées : rotation, perspective, flou, bruit, contraste, "
            "bavure, pliure",
            "**courbe de dégradation** : taux d'erreur en fonction de l'amplitude — "
            "c'est elle qui devient le test de non-régression le plus parlant",
            "⚠️ `blocked` : retirer le label quand rastérisation, QR et homographie sont "
            "fusionnés",
        ),
    ),
    # ── Chemin critique physique ──────────────────────────────────────────────
    Issue(
        title="Spike S2 — le round-trip impression → remplissage → scan",
        context=(
            "**Sur le chemin critique.** Imprimer une grille test sur *ton* imprimante, "
            "la faire remplir salement (ratures, croix débordantes, crayon pâle), scanner "
            "sur *ton* scanner, mesurer.\n\n"
            "Point le plus critique : **le QR est-il encore lisible après impression puis "
            "scan ?** Si non, rien d'autre ne compte.\n\n"
            "Les valeurs de départ à tester sont dans `decisions/0001` §D. Le résultat "
            "peut demander de les ajuster — c'est prévu, et c'est pour ça que ce spike "
            "passe avant S1."
        ),
        labels=("human-only",),
    ),
    Issue(
        title="Rédiger le sujet et le barème de l'examen du 23 novembre",
        context=(
            "**Sur le chemin critique.** ~70 % QCM / 30 % questions ouvertes.\n\n"
            "Rappel de conception : l'outil change la façon d'écrire les sujets "
            "(cahier des charges §9.2 A). Réponses encadrées, questions décomposées en "
            "étapes, réponses qui tiennent dans le cadre prévu."
        ),
        labels=("human-only",),
    ),
    Issue(
        title="Répétition générale — 29 octobre 2026",
        context=(
            "**Le jalon qui décide de tout**, davantage que le 23 novembre lui-même.\n\n"
            "10 feuilles imprimées, remplies salement par des cobayes, scannées, corrigées "
            "par le pipeline.\n\n"
            "Si ça passe, le reste est du confort. Si ça échoue, il reste trois semaines "
            "pour replier sur un sujet classique sans QR — **et cette décision se prend ce "
            "jour-là, pas en novembre.**"
        ),
        labels=("human-only",),
    ),
]


def create(issue: Issue, dry_run: bool) -> None:
    labels = list(issue.labels)
    if issue.done:
        labels.append(f"role:{issue.role}")
    args = ["gh", "issue", "create", "--title", issue.title, "--body", issue.body()]
    for label in labels:
        args += ["--label", label]
    if dry_run:
        print(f"\n{'=' * 78}\n{issue.title}\n{'-' * 78}")
        print(issue.body())
        print(f"labels : {', '.join(labels) or '(aucun)'}")
        return
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ {issue.title}\n  {result.stderr.strip()}", file=sys.stderr)
    else:
        print(f"✓ {result.stdout.strip()}  {issue.title}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="afficher sans créer")
    args = parser.parse_args()

    if not args.dry_run:
        ready = sum(1 for i in ISSUES if i.done and "blocked" not in i.labels)
        print(f"{len(ISSUES)} issues — dont {ready} immédiatement prêtes pour `crank next`.")
        if input("Créer sur GitHub ? [o/N] ").strip().lower() not in ("o", "oui", "y"):
            print("Annulé.")
            return 1

    for issue in ISSUES:
        create(issue, args.dry_run)

    if args.dry_run:
        print(f"\n{'=' * 78}\n{len(ISSUES)} issues seraient créées. Relance sans --dry-run.")
    else:
        print("\nEnsuite : `crank init` pour les labels, puis `crank next`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
