# Format de la feuille de réponses

statut: actée

_Validée le 2026-09-19, en conversation, avant la mise en place du flux de PRs._

## Contexte

La feuille de réponses détachée est la **seule** page que le pipeline lit (cahier des
charges §6, §16.3). Tout en dépend : recalage, extraction, planches de vignettes. Elle est
imprimée **une fois** — ce qui n'y est pas ne pourra jamais y être. Chemin critique du
23 novembre ; bloque `build` et `locate`.

## Ce qui se décide maintenant, et ce qui se mesure

| | |
| --- | --- |
| **La structure** — quels éléments, quel encodage, quelle disposition | **décidable maintenant** |
| **Les dimensions** — millimètres exacts des bulles, du QR, des marges | **mesuré par le spike S2** |

On ne peut pas lancer S2 sans structure à imprimer. La structure est donc l'objet de cette
décision ; S2 règle ensuite les millimètres et peut demander un ajustement.

## A. Marqueurs de calage

**Proposition : quatre carrés noirs pleins aux coins, plus un cinquième près du coin
haut-gauche pour lever l'ambiguïté d'orientation.**

Pourquoi pas des marqueurs codés (ArUco) : ils portent une information dont on n'a pas
besoin — le QR identifie déjà la page — et ils sont plus fragiles à basse résolution et en
photo de biais. Les carrés pleins sont ce qu'il y a de plus robuste à détecter, et c'est
le choix d'AMC après vingt ans d'usage en université.

Le cinquième marqueur règle un vrai problème : quatre coins identiques sont indiscernables
à 180°. Si le QR est abîmé, la géométrie doit rester récupérable seule.

## B. Contenu du QR

**Proposition : un identifiant opaque et court, rien d'autre.**

```text
tali:<exam_id>:<copy_id>:<page>:<template_version>
```

- **Pas de numéro étudiant** — voir `0003`. Garde la porte ouverte à l'anonymat sans
  réimprimer, et découple le pipeline de l'identité.
- **La version du modèle** permet de refuser proprement une feuille d'une autre session
  plutôt que de la mal lire.
- Court volontairement : ~35 caractères tiennent dans un QR de petite version, donc plus
  robuste après impression et scan. C'est précisément ce que S2 doit vérifier.

## C. Pagination

**Proposition : chaque page porte son propre QR et ses propres marqueurs.**

Conséquence, et c'est le point important : **le pipeline ne fait jamais d'hypothèse sur
l'ordre des pages.** Une page est identifiée par elle-même. Un scanner qui désordonne,
duplique ou perd une page devient détectable et réparable automatiquement.

Cela rend le **recto-verso sans risque** — un décalage duplex se répare tout seul — et
divise par deux le papier : 200 feuilles au lieu de 400.

## D. Valeurs de départ pour S2

À imprimer et mesurer, pas à graver :

| Élément | Départ | À vérifier en S2 |
| --- | --- | --- |
| bulle QCM | ⌀ 5 mm, entraxe 8 mm | lisible après photocopie ? croix débordante gérée ? |
| marqueur de coin | carré 8 mm, marge 10 mm | survit à la marge d'impression ? |
| QR | 18 mm | **lisible après impression puis scan** — le point critique |
| grille de chiffres | même bulle que le QCM | |
| cadre de réponse ouverte | largeur pleine, lignes guides 8 mm | l'écriture tient-elle dedans ? |
| papier | A4, recto-verso | |

## Conséquences

Fige le gabarit de génération et le format d'extraction. Un changement après impression est
impossible ; un changement après la répétition générale du 29 octobre coûte une
réimpression complète.
