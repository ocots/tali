# tali

Aide à la correction de copies d'examen scannées.

> **En chantier.** Rien n'est encore implémenté. Le cahier des charges est écrit, le
> périmètre est arrêté, l'échéance est réelle : examen du **lundi 23 novembre 2026**.

## L'idée

Un outil en ligne de commande, sur fichiers texte, qui :

1. **génère** les sujets — une feuille de réponses détachée, avec marqueurs de calage,
   QR par page, et une clé de correction par copie (questions et réponses mélangées) ;
2. **lit** les copies scannées — recalage géométrique, extraction des cases cochées ;
3. **pré-corrige** et présente à l'enseignant une revue **par question, en ordre
   aléatoire, en aveugle**, sous forme de planches de vignettes — c'est là qu'est le gain
   de temps, et accessoirement la suppression des biais de notation classiques ;
4. **rend à l'étudiant** une consultation en trois temps : ce que la machine a lu, puis
   la note, puis la correction détaillée avec droit de réclamation.

## Ce qui le distingue

Ni l'OMR ni la notation par IA ne sont nouveaux. Deux choses le sont :

**Séparer la lecture de la notation.** « La machine a-t-elle bien lu ce que j'ai écrit ? »
est une question objective, tranchée par l'image, sans enjeu juridique et sans fuite du
corrigé. « Suis-je d'accord avec le barème ? » est autre chose. Les traiter séparément
débloque tout : l'étudiant peut confirmer la lecture **avant** de connaître le corrigé,
donc sans aucune incitation à mentir.

**La note qui converge.** À tout instant, la note est un encadrement qui ne fait que se
resserrer : « 80 % du barème est stabilisé, votre note est entre 13 et 15 ». Une note ne
« baisse » donc jamais — elle était toujours dans la fourchette annoncée. C'est ce qui
rend la divulgation précoce sûre.

## Documentation

| | |
| --- | --- |
| [`docs/00-cahier-des-charges.md`](docs/00-cahier-des-charges.md) | le document de référence — périmètre, conception, calendrier, décisions |
| [`AGENTS.md`](AGENTS.md) | les règles du dépôt, pour toute intervention |
| [`decisions/`](decisions/) | une décision par fichier ; fusionner la PR vaut décider |
| [`.crank/runs/`](.crank/) | les suivis d'intervention, conservés |
| [`tools/crank/`](tools/crank/) | l'orchestrateur d'agents (dépôt distinct) |

## Développement

```bash
git submodule update --init     # tools/crank vit dans son propre dépôt
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]" -e ./tools/crank
.venv/bin/python -m pytest
```

Le travail est orchestré par `crank` : `crank next` désigne la tâche, `crank setup <n>`
prépare le terrain, `crank finalize` ouvre la PR. Voir [`AGENTS.md`](AGENTS.md).
