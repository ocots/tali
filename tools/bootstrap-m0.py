#!/usr/bin/env python3
"""Crée les issues de M0. À lancer UNE FOIS, après le premier push sur GitHub.

    python3 tools/bootstrap-m0.py --dry-run    # voir ce qui serait créé
    python3 tools/bootstrap-m0.py

Ce n'est pas une file d'attente parallèle : c'est un amorçage. Une fois lancé, la
seule source de vérité est GitHub, et ce fichier peut être supprimé.

⚠️  DÉJÀ LANCÉ (2026-09-19). GitHub a depuis divergé de ce fichier : l'issue #1
    a été découpée en #1 (domaine, objets purs) et #11 (codec exam.toml, `blocked`
    sur #1) après que sa PR a dépassé `max_diff_lines` une fois les deux briques
    réunies. Ce fichier n'est plus rejoué — il documente l'intention de départ,
    pas l'état courant du backlog.

⚠️  Relis les critères `done` avant de lancer. C'est le champ qui décide de tout
    (AGENTS.md) : un `done` mal formulé produit du volume, pas du progrès.

    Et sache ce que `done` ne garantit PAS : nommer un test force l'agent à traiter
    le cas, mais c'est toujours lui qui écrit l'assertion. Rien n'empêche un
    `assert True`. Le rempart reste ta relecture — et plus tard le score de mutation.
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

# La chaîne de génération a une échéance DURE (la feuille s'imprime une fois) et elle
# est sérielle. La lecture a une échéance souple et se parallélise. `priority:high`
# encode cette asymétrie dans la file — sans ça, rien ne la porte (AGENTS.md).
CRITIQUE = ("priority:high",)

ISSUES: list[Issue] = [
    # ══ Chaîne de génération — chemin critique, sérielle ══════════════════════
    Issue(
        title="Modèle d'examen — lire et valider exam.toml",
        context=(
            "Le dossier d'examen est autodescriptif et `exam.toml` en est le marqueur "
            "(`decisions/0004`). Première brique : le lire et produire les objets du "
            "domaine. Aucun rendu, aucune E/S au-delà de la lecture du fichier.\n\n"
            "⚠️ **Le schéma du §4.3 du cahier des charges est normatif.** Ne pas en "
            "inventer un autre : si quelque chose y manque ou s'y contredit, ouvrir une "
            "décision dans `decisions/` et s'arrêter. Le schéma d'`exam.toml` est une "
            "décision de conception structurante, pas un détail d'implémentation."
        ),
        done=(
            f".venv/bin/python -m pytest -q {T}/test_model.py::test_round_trip_toml "
            f"{T}/test_model.py::test_rejette_un_champ_inconnu_en_le_nommant "
            f"{T}/test_model.py::test_cle_de_correction_est_par_copie"
        ),
        touche=(f"{P}/domain/**", f"{P}/codecs/**", f"{T}/test_model.py"),
        labels=CRITIQUE,
        attendu=(
            "modèles purs : `Exam`, `Exercise`, `Question`, `Zone`, `Sheet`",
            "`test_round_trip_toml` : charger puis réécrire rend le même contenu. "
            "Propriété objective, et elle attrape le parsing qui perd de l'information — "
            "contrairement à « charge un exemple minimal », où c'est l'agent qui définit "
            "ce qu'est un minimum",
            "validation aux frontières avec des messages d'erreur **qui nomment le champ "
            "fautif** — le fichier est écrit à la main, les fautes de frappe sont la norme",
            "**la clé de correction est par copie dès maintenant**, même sans mélange "
            "(cahier des charges §8.3) — rétro-adapter coûterait cher",
        ),
    ),
    Issue(
        title="Primitive de dessin — interface étroite au-dessus de ReportLab",
        context=(
            "ReportLab est acté (`decisions/0002`), mais il ne doit pas s'infiltrer "
            "partout : une interface étroite permet d'en changer sans toucher au reste.\n\n"
            "Cette intention est **vérifiée, pas promise** — voir le dernier critère."
        ),
        done=(
            f".venv/bin/python -m pytest -q {T}/test_canvas.py::test_origine_en_haut_a_gauche "
            f"{T}/test_canvas.py::test_conversion_millimetres_vers_points "
            f"{T}/test_canvas.py::test_qr_pose_a_la_position_demandee "
            f"{T}/test_canvas.py::test_reportlab_nest_importe_que_dans_render"
        ),
        touche=(f"{P}/render/**", f"{T}/test_canvas.py"),
        labels=CRITIQUE,
        attendu=(
            "`rect`, `circle`, `text`, `qr`, et rien de plus tant que rien de plus n'est utile",
            "**coordonnées en millimètres, origine en haut à gauche** — ReportLab compte "
            "en points depuis le bas ; faire la conversion une fois ici évite de la refaire "
            "partout et de s'y tromper",
            "`test_reportlab_nest_importe_que_dans_render` : **test de règle**. Parcourir "
            "les imports de `src/tali/**` et vérifier qu'aucun module hors `render/` "
            "n'importe `reportlab`. On ne demande pas de promettre le confinement, on le "
            "vérifie — même principe que le contrôle AST du rôle `doc`",
            "les tests vérifient des positions, sans rendre d'image",
        ),
    ),
    Issue(
        title="Gabarit de la feuille de réponses",
        context=(
            "Compose la feuille décrite par `decisions/0001` et produit `template.json`, "
            "qui donne les coordonnées de chaque zone. C'est le chemin critique du "
            "23 novembre : la feuille est imprimée une fois."
        ),
        done=(
            f".venv/bin/python -m pytest -q {T}/test_sheet.py::test_cinq_marqueurs_dont_un_asymetrique "
            f"{T}/test_sheet.py::test_template_json_donne_toute_zone_par_identifiant "
            f"{T}/test_sheet.py::test_inventaire_exact_des_zones"
        ),
        touche=(f"{P}/render/**", f"{T}/test_sheet.py"),
        labels=CRITIQUE,
        attendu=(
            "4 carrés pleins aux coins **plus un 5e** près du haut-gauche pour l'orientation",
            "QR par page : `tali:<exam>:<copie>:<page>:<version>`",
            "grilles `NOM` / `PRÉNOM`, une lettre par case (`decisions/0003`)",
            "bulles QCM et cadres de réponse ouverte",
            "`test_inventaire_exact_des_zones` : **test de règle**. L'ensemble des **types** "
            "de zone produits est exactement `{marqueur, qr, grille_lettres, bulle_qcm, "
            "cadre_ouvert}` — ni plus, ni moins. Rend `decisions/0003` exécutable : une "
            "grille de chiffres ajoutée sans avoir lu la décision fait échouer le test",
            "**toutes les dimensions dans un seul endroit déclaratif** — le spike S2 n'a pas "
            "encore tourné, ses mesures demanderont de les ajuster, et ça doit rester un "
            "changement d'un fichier",
            "`template.json` : toute zone doit être retrouvable par son identifiant",
        ),
    ),
    Issue(
        title="tali build — générer les copies d'un dossier d'examen",
        context=(
            "Bout en bout : `exam.toml` → `build/copies/NNNN.pdf` + `build/keys/NNNN.json` "
            "+ `build/template.json`. Sans mélange pour l'instant (il viendra en M3)."
        ),
        done=(
            f".venv/bin/python -m pytest -q {T}/test_build_e2e.py::test_produit_exactement_n_copies "
            f"{T}/test_build_e2e.py::test_deux_executions_donnent_les_memes_cles"
        ),
        touche=(f"{P}/cli.py", f"{P}/services/**", f"{T}/test_build_e2e.py", "examples/**"),
        budget="1 à 2 sessions",
        labels=CRITIQUE + ("blocked",),
        attendu=(
            "`test_produit_exactement_n_copies` : 220 demandées, 220 produites. Attrape la "
            "troncature silencieuse, qui ne se verrait qu'au moment d'imprimer",
            "`test_deux_executions_donnent_les_memes_cles` : le **déterminisme** permet de "
            "regénérer une copie perdue à l'identique. Comparer les clés, pas les PDF : "
            "ceux-ci portent un horodatage et ne sont pas identiques octet à octet",
            "un examen d'exemple **synthétique** dans `examples/` — il sert aussi de fixture",
            "la commande s'exécute dans le dossier courant, jamais sur un chemin configuré "
            "(`decisions/0004`)",
            "⚠️ `blocked` : retirer le label quand le modèle et le gabarit sont fusionnés",
        ),
    ),
    # ══ Chaîne de lecture — échéance souple, parallélisable ═══════════════════
    Issue(
        title="Lecture du QR d'une page",
        context=(
            "Décoder `tali:<exam>:<copie>:<page>:<version>` depuis une image de page.\n\n"
            "Doit **refuser proprement** une version de gabarit inconnue plutôt que de "
            "lire de travers une feuille d'une autre session."
        ),
        done=(
            f".venv/bin/python -m pytest -q {T}/test_qr.py::test_decode_un_qr_genere "
            f"{T}/test_qr.py::test_refuse_une_version_de_gabarit_inconnue"
        ),
        touche=(f"{P}/vision/**", f"{T}/test_qr.py"),
        budget="½ session",
    ),
    Issue(
        title="Détection des marqueurs et homographie",
        context=(
            "Le cœur du recalage : depuis une image quelconque, retrouver les marqueurs de "
            "coin, lever l'orientation avec le 5e, et produire l'homographie "
            "millimètres ↔ pixels qui permet de découper n'importe quelle zone du gabarit."
        ),
        done=(
            f".venv/bin/python -m pytest -q {T}/test_locate.py::test_retrouve_une_homographie_connue "
            f"{T}/test_locate.py::test_leve_orientation_180_degres_sans_qr "
            f"{T}/test_locate.py::test_refuse_si_moins_de_trois_marqueurs"
        ),
        touche=(f"{P}/vision/**", f"{T}/test_locate.py"),
        budget="1 à 2 sessions",
        attendu=(
            "fonction **pure** image → homographie, testable sans dépôt ni réseau",
            "`test_retrouve_une_homographie_connue` : appliquer une homographie connue à "
            "l'image, la retrouver à ε près. Propriété de round-trip, autonome — bien plus "
            "informative que le cas identité, et sans dépendre du corpus synthétique",
            "l'orientation doit être levée **sans le QR** : si le QR est abîmé, la "
            "géométrie doit rester récupérable seule",
            "**refuser plutôt que deviner** quand moins de 3 marqueurs sont trouvés",
        ),
    ),
    Issue(
        title="Corpus synthétique — rastérisation, déformations, round-trip",
        context=(
            "L'actif de test le plus précieux du projet (cahier des charges §13.1) : "
            "générer une feuille, la rendre en image, la déformer, et vérifier que le "
            "pipeline retrouve exactement la vérité terrain connue.\n\n"
            "Reproductible, sans aucune donnée personnelle, et couvre à volonté les cas "
            "rares qu'on ne verra jamais assez souvent en vrai.\n\n"
            "Inclut la rastérisation (pypdfium2, `decisions/0002`), qui n'avait pas à être "
            "une tâche séparée : ~20 lignes de bibliothèque dont ce corpus est le seul "
            "consommateur, et un créneau de relecture est plus cher que ça."
        ),
        done=(
            f".venv/bin/python -m pytest -q {T}/test_synthetic.py::test_rend_une_page_a_200_dpi "
            f"{T}/test_synthetic.py::test_round_trip_sans_deformation "
            f"{T}/test_synthetic.py::test_round_trip_perspective_30_degres "
            f"{T}/test_synthetic.py::test_refuse_plutot_que_de_se_tromper_aux_extremes"
        ),
        touche=(f"{T}/support/**", f"{T}/test_synthetic.py"),
        budget="2 sessions",
        labels=("blocked",),
        attendu=(
            "rastérisation PDF → image à un dpi donné — dépendance **de test uniquement**",
            "déformations paramétrées : rotation, perspective, flou, bruit, contraste, "
            "bavure, pliure",
            "`test_refuse_plutot_que_de_se_tromper_aux_extremes` : **le critère le plus "
            "important**. Aux déformations fortes on veut un refus explicite, pas une "
            "réponse fausse — un recalage silencieusement faux corrompt toute la notation",
            "**pas d'assertion de monotonie** sur la courbe de dégradation : le taux "
            "d'erreur n'a aucune raison d'être monotone (bruit, seuils, discrétisation), "
            "et un test instable finit ignoré. Asserter des **seuils** à des amplitudes "
            "nommées, et produire la courbe comme artefact à regarder",
            "⚠️ `blocked` : retirer le label quand le gabarit, le QR et l'homographie sont "
            "fusionnés",
        ),
    ),
    # ══ Chemin critique physique — aucun agent ne peut le faire ═══════════════
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
        print("\nEnsuite : `crank next`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
