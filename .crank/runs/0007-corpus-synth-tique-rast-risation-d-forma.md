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

**`finalize --draft` ne servait à rien : corrigé dans `crank` d'abord.** Son message dit
« corrige, ou déclare-toi bloqué avec --draft », mais le code refusait la PR AVANT même
de regarder `--draft` — l'option n'avait jamais d'effet. Trouvé en voulant l'utiliser
pour de vrai. Corrigé sur `crank` (`703f999`) : l'hygiène du diff bloque toujours, le
critère fonctionnel ne bloque plus hors `--draft`.

**Le conflit de fond, découvert en écrivant le round-trip, pas en le lisant.** `#6` a
choisi une transformation affine, en supposant l'affine suffisante pour un scan à plat.
`test_round_trip_perspective_30_degres` demande une vraie perspective (§13.1 la liste
séparément de la rotation ; §9.4 en fait un cas explicite du canal photo). Vérifié
numériquement (voir `decisions/0005`) : une affine ajustée sur une vraie perspective à
30° laisse des dizaines de pixels d'erreur — largement plus qu'une bulle QCM. Je ne
tranche pas seul un changement qui reviendrait sur le modèle géométrique d'une tâche déjà
mergée : décision proposée, recommandation donnée, en attente.

**Deux bugs trouvés dans `find_marker_centers` (#6) en le confrontant à une vraie page
construite**, pas aux marqueurs synthétiques isolés des tests de `#6` :
1. Le remplissage se mesurait par l'aire du contour (`cv2.contourArea`), qui vaut ~toute
   la boîte même pour un contour **creux** — chaque case des grilles NOM/PRÉNOM (un cadre,
   pas un carré plein) était détectée comme marqueur. Corrigé en mesurant les pixels
   réellement sombres dans le rectangle englobant.
2. Un piège de cache : après cette correction, un `__pycache__` obsolète (d'une édition
   précédente dans ce même worktree) a fait croire à un troisième faux positif près du
   QR pendant près d'une heure d'investigation. Réglé en vidant les `__pycache__` et en
   revérifiant avec `python -B`. Aucun code n'a été ajouté pour ce « bug » : il n'existait
   pas. Noté ici pour ne pas refaire l'enquête si ça se reproduit.

Les trois tests atteignables mutation-testés (seuil de remplissage relâché, facteur
dpi erroné, une déformation extrême neutralisée) : les trois mutants sont tués.

## Bilan

`tests/support/raster.py` (rastérisation pypdfium2) et `tests/support/deform.py`
(rotation, perspective, flou, bruit, contraste, bavure, pliure) livrés. Trois des
quatre tests du contrat passent, avec un vrai round-trip bout en bout (`tali build` →
rastérisation → `locate`/`decode_page_qr`) sur du contenu généré, pas simulé.

`test_round_trip_perspective_30_degres` échoue, honnêtement : `decisions/0005` (proposée)
explique pourquoi et recommande d'étendre `locate()` à une homographie complète.

## Points d'incertitude

- `decisions/0005` attend un arbitrage : upgrader `locate()` en homographie (mon
  recommandation) change aussi le seuil « refuse sous 3 marqueurs » de `#6` en « sous 4 ».
- La courbe de dégradation (§13.1 : « donne une courbe... test de non-régression le
  plus parlant ») n'est pas produite comme artefact ici — seuils nommés testés
  directement, la production d'une vraie courbe reste à faire.
