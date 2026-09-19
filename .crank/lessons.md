# Leçons

Leçons réutilisables et pièges récurrents. Un agent les lit avant d'intervenir ;
il en ajoute une quand il a perdu du temps sur quelque chose d'évitable.

Une leçon utile est **spécifique et vérifiable**. « Faire attention aux chemins » n'est
pas une leçon ; « `git worktree add` ne peuple pas les sous-modules » en est une.

---

## Orchestration

- **Le suivi survit à la PR.** Les fichiers de `.crank/runs/` sont commités et conservés :
  avant d'intervenir sur un fichier, chercher si quelqu'un s'y est déjà cassé les dents.
- **Un échec n'est jamais retenté automatiquement.** `crank fail` pose `agent:failed` ;
  retirer le label remet la tâche en jeu. C'est une décision humaine, pas une boucle.

## Génération et impression

- _(à remplir après le spike S2 — ce que l'imprimante et le scanner font vraiment subir
  aux marqueurs et au QR)_
