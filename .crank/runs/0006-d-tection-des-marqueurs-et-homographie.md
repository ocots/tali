# Tâche #6 — Détection des marqueurs et homographie

- **rôle** : `feature`
- **critère de complétion** : `.venv/bin/python -m pytest -q tests/test_locate.py::test_retrouve_une_homographie_connue tests/test_locate.py::test_leve_orientation_180_degres_sans_qr tests/test_locate.py::test_refuse_si_moins_de_trois_marqueurs`
- **périmètre** : `src/tali/vision/**`, `tests/test_locate.py`
- **budget** : 1 à 2 sessions

## Plan

- [x] `find_marker_centers` — détection des carrés noirs pleins (seuillage + forme)
- [x] `_label` — identifier chaque marqueur sans supposer d'orientation
- [x] `locate` — correspondances mm ↔ px, transformation affine
- [x] `tests/test_locate.py` — marqueurs dessinés directement en `cv2`, sans #7

## Journal

**Modèle affine, pas une homographie projective complète.** Novembre ne couvre que le
scan à plat (le canal photo, qui introduirait une vraie perspective, est explicitement
hors périmètre — AGENTS.md). Une transformation affine (rotation, échelle,
cisaillement, translation, 6 degrés de liberté) suffit, et se résout à partir de trois
correspondances — exactement le seuil que `done` demande de refuser en-dessous.

**Identifier chaque marqueur sans connaître l'orientation, c'est le vrai problème.**
La paire de marqueurs la plus proche est toujours {haut-gauche, orientation} (~16 mm,
contre des dizaines à des centaines de mm entre deux vrais coins) — ça, c'est facile et
indépendant de la rotation. Le vrai piège : **lequel des deux est lequel ?**

Premier essai, faux : trancher par somme de coordonnées (`x+y` le plus petit). Passe en
orientation normale, **échoue à 180°** — trouvé par `test_leve_orientation_180_degres_
sans_qr`. Corrigé par une propriété géométrique invariante par rotation : le marqueur
d'orientation est décalé vers le reste du bord haut, donc toujours plus proche de
n'importe quel autre coin que ne l'est le vrai coin haut-gauche. Voter sur les
marqueurs restants tranche, même avec un seul restant (le cas minimal à 3 marqueurs).

Ce premier échec ne se voyait pas en rotation ~0° : ajouté
`test_label_ignore_lordre_de_detection`, qui appelle `_label` avec l'ordre d'entrée
inversé — cv2 ne garantit aucun ordre de contours.

Mutation-testés les trois tests du contrat : le refus sous 3 marqueurs survivait
d'abord, par un mutant retombant sur une erreur différente (`estimateAffine2D` refusant
2 points), pas le refus explicite voulu. Corrigé en vérifiant le message d'erreur.

## Bilan

`locate(image)` : détecte, identifie, ajuste une transformation affine mm ↔ px.
`Transform.to_pixels`/`to_mm` pour les deux sens. Refuse (`LocateError`, message
explicite) sous 3 marqueurs, ou si les marqueurs détectés ne se distinguent pas assez
pour lever l'orientation de façon fiable.

## Points d'incertitude

- Le seuil de détection (`cv2.threshold(image, 128, ...)`) est une valeur de départ,
  jamais vérifiée sur un vrai scan — à revoir avec S2 (#8) ou le corpus synthétique (#7).
- Le vote majoritaire suppose qu'au plus un marqueur restant présente une géométrie
  atypique. Un désaccord à 2 contre 2 (non couvert par les tests) dépendrait de l'ordre
  de tri Python — à surveiller si #7 révèle des faux votes en pratique.
