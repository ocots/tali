# Brainstorm — Outil d'aide à la correction de copies

_Document de travail, mis à jour au fil de la discussion._
_Dernière mise à jour : 2026-09-17_

Noms possibles : **Kopia**, **CoCopie**, **Rendu**, **Barème**. (sans importance, à trancher plus tard)

---

## 1. Le principe fondateur : un gain des deux côtés

**L'outil doit apporter quelque chose à l'enseignant _et_ à l'étudiant.** Ce n'est pas une
formule de présentation : c'est le critère qui décide si une fonctionnalité mérite d'exister.

| | Ce que ça apporte |
| --- | --- |
| **Enseignant** | moins de _correction_, plus de _relecture_. Le travail mécanique disparaît, l'expertise reste. ~40 h → ~4-6 h pour 200 copies. |
| **Étudiant** | une réponse **tout de suite**, quitte à être incomplète, qui se précise avec le temps : « 80 % du barème est stabilisé, votre note est entre 13 et 15 », puis la note officielle. |

Les deux gains se **renforcent** au lieu de s'opposer : l'étudiant qui relit sa copie en
phase 0 fournit à l'enseignant une information qu'il n'a pas (§3.4), et l'enseignant qui
valide une passe resserre immédiatement l'intervalle de tous les étudiants (§3.3).

C'est aussi un test de conception : **toute fonctionnalité qui améliore un côté en
dégradant l'autre doit être écartée.** Exemple concret — la validation implicite du schéma
initial faisait gagner du temps à l'enseignant au prix d'une note moins sûre pour
l'étudiant : écartée (§3.1).

**Comment** : un outil **en ligne de commande, sur fichiers texte** (§4), qui pré-corrige
les copies scannées, présente à l'enseignant une revue rapide et ordonnée intelligemment,
et ouvre à l'étudiant une consultation progressive en trois temps (§3.2).

---

## 2. Le problème

- 200 copies × ~30 min = **plus d'une semaine de travail**.
- Le travail est majoritairement **mécanique** et **répétitif** — donc automatisable.
- La correction manuelle a des **défauts de qualité connus** que l'outil peut corriger
  au passage (voir §5.1) : effet d'ordre, effet de halo, dérive du barème en cours de pile.
- Le cycle de réclamation est lent, informel, asymétrique : l'étudiant ne voit
  souvent jamais le détail de sa correction.

---

## 3. Le principe : séparer la LECTURE de la NOTATION

C'est la clarification la plus importante de la conception. Deux choses très différentes
sont mélangées quand on dit « l'étudiant vérifie sa correction » :

| | **Co-validation de la lecture** | **Contestation de la notation** |
| --- | --- | --- |
| Question posée | « la machine a-t-elle bien lu ce que j'ai écrit ? » | « suis-je d'accord avec le barème / le jugement ? » |
| Qui tranche | la preuve matérielle (l'image) — objectif | l'enseignant — subjectif |
| Enjeu juridique | **aucun** | réel |
| Fuite du corrigé | **aucune** (l'étudiant voit ses propres réponses) | oui, nécessite le corrigé |
| Peut arriver quand ? | **immédiatement**, dès la fin de l'épreuve | après validation enseignant |
| Valeur technique | **maximale** — c'est là que sont les erreurs machine | pédagogique |

→ **Conséquence de conception** : ce sont deux fonctionnalités distinctes, avec des
calendriers, des interfaces et des niveaux de risque différents. Les traiter séparément
débloque tout : la partie à forte valeur technique (lecture) est aussi celle qui n'a
**aucun** problème juridique ni de fuite.

### 3.1 Pas de validation implicite — position retenue

**L'enseignant valide toutes les copies.** Décision actée (§12). Juridiquement sain, et ça
ne coûte pas cher **si la revue est bien conçue** (§5) : valider 200 réponses à la même
question via une planche de vignettes prend ~1 min, pas 200 × 30 s.

Le rôle du **score de confiance** change en conséquence : il ne sert **pas à sauter** du
travail, mais à **ordonner** le travail et à **dimensionner** l'effort de relecture.

### 3.2 Divulgation en trois temps

```text
  ┌─ PHASE 0 ─ dès l'ingestion (instantanée si canal photo) ──────────┐
  │  « voici ce que la machine a lu sur ta copie »                    │
  │  ▸ pas de note, pas de corrigé, aucune fuite                      │
  │  ▸ l'étudiant signale une erreur de lecture, mémoire fraîche      │
  │  ▸ il peut RETRANSCRIRE lui-même une réponse mal lue (§9.3)       │
  │  ▸ il valide aussi son identité (§7)                              │
  └───────────────────────────────────────────────────────────────────┘
                                 ▼
             ══ revue et validation par l'enseignant (§5) ══
                                 ▼
  ┌─ PHASE 1 ─ dès validation ────────────────────────────────────────┐
  │  la NOTE, et rien d'autre                                          │
  │  ▸ pas de détail, pas de barème, pas de réclamation                │
  │  ▸ ne nécessite aucun serveur : PDF/HTML statique envoyé par mail  │
  └───────────────────────────────────────────────────────────────────┘
                                 ▼
  ┌─ PHASE 2 ─ à la date choisie par l'enseignant ────────────────────┐
  │  correction complète : copie, détection, corrigé, barème détaillé  │
  │  ▸ réclamations à motifs structurés, fenêtre limitée dans le temps │
  │  ▸ nécessite le portail web                                        │
  └───────────────────────────────────────────────────────────────────┘
```

**Pourquoi c'est mieux que « tout ouvrir d'un coup » :**
- la phase 1 satisfait l'attente immédiate (« j'ai combien ? ») sans rien exposer
- elle absorbe le pic émotionnel avant d'ouvrir la discussion technique
- elle laisse à l'enseignant le temps de préparer le corrigé diffusable
- elle sépare deux flux de questions (« ma note » / « votre barème ») au lieu de les
  recevoir en même temps

**Point de vigilance sur la phase 0** : elle ne doit **jamais** donner de note avant
validation. Une note qui **baisse** après publication est ingérable socialement. Montrer
la lecture, pas le score. → cette contrainte est **levée** par le mécanisme du §3.3.

**La phase 0 est la clé de voûte technique du projet.** C'est là que se joue la
co-validation de la lecture (§3), l'identification (§7) et la transcription par l'auteur
(§9.3) — c'est-à-dire tout ce qui rend la notation automatique fiable. Elle n'exige **pas**
le canal photo : le portail suffit, le photo n'en est que la version instantanée.

### 3.3 La note qui converge — le gain côté étudiant

Ne pas attendre que tout soit corrigé pour rendre quelque chose. À tout instant, la note
est un **encadrement qui se resserre**.

```text
acquis     = Σ points des questions déjà validées par l'enseignant
restant    = Σ points max des questions pas encore validées
note ∈ [ acquis , acquis + restant ]
stabilisé  = barème validé / barème total
```

> « QCM validé (11 pts), 2 questions ouvertes en cours (9 pts) →
> votre note est **entre 11 et 20**, 55 % du barème est stabilisé. »
> puis « **entre 13 et 15**, 80 % stabilisé »
> puis « **14/20**, note officielle. »

**Propriété garantie — et testable** : l'encadrement ne fait que se resserrer.

```text
[min, max]_{t+1} ⊆ [min, max]_t
```

Invariant parfait pour un test basé sur les propriétés (§13.4). Seule exception à traiter
hors modèle : une sanction disciplinaire globale (transcription infidèle, fraude).

**Pourquoi c'est structurant, et pas cosmétique** : ça **résout la tension du §3.2**. Une
note ne « baisse » jamais, puisqu'elle n'a jamais été promise — la note finale était
toujours **dans l'intervalle annoncé**. L'encadrement est donc **le mécanisme qui rend la
divulgation précoce sûre**. Sans lui, il faut tout attendre ; avec lui, on publie dès la
première passe.

**Recommandation : encadrement dur uniquement, pas d'estimation ponctuelle.** Afficher
« estimation : 14 ± 1 » à partir de la confiance machine est tentant, mais :

- l'encadrement est **prouvable** et ne peut pas être faux ; une estimation, si
- l'étudiant retiendra le chiffre et oubliera la marge
- KISS : une seule notion à expliquer, pas deux

Et l'encadrement devient informatif **vite**, parce que la validation QCM en planches est
rapide (§5.2) : une heure après le scan, tout le QCM peut être validé et une bonne moitié
du barème stabilisée.

**Nouveau critère d'ordonnancement** (complète §5.3) : valider d'abord ce qui **stabilise
le plus de points pour le moins d'effort**. L'enseignant voit sa progression en « % de
barème stabilisé » plutôt qu'en « copies faites » — plus motivant et plus utile à piloter.

### 3.4 L'étudiant peut-il dispenser l'enseignant de revalider ?

**Oui pour la lecture. Jamais pour la notation.**

Ce qui rend la réponse solide : **en phase 0, l'étudiant ne connaît pas le corrigé.**
Valider « j'ai bien coché B » est donc un acte **sans incitation** — il ne sait pas si B
vaut mieux que A. C'est une conséquence directe de la séparation des phases (§3.2), et
c'est exactement ce qui manquait au schéma de co-validation initial.

**Trois conditions :**

1. **Lecture seulement.** On ne délègue pas la note, on délègue **l'établissement du fait** :
   ce que l'étudiant a écrit. Sur ce point il est plus autoritaire que l'enseignant, qui ne
   fait qu'inférer depuis une image. L'enseignant valide toujours la **notation**.
2. **Avant divulgation du corrigé, fenêtre courte.** Les étudiants échangent en sortant de
   salle : plus la fenêtre est longue, plus l'incitation réapparaît (cas typique — une
   réponse numérique dont on apprend la valeur par un camarade, puis on « valide » une
   lecture erronée qui tombe juste).
3. **Audit résiduel** de 5 à 10 % tiré au hasard. Pas pour attraper des tricheurs, mais
   pour **mesurer** le taux d'erreur et garder la garantie signifiante (§5.4).

**Asymétrie fondamentale** : une validation **confirme** (pas de passage enseignant) ; un
**désaccord** va toujours à l'enseignant. Et le silence reste un non-événement : les items
non validés rejoignent la file enseignant. **Toujours pas de validation implicite** — la
décision §3.1 tient, elle est seulement précisée.

**Effet** : si 90 % des étudiants relisent, la file de validation de lecture fond de 90 %,
et l'enseignant se concentre sur ce qui demande son expertise. C'est précisément
l'objectif du §1.

#### Le point de relecture : à faire, mais en bonus

Donner 1 point pour la relecture maximise la participation, et la participation est ce qui
fait tenir tout le dispositif. Mais c'est la partie la plus contestable du schéma :

- on note un acte **administratif**, pas un apprentissage
- un étudiant malade, sans connexion, ou en difficulté numérique perd un point pour une
  raison **étrangère à la matière** → problème d'équité réel

**Acté : un point de _bonus_, jamais pris sur le total**, plus un moyen de relecture hors
ligne (permanence, version papier). L'incitation est quasi identique ; la défendabilité
n'a rien à voir. Un bonus ne peut que aider ; un point retiré par omission crée un
contentieux.

Conséquence à ne pas oublier au moment de l'implémentation : le bonus **sort du modèle
d'encadrement** du §3.3 — il s'ajoute après coup et peut faire dépasser le `max` annoncé.
C'est la seule entorse tolérée à la propriété de resserrement, et elle est dans le bon
sens (vers le haut). À traiter comme un terme séparé, pas comme une question du barème.

---

## 4. Philosophie : fichiers d'abord, CLI d'abord

Décision actée. Même esprit qu'`acthub` : tout est un fichier lisible, inspectable,
versionnable dans git ; la GUI viendra après, si elle vient.

**Bénéfices directs, pas idéologiques :**
- tout est `grep`-able, `diff`-able, réparable à la main quand ça casse
- les tests d'intégration sont des comparaisons de fichiers → triviaux à écrire
- le sujet et le barème vivent dans git, avec historique et branches
- l'automatisation (Makefile, CI, scripts) tombe gratuitement
- pas d'interface à maintenir pendant que le pipeline bouge encore

### 4.1 Arborescence d'un examen

```text
examen-ct-2026/
  exam.toml               # configuration : structure, mélange, phases, identité
  sujet/
    ex1.md  ex2.md  ...   # contenu des questions (Markdown + frontmatter)
  roster.csv              # liste des étudiants
  build/                  # PRODUIT, jamais édité à la main
    template.json         #   zones et coordonnées, dérivé de la compilation
    copies/0001.pdf …     #   un PDF par copie (mélange appliqué)
    keys/0001.json …      #   clé de correction DE CETTE copie
  scans/                  # images brutes — IMMUABLES, jamais modifiées
  work/                   # état dérivé, reconstructible
    located.jsonl         #   page → (copie, page, homographie, qualité)
    signals.jsonl         #   zone → signal brut (taux de remplissage, crop)
    events.jsonl          #   ◀── JOURNAL APPEND-ONLY : la source de vérité
  out/
    notes.csv
    copies-annotees/
    rapport.md
```

**Règle d'or** : `events.jsonl` est la **seule** source de vérité. Tout le reste
(`notes.csv`, les vues, les statistiques) est une **projection reconstructible**.
`exam rebuild` régénère tout depuis le journal.
→ traçabilité juridique gratuite, non-régression naturelle (rejouer le journal),
débogage trivial, et pas de risque d'état incohérent.

### 4.2 Esquisse des commandes

```text
exam init <dir>                      # squelette de projet
exam build                           # sujet → PDF par copie + clés + template.json
exam scan <pdf|dir>                  # ingestion des images (immuables)
exam locate                          # QR + marqueurs → homographie par page
exam extract                         # zones → signaux bruts
exam grade                           # signaux + clés → notation provisoire
exam identify                        # grille chiffres + OCR nom → rapprochement roster
exam review --by question --order random    # ◀ passe 1 : planches de vignettes
exam review --sort confidence               # ◀ passe 2 : ciblée
exam publish --phase note            # diffusion de la note seule (statique)
exam publish --phase correction      # ouvre la consultation et les réclamations
exam claims                          # liste / arbitre les réclamations
exam finalize                        # fige, export CSV / Moodle
exam report                          # statistiques, taux d'erreur machine, audit
exam doctor                          # vérifications de cohérence du chantier
exam status                          # où en est-on ?
```

### 4.3 Esquisse des formats

`exam.toml` :
```toml
[exam]
id = "ct-2026-01"
title = "Contrôle optimal — Examen final"
seed = 4711                 # graine des permutations : rejouable à l'identique
copies = 220

[answer_sheet]
separate = true             # feuille de réponses détachée (§6)
pages = 2

[identity]
digit_grid = 8              # numéro étudiant, 8 chiffres — lecture déterministe
name_zone = true            # nom manuscrit : contrôle croisé (§7)
roster = "roster.csv"

[shuffle]
exercises = true
questions = "within_exercise"
answers = true

[phases]
note = "2026-01-20T18:00"
correction = "2026-01-23T09:00"
claims_deadline = "2026-01-30T23:59"
```

Une question QCM (`sujet/ex1.md`) :

```markdown
---
id: q12
type: mcq
points: 2
shuffle_answers: true
answers:
  - { text: "$H$ est constant",  correct: true  }
  - { text: "$H$ est croissant", correct: false }
  - { text: "aucune des réponses", correct: false, pin: last }   # jamais mélangée
---
Que peut-on dire du hamiltonien le long d'une extrémale ?
```

Une question ouverte :

```markdown
---
id: q20
type: open
points: 4
answer_box: { lines: 6 }
rubric:
  - { id: r1, points: 1, criterion: "Écrit le hamiltonien complet" }
  - { id: r2, points: 2, criterion: "Applique la condition de stationnarité" }
  - { id: r3, points: 1, criterion: "Conclut sur le signe du multiplicateur" }
---
Montrer que ...
```

Note : le barème n'est **pas** « note sur 4 », c'est une **liste de critères**. Voir §9.2 —
c'est ce qui rend la notation IA fiable, et c'est aussi ce qu'on montre à l'étudiant.

---

## 5. La revue enseignant — **c'est ici qu'est le gain de temps**

Puisqu'on valide tout, cette brique **est** le projet. Trois idées portent l'essentiel.

### 5.1 Corriger par question, en ordre aléatoire, en aveugle

Trois choix qui améliorent la **qualité** de notation, pas seulement la vitesse :

| Choix | Corrige quel biais |
| --- | --- |
| **par question** (toutes les copies pour Q1, puis Q2…) | dérive du barème entre le début et la fin de la pile |
| **ordre aléatoire dans la question** | effet d'ordre, fatigue, effet de contraste avec la copie précédente |
| **sans le nom ni la note cumulée** | effet de halo, biais de réputation |

C'est de la littérature classique sur la docimologie ; l'outil rend ces bonnes pratiques
**gratuites** alors qu'elles sont pénibles à la main. Argument fort pour l'adoption, et
argument de qualité opposable si le dispositif est contesté.

**Quatrième biais, souvent oublié : la calligraphie.** Une belle écriture obtient de
meilleures notes, à contenu égal. Si l'enseignant note depuis le **texte transcrit**
(§9.3) plutôt que depuis l'image, ce biais disparaît.
→ Règle d'affichage : **le texte par défaut, le crop à un clic.**

#### L'anonymat n'est pas un réglage global, c'est un attribut de chaque passe

Principe du moindre privilège appliqué à l'information : **anonyme par défaut, on révèle
seulement ce que la tâche exige.**

| Passe | Nom | Écriture | Pourquoi |
| --- | --- | --- | --- |
| Validation de lecture (QCM) | non | crop seul | jugement **factuel** : le nom n'apporte rien |
| **Validation d'identité** (§7) | **oui** | zone nom | c'est l'objet même de la tâche |
| **Notation** (planches, critères) | non | texte transcrit d'abord | c'est là que le biais **coûte cher** |
| Arbitrage d'une transcription | non nécessaire | crop + transcription | jugement factuel |
| Arbitrage d'une réclamation de fond | **de préférence non** | réponse | c'est du jugement → biais |
| Finalisation, export | oui | — | nécessaire |

Nuance retenue : sur les passes **factuelles** (lecture, transcription), voir le nom n'est
pas grave. Sur les passes de **jugement** (notation, réclamation de fond), il faut le
masquer. La ligne de partage est « est-ce que je constate, ou est-ce que j'apprécie ? »

### 5.2 Planche de vignettes (contact sheet) — le vrai accélérateur

Au lieu d'afficher une copie à la fois, afficher **toutes les réponses à la même question,
côte à côte**, groupées par ce que la machine a décidé.

- QCM : une grille de 200 crops de la même zone. L'œil humain détecte une anomalie dans
  une grille homogène **en quelques secondes**. Valider 200 copies pour une question :
  ~1 minute.
- Question ouverte : grouper par **verdict de critère**. « Voici les 40 copies où l'IA a
  coché _a posé l'équation d'état_ » → on parcourt, on décoche les erreurs.
  → **revue par grappe**, pas par copie. C'est un facteur 10, pas 20 %.

Techniquement, c'est une page HTML statique générée par le CLI (grille d'images + cases),
qui enregistre un JSON de corrections. Pas besoin de serveur. `exam review --serve` peut
lancer un petit serveur local si l'interaction le demande.

### 5.3 Deux passes, deux tris

| Passe | Ordre | But |
| --- | --- | --- |
| **1 — validation** | aléatoire, par question, en aveugle | passer sur **tout**, vite, sans biais |
| **2 — ciblée** | confiance croissante, puis seuils de note, puis réclamations | concentrer l'attention là où elle vaut |

Les seuils de note (10/20, admission, mention) méritent un traitement à part : c'est là
qu'une erreur d'un demi-point a des conséquences disproportionnées.

### 5.4 Le taux d'erreur machine, mesuré gratuitement

Chaque correction faite par l'enseignant, chaque désaccord signalé par un étudiant, chaque
transcription acceptée est **un cas d'erreur machine étiqueté** — produit gratuitement par
la personne la mieux placée pour le faire. C'est un **artefact de première classe**, pas un
sous-produit : il mérite son propre schéma et sa propre commande (`exam report`).

Ce qu'il faut enregistrer à chaque correction :
`(type de zone, signal brut, décision machine, confiance, décision retenue, qui a corrigé,
outil utilisé, version du modèle / du prompt)`.

Ce que ça permet, concrètement :

- **taux d'erreur par type de question et par outil** → quoi automatiser, quoi router
  systématiquement vers l'humain
- **calibrer les seuils sur des données** plutôt que sur l'intuition : seuil de remplissage
  d'une bulle, seuil de confiance au-delà duquel on ne relit plus
- **détecter une régression** lors d'un changement de modèle ou de prompt (§13.3)
- **choisir le bon outil** à chaque barreau de l'échelle (§14.1) sur des mesures
- **un corpus de non-régression qui grossit à chaque examen**, sans effort (§13.2)
- **une métrique publiable** et un argument de qualité opposable (§17)

C'est aussi ce qui donne son sens à l'audit résiduel du §3.4 : sans mesure du taux
d'erreur, la garantie offerte à l'étudiant n'est qu'une affirmation.

---

## 6. Feuille de réponses détachée

Idée retenue : les **cases de réponse** (QCM **et** questions ouvertes) sur les 1-2
premières pages, les **énoncés** après.

**Bénéfices, plus gros qu'il n'y paraît :**
- l'étudiant ne photographie/on ne scanne que **1-2 pages au lieu de 4-8** → volume divisé
  par 4, et c'est le goulot d'étranglement du processus
- la mise en page des zones est **fixe et connue** → le recalage géométrique devient
  quasi-trivial et très robuste
- la planche de vignettes (§5.2) devient facile : même zone, même position, toutes copies
- le mélange des questions (§8) n'affecte **pas** la feuille de réponses : la case _k_
  correspond toujours à la « question _k_ » telle que numérotée sur _son_ sujet

**Contraintes à assumer :**
- les réponses ouvertes doivent **tenir dans les cadres** → cohérent avec §9.2.A, et c'est
  de toute façon une bonne pratique de conception de sujet
- prévoir un type de zone « réponse longue » occupant une page entière quand nécessaire
- le brouillon n'est pas ramassé : à annoncer clairement
- **feuilles annexes** : prévoir dans le modèle de données dès le début un concept de
  feuille supplémentaire avec son propre QR, rattachée à une copie (implémentation différée)

---

## 7. Identification des étudiants

### 7.1 Deux canaux redondants — recommandation

| Canal | Fiabilité | Coût |
| --- | --- | --- |
| **Grille de chiffres** (numéro étudiant, 8 chiffres à cocher) | très haute — c'est de l'OMR, déterministe, testable | une zone sur la feuille |
| **Nom manuscrit + OCR + rapprochement roster** | moyenne | l'IA, avec sa variance |

→ **Utiliser les deux.** La grille est le canal principal (déterministe) ; le nom est le
**contrôle croisé**. Quand les deux concordent, confiance maximale sans intervention.
Quand ils divergent → file enseignant. C'est du KISS bien placé : le cas difficile devient
rare au lieu d'être le cas nominal.

### 7.2 Chaîne de rapprochement du nom

```text
crop zone nom → OCR/VLM → chaîne normalisée
   → appariement flou sur roster.csv (Jaro-Winkler / Levenshtein)
      → candidat unique, score élevé          → proposition, confiance haute
      → plusieurs candidats proches           → LLM avec la liste restreinte en contexte
      → rien de convaincant                   → file enseignant
```

Contraintes de cohérence à vérifier automatiquement (`exam doctor`) :

- un étudiant du roster reçoit **au plus une** copie
- toute copie non attribuée ou en conflit est signalée, jamais résolue en silence

### 7.3 Validation par l'étudiant — et le piège de sécurité

L'étudiant valide son identité (phase 0 ou 1). S'il n'est pas d'accord, il choisit dans
la liste.

⚠️ **Piège** : si un étudiant peut réassigner une copie, il peut **revendiquer la copie
d'un autre**, ou détacher la sienne d'une mauvaise note. C'est une vraie faille.

**Règle** : la correction de nom par l'étudiant est une **demande**, jamais une écriture.
C'est **le même primitif que la transcription d'une réponse** (§9.3) — la machine n'a pas
su lire une zone, l'auteur fournit la lecture, l'enseignant valide. À implémenter une
seule fois. Mécanismes :

- rien n'est appliqué sans validation enseignant
- la liste proposée est restreinte (candidats proches), pas le roster complet
- une réassignation vers un étudiant qui a déjà une copie est **bloquée** et signalée
- tout est journalisé comme événement distinct

**Vue enseignant** : le crop de la zone nom, le nom détecté, la confiance, le canal
(grille / OCR / les deux), et **un marqueur explicite** si l'étudiant a demandé un
changement. Cette information doit sauter aux yeux.

### 7.4 Anonymat

**L'anonymat n'est pas imposé dans son établissement** (§16.1). Ça ne change rien à la
conception : le masquage par passe du §5.1 reste recommandé, mais pour **réduire le biais
de notation**, pas pour satisfaire une règle. C'est un choix de qualité, révocable, et non
une contrainte.

Si l'anonymat devenait obligatoire un jour : le crop de la zone nom est simplement masqué
pendant les passes de correction et révélé à l'étape d'attribution. Anonymat fonctionnel,
zéro complexité ajoutée — le mécanisme est déjà là.

---

## 8. Sujets mélangés (à la AMC)

Mélanger exercices, questions et réponses pour limiter la copie entre voisins.

### 8.1 Déclaration d'indépendance

Le mélange n'est valide que là où c'est dit explicitement. À prévoir :

- `shuffle: true/false` par niveau (exercice / question / réponse)
- `depends_on: [qN]` — une question qui utilise le résultat d'une autre ne bouge pas
- `pin: last|first` sur une réponse (« aucune des réponses ci-dessus », réponses numériques
  ordonnées, « toutes les précédentes »)
- groupes de questions déplaçables en bloc

### 8.2 Mise en œuvre

Permutation dérivée de façon **déterministe** de `(seed, copy_id)` — donc rejouable à
l'identique, et **stockée** dans `build/keys/NNNN.json` pour l'audit. Les deux : la
dérivation garantit la reproductibilité, le stockage garantit la traçabilité.

L'identifiant de variante est imprimé **et** encodé dans le QR → un appariement copie/clé
erroné est structurellement impossible.

### 8.3 Décision structurante à prendre dès M0

Même si le mélange n'est implémenté que plus tard : **la clé de correction doit être
par copie, pas par examen, dès le premier jour.** C'est un choix de modèle de données à
un champ près, mais le rétro-adapter coûterait cher. YAGNI s'applique à la fonctionnalité,
pas à cette décision de structure.

### 8.4 Tests

Terrain idéal pour les tests basés sur les propriétés :

- `dépermuter(permuter(clé, seed, id)) == clé` pour tout `(seed, id)`
- toute contrainte `pin` / `depends_on` est respectée pour toute graine
- l'ensemble des réponses correctes est invariant par permutation
- deux copies tirées au hasard ont une probabilité faible de permutation identique

---

## 9. Les points durs techniques

### 9.1 QCM — facile, mais à ne pas sous-estimer

Vision classique (OpenCV), pas d'IA. Les vrais pièges : ratures, cases à moitié cochées,
croix qui débordent, pliures, agrafes, page à l'envers ou manquante, et surtout les
**cas ambigus** (0 case cochée, 2 cases cochées) — exactement ceux où la confiance doit
être basse.

**Antériorité** : [AMC](https://www.auto-multiple-choice.net/) fait déjà très bien ça,
open source, français, mature. Écrit en Perl, très couplé à LaTeX, difficile à embarquer
comme bibliothèque. → Décision en §12 : réimplémenter le noyau OMR (quelques centaines
de lignes, testable, embarquable) en s'inspirant sans scrupule de ses choix de conception.

### 9.2 Questions ouvertes — **le vrai point dur**

Difficultés, par gravité :

1. **L'écriture manuscrite mathématique.** Les VLM lisent correctement du texte manuscrit
   propre mais se trompent régulièrement sur des formules (indices, exposants, fractions,
   lettres grecques, `ẋ` vs `x`). **Si tes examens contiennent des calculs, c'est le
   facteur limitant n°1.** → spike S1 (§11).
2. **Cohérence.** Le même modèle, sur la même copie, deux fois, peut noter différemment.
   Il faut **mesurer** cette variance, pas l'ignorer.
3. **Complaisance.** Les LLM sont structurellement trop généreux. Calibration obligatoire.
4. **Hallucination.** Le modèle « lit » une étape qui n'est pas sur la copie.

**Atténuations, par efficacité décroissante :**

- **A. Contraindre l'espace de réponse.** De loin le plus efficace, et gratuit.
  Résultat final encadré, grille de chiffres pour le numérique, « justifiez en 3 lignes
  dans le cadre », décomposition en étapes avec cases intermédiaires.
  → **Le projet change ta façon d'écrire les sujets.** À assumer, et cohérent avec §6.

- **B. Barème structuré, pas note globale.** Le modèle ne note pas « sur 4 » : il répond
  à une liste de critères (§4.3). La note est **déterministe** étant donné les critères ;
  le modèle ne fait qu'une **classification**, où il est bien meilleur.
  Trois bénéfices d'un coup : fiabilité, justification directement affichable à
  l'étudiant, et **revue par grappe** (§5.2) rendue possible.

- **C. Auto-cohérence pour la confiance.** Noter k fois (k = 3 à 5), mesurer l'accord.
  **Le désaccord entre tirages est le signal de confiance le plus fiable** — bien meilleur
  que la confiance auto-déclarée par le modèle, qui ne vaut rien.

- **D. Droit de refus.** Le modèle doit pouvoir répondre « illisible / je ne sais pas »
  → routage direct vers la file enseignant. Un système qui sait dire non est bien plus
  utile qu'un système toujours confiant.

- **E. Transcription explicite avant notation.** Le modèle écrit d'abord ce qu'il lit,
  puis note. La transcription est montrée à l'étudiant → l'hallucination devient visible
  et contestable.

- **F. Laisser l'auteur fournir la lecture.** → §9.3, c'est le mécanisme le plus puissant
  et il mérite une section à lui.

### 9.3 La transcription par l'auteur — **le déblocage du point dur**

**Principe** : quand la machine n'arrive pas à lire une réponse manuscrite, on demande à
l'étudiant de **la retranscrire lui-même** en Markdown + LaTeX. Il obtient en échange une
notation rapide et correcte. L'enseignant est notifié et valide. Au moment de la saisie,
un avertissement explicite : **écrire autre chose que ce qui est sur la copie fait perdre
des points.**

#### Pourquoi c'est fort

1. **Seul l'auteur connaît la réponse avec certitude.** Sur une formule manuscrite ambiguë,
   l'étudiant a une information que ni la machine ni l'enseignant n'ont.
2. **Vérifier est beaucoup plus facile que lire.** Pour l'enseignant : comparer un crop à une
   transcription proposée prend ~3 secondes ; déchiffrer la même formule de zéro en prend 60.
   Pour la machine : « cette transcription est-elle cohérente avec cette image ? » est une
   tâche de **vérification**, où les VLM sont nettement plus fiables que sur la **génération**.
   C'est l'asymétrie à exploiter.
3. **Le travail est réparti sur ceux qui en profitent**, et seulement sur les cas problématiques.
4. **Ça ne coûte rien en cas d'échec** : le repli est la lecture manuelle par l'enseignant,
   c'est-à-dire exactement le statu quo.
5. **Bénéfice pédagogique** : l'étudiant relit et reformule sa propre réponse.

#### La cascade à trois niveaux

```text
  la machine lit, confiance haute              →  notation automatique
       │ sinon
       ▼
  la machine dit « je ne sais pas lire »       →  on demande la transcription à l'auteur
       │                                          (pré-remplie avec la tentative machine)
       │ transcription fournie et cohérente    →  notation reprise, validée par l'enseignant
       │ sinon
       ▼
  lecture manuelle par l'enseignant            →  statu quo, jamais pire qu'aujourd'hui
```

Chaque niveau est le repli du précédent. **Rien n'est jamais perdu** — c'est exactement
l'esprit « toujours fonctionnel ».

#### Le vecteur de fraude, et comment le fermer

⚠️ Le risque est évident : **l'étudiant transcrit une meilleure réponse que celle qu'il a
écrite.** Quatre garde-fous, du moins au plus coûteux :

1. **Pré-remplissage** avec la tentative de la machine. L'étudiant **corrige** au lieu de
   saisir de zéro. On obtient un **diff** : c'est ça que l'enseignant regarde, pas le texte
   entier. Réduit énormément le coût de vérification et rend l'ajout visible.
2. **Heuristiques automatiques, sans IA** : ratio de longueur transcription / taille du
   cadre, nombre de lignes, présence de symboles absents du crop. Une transcription trois
   fois trop longue pour le cadre est signalée **avant** toute intervention humaine.
3. **Vérification par VLM** : « image + transcription → cohérent / incohérent / incertain ».
   Tâche facile. `incohérent` = alerte forte vers l'enseignant.
4. **Asymétrie de la sanction.** C'est le vrai dissuasif. Le gain d'une transcription
   infidèle (quelques points) doit être très inférieur au coût si elle est détectée
   (zéro à la question, voire procédure disciplinaire). À **annoncer avant l'examen**,
   pas seulement au moment de la saisie.

L'affichage côté enseignant doit être : **crop | lecture machine | transcription étudiant**,
côte à côte, différences surlignées. En planche de vignettes (§5.2), 20 à la fois.

#### C'est le même mécanisme que la correction du nom (§7.3)

Un seul primitif, deux usages :

> _la machine n'a pas su lire la zone Z → l'auteur fournit la lecture → l'enseignant valide_

Mêmes règles dans les deux cas : c'est une **demande**, jamais une écriture ; c'est
journalisé comme événement distinct ; l'enseignant voit toujours le crop à côté.
→ À implémenter **une fois**, à réutiliser. DRY au niveau de la conception, pas du code.

#### Où ça se place dans le calendrier

La transcription doit avoir lieu **avant la notation**, sinon la note change après
publication (§3.2, point de vigilance). Donc c'est de la **phase 0**.

**Important** : la phase 0 n'a pas besoin du canal photo (M7). Scanner lundi, ouvrir la
phase 0 lundi soir, la fermer mardi, noter mercredi, diffuser la note jeudi — il suffit du
portail (M5). Le canal photo n'est que le cas particulier « instantané » de la phase 0.

#### Ce que ça change pour le risque du projet

Sans ce mécanisme, la question est : _« le VLM sait-il lire les maths manuscrites ? »_ —
et la réponse est probablement « pas assez bien », ce qui tue M6.

Avec ce mécanisme, la question devient : *« le VLM sait-il reconnaître qu'il ne sait pas
lire ? »* — un problème de **calibration**, nettement plus facile — *« et les étudiants
joueront-ils le jeu ? »* — un problème de **participation**, pas un problème technique.
Et l'incitation est forte : note plus rapide et plus juste.

→ **Le point dur n°1 du projet passe d'un risque technique à un risque d'usage.**
C'est un très bon échange. Conséquence directe sur le spike S1 (§11).

#### Équité — exigence, pas confort

Un étudiant mal à l'aise avec LaTeX ne doit **pas** être pénalisé sur sa note. Le repli
« lecture manuelle par l'enseignant » doit donner **exactement le même résultat**,
seulement plus tard. La transcription achète de la **vitesse**, jamais des **points**.
À vérifier explicitement dans les tests et à écrire dans la consigne.

### 9.4 Photo smartphone (canal instantané de la phase 0)

- **Fuite du corrigé** : réglée par construction. La phase 0 ne montre que la lecture, pas
  le corrigé ni la note (§3.2). Reste à bloquer l'accès avant la fin de l'épreuve pour tous.
- **Divergence photo ↔ scan officiel** : ce n'est pas un bug, c'est un **capteur de fraude
  gratuit**. Signalé à l'enseignant. L'annoncer suffit à dissuader.
- **Qualité d'image** : perspective gérée par les marqueurs de coin ; pour le reste,
  **retour immédiat côté téléphone** (« page 2 floue, reprenez ») plutôt qu'un traitement
  héroïque côté serveur.
- **Sécurité des jetons** : le QR de la copie porte un `submit_token` en **écriture seule**.
  Le `review_token` (consultation, réclamation) est **distinct** et envoyé par l'enseignant.
- **Bénéfice caché** : si le canal photo devient fiable, **le scan des 200 copies disparaît**.
  C'est peut-être le plus gros gain de temps de tout le projet — mais c'est le plus risqué,
  donc le plus tard.

---

## 10. Points bloquants non techniques

### 10.1 Juridique — très allégé par la décision §3.1

Sans validation implicite, l'essentiel du risque disparaît : l'enseignant valide tout, la
consultation étudiante est une **phase de réclamation anticipée et tracée** qui précède et
n'éteint pas les voies de recours. Ça améliore la situation actuelle au lieu de la fragiliser.
Reste à faire : une conversation d'information avec la direction des études (§11, S3),
peu risquée désormais.

### 10.2 RGPD / hébergement

- Copies + notes = données personnelles en contexte scolaire.
- **Hébergement auto-géré obligatoire** (VM université ou VPS maîtrisé). Pas de SaaS tiers.
- **Envoyer des copies manuscrites à une API LLM externe est le point délicat.** Par ordre
  de conformité : (1) modèle local (Qwen-VL, InternVL) ; (2) **Albert** (LLM de l'État,
  hébergé en France — probablement la bonne réponse institutionnelle) ; (3) API commerciale,
  qui demande une base légale (les copies anonymes aident beaucoup).
- → **Abstraction du fournisseur LLM dès le début** : une interface, des adaptateurs
  interchangeables (Albert / API / local / **mock**). Du SOLID là où il sert vraiment.
- Bonne nouvelle : la phase CLI (M0–M4) ne sort **aucune donnée** de ta machine.

### 10.3 Adoption

- Risque de **déluge de réclamations** la première fois. → plafonner le nombre de
  réclamations par copie, motif structuré obligatoire, traitement en lot côté enseignant.
- **Effet secondaire positif majeur** : les étudiants voient enfin le barème détaillé.
  Gain pédagogique réel, à mettre en avant pour faire accepter le dispositif.

---

## 11. À valider AVANT de construire (spikes)

Expériences courtes et jetables, à faire en premier. **Ordre revu après le §12** : S2
d'abord, parce qu'il est sur le chemin critique du 23 novembre.

| # | Question | Protocole | Durée | Si ça échoue |
| --- | --- | --- | --- | --- |
| **S2** ⚡ | Le round-trip **impression → remplissage → scan** tient-il sur _ton_ matériel ? | Imprimer une grille test sur **ton** imprimante, la faire remplir salement (ratures, croix débordantes, crayon pâle), scanner sur **ton** scanner. Mesurer le taux d'erreur de lecture des bulles **et la lisibilité du QR après impression**. | ~1 j | Ajuster le design : taille des bulles, contraste, taille et redondance du QR, position des marqueurs. **À refaire jusqu'à ce que ça passe** — tout en dépend. |
| **S1** | Le VLM **sait-il quand il ne sait pas lire** ? | 20 réponses réelles variées. Mesurer **trois** choses : (a) taux de lecture correcte ; (b) **calibration du refus** — quand il se trompe, le dit-il ? ; (c) **taux de détection d'incohérence** entre une image et une transcription falsifiée exprès. Tester Albert et Claude. | ~1 j | Si (a) est faible mais (b) et (c) sont bons → le projet tient via la transcription par l'auteur (§9.3). Si (b) est mauvais → pas d'IA sur les questions ouvertes. **Ne conditionne rien avant décembre** (§16.2). |
| **S3** | Le cadre institutionnel passe-t-il ? | Une conversation : direction des études. | 1 réunion | Peu de risque désormais (§10.1). Le périmètre de novembre (pas de portail, pas d'IA, aucune donnée sortante) ne soulève presque rien. |

**S2 est sur le chemin critique : si le QR ou les marqueurs ne survivent pas à
l'impression et au scan, rien d'autre ne compte.** À lancer cette semaine.

---

## 12. Roadmap — chaque étape livre quelque chose d'utilisable

Principe : **à la fin de chaque milestone, tu peux t'en servir sur un vrai examen.**

### Cible réelle : examen du lundi 23 novembre 2026

**9,6 semaines.** C'est désormais ce qui cadre le périmètre, pas l'inverse.

#### L'asymétrie qui doit piloter le plan

Le projet a deux moitiés, avec deux échéances **très** différentes :

| Moitié | Échéance | Pourquoi |
| --- | --- | --- |
| **Génération** — `build` : feuille de réponses, marqueurs, QR, clés par copie, mélange | **dure : début novembre** | La feuille est imprimée **une fois**. Ce qui n'y est pas ne pourra jamais y être. |
| **Lecture et revue** — `locate`, `extract`, `grade`, `review` | **souple : décembre** | Les scans ne périment pas. On peut finir le pipeline après l'examen et corriger avec. |

→ **Priorité absolue à ce qui est irréversiblement lié à la date.** Si `build` est juste,
tout le reste peut glisser sans dommage. Si `build` est faux, les scans ne valent rien.

#### Le repli qui rend l'opération sans risque

La feuille de réponses doit rester **corrigeable à la main**. Si le pipeline n'est pas prêt
le 24 novembre, tu corriges comme d'habitude — et tu y gagnes même un peu, puisque toutes
les réponses sont regroupées sur 1-2 pages au lieu d'être dispersées dans la copie.

**Il n'y a donc pas de scénario catastrophe.** C'est ce qui rend l'expérience acceptable
dès la première fois, et c'est à vérifier explicitement avant d'imprimer.

#### Périmètre retenu

**Dedans :**

- **M0** — socle, `build`, `locate`
- **M1** — QCM de bout en bout, export CSV → **couvre 70 % du barème** (§16.2)
- **la moitié génération de M3** (mélange) — parce que non rattrapable après coup

**Dehors, explicitement :**

- **M2** (planches de vignettes) — très utile, mais peut arriver en décembre et servir quand même
- **M4 à M8** — diffusion, portail, transcription, IA, photo. Aucun n'est nécessaire.
- **les questions ouvertes restent corrigées à la main** : 30 % du barème, statu quo.

#### Calendrier

| Période | Objet | Sortie attendue |
| --- | --- | --- |
| 17 sept – 1er oct | **Spikes S2 puis S1** | le round-trip impression → remplissage → scan tient-il sur _ton_ matériel ? |
| 1er – 22 oct | M0 + M1 | `build` → `locate` → `extract` → `grade` → CSV |
| **22 – 29 oct** | **Répétition générale** | 10 feuilles imprimées, remplies salement par des cobayes, scannées, corrigées |
| 29 oct – 12 nov | Corrections issues de la répétition, puis mélange | |
| **12 – 19 nov** | **Gel** | sujet final, impression. Zéro changement de code. |
| 23 nov | Examen | |
| après | Correction, mesure du taux d'erreur (§5.4), puis M2 | |

**Le jalon qui compte n'est pas le 23 novembre, c'est le 29 octobre.** Si la répétition
générale passe, le reste est du confort. Si elle échoue, il reste trois semaines pour
replier sur un sujet classique sans QR. **Cette décision se prend le 29 octobre, pas le 20
novembre** — la poser dans l'agenda maintenant.

#### Inversion de l'ordre des spikes

**S2 passe avant S1.** Avec 70 % de QCM et des questions ouvertes corrigées à la main en
novembre, S1 (le VLM sur les maths manuscrites) ne conditionne plus rien avant décembre.
S2 (l'OMR sur ton imprimante et ton scanner) conditionne **tout**, et il est sur le chemin
critique de la génération.

---

### M0 — Socle : fichiers, formats, géométrie

`exam init`, `exam build` (PDF + clés **par copie**, sans mélange), `exam locate`.
Modèle de données, journal d'événements, corpus synthétique de test.
**Utilisable seul ?** Non — c'est la seule étape sans valeur directe. Assumé, et courte.

### M1 — QCM de bout en bout, CLI ⭐

`scan` → `locate` → `extract` → `grade` → `export`. Identification par grille de chiffres.
Pas de web, pas d'IA, pas de mélange.
**Utilisable seul ?** **Oui, massivement.** L'essentiel du gain sur un examen à dominante
QCM. Si le projet s'arrêtait là, il aurait déjà payé son coût. → **la vraie première release.**

### M2 — Revue enseignant ⭐⭐

`exam review` : planches de vignettes, par question, ordre aléatoire, en aveugle, puis
passe ciblée par confiance. Corrections enregistrées comme événements.
**Utilisable seul ?** Oui — **c'est le cœur du gain de temps** une fois qu'on valide tout.

### M3 — Sujets mélangés

Déclaration d'indépendance, permutations par copie, tests de propriété.
(Modèle de données prévu dès M0, §8.3.)
**Utilisable seul ?** Oui — c'est une fonctionnalité d'intégrité, indépendante du reste.

### M4 — Diffusion phase 1 (la note seule)

`exam publish --phase note` : un retour PDF/HTML **statique** par étudiant, envoyé par mail.
**Aucun serveur nécessaire.** Boucle complète scan → note → étudiant, toujours en CLI.

### M5 — Portail étudiant : phase 0 (lecture) et phase 2 (réclamations)

Serveur minimal, liens magiques. Deux usages du **même primitif** « l'auteur fournit la
lecture que la machine n'a pas su faire » (§9.3) :

- **validation d'identité** (§7.3) — le cas simple, à faire en premier
- **consultation du détail et réclamations structurées** (phase 2), `exam claims` en CLI

**Première brique web du projet** — volontairement tard, et elle ouvre la voie à M6.

### M6 — Transcription par l'auteur

Éditeur Markdown + LaTeX avec aperçu, pré-rempli par la tentative machine, avertissement
et certification de fidélité, heuristiques de détection, vue enseignant
crop | machine | étudiant.
**Livrable indépendant de l'IA** : marche déjà pour une réponse numérique mal lue ou une
zone abîmée. C'est l'infrastructure qui rend M7 viable.

### M7 — Questions ouvertes assistées par IA

Barème structuré, notation par VLM avec sortie contrainte, **refus calibré**, confiance par
auto-cohérence, vérification image↔transcription, **revue par grappe** (§5.2).
Le risque principal est déjà absorbé par M6.

### M8 — Canal photo instantané

Dépôt mobile, contrôle qualité côté client, blocage temporel, détection de divergence
photo ↔ scan. Rend la phase 0 instantanée — et, si la fiabilité suit, peut faire
**disparaître le scan** complètement.

**Ordre justifié** : le risque décroît (géométrie → OMR → ergonomie → web → transcription
→ IA → mobile) pendant que la valeur croît, et chaque étape s'appuie sur un socle déjà
éprouvé en conditions réelles. Les cinq premières n'ont **ni serveur ni IA ni donnée
sortante**. M6 avant M7 est délibéré : on construit le filet **avant** de marcher sur le fil.

---

## 13. Stratégie de test

### 13.1 Corpus synthétique — **l'actif le plus précieux du projet**

Générer programmatiquement des copies remplies, les rendre en image, appliquer des
déformations paramétrées (rotation, perspective, bruit, flou, contraste, bavure, pliure,
tache), vérifier que le pipeline retrouve **exactement** la vérité terrain connue.

Reproductible, aucune donnée personnelle, couvre les cas rares à volonté, et donne une
**courbe de dégradation** (taux d'erreur vs amplitude de déformation) qui devient le test
de non-régression le plus parlant du projet.

### 13.2 Corpus réel anonymisé

Petit jeu de scans réels annotés à la main. Figé, versionné, rejoué à chaque changement.
**Il grossit gratuitement** : chaque correction faite en passe 1 (§5.4) est un cas étiqueté.

### 13.3 Tests de la partie IA

On ne teste pas un LLM comme une fonction pure.

- **Unitaires** : LLM **toujours mocké**. On teste le parsing, la validation du schéma de
  sortie, l'application du barème, la gestion des refus, les timeouts, les réponses malformées.
- **Suite d'évaluation** (séparée, manuelle ou nocturne) : assertions **statistiques**,
  pas exactes — `|note_machine − note_humaine| ≤ 1 pt` sur ≥ 90 % des cas, aucun écart > 3 pts.
- **Test de variance** : noter 5 fois la même copie, vérifier que l'écart-type reste sous
  un seuil. Un modèle instable est inutilisable quelle que soit sa moyenne.
- Tout changement de prompt **ou de modèle** rejoue cette suite. Seule protection contre
  la régression silencieuse.

### 13.4 Tests basés sur les propriétés

Deux terrains naturels : la géométrie (homographies, round-trip) et les permutations (§8.4).

### 13.5 Mocks nécessaires

`LLMClient`, `Storage`, `Mailer`, et surtout **`Clock`** — toute la logique de phases et
d'échéances en dépend, et ce sera une source de bugs subtils si l'horloge n'est pas injectable.

### 13.6 Tests d'intégration = comparaisons de fichiers

Bénéfice direct du choix « fichiers d'abord » (§4) : un test d'intégration est un dossier
d'entrée, une commande, et un dossier attendu. Les `.jsonl` se diffent, les images se
comparent par métrique. Presque rien à écrire.

---

## 14. Architecture logicielle

Aligné sur `acthub` (Python, click, séparation `core`/`cli`, domaine + repositories + codecs).

```text
exam_core/          # aucune dépendance à l'IHM, au réseau, au système de fichiers concret
  domain/           #   modèles purs : Exam, Question, Zone, Copy, Key, Signal, Grade, Event
  codecs/           #   lecture/écriture TOML, Markdown+frontmatter, JSONL
  vision/           #   locate, extract — fonctions pures image → signal
  reading/          #   port LECTURE  : image → texte   (OMR / HTR / VLM / étudiant)
  judging/          #   port JUGEMENT : texte + barème → critères cochés
  grading/          #   critères → note. Déterministe, sans IA.
  repositories/     #   accès au journal d'événements et aux projections
  services/         #   orchestration des cas d'usage
exam/               # CLI click, une commande par fichier (convention acthub)
```

Points de conception qui comptent vraiment (le reste suivra) :

- **`vision` et `grading` sont des fonctions pures** → testables sans monde extérieur.
- **`reading` et `judging` sont deux ports distincts** → voir §14.1, c'est la décision
  structurante de cette section.
- **`Clock` injectable** → les phases et échéances sont testables.
- **Le journal d'événements est append-only** → tout le reste est une projection.

### 14.1 L'échelle des outils — le bon outil au bon endroit

Principe : **ne monter l'échelle que quand c'est nécessaire.** Chaque barreau est plus
cher, plus lent, plus flou et moins testable que le précédent.

| # | Outil | Pour quoi | Testable comment |
| --- | --- | --- | --- |
| 0 | **OMR pur** (OpenCV, seuils) | bulles QCM, grille de chiffres, marqueurs | déterministe, corpus synthétique |
| 1 | **Appariement flou** (Levenshtein, Jaro-Winkler) | nom → roster (§7.2) | déterministe, table de cas |
| 2 | **OCR / HTR spécialisé** | texte manuscrit, formules | jeu annoté, métriques CER/WER |
| 3 | **VLM** (image → texte) | ce que le barreau 2 rate, et le **refus calibré** | eval set d'images, mesure de variance |
| 4 | **LLM texte** (texte + barème → critères) | jugement sur une réponse **déjà transcrite** | **fixtures texte** — rapide et peu cher |

**Vocabulaire** : un **VLM** (_vision-language model_) prend des images en entrée ; un
**LLM** ne prend que du texte. Claude, GPT-4o, Qwen-VL sont des VLM, utilisables aussi en
mode texte seul. Pour lire un scan il faut un VLM ; pour juger un texte déjà transcrit, un
LLM suffit — moins cher, plus rapide, plus stable, et disponible en local.

Pour les maths au barreau 2, mettre en concurrence dans le spike S1 (§11) les outils de
**HMER** (_handwritten mathematical expression recognition_) et les convertisseurs
formule → LaTeX face à un VLM généraliste. Rien ne dit que le VLM gagne.

#### Conséquence architecturale : séparer `lecture` et `jugement`

```text
image ──▶ [ LECTURE ] ──▶ texte ──▶ [ JUGEMENT ] ──▶ critères cochés ──▶ note
            port L                     port J                          déterministe
         OMR / HTR / VLM            LLM texte / humain
         / ÉTUDIANT (§9.3)
```

Deux ports, deux familles d'adaptateurs interchangeables. Bénéfices, tous concrets :

- **on change d'outil de lecture sans toucher au jugement**, et réciproquement — c'est
  exactement le « bon outil au bon endroit », rendu possible par l'interface
- le jugement devient une tâche **purement textuelle** → son jeu d'évaluation est un CSV de
  `(transcription, barème, verdicts attendus)`. Une suite d'éval qui tourne en 3 minutes au
  lieu d'une heure, et qui ne coûte presque rien. **C'est le plus gros gain de testabilité
  de toute l'architecture.**
- **la transcription par l'auteur (§9.3) se branche sans code supplémentaire** : l'étudiant
  est simplement un troisième adaptateur du port `lecture`. Même interface, même aval.
- **RGPD** (§10.2) : le jugement porte sur du **texte anonymisé**, bien plus facile à
  envoyer à un service externe qu'une image d'écriture manuscrite.
- **biais de calligraphie** : noter depuis le texte plutôt que depuis l'image le supprime
  (§5.1).

**Corollaire de calendrier** : le port `jugement` peut être développé et évalué **avant**
que le port `lecture` ne fonctionne sur du manuscrit — avec des transcriptions saisies à
la main. Les deux risques sont découplés.

---

## 15. Décisions prises

| Date | Décision | Raison |
| --- | --- | --- |
| 2026-09-17 | **Pas de validation implicite.** L'enseignant valide toutes les copies. | Fragilité juridique. Le coût est absorbé par la revue en planches (§5.2). |
| 2026-09-17 | La confiance sert à **ordonner** le travail, pas à en sauter. | Corollaire du point précédent. |
| 2026-09-17 | **Ordre de correction aléatoire**, par question, en aveugle. | Supprime les biais docimologiques classiques (§5.1). |
| 2026-09-17 | **Divulgation en trois phases** : lecture → note → correction. | Sépare co-validation de lecture et contestation de notation (§3). |
| 2026-09-17 | **CLI et fichiers texte d'abord**, GUI plus tard. | Inspectable, versionnable, testable ; aligné sur `acthub`. |
| 2026-09-17 | **Feuille de réponses détachée** (option). | Divise le volume à scanner par 4 et simplifie radicalement le recalage (§6). |
| 2026-09-17 | **Sujets mélangés** à la AMC. | Intégrité de l'examen. |
| 2026-09-17 | **Clé de correction par copie dès M0**, même sans mélange. | Rétro-adaptation coûteuse ; c'est un choix de structure, pas une fonctionnalité (§8.3). |
| 2026-09-17 | Identification : **grille de chiffres principale + nom manuscrit en contrôle croisé**. | Déterministe d'abord, IA en vérification (§7.1). |
| 2026-09-17 | Correction de nom par l'étudiant = **demande**, jamais écriture. | Faille de réassignation de copie (§7.3). |
| 2026-09-17 | **Transcription par l'auteur** quand la machine ne sait pas lire (§9.3). | Seul l'auteur connaît sa réponse ; vérifier coûte 20× moins cher que lire. Transforme le point dur n°1 en problème d'usage. |
| 2026-09-17 | Transcription et correction de nom = **un seul primitif**, implémenté une fois. | « La machine n'a pas su lire la zone Z → l'auteur fournit la lecture → l'enseignant valide » (§7.3, §9.3). |
| 2026-09-17 | La transcription achète de la **vitesse**, jamais des **points**. | Équité : le repli « lecture manuelle » doit donner le même résultat, seulement plus tard (§9.3). |
| 2026-09-17 | **M6 (transcription) avant M7 (IA sur questions ouvertes).** | Construire le filet avant de marcher sur le fil. |
| 2026-09-17 | **Critère fondateur : gain des deux côtés.** Toute fonctionnalité qui améliore un côté en dégradant l'autre est écartée. | §1 — c'est le test de conception, pas un slogan. |
| 2026-09-17 | **La note est un encadrement qui se resserre**, jamais une valeur provisoire. | Rend la divulgation précoce sûre : la note ne « baisse » jamais, elle était toujours dans l'intervalle (§3.3). |
| 2026-09-17 | Encadrement **dur** uniquement, pas d'estimation ponctuelle. | Prouvable et monotone ; l'étudiant retiendrait le chiffre et oublierait la marge (§3.3). |
| 2026-09-17 | **La validation de lecture par l'étudiant dispense l'enseignant de revalider** — lecture seulement, fenêtre courte avant corrigé, audit résiduel 5-10 %. | En phase 0 l'étudiant ignore le corrigé : sa validation est sans incitation (§3.4). |
| 2026-09-17 | Point de relecture en **bonus**, pas pris sur le total, avec repli hors ligne. | Équité : ne pas pénaliser pour une raison étrangère à la matière (§3.4). |
| 2026-09-17 | **L'anonymat est un attribut de chaque passe**, pas un réglage global. | « Est-ce que je constate, ou est-ce que j'apprécie ? » — masquer sur les passes de jugement (§5.1). |
| 2026-09-17 | **Séparer les ports `lecture` et `jugement`**, outils indépendants. | Le bon outil au bon endroit ; le jugement devient testable sur fixtures texte (§14.1). |
| 2026-09-17 | Le **journal d'erreurs machine** est un artefact de première classe. | Calibration des seuils, choix des outils, non-régression, métrique publiable (§5.4). |
| 2026-09-17 | **Cible : examen du lundi 23 novembre 2026.** Périmètre = M0 + M1 + génération du mélange. | 9,6 semaines. Une échéance réelle est le meilleur cadrage de périmètre (§12). |
| 2026-09-17 | **Priorité au côté génération** (échéance dure) sur le côté lecture (échéance souple). | La feuille est imprimée une fois ; les scans ne périment pas (§12). |
| 2026-09-17 | La feuille de réponses doit rester **corrigeable à la main**. | Supprime le scénario catastrophe : repli manuel toujours disponible (§12). |
| 2026-09-17 | **S2 avant S1.** | Avec 70 % de QCM, S2 est sur le chemin critique et S1 ne conditionne rien avant décembre (§12). |
| 2026-09-17 | **Feuille de réponses générée programmatiquement**, cahier du sujet en LaTeX. | La feuille ne contient aucune formule → plus besoin d'extraire des coordonnées de LaTeX (§16.3). |
| 2026-09-17 | **Fenêtre de phase 0 : 24 h.** | Compromis participation / intégrité (§3.4). |
| 2026-09-17 | Mono-utilisateur strict, pas d'anonymat imposé. | Contexte confirmé (§16.1) — YAGNI plein régime. |
| 2026-09-19 | **`tali`** (logiciel) et **`crank`** (orchestrateur) : deux dépôts git, une seule arborescence. | Un centre de gravité, sans coupler le produit à son échafaudage. |
| 2026-09-19 | **Les données d'examen vivent hors du dépôt.** `tali` s'exécute dans un dossier d'examen, comme `git` dans un dépôt. | Le dépôt ne peut pas fuiter ce qu'il ne produit pas (`decisions/0004`). |
| 2026-09-19 | Un seul fichier marqueur, **`exam.toml`, visible**. Ni `.tali.toml`, ni `.tali/`, ni config utilisateur. | C'est la matière qu'on édite, pas de l'état dérivé (`0004`). |
| 2026-09-19 | Feuille : **4 carrés pleins + un 5e** pour l'orientation ; **QR opaque court** ; **chaque page porte son QR**. | La géométrie reste récupérable si le QR est abîmé ; le pipeline ne suppose jamais l'ordre des pages, donc recto-verso sans risque (`0001`). |
| 2026-09-19 | **ReportLab** (écriture) + **pypdfium2** (rastérisation de test), tous deux BSD. | PyMuPDF ferait les deux mais impose l'AGPL à tout le projet. La rastérisation porte le corpus synthétique (`0002`). |
| 2026-09-19 | **Aucune pré-affectation copie → étudiant.** L'identifiant désigne une permutation, jamais une personne. | Contrainte d'Olivier : n'importe quel sujet à n'importe quel étudiant (`0003`). |
| 2026-09-19 | **Pas de grille de chiffres.** Identité = `NOM`/`PRÉNOM` en capitales, **une lettre par case**. | Un numéro 1..220 devrait être attribué et communiqué — de la logistique. La grille de lettres transforme la lecture d'écriture cursive en classification d'un caractère parmi 26, appariée contre 220 noms (`0003`). |

---

## 16. Le contexte, précisé

### 16.1 Réponses obtenues (2026-09-17)

| # | Question | Réponse | Conséquence |
| --- | --- | --- | --- |
| 1 | Maths manuscrites à corriger ? | **oui** | Confirme que l'IA sur questions ouvertes (M7) est risquée → tard, et jamais sur le chemin critique. |
| 2 | Proportion QCM / ouvert | **~70 % / 30 %** | **Le fait le plus structurant du projet** → §16.2 |
| 3 | Anonymat imposé ? | **non** | Simplifie §7.4. On garde le masquage **par passe** (§5.1), mais pour le biais, pas pour la règle. |
| 4 | Hébergement | _pas encore décidé_ | Sans objet avant M5 (portail). Rien ne bloque. |
| 5 | Cible d'usage | **lui seul d'abord** | YAGNI plein régime : pas de comptes, pas de rôles, pas de multi-examen. |
| 6 | Examen cible | **lundi 23 novembre 2026** | Cadre tout le périmètre → §12 |
| 7 | LaTeX ou non | _« le plus pratique »_ | **Question dissoute** → §16.3 |
| 8 | Bonus possible ? | **oui** | Le point de relecture (§3.4) est viable. |
| 9 | Fenêtre de phase 0 | **24 h** | Acté. Bon compromis participation / intégrité. |
| 10 | Afficher le « % stabilisé » ? | _indécis_ | Sans objet avant M4/M5. À trancher en voyant l'écran. |

Les questions 4 et 10 n'ont pas besoin de réponse : elles ne concernent que des jalons
hors du périmètre de novembre. C'est une bonne nouvelle en soi.

### 16.2 70 % de QCM — ce que ça change

C'est le chiffre le plus important de tout le document.

- **M1 seul (QCM, zéro IA, zéro serveur) automatise 70 % du barème.** Le rapport
  valeur/risque du projet est excellent **sans jamais toucher à un modèle de langage**.
- Le risque technique n°1 (lecture des maths manuscrites, §9.2) ne porte que sur **30 %
  des points** — et ces 30 % sont corrigés à la main en novembre, comme aujourd'hui.
- L'encadrement du §3.3 devient immédiatement parlant : une fois le QCM validé, 14 points
  sur 20 sont stabilisés. « Votre note est entre 14 et 20 » dès le premier jour.
- Corollaire pour la suite : quand l'IA arrivera (M7), elle jouera sur 6 points. Son
  intérêt est réel mais **borné** — à garder en tête avant d'y investir beaucoup.

### 16.3 Question 7 dissoute : la feuille de réponses n'a pas besoin de LaTeX

Conséquence directe de la décision « feuille de réponses détachée » (§6), que je n'avais
pas exploitée à fond :

| Document | Comment le produire | Le pipeline le lit-il ? |
| --- | --- | --- |
| **Feuille de réponses** | **programmatiquement**, layout fixe, coordonnées connues par construction | **oui — et c'est le seul** |
| **Cahier du sujet** | LaTeX (ou Markdown → LaTeX), maths parfaites, mise en page libre | **jamais** |

La feuille de réponses ne contient **que** des bulles étiquetées A/B/C/D, des grilles de
chiffres et des cadres vides. **Aucune formule, aucun énoncé.** Les maths (énoncés,
options de QCM) vivent entièrement dans le cahier, que le pipeline ne regarde jamais.

→ Plus besoin d'extraire des coordonnées d'une compilation LaTeX (`zref-savepos` et
compagnie), qui était la partie fragile et pénible à tester. **Les coordonnées sont
choisies, pas découvertes.** Tu écris tes sujets en LaTeX comme d'habitude ; le pipeline
s'en moque.

C'est aussi ce qui rend le calendrier de novembre tenable : la moitié « génération »
(chemin critique, §12) devient un problème de mise en page simple et entièrement testable.

---

## 17. Notes libres

- **Antériorité à regarder avant d'écrire du code** : AMC, Gradescope, OMRChecker.
  Le différenciateur n'est ni l'OMR ni la notation IA — c'est **la revue en planches
  (§5.2) et la boucle de consultation en phases (§3.2)**. C'est là qu'il faut mettre
  l'effort de conception ; le reste, s'en inspirer sans scrupule.
- **Chaque réclamation validée est un cas d'échec étiqueté**, produit gratuitement par
  l'utilisateur le mieux placé pour le faire. Le corpus de test s'auto-alimente.
- **Angle recherche** : « correction assistée par IA sous supervision humaine intégrale :
  ordonnancement, revue par grappe, et taux d'erreur mesuré ». Le protocole est publiable
  et le dispositif fournit ses propres métriques. Peut justifier du temps, voire un stage.
- **Garde-fou YAGNI permanent** : pas de multi-établissement, pas de multi-langue, pas de
  système de rôles, pas de mode collaboratif. Un enseignant, un examen, une machine.
