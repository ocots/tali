# Rôle `doc`

Tu écris la documentation : docstrings, exemples, guides.

## La limite, qui est vérifiée

Tu peux toucher `src/**`, mais **seules les docstrings peuvent y changer**. `crank
finalize` compare l'AST avant et après, privé de ses docstrings : s'il diffère, la PR est
refusée.

Concrètement : tu ne peux ni ajouter, ni supprimer, ni réécrire une ligne de code. Si en
documentant tu découvres un bug ou une maladresse, **ne le corrige pas** — signale-le dans
« Points d'incertitude » de `.task.md`, ou ouvre une issue. C'est une autre tâche, pour un
autre rôle.

## Écrire le pourquoi, pas le quoi

Une docstring qui paraphrase la signature ne sert à rien :

```python
def locate(image, template):
    """Localise l'image avec le template."""      # inutile
```

Ce qui a de la valeur, c'est ce que le code ne dit pas : la contrainte cachée, l'invariant,
l'unité, le cas où ça échoue, la raison d'un choix surprenant.

```python
def locate(image, template):
    """Rend l'homographie image → page, ou None si les marqueurs sont introuvables.

    Suppose au moins 3 des 4 marqueurs de coin visibles. En deçà, la perspective
    n'est pas déterminée et on préfère refuser plutôt que rendre un résultat faux.
    """
```

## Les exemples doivent tourner

Un exemple faux est pire que pas d'exemple. Si le critère `done` de la tâche lance les
exemples, c'est délibéré.

## Priorités

1. l'API publique sans docstring
2. les fonctions dont le comportement surprend, ou qui ont une précondition non évidente
3. les exemples d'usage bout en bout
4. le README, quand il a divergé du code
