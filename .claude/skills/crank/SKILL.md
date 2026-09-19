---
name: crank
description: Fait avancer le projet d'un cran, de façon autonome. Le sélecteur `crank` choisit la tâche (déterministe), tu l'exécutes. À utiliser quand on te dit « crank », « continue le projet », « la suite », ou quand on te demande de travailler sans préciser sur quoi.
---

# crank

Tu ne choisis pas sur quoi travailler. Un script le fait, à partir de l'état objectif du
dépôt. Ton travail est d'exécuter la tâche qu'il désigne, et rien d'autre.

## 1. Demander le plan

```bash
crank next --json
```

Agis selon `action` :

| `action` | Ce que tu fais |
| --- | --- |
| `work-task` | la suite de cette procédure |
| `fix-ci` | répare la CI de `main` en priorité, rien d'autre |
| `address-review` | traite les demandes de changement de la PR indiquée |
| `stop` | **arrête-toi** et rapporte les `notes` à l'utilisateur, telles quelles |

Sur `stop`, ne cherche pas du travail par toi-même. Un arrêt est un résultat normal : soit
le plafond de PRs est atteint (c'est à l'utilisateur de relire), soit des décisions
l'attendent. Dans les deux cas, ce qu'il faut, c'est **lui dire**, pas contourner.

## 2. Préparer le terrain

```bash
crank setup <numéro>
```

Crée le worktree, la branche, réclame la tâche, écrit `.task.md`, et affiche le brief de
ton rôle. **Travaille dans le worktree**, jamais dans le dépôt principal.

## 3. Travailler

- Lis `.task.md` en entier. S'il contient déjà un journal, tu reprends un travail
  interrompu.
- Lis le brief de ton rôle, affiché par `setup`. Il dit comment travailler ; les limites,
  elles, sont vérifiées automatiquement.
- Le champ `done` est le contrat. Rien d'autre ne compte comme « fini ».
- Tiens le journal de `.task.md` au fil de l'eau : il devient la description de la PR, et
  c'est lui qui rend la relecture rapide.
- Commite dans le worktree.

## 4. Finaliser

```bash
crank finalize
```

Lance les vérifications (périmètre, taille, critère `done`, contrôles du projet) puis ouvre
la PR. **Si une vérification échoue, aucune PR n'est ouverte** : corrige et relance.

Si tu ne peux pas satisfaire `done`, **ne simule pas la réussite**. Écris dans `.task.md`
ce que tu as tenté et pourquoi ça bloque, puis `crank finalize --draft`.

## 5. Rendre compte

Une PR par tâche, puis tu t'arrêtes et tu dis ce que tu as fait. Ne relance pas `crank
next` en boucle : c'est l'utilisateur qui décide d'enchaîner.

## Ce que tu ne fais jamais

- fusionner une PR — c'est à l'utilisateur, toujours
- choisir une autre tâche que celle indiquée
- travailler sur une tâche `human-only`
- contourner une vérification qui échoue
