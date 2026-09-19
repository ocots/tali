# Tâche #7 — Corpus synthétique — rastérisation, déformations, round-trip

- **rôle** : `feature`
- **critère de complétion** : `.venv/bin/python -m pytest -q tests/test_synthetic.py::test_rend_une_page_a_200_dpi tests/test_synthetic.py::test_round_trip_sans_deformation tests/test_synthetic.py::test_round_trip_perspective_30_degres tests/test_synthetic.py::test_refuse_plutot_que_de_se_tromper_aux_extremes`
- **périmètre** : `tests/support/**`, `tests/test_synthetic.py`
- **budget** : 2 sessions
- **bloqué** : `test_round_trip_perspective_30_degres` — voir `decisions/0005` (proposée)

## Plan

- [x] `tests/support/raster.py` — rastérisation pypdfium2 (décision 0002, test uniquement)
- [x] `tests/support/deform.py` — rotation, perspective, flou, bruit, contraste, bavure, pliure
- [x] `tests/test_synthetic.py`
- [x] Corriger deux bugs de `#6` trouvés en testant contre du contenu réel (pas seulement
      les marqueurs synthétiques isolés de `#6`)
- [ ] `test_round_trip_perspective_30_degres` — **bloqué**, voir `decisions/0005`

## Journal

**`finalize --draft` ne servait à rien : corrigé dans `crank` d'abord.** Son message
dit « corrige, ou déclare-toi bloqué avec --draft », mais le code refusait la PR avant
même de regarder `--draft`. Trouvé en voulant l'utiliser pour de vrai. Corrigé sur
`crank` (`703f999`) : l'hygiène du diff bloque toujours, le critère fonctionnel ne
bloque plus hors `--draft`.

**Le conflit de fond, découvert en écrivant le round-trip, pas en le lisant.** `#6` a
choisi l'affine, en supposant l'affine suffisante pour un scan à plat.
`test_round_trip_perspective_30_degres` demande une vraie perspective (§13.1 la
distingue de la rotation ; §9.4 en fait un cas du canal photo). Vérifié
numériquement (`decisions/0005`) : une affine ajustée sur une vraie perspective à 30°
laisse des dizaines de pixels d'erreur, plus qu'une bulle QCM. Je ne tranche pas
seul un changement qui reviendrait sur le modèle géométrique d'une tâche déjà mergée.

**Un bug réel dans `find_marker_centers` (#6), trouvé en le confrontant à une vraie
page construite**, pas aux marqueurs synthétiques isolés de ses propres tests : le
remplissage se mesurait par l'aire du contour (`cv2.contourArea`), qui vaut ~toute la
boîte même pour un contour **creux** — chaque case des grilles NOM/PRÉNOM était
détectée comme marqueur. Corrigé en mesurant les pixels réellement sombres. (Un
second « bug » suspecté ensuite près du QR s'est révélé être un `__pycache__`
obsolète de ce worktree — vidé, revérifié avec `python -B`, aucun code à changer.)

Les trois tests atteignables mutation-testés (seuil relâché, facteur dpi erroné,
déformation extrême neutralisée) : les trois mutants sont tués.

## Bilan

`raster.py` (pypdfium2) et `deform.py` (rotation, perspective, flou, bruit,
contraste, bavure, pliure) livrés. Trois tests sur quatre passent, avec un vrai
round-trip bout en bout (`tali build` → rastérisation → `locate`/`decode_page_qr`)
sur du contenu généré, pas simulé. `test_round_trip_perspective_30_degres` échoue
honnêtement : `decisions/0005` explique pourquoi et recommande l'homographie.

## Points d'incertitude

- `decisions/0005` : upgrader en homographie change aussi le seuil « sous 3
  marqueurs » de `#6` en « sous 4 ».
- La courbe de dégradation (§13.1) n'est pas produite comme artefact — seuils
  nommés testés directement, la courbe reste à faire.
