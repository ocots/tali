# Bibliothèque de génération du PDF

statut: actée

_Validée le 2026-09-19, en conversation, avant la mise en place du flux de PRs._

## Contexte

La feuille de réponses est générée **programmatiquement**, avec des coordonnées choisies et
non découvertes (cahier des charges §16.3). Le cahier du sujet, lui, reste en LaTeX et
n'est jamais lu par le pipeline — il n'entre donc pas dans ce choix.

Bloque toute la moitié « génération », qui est le chemin critique.

## Le besoin est double, et c'est ce qui tranche

| | Pour quoi |
| --- | --- |
| **écrire** un PDF | générer 220 feuilles de réponses |
| **rasteriser** un PDF en image | le corpus synthétique (§13.1) : générer une feuille, la rendre en image, la déformer, vérifier que `locate` la retrouve |

Le second besoin est souvent oublié. Or c'est lui qui porte tout le test de non-régression
du projet : sans rastérisation, on ne peut pas tester le round-trip sans imprimante.

## Options pour écrire

| | Licence | Pour | Contre |
| --- | --- | --- | --- |
| **ReportLab** | BSD | conçu exactement pour ça, coordonnées en points, mature, très stable | API un peu datée |
| **PyMuPDF** (fitz) | **AGPL** | écrit *et* rasterise, très rapide | licence contaminante pour une diffusion ouverte ; licence commerciale sinon |
| **fpdf2** | LGPL | léger, simple | moins précis sur le dessin vectoriel, écosystème plus mince |

## Proposition

**ReportLab pour écrire, `pypdfium2` (BSD) pour rasteriser dans les tests.**

Les deux en licence permissive, ce qui laisse `tali` diffusable sans contrainte. C'est
l'argument décisif face à PyMuPDF, qui ferait les deux à lui seul mais impose l'AGPL à
tout le projet — problématique pour un outil qu'on peut vouloir partager entre collègues
ou publier.

Deux dépendances plutôt qu'une, pour une liberté de licence : l'échange est bon.

## Conséquences

- Fige la manière d'écrire le gabarit.
- À isoler derrière une interface étroite (« poser un rectangle, un cercle, un texte, un QR
  à telles coordonnées ») pour qu'un changement reste local à un module. À prévoir dans le
  découpage de M0.
- La rastérisation n'est utilisée **que dans les tests** : ce n'est pas une dépendance
  d'exécution.
