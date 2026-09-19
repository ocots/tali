# Tâche #1 — Modèle d'examen — objets du domaine

- **rôle** : `feature`
- **critère de complétion** : `pytest -q tests/test_model.py::test_construit_un_examen_valide tests/test_model.py::test_refuse_des_phases_dans_le_desordre tests/test_model.py::test_cle_de_correction_est_par_copie`
- **périmètre** : `src/tali/domain/**`, `tests/test_model.py`
- **budget** : 1 session

## Plan

- [x] Trancher la contradiction §4.3 / décision `0003` (grille de chiffres)
- [x] `domain/exam.py` — objets purs, aucune E/S
- [x] `tests/test_model.py` — construction, validations aux frontières, clé par copie
- [x] Découper la tâche : domaine ici, codec `exam.toml` dans une tâche séparée (#11)

## Journal

**§4.3 vs décision `0003` : `0003` l'emporte.** L'esquisse du §4.3 porte
`[identity] digit_grid = 8` / `name_zone = true` ; `0003` B est postérieure, actée, et
dit l'inverse — pas de grille de chiffres. `[identity]` ne garde que `roster`. Le §4.3
est à corriger, hors de mon périmètre ; signalé ci-dessous.

**L'« Attendu » de l'issue citait `Exercise`/`Question`/`Zone`/`Sheet`.** Aucun n'est une
table de `exam.toml` : `Exercise`/`Question` viennent de `sujet/*.md` (§4.1),
`Zone`/`Sheet` du gabarit (#3, déjà couvert). Non implémentés — `done` ne les demandait
pas, donc rien ne les aurait vérifiés.

**Domaine + codec écrits ensemble d'abord (487 lignes) : trop tard pour la découpe.**
Mutation-testé les trois tests du contrat avant de finaliser : un mutant (`dumps`
figeant `copies` en dur dans la sortie) a survécu, la fixture unique ne distinguant pas
lecture réelle et constante. Corrigé par `VARIANT`, un second examen sans valeur
commune avec le premier, plus un test que les deux ne se recouvrent pas.

En exécutant `crank finalize --dry-run` pour de vrai (pas en le relisant), deux défauts
systémiques sont apparus — corrigés sur `main`, hors PR (`1748b91`) : les 7 `done` du
backlog invoquaient `pytest` nu (résout l'interpréteur système, pas le venv), et aucun
rôle n'autorisait `.crank/runs/**` alors qu'AGENTS.md impose de tenir ce fichier.

Diff toujours à 460 lignes après. La tâche regroupait deux briques derrière un même
`done` — découpé le long de la frontière déjà dans le code (`tali.domain` /
`tali.codecs`) : domaine ici, codec dans #11 (`blocked` sur celle-ci, code déjà écrit).

## Bilan

`Exam`, `AnswerSheet`, `Identity`, `Shuffle`, `Phases`, `CorrectionKey` — purs, validés
aux frontières, champ fautif nommé dans chaque erreur. `correction_key` déterministe
par copie (`blake2b`, pas `hash()`). Un test d'architecture (AST) fige les imports du
module : `tali.domain` ne connaîtra jamais un format de fichier.

## Points d'incertitude

- §4.3 à corriger pour retirer `digit_grid`/`name_zone` (contredit `0003`) — document
  qui fait autorité, je ne l'ai pas touché.
- « Attendu » de l'issue #1 corrigé côté GitHub en parallèle de cette PR.
