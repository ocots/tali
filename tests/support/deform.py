"""Déformations paramétrées d'une image de page (cahier des charges §13.1).

Chaque fonction prend une image en niveaux de gris et une amplitude nommée, et rend
une image de même taille. Rien ici n'imite un scanner ou un téléphone en particulier :
le but est de couvrir, à volonté, des cas rares qu'un vrai corpus ne réunit jamais
assez souvent.
"""

from __future__ import annotations

import cv2
import numpy as np


def rotate(image: np.ndarray, degrees: float) -> np.ndarray:
    """Un scan légèrement de travers — la feuille posée en biais sur la vitre."""
    h, w = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), degrees, 1.0)
    return cv2.warpAffine(image, matrix, (w, h), borderValue=255)


def perspective_point(
    shape: tuple[int, int], x_px: float, y_px: float, degrees: float, *, focal_px: float = 1500.0
) -> tuple[float, float]:
    """Où atterrit le pixel `(x_px, y_px)` sous `perspective(image, degrees)`.

    Extrait de `perspective()` pour que les tests connaissent la vérité terrain d'un
    point donné, pas seulement l'image déformée dans son ensemble.
    """
    h, w = shape[:2]
    theta = np.radians(degrees)
    x0, y0 = x_px - w / 2, y_px - h / 2
    y1 = y0 * np.cos(theta)
    z1 = y0 * np.sin(theta) + focal_px
    return focal_px * x0 / z1 + w / 2, focal_px * y1 / z1 + h / 2


def perspective(image: np.ndarray, degrees: float, *, focal_px: float = 1500.0) -> np.ndarray:
    """Une page vue par une caméra basculée de `degrees` autour de son axe horizontal —
    le cas du canal photo (§9.4), une vraie distorsion **projective**, pas juste un biais.
    """
    h, w = image.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([perspective_point((h, w), x, y, degrees, focal_px=focal_px) for x, y in src])
    matrix = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(image, matrix, (w, h), borderValue=255)


def blur(image: np.ndarray, sigma: float) -> np.ndarray:
    """Une mise au point ratée."""
    k = max(1, int(sigma * 3) | 1)
    return cv2.GaussianBlur(image, (k, k), sigma)


def noise(image: np.ndarray, sigma: float, *, seed: int = 0) -> np.ndarray:
    """Le grain d'un scan bas de gamme."""
    rng = np.random.default_rng(seed)
    noisy = image.astype(np.float64) + rng.normal(0, sigma, image.shape)
    return np.clip(noisy, 0, 255).astype(np.uint8)


def contrast(image: np.ndarray, factor: float) -> np.ndarray:
    """`factor` < 1 délave l'image, > 1 l'assombrit aux extrêmes."""
    return np.clip(128 + (image.astype(np.float64) - 128) * factor, 0, 255).astype(np.uint8)


def smudge(image: np.ndarray, size: int) -> np.ndarray:
    """De l'encre qui bave : les traits sombres s'épaississent."""
    k = max(1, size | 1)
    return cv2.erode(image, np.ones((k, k), np.uint8))


def fold(image: np.ndarray, position_frac: float, *, width_px: int = 15, darkness: float = 0.5) -> np.ndarray:
    """L'ombre d'un pli de papier, en bande horizontale."""
    h = image.shape[0]
    y = int(h * position_frac)
    y0, y1 = max(0, y - width_px // 2), min(h, y + width_px // 2)
    folded = image.copy()
    folded[y0:y1] = np.clip(folded[y0:y1].astype(np.float64) * darkness, 0, 255).astype(np.uint8)
    return folded
