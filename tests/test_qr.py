"""Lecture du QR d'une page : `tali:<exam>:<copie>:<page>:<version>` (décision `0001`)."""

from __future__ import annotations

import numpy as np
import pytest
import qrcode

from tali.vision.qr import PagePayload, QrError, decode_page_qr


def make_qr_image(payload: str) -> np.ndarray:
    """Un QR de test, généré par une bibliothèque distincte de celle qui décode :
    `qrcode` ne sert jamais en production, seulement à fabriquer des fixtures."""
    return np.array(qrcode.make(payload).convert("L"))


def test_decode_un_qr_genere() -> None:
    image = make_qr_image("tali:ct-2026-01:0007:1:1")
    assert decode_page_qr(image) == PagePayload(
        exam_id="ct-2026-01", copy_id=7, page=1, template_version="1"
    )


def test_refuse_une_version_de_gabarit_inconnue() -> None:
    """Une feuille d'une autre session ne doit jamais être lue de travers."""
    image = make_qr_image("tali:ct-2026-01:0007:1:99")
    with pytest.raises(QrError) as err:
        decode_page_qr(image)
    assert "99" in str(err.value)


def test_refuse_une_page_sans_qr() -> None:
    blank = np.full((200, 200), 255, dtype=np.uint8)
    with pytest.raises(QrError) as err:
        decode_page_qr(blank)
    assert "aucun QR" in str(err.value)


def test_refuse_un_contenu_qui_nest_pas_un_qr_tali() -> None:
    image = make_qr_image("https://example.org")
    with pytest.raises(QrError) as err:
        decode_page_qr(image)
    assert "mal formé" in str(err.value)


def test_refuse_une_copie_non_numerique() -> None:
    image = make_qr_image("tali:ct-2026-01:abc:1:1")
    with pytest.raises(QrError) as err:
        decode_page_qr(image)
    assert "abc" in str(err.value)
