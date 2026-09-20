# `test_round_trip_perspective_30_degres` reste bloqué après `0005` — la détection, pas le recalage

statut: actée
_Ouverte le 2026-09-20, en implémentant l'option A de `decisions/0005`. Actée le
2026-09-20 par Olivier (option A, « pour le moment »)._

## Contexte

`0005` a étendu `locate()` à une homographie complète — bon changement, tout `#6` et
`#7` passe, y compris le refus à 60°. Mais le round-trip à 30° échoue encore, pour une
raison différente : `find_marker_centers` (#6), pas le recalage.

Vérifié numériquement sur la page réelle de `#7` : à la focale par défaut de
`deform.perspective` (1500 px), trois des cinq marqueurs sortent du cadre à 30°. En
augmentant la focale pour les garder dans le cadre, leur rectangle englobant (même
orienté, `minAreaRect`) n'est plus assez carré pour le filtre de forme de `#6` — un
carré vu de biais près d'un coin de page perd sa squareté, quelle que soit la focale.

Le test demande donc explicitement le **canal photo** (§9.4) : `locate()` est prêt,
`find_marker_centers` non, et l'y rendre robuste (détection par quadrilatère
quelconque) est un chantier comparable à `#6`, hors périmètre de novembre (AGENTS.md).

## Ce qui se décide

**A. Réviser le test** : une prise de vue à 30° mais moins grand-angle (focale plus
longue), qui garde les marqueurs dans le cadre et raisonnablement carrés, sans exiger
de détection robuste au canal photo.

**B. Ouvrir une tâche dédiée pour `find_marker_centers` v2** (quadrilatère, pas
rectangle) et laisser le test bloqué jusque-là.

## Recommandation

**A.** `locate()` est déjà prêt pour M7/M8 grâce à `0005` ; refaire la détection
maintenant revient à commencer le canal photo hors périmètre. B reste ouvert si ce
canal devient prioritaire.

## Suite

Implémenté : `focal_px=40_000` (au lieu de 1500) pour ce test — `degrees=30.0`
inchangé, squareness mesurée ≥ 0.86 (marge confortable au-dessus du seuil 0.8 de `#6`,
stable sur toute une plage de focales), erreur de recalage < 1 px. Le défaut de
`deform.perspective` n'a pas changé, `test_refuse_plutot_que_de_se_tromper_aux_
extremes` (60°) refuse toujours.
