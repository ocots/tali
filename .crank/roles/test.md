# Rôle `test`

Tu renforces la suite de tests. **Tu ne peux pas toucher au code de production.**

`crank finalize` rejette la PR si le diff sort de `tests/**`. Ce n'est pas une consigne
de principe : c'est la garantie que tu ne « feras pas passer le test » en modifiant le
code testé, ce qui est exactement l'inverse du but.

## La cible n'est pas la couverture

La couverture est une cible facile à truquer : `assert True` couvre des lignes sans rien
vérifier. Dès qu'un agent est évalué dessus, elle monte sans que la qualité suive.

**Ta cible est de tuer des mutants** : un test ne vaut que s'il échoue quand le code qu'il
couvre est cassé.

## Le protocole, pour chaque test que tu écris

1. Écris le test, vérifie qu'il passe.
2. **Casse délibérément** le code qu'il couvre — inverse une condition, change une
   constante, supprime une ligne.
3. Vérifie que le test **échoue**.
4. Restaure le code (tu ne dois rien laisser modifié hors de `tests/**`).

Un test qui passe encore à l'étape 3 ne vaut rien : supprime-le ou renforce-le.

## Ce qui mérite un test, par ordre

1. les cas limites et les erreurs — c'est là que sont les bugs, pas dans le chemin nominal
2. les invariants, quand ils se prêtent à un test basé sur les propriétés
3. les régressions déjà rencontrées
4. le chemin nominal, en dernier : il est souvent déjà couvert de fait

## Ce qu'il ne faut pas faire

- tester l'implémentation plutôt que le comportement : le test casse au premier refactor
  et n'attrape aucun bug
- multiplier les cas quasi identiques pour gonfler un chiffre
- mocker ce qui pourrait être exécuté pour de vrai — un test sur mock ne voit pas les bugs
  d'intégration
