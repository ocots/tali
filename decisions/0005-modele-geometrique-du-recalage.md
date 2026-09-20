# Modèle géométrique du recalage : affine ou homographie complète

statut: actée
_Ouverte le 2026-09-19, en écrivant #7. Actée le 2026-09-20 par Olivier (option A)._

## Contexte

`#6` a choisi une transformation **affine** (6 degrés de liberté, 3 correspondances
minimum), au motif que novembre ne couvre que le **scan à plat** — le canal photo,
qui introduirait une vraie perspective, est hors périmètre (AGENTS.md). `#6` en a
tiré son critère « refuse sous 3 marqueurs ».

`#7` demande `test_round_trip_perspective_30_degres`. Le cahier des charges liste
`perspective` séparément de `rotation` (§13.1), et l'associe explicitement au canal
photo (§9.4) — une vraie distorsion **projective**, pas une simple rotation.

**Une affine ne peut pas représenter une projective.** Vérifié numériquement : un
basculement à 30°, ajusté au mieux par une affine sur les cinq marqueurs, laisse
~35-40 px d'erreur résiduelle sur les marqueurs non colinéaires entre eux, et
~15-35 px à l'intérieur de la page — plus que la taille d'une bulle QCM (5 mm). Un
tel écart place le recadrage sur la mauvaise case, silencieusement.

## Ce qui se décide

**A. Étendre `locate()` à une homographie complète** (`cv2.findHomography`, 4
correspondances minimum, au lieu de 3 pour l'affine).

- Coût : `test_refuse_si_moins_de_trois_marqueurs` (#6, mergée) devient « sous 4 ».
- Bénéfice : rend `#7` réalisable tel qu'écrit, et anticipe M7/M8 (canal photo), où
  le cahier des charges attend déjà cette capacité (§9.4). La labellisation
  (`_label`, la partie difficile de #6) ne change pas — seul l'appel final change.

**B. Garder l'affine, réviser `#7`** : remplacer `perspective_30_degres` par une
déformation affine (rotation forte, cisaillement) testant la même robustesse sans
dépasser ce que `locate()` sait faire.

## Recommandation

**A.** Le cahier des charges anticipe déjà la perspective par les marqueurs de coin,
le coût est isolé (un seuil et un appel `cv2`, pas la labellisation), et concevoir
pour l'homographie maintenant coûte moins cher que de re-découper `locate()` en M7.

## Suite

Implémenté ici, extrait du diff de `#7` (déjà au plafond de taille) pour rester une
PR petite et indépendante : `locate()` utilise `cv2.findHomography`, `#6`
(`test_refuse_si_moins_de_trois_marqueurs`) devient `..._quatre_marqueurs`. Une fois
mergé, `#7` se rebase dessus — cela ne suffira pas à lui seul à faire passer
`test_round_trip_perspective_30_degres` : un second blocage, sans rapport avec le
recalage, reste à documenter et résoudre dans le suivi de `#7`.
