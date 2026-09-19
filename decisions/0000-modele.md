# Modèle de décision

statut: actée

## Contexte

Ce fichier n'est pas une décision : c'est le gabarit. Le copier sous
`NNNN-titre-court.md` en incrémentant le numéro.

## Comment ça marche

- `statut: proposée` → toute tâche qui déclare `bloque_sur: ["NNNN"]` est invisible
  pour `crank next`.
- **Fusionner la PR vaut décision** : passer `statut` à `actée`.
- Fermer la PR sans fusionner → `rejetée`, avec la raison en commentaire.
- `actée` comme `rejetée` débloquent : ce qui bloque, c'est l'indécision.

Un fichier par décision, jamais une table : plusieurs décisions peuvent être en vol,
et une table entrerait en conflit à chaque fois.
