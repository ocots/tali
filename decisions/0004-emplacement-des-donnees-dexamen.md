# Emplacement des données d'examen

statut: actée

_Validée le 2026-09-19, en conversation, avant la mise en place du flux de PRs._

## Contexte

Le dépôt `tali` contient le **logiciel**. Un examen produit des **données** : sujets
générés, scans de copies, liste nominative, notes. Ce sont des données personnelles en
contexte scolaire (cahier des charges §10.2).

Aujourd'hui, seul un `.gitignore` les tient à l'écart. C'est un filet, pas une garantie :
il suffit d'un chemin non prévu pour qu'une copie entre dans l'historique — et un commit
poussé ne se rattrape pas.

## Trois natures de matériau, à ne pas confondre

| | Contenu | Sensibilité | Où |
| --- | --- | --- | --- |
| **le logiciel** | `src/`, `tests/`, docs | aucune | dépôt `tali`, public possible |
| **la définition d'un examen** | `exam.toml`, sujet, barème | **confidentielle avant l'épreuve** | dossier de l'examen |
| **les données** | scans, `roster.csv`, notes, PDF générés | **personnelles** | dossier de l'examen, jamais versionné |

Le sujet lui-même est confidentiel avant l'épreuve : le versionner dans un dépôt public
serait une fuite. Il n'a donc pas plus sa place dans `tali` que les scans.

## Décision proposée

**`tali` ne connaît aucun chemin de données. Il s'exécute dans un dossier d'examen, comme
`git` s'exécute dans un dépôt.**

```bash
cd ~/Examens/ct-2026-11      # le dossier de travail de CET examen
tali build                   # lit ./exam.toml, écrit ./build/
tali scan ./scans            # lit ./scans, écrit ./work/
```

Un dossier d'examen est **autodescriptif** : il contient son `exam.toml`, son sujet, son
roster, ses scans, ses sorties. Il est déplaçable, archivable, sauvegardable d'un bloc,
et rien dans le dépôt n'y fait référence.

Conséquence directe : **le `.gitignore` n'est plus une ligne de défense**, juste un
confort. Le dépôt ne peut pas contenir de données, parce qu'aucune donnée n'y est produite.

### Ce qui marque un dossier d'examen — un seul fichier, visible

**`exam.toml`, à la racine du dossier. Ni `.tali.toml`, ni `.tali/`.**

`tali` le cherche en remontant depuis le dossier courant, comme `git` cherche `.git`.

Pourquoi pas un fichier caché : `exam.toml` n'est pas de la configuration d'outil, c'est
**le contenu principal que tu édites** — structure de l'examen, barème, graine des
permutations, dates de phases. Un point devant le nom cacherait précisément le fichier
qu'on ouvre le plus souvent. Les dotfiles sont pour l'état dérivé, pas pour la matière.

Et pas deux fichiers : `exam.toml` sert à la fois de configuration **et** de marqueur. Un
`.tali.toml` séparé n'aurait rien de plus à dire.

Le reste du dossier (`build/`, `scans/`, `work/`, `out/`) est visible aussi : ce sont des
dossiers qu'on inspecte, qu'on sauvegarde, qu'on nettoie à la main. Rien à cacher.

### Ce que le dépôt contient quand même

- `examples/` : un examen **synthétique**, entièrement généré, sans aucune donnée réelle.
  C'est le corpus de test du §13.1 — il sert aussi d'exemple exécutable.
- `tests/fixtures/` : images de test, toutes synthétiques ou anonymisées.

### Pas de configuration utilisateur non plus

Un `~/.config/tali/config.toml` avec un `workspace_root` permettrait `tali open ct-2026-11`
depuis n'importe où. **Écarté pour l'instant** : `cd` fait déjà le travail, et une
configuration globale est un état invisible de plus à déboguer.

À ajouter le jour où son absence coûte quelque chose de mesurable, pas avant.

## Alternatives écartées

- **Un chemin de données dans le dépôt** (`data_dir = "..."` dans un fichier versionné) :
  réintroduit exactement le couplage qu'on veut supprimer, et le chemin d'un collègue
  n'est pas le sien.
- **Un sous-dossier du dépôt ignoré par git** : fonctionne jusqu'au jour où quelqu'un
  fait `git add -f`, change de branche avec des données non suivies, ou clone ailleurs.

## Conséquences

- `tali init <nom>` crée un dossier d'examen **hors du dépôt**, pas dedans.
- Toutes les commandes deviennent relatives au dossier courant : testables en `tmp_path`,
  sans variable d'environnement ni chemin absolu dans le code.
- Le dépôt peut être rendu public sans audit d'historique.
