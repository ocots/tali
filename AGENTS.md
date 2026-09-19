# AGENTS.md — règles du dépôt

À lire **avant toute intervention**, humaine ou automatique.

## Le projet

`tali` est un outil d'aide à la correction de copies d'examen scannées. Il pré-corrige,
présente à l'enseignant une revue rapide et ordonnée, puis ouvre à l'étudiant une
consultation progressive où il vérifie ce que la machine a lu.

Le cahier des charges est dans **[`docs/00-cahier-des-charges.md`](docs/00-cahier-des-charges.md)**.
Il fait autorité : périmètre, décisions actées, calendrier. Le lire avant de proposer
quoi que ce soit.

## L'échéance, qui commande tout

**Examen réel : lundi 23 novembre 2026.** ~200 étudiants, 70 % QCM / 30 % questions
ouvertes.

**Jalon décisif : répétition générale le 29 octobre 2026.** C'est là que se décide un
éventuel repli sur un sujet classique sans QR — pas en novembre.

Le projet a deux moitiés aux échéances très différentes :

| Moitié | Échéance | Pourquoi |
| --- | --- | --- |
| **génération** (`build` : feuille de réponses, marqueurs, QR, clés) | **dure** — début novembre | la feuille est imprimée **une fois** |
| **lecture et revue** (`scan`, `grade`, `review`) | souple — décembre | les scans ne périment pas |

→ En cas d'arbitrage, **la génération passe devant**. Si `build` est faux, les scans ne
valent rien.

## Le périmètre de novembre

**Dedans** : M0 (socle, formats, géométrie), M1 (QCM de bout en bout en CLI), la
génération du mélange des sujets.

**Dehors, explicitement** : portail étudiant, IA sur les questions ouvertes, canal photo,
diffusion des notes. Ne pas les commencer. Les questions ouvertes restent corrigées à la
main en novembre — c'est le statu quo, et il est acceptable.

## Comment on travaille ici

Le travail est orchestré par **`crank`** (dans `tools/crank/`, voir son README).

**Tu ne choisis pas sur quoi travailler.** `crank next` le fait, à partir de l'état
objectif du dépôt. Tu exécutes la tâche désignée, et rien d'autre.

```bash
crank next            # que faut-il faire ?
crank setup <n>       # worktree + branche + réclamation + fichier de suivi
#   … tu travailles dans le worktree …
crank finalize        # vérifications, puis PR
crank fail <n> "…"    # si tu es bloqué — jamais laisser une issue réclamée
```

### Avant d'intervenir

1. Lire ce fichier et le cahier des charges.
2. **Chercher dans `.crank/runs/` et `.crank/archived/`** les suivis portant sur le même
   terrain. Quelqu'un a peut-être déjà tenté, et documenté pourquoi ça n'a pas marché.
3. Lire `.crank/lessons.md`.
4. Lire le brief de ton rôle (`.crank/roles/<rôle>.md`), affiché par `crank setup`.

### Pendant

- Le champ `done` de la tâche est le **seul** contrat. Tant qu'il ne passe pas, tu n'as
  pas fini — même si le code « a l'air bon ».
- Tenir le fichier de suivi **au fil de l'eau** (Plan, Journal, Bilan), jamais reconstitué
  à la fin. Il devient la description de la PR, et c'est lui qui rend la relecture rapide.
- Commiter au fur et à mesure. Ne jamais pousser sur autre chose que ta branche.

### Ce qu'on ne fait jamais

- **fusionner une PR** — c'est Olivier, toujours, sans exception
- **simuler la réussite** quand `done` ne passe pas → `crank fail` avec une raison précise
- **laisser une issue réclamée** sans `finalize` ni `fail`
- **contourner une vérification** qui échoue
- toucher une tâche `human-only`
- travailler sur une tâche que `crank next` n'a pas désignée

## Le dépôt est public

`github.com/ocots/tali` et `github.com/ocots/crank` sont publics. C'est un choix assumé et
cohérent avec le projet : les étudiants verront de toute façon le barème détaillé (cahier
des charges §10.3). Mais il impose quatre règles.

**1. Aucune donnée d'examen, jamais.** Copies, scans, listes nominatives, notes. La
décision `0004` fait que ça n'arrive pas par construction — `tali` ne produit rien dans le
dépôt — mais la règle tient même si l'architecture change.

**2. Aucun `exam.toml` réel.** Il contient la graine des permutations. Combinée au barème,
elle donne les bonnes réponses de chaque copie. C'est le fichier le plus sensible du
système, et il ressemble à un banal fichier de configuration. Seul l'exemple **synthétique**
de `examples/` a sa place ici.

**3. Un suivi fusionné est public pour toujours.** Ne jamais coller dans `.crank/runs/` un
nom d'étudiant, un extrait de copie réelle, ou une question de l'examen à venir. C'est le
piège le plus probable : documenter un bug en y collant le cas réel qui l'a révélé.
Reproduire avec des données synthétiques, toujours.

**4. À réexaminer en M7.** Quand la notation assistée par IA arrivera, ses prompts
deviendront publics — un étudiant pourra optimiser ses réponses contre un barème et un
prompt connus. Ce n'est pas un problème aujourd'hui ; ça le deviendra. Ne pas trancher
maintenant, mais ne pas l'oublier.

**En cas de doute sur un fichier : ne le commite pas, demande.** Un commit poussé sur un
dépôt public ne se retire pas.

## Les décisions

Un fichier par décision dans `decisions/`, avec un champ `statut`.

**Fusionner la PR vaut décision.** Une tâche qui déclare `bloque_sur: ["0002"]` reste
invisible pour `crank next` tant que `decisions/0002-*.md` n'est pas `actée` ou `rejetée`.

Si un choix durable se présente en chemin, **ne le tranche pas seul** : propose un fichier
dans `decisions/` et signale-le dans ton suivi.

## Les tâches que les agents ne peuvent pas faire

Label **`human-only`**. Elles sont sur le chemin critique et n'avancent que par Olivier :
imprimer et faire remplir des feuilles test, la répétition générale du 29 octobre, rédiger
le contenu du sujet et le barème, trancher les décisions.

`crank status` les rappelle. Ne jamais les réclamer.

## Le rythme

Olivier relit en **une session de 2 h tous les 3 jours**, environ 10 PRs par semaine.
`wip_max = 4`, dimensionné pour qu'une session vide la file.

Conséquence concrète : **la ressource rare est sa relecture, pas ton temps.** Une PR
petite, bien décrite, dont le `done` passe du premier coup vaut mieux que trois PRs
approximatives. Diviser par deux le temps de relecture d'une PR double la vitesse du
projet — aucun autre levier n'approche celui-là.

## Structure

```text
docs/           cahier des charges — fait autorité
decisions/      une décision par fichier, fusionner vaut décider
.crank/
  roles/        briefs de rôle
  runs/         suivis d'intervention — durables, à consulter avant d'agir
  archived/     campagnes terminées
  lessons.md    leçons réutilisables et pièges récurrents
src/tali/       le logiciel
tests/          ses tests
tools/crank/    l'orchestrateur (dépôt git distinct)
```
