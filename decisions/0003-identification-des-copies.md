# Identification des copies

statut: actée

_Validée le 2026-09-19, en conversation, avant la mise en place du flux de PRs._

## Contexte

Il faut établir la correspondance `copie → étudiant`. Contrainte posée par Olivier
(2026-09-19) : **n'importe quel sujet doit pouvoir être donné à n'importe quel étudiant**.
Aucune pré-affectation, aucune distribution triée.

L'anonymat n'est pas imposé dans l'établissement (§16.1).

## A. L'identifiant de copie n'est pas une identité

Chaque feuille porte un identifiant opaque pré-imprimé, encodé dans le QR (`0001` B).
**Il désigne une permutation de sujet, jamais une personne.**

C'est ce qui rend la distribution libre : les copies sont distinctes entre elles — il le
faut, sinon on ne sait pas quelle clé de correction appliquer — mais aucune n'est
attribuée d'avance. On distribue au hasard, y compris les feuilles restantes d'une session
précédente si le modèle n'a pas changé.

Conséquence : le pipeline entier tourne **sans jamais connaître d'identité**. La table
`copie → étudiant` n'existe qu'à l'étape d'attribution, à la fin. Bonne séparation de
responsabilité, et l'anonymat devient gratuit si l'établissement l'impose un jour.

## B. Le numéro étudiant ne sert pas — question caduque

La question initiale (« combien de chiffres ? ») supposait un numéro institutionnel.
Réponse d'Olivier : les numéros utilisés vont de **1 au nombre d'étudiants, jamais plus de
220**.

Or un tel numéro n'est pas une donnée que l'étudiant porte sur lui : il faudrait
l'attribuer, le communiquer, et compter sur sa recopie exacte le jour de l'épreuve. C'est
de la logistique en échange d'une fiabilité que le point C obtient autrement.

→ **Pas de grille de chiffres sur la feuille.** Si un second canal s'avère nécessaire
après la répétition générale, 3 chiffres suffiront (001–220) et la zone est facile à
ajouter.

## C. L'identité se lit dans une grille de lettres

**Proposition : `NOM` et `PRÉNOM` en capitales, une lettre par case.**

C'est le point technique important. Une signature manuscrite libre est difficile à lire ;
un caractère isolé dans une case l'est beaucoup moins — le problème passe de
« reconnaissance d'écriture cursive » à « classification d'un caractère parmi 26 »,
segmenté d'avance par la grille elle-même.

Et l'appariement se fait contre un **vocabulaire fermé de 220 noms** : même avec plusieurs
caractères mal lus, le plus proche voisin dans le roster reste très généralement le bon.
Un appariement flou sur liste courte est un problème facile ; de l'OCR libre ne l'est pas.

Zéro logistique : rien à attribuer, rien à communiquer, rien à recopier.

## D. Quand la lecture est douteuse

**File enseignant, avec le crop de la zone nom affiché. Jamais de repli automatique
silencieux.**

- candidat unique et score élevé → attribué sans intervention
- plusieurs candidats proches, ou score faible → décision humaine, trois secondes devant
  l'image
- un étudiant du roster ne peut jamais recevoir deux copies : conflit signalé, jamais
  résolu en silence

Estimation à vérifier : avec une grille de lettres et 220 noms, on vise moins de 5 % de
copies en file manuelle — soit une dizaine, une poignée de minutes.

## Conséquences

- Fige la zone d'identité sur la feuille (`0001`) : deux grilles de lettres, pas de grille
  de chiffres.
- L'attribution devient un module distinct, exécuté **après** toute la notation.
- Le roster attendu se réduit à une liste de noms — pas de numéros à maintenir.
- `tali doctor` doit vérifier l'unicité de l'attribution.
