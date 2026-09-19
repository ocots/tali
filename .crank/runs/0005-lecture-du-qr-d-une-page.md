# Tâche #5 — Lecture du QR d'une page

- **rôle** : `feature`
- **critère de complétion** : `.venv/bin/python -m pytest -q tests/test_qr.py::test_decode_un_qr_genere tests/test_qr.py::test_refuse_une_version_de_gabarit_inconnue`
- **périmètre** : `src/tali/vision/**`, `tests/test_qr.py`
- **budget** : ½ session

## Plan

- [x] `vision/qr.py` — décodage + validation de la version de gabarit
- [x] Choisir l'outillage : OpenCV pour décoder, `qrcode` pour fabriquer les QR de test
- [x] `tests/test_qr.py`

## Journal

**OpenCV n'était pas encore une dépendance.** Le cahier des charges (§14.1, §9.3) le
nomme déjà pour la vision classique ; pas de nouvelle décision nécessaire, juste
l'ajout d'`opencv-python-headless` (sans les bindings GUI, inutiles ici).

**Décoder n'est pas encoder : deux bibliothèques, jamais la même en test et en
production.** `cv2.QRCodeDetector` décode ; rien dans OpenCV ne génère de QR
proprement. Pour fabriquer la fixture de test, `qrcode` (+ `pillow`, sa dépendance
d'image) — tous deux en `dev`, jamais importés par le code de production. Le vrai
générateur de QR sera `ReportLabBackend.qr` (#2), déjà écrit et indépendant de celui-ci.

Mutation-testé les deux tests du contrat : désactiver la vérification de version, et
faire ignorer le `copy_id` lu — les deux mutants sont tués.

## Bilan

`decode_page_qr` : lève `QrError` si aucun QR, si le format ne suit pas
`tali:<exam>:<copie>:<page>:<version>`, ou si la version n'est pas dans
`SUPPORTED_TEMPLATE_VERSIONS` — jamais un repli silencieux sur une version inconnue.

## Points d'incertitude

- `SUPPORTED_TEMPLATE_VERSIONS = ("1",)` est une hypothèse : la vraie valeur dépendra du
  gabarit une fois #3 écrit. Le format est celui de `decisions/0001`, pas encore vérifié
  contre un vrai gabarit généré par `tali build`.
