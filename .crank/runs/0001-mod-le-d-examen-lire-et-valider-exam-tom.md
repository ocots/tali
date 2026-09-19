# Tâche #1 — Modèle d'examen — objets du domaine

- **rôle** : `feature`
- **critère de complétion** : `pytest -q tests/test_model.py::test_construit_un_examen_valide tests/test_model.py::test_refuse_des_phases_dans_le_desordre tests/test_model.py::test_cle_de_correction_est_par_copie`
- **périmètre** : `src/tali/domain/**`, `tests/test_model.py`
- **budget** : 1 session

## Plan

- [x] Trancher la contradiction §4.3 / décision `0003` (grille de chiffres)
- [x] `domain/exam.py` — objets purs, aucune E/S
- [x] `tests/test_model.py` — construction, validations aux frontières, clé par copie
- [x] Découper la tâche : domaine ici, codec `exam.toml` dans une tâche séparée

## Journal

**Le §4.3 contredit la décision `0003`, qui est postérieure et `actée`.** Le schéma
d'esquisse porte `[identity] digit_grid = 8` et `name_zone = true` ; la décision `0003` B
écrit « **Pas de grille de chiffres sur la feuille** » et C fait de la grille de lettres
le canal unique. L'esquisse date d'avant la décision.

Je n'ouvre pas de nouvelle décision : il n'y a rien d'indécidé, `0003` a tranché. Je suis
`0003` et je signale que le §4.3 doit être corrigé — hors de mon périmètre.

Conséquence sur `[identity]` : il ne reste que `roster`. Le nombre de cases des grilles
`NOM` / `PRÉNOM` est de la **géométrie**, donc du ressort du gabarit (#3) et de la
décision `0001`, pas de la configuration d'examen.

**L'« Attendu » de l'issue listait `Exercise`, `Question`, `Zone`, `Sheet` comme modèles
purs attendus ici.** Aucun n'appartient à `exam.toml` (§4.3) : les tables du fichier sont
`[exam]`, `[answer_sheet]`, `[identity]`, `[shuffle]`, `[phases]`. `Exercise`/`Question`
viennent de `sujet/*.md` (§4.1), `Zone`/`Sheet` du gabarit — déjà couverts par la tâche
#3 (« toute zone par identifiant »). Je ne les implémente pas ici : ç'aurait été du
travail non demandé par `done`, donc non vérifié.

**Domaine + codec + tests ont d'abord été écrits ensemble (487 lignes), avant vérification
du plafond `max_diff_lines = 300`.** Trois mutants injectés dans les trois tests du
contrat pour vérifier qu'ils savaient échouer : le premier (`dumps` figeant `copies` en
dur) a survécu — la fixture unique ne distinguait pas une vraie lecture d'une constante.
Corrigé en ajoutant `VARIANT`, un second examen qui ne partage aucune valeur avec le
premier, plus un test qui vérifie que les deux fixtures ne se recouvrent pas.

En corrigeant ce mutant survivant, deux défauts systémiques sont apparus en exécutant
`crank finalize --dry-run` pour de vrai (pas en le relisant) — corrigés directement sur
`main`, hors de cette PR : les 7 critères `done` du backlog invoquaient `pytest` nu au
lieu de `.venv/bin/python -m pytest`, et aucun rôle n'autorisait `.crank/runs/**` alors
qu'AGENTS.md impose de tenir ce fichier. Voir `1748b91`.

Une fois ces deux défauts corrigés, le diff restait à 460 lignes — au-dessus du plafond
même après avoir consolidé cinq tests de rejet en un seul paramétré. Le code n'était pas
gonflé : c'est la tâche qui regroupait deux briques distinctes derrière un même `done`.
**Découpage le long de la frontière déjà présente dans le code** (`tali.domain` /
`tali.codecs`) plutôt qu'un découpage arbitraire :

- ici : les objets du domaine, construits directement dans les tests (aucun TOML)
- tâche séparée, `blocked` sur celle-ci : le codec `exam.toml` (round-trip, rejets),
  qui réutilise `src/tali/codecs/exam_toml.py` et `tests/test_exam_toml.py` déjà écrits

Diff final de cette PR : domaine + tests seulement, ~185 lignes.

## Bilan

`Exam`, `AnswerSheet`, `Identity`, `Shuffle`, `Phases`, `CorrectionKey` — objets purs,
validés aux frontières, messages d'erreur nommant le champ fautif. `correction_key`
déterministe par copie (`blake2b`, pas `hash()`). Un test d'architecture (AST) fige la
liste des imports du module : `tali.domain` ne connaîtra jamais un format de fichier.

Reste ouvert, dans la tâche suivante : le codec `exam.toml` lui-même.

## Points d'incertitude

- Le §4.3 du cahier des charges doit être corrigé pour retirer `digit_grid` et
  `name_zone` (contredit la décision `0003`, actée et postérieure). Je ne l'ai pas
  touché : hors de mon périmètre, et c'est un document qui fait autorité.
- L'« Attendu » de l'issue #1 sera à corriger côté GitHub pour ne plus citer
  `Exercise`/`Question`/`Zone`/`Sheet` — fait en parallèle de cette PR.
