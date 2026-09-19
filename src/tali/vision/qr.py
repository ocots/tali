"""Lecture du QR d'une page (décision `0001`) : `tali:<exam>:<copie>:<page>:<version>`.

Vision classique (OpenCV), déterministe — pas d'IA (cahier des charges §14.1). Une
version de gabarit inconnue est refusée plutôt que lue de travers : une feuille d'une
autre session, avec d'autres coordonnées, ne doit jamais être traitée en silence.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

# Versions de gabarit que ce code sait interpréter. En ajouter une quand `decisions/0001`
# évolue ; en retirer une rendrait les feuilles de cette version illisibles à dessein.
SUPPORTED_TEMPLATE_VERSIONS = ("1",)


class QrError(ValueError):
    """Le QR est absent, mal formé, ou porte une version de gabarit non supportée."""


@dataclass(frozen=True)
class PagePayload:
    exam_id: str
    copy_id: int
    page: int
    template_version: str


def decode_page_qr(image: np.ndarray) -> PagePayload:
    """Décode le QR d'une image de page. Lève `QrError` plutôt que de deviner."""
    text, _points, _straight = cv2.QRCodeDetector().detectAndDecode(image)
    if not text:
        raise QrError("aucun QR détecté sur la page")
    return _parse(text)


def _parse(text: str) -> PagePayload:
    parts = text.split(":")
    if len(parts) != 5 or parts[0] != "tali":
        raise QrError(
            f"QR mal formé, attendu tali:<exam>:<copie>:<page>:<version>, reçu {text!r}"
        )
    _, exam_id, copy_id, page, version = parts
    if version not in SUPPORTED_TEMPLATE_VERSIONS:
        raise QrError(
            f"version de gabarit inconnue : {version!r} — versions supportées : "
            f"{', '.join(SUPPORTED_TEMPLATE_VERSIONS)}"
        )
    try:
        return PagePayload(
            exam_id=exam_id, copy_id=int(copy_id), page=int(page), template_version=version
        )
    except ValueError as exc:
        raise QrError(f"copie ou page non numérique dans {text!r}") from exc
