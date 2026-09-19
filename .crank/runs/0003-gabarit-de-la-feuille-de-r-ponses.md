# Tâche #3 — Gabarit de la feuille de réponses

- **rôle** : `feature`
- **critère de complétion** : `.venv/bin/python -m pytest -q tests/test_sheet.py::test_cinq_marqueurs_dont_un_asymetrique tests/test_sheet.py::test_template_json_donne_toute_zone_par_identifiant tests/test_sheet.py::test_inventaire_exact_des_zones`
- **périmètre** : `src/tali/render/**`, `tests/test_sheet.py`
- **budget** : 1 session

## Plan

- [x] `dimensions.py` — toutes les dimensions en un seul endroit
- [x] `sheet.py` — `Zone`, `Template`, `build_template`
- [x] `tests/test_sheet.py`

## Journal

**Le nombre de questions n'est pas connu avant la rédaction du sujet** (le sujet est
`human-only`, tâche #9). `build_template` est donc paramétré par les comptages
(`n_qcm_questions`, `n_qcm_choices`, `n_open_questions`) plutôt que de figer un examen
particulier — cohérent avec §6 : la mise en page des zones est fixe *pour un comptage
donné*, pas pour un contenu donné.

**« Un cinquième marqueur asymétrique »**, testé géométriquement plutôt que par
convention : le test calcule les centres des cinq marqueurs, les fait pivoter de 180°
autour du centre de la page, et vérifie que l'ensemble obtenu diffère de l'original. Un
5e marqueur posé au centre (donc invariant par la rotation) ferait échouer ce test —
vérifié par mutation.

**`decisions/0001` D nomme encore une « grille de chiffres »** (langage antérieur à
`0003`, qui l'a supprimée). Je n'ai pas modélisé de grille de chiffres : `ZONE_TYPES`
n'en contient pas, et `test_inventaire_exact_des_zones` le fige. Signalé, pas corrigé —
`decisions/0001` est un document qui fait autorité, hors de mon périmètre.

Mutation-testé les trois tests du contrat (5e marqueur symétrique, version ignorée au
rechargement JSON, grille de chiffres réintroduite dans `ZONE_TYPES`) : les trois
mutants sont tués.

## Bilan

`build_template(...)` compose marqueurs, QR, grilles NOM/PRÉNOM (décision `0003`),
bulles QCM et cadres ouverts. `Template.to_json`/`from_json` : toute zone retrouvable
par son identifiant, une erreur nommée sur type inconnu ou identifiant en double.
`dimensions.py` centralise les millimètres : le spike S2 n'y touchera qu'un fichier.

## Points d'incertitude

- `decisions/0001` D à corriger pour retirer la mention de « grille de chiffres »
  (obsolète depuis `0003`) — document qui fait autorité, non touché ici.
- La disposition verticale (identité → QCM → cadres ouverts, empilés) est une hypothèse
  de mise en page raisonnable, pas une exigence du cahier des charges. À revoir une fois
  le sujet réel connu (#9) si ça ne tient pas sur une page A4.
