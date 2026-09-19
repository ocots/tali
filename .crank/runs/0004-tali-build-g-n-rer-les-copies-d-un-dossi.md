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

**Pas de contenu réel pour dessiner les zones QCM/ouvertes** : le sujet n'est pas
encore rédigé (#9, human-only), et son analyse est hors périmètre de novembre
(AGENTS.md). `build_template` est appelé avec des comptages **provisoires**
(`PLACEHOLDER_*`), documentés comme tels — cette tâche prouve la chaîne
exam.toml → copies, pas le contenu d'un examen réel.

**`src/tali/cli.py` n'existait pas** malgré la référence dans `pyproject.toml`
(`tali = "tali.cli:app"`). Créé avec `click` (même famille que `crank`), ajouté aux
dépendances. Une seule commande pour l'instant : `build`.

**`Canvas.rect` ne savait pas remplir** — nécessaire pour les marqueurs de calage
(carrés pleins), pas pour les cadres (contour seul). Ajouté un paramètre `fill: bool
= False` à `Canvas.rect`/`Backend.rect`/`ReportLabBackend.rect`, rétrocompatible ;
`test_rect_ne_remplit_pas_par_defaut` couvre le défaut et le cas explicite.

**L'exemple synthétique sert aussi de fixture** (décision 0004) : les tests copient
`examples/synthetic-exam/exam.toml` dans un `tmp_path`, jamais n'écrivent dans
`examples/` — le dépôt ne doit produire aucune donnée, même de test.

Mutation-testés les deux tests du contrat (troncature d'une copie, clé non
déterministe) : les deux mutants sont tués.

## Bilan

`build(exam_dir)` : lit `exam.toml`, écrit `build/{copies,keys}/NNNN.{pdf,json}` et
`build/template.json`. `tali build` (CLI) l'appelle sur le dossier courant, jamais un
chemin configuré — vérifié par `test_cli_build_utilise_le_dossier_courant`.

## Points d'incertitude

- Une seule page par copie : `answer_sheet.pages` n'est pas encore consulté. Les sujets
  à plusieurs pages ne sont pas couverts.
- Les comptages de contenu sont provisoires (`PLACEHOLDER_*`) — à remplacer quand le
  sujet réel sera analysable, hors périmètre de novembre pour l'instant.
- 220 PDF réels par test (~2,5 s) : la suite complète est passée de ~12 s à ~22 s.
  À surveiller si d'autres tâches ajoutent des tests aussi coûteux.
