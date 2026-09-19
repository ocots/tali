# Tâche #4 — tali build — générer les copies d'un dossier d'examen

- **rôle** : `feature`
- **critère de complétion** : `.venv/bin/python -m pytest -q tests/test_build_e2e.py::test_produit_exactement_n_copies tests/test_build_e2e.py::test_deux_executions_donnent_les_memes_cles`
- **périmètre** : `src/tali/cli.py`, `src/tali/services/**`, `tests/test_build_e2e.py`, `examples/**`
- **budget** : 1 à 2 sessions

## Plan

- [x] `src/tali/cli.py` — n'existait pas encore, créé avec `click`
- [x] `services/build.py` — exam.toml → copies, clés, template.json
- [x] `examples/synthetic-exam/` — sert d'exemple et de fixture (décision 0004)
- [x] `tests/test_build_e2e.py`

## Journal

**Pas de contenu réel pour les zones QCM/ouvertes** : le sujet n'est pas encore
rédigé (#9, human-only), son analyse est hors périmètre de novembre. `build_template`
prend des comptages **provisoires** (`PLACEHOLDER_*`) — cette tâche prouve la chaîne
exam.toml → copies, pas le contenu d'un examen réel.

**`src/tali/cli.py` n'existait pas** malgré la référence dans `pyproject.toml`. Créé
avec `click`, ajouté aux dépendances. Une commande : `build`.

**`Canvas.rect` ne savait pas remplir** — nécessaire pour les marqueurs, pas les
cadres. Ajouté `fill: bool = False`, rétrocompatible.

**`examples/**` n'était couvert que par le rôle `doc`, jamais `feature`** — corrigé sur
`main`, hors PR (troisième défaut de ce genre trouvé en exécutant, pas en relisant).
L'exemple sert aussi de fixture (décision 0004) : les tests le copient dans `tmp_path`.

Mutation-testés les deux tests du contrat (troncature, clé non déterministe) : tués.

## Bilan

`build(exam_dir)` : lit `exam.toml`, écrit `build/{copies,keys}/NNNN.{pdf,json}` et
`build/template.json`. `tali build` (CLI) l'appelle sur le dossier courant, jamais un
chemin configuré — vérifié par `test_cli_build_utilise_le_dossier_courant`.

## Points d'incertitude

- Une seule page par copie : `answer_sheet.pages` n'est pas encore consulté.
- Comptages de contenu provisoires (`PLACEHOLDER_*`), à remplacer quand le sujet réel
  sera analysable — hors périmètre de novembre pour l'instant.
- 220 PDF réels par test : la suite est passée de ~12 s à ~22 s, à surveiller.
