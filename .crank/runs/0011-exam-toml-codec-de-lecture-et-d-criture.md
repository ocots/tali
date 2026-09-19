# Tâche #11 — exam.toml — codec de lecture et d'écriture

- **rôle** : `feature`
- **critère de complétion** : `.venv/bin/python -m pytest -q tests/test_exam_toml.py::test_round_trip_toml tests/test_exam_toml.py::test_rejette_un_champ_inconnu_en_le_nommant`
- **périmètre** : `src/tali/codecs/**`, `tests/test_exam_toml.py`
- **budget** : 1 session

## Plan

- [x] `codecs/exam_toml.py` — schéma fermé, écriture canonique
- [x] `tests/test_exam_toml.py`

## Journal

Cette tâche vient du découpage de #1 (voir son suivi, `.crank/runs/0001-*.md`) : le
code et les tests étaient déjà écrits, mutation-testés, et mis de côté quand #1 a été
réduit au domaine seul pour tenir sous `max_diff_lines`. Repris ici sans modification —
seul l'import de `tali.domain.exam` (fusionné entre-temps par #1) a été vérifié.

Round-trip testé sur **deux** examens qui ne partagent aucune valeur (`CANONICAL` et
`VARIANT`) : une implémentation qui figerait une valeur en dur dans `dumps` ne serait
pas détectée par un seul examen — c'est le mutant trouvé en écrivant #1. Les rejets
(table inconnue, champ manquant, booléen pour un entier) sont un seul test paramétré
plutôt que quatre répétitions de la même mécanique `pytest.raises`.

Re-mutation-testé les deux tests du contrat sur le code tel qu'il atterrit ici (`dumps`
figeant `copies`, rejet des clés inconnues désactivé) : les deux mutants sont tués.

## Bilan

`loads`/`dumps` : schéma fermé (table ou clé inconnue refusée, en la nommant),
écriture canonique (ordre fixe, round-trip stable après une seconde passe). `load(path)`
est la seule fonction qui touche au disque.

## Points d'incertitude

- Aucun nouveau : les points ouverts (§4.3 à corriger, cf. `0003`) restent ceux notés
  dans le suivi de #1, pas de mon ressort ici non plus.
