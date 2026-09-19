"""Gabarit de la feuille de réponses (décision `0001`).

Marqueurs, QR, grilles d'identité, bulles QCM, cadres de réponse ouverte — et rien
d'autre : `ZONE_TYPES` est l'inventaire exact, pas une liste indicative. Un type de zone
ajouté sans avoir relu `decisions/0003` (ex. une grille de chiffres) fait échouer
`test_inventaire_exact_des_zones` — la décision devient exécutable, pas seulement écrite.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from tali.render.dimensions import DEFAULT, Dimensions

ZONE_TYPES = frozenset({"marqueur", "qr", "grille_lettres", "bulle_qcm", "cadre_ouvert"})


class SheetError(ValueError):
    """Gabarit invalide — type de zone inconnu, ou identifiant en double."""


@dataclass(frozen=True)
class Zone:
    id: str
    type: str
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float

    def __post_init__(self) -> None:
        if self.type not in ZONE_TYPES:
            raise SheetError(
                f"type de zone inconnu : {self.type!r} — admis : {sorted(ZONE_TYPES)}"
            )


@dataclass(frozen=True)
class Template:
    version: str
    zones: tuple[Zone, ...]

    def __post_init__(self) -> None:
        ids = [z.id for z in self.zones]
        if len(ids) != len(set(ids)):
            doublons = sorted({i for i in ids if ids.count(i) > 1})
            raise SheetError(f"identifiants de zone en double : {doublons}")

    def zone(self, zone_id: str) -> Zone:
        for z in self.zones:
            if z.id == zone_id:
                return z
        raise KeyError(f"zone inconnue : {zone_id!r}")

    def types(self) -> frozenset[str]:
        return frozenset(z.type for z in self.zones)

    def to_json(self) -> str:
        return json.dumps({"version": self.version, "zones": [asdict(z) for z in self.zones]})

    @staticmethod
    def from_json(text: str) -> Template:
        data = json.loads(text)
        return Template(version=data["version"], zones=tuple(Zone(**z) for z in data["zones"]))


def build_template(
    *,
    n_qcm_questions: int,
    n_qcm_choices: int,
    n_open_questions: int,
    n_letters: int = 15,
    version: str = "1",
    dims: Dimensions = DEFAULT,
) -> Template:
    """Compose le gabarit d'une page. Paramétré par le contenu réel de l'examen — le
    nombre de questions n'est pas connu avant la rédaction du sujet."""
    zones: list[Zone] = []
    m, s = dims.marker_margin_mm, dims.marker_size_mm

    # A. cinq marqueurs — quatre coins, plus un cinquième qui casse la symétrie à 180°
    # (décision 0001 A : sans lui, une feuille tournée de 180° serait indiscernable).
    corners = {
        "marqueur-haut-gauche": (m, m),
        "marqueur-haut-droit": (dims.page_width_mm - m - s, m),
        "marqueur-bas-gauche": (m, dims.page_height_mm - m - s),
        "marqueur-bas-droit": (dims.page_width_mm - m - s, dims.page_height_mm - m - s),
    }
    for zone_id, (x, y) in corners.items():
        zones.append(Zone(zone_id, "marqueur", x, y, s, s))
    zones.append(Zone("marqueur-orientation", "marqueur", m + 2 * s, m, s, s))

    # B. le QR de cette page, à côté du marqueur haut-droit
    zones.append(Zone("qr", "qr", dims.page_width_mm - m - s - dims.qr_size_mm - 4, m,
                       dims.qr_size_mm, dims.qr_size_mm))

    # C. identité — NOM et PRÉNOM, une lettre par case (décision 0003)
    y = m + s + 10
    for label in ("nom", "prenom"):
        for i in range(n_letters):
            zones.append(Zone(f"identite-{label}-{i}", "grille_lettres",
                               m + i * dims.letter_cell_mm, y,
                               dims.letter_cell_mm, dims.letter_cell_mm))
        y += dims.letter_cell_mm + 4

    # D. bulles QCM — une grille question × choix
    y += 10
    for q in range(n_qcm_questions):
        for c in range(n_qcm_choices):
            zones.append(Zone(f"qcm-{q}-{c}", "bulle_qcm",
                               m + c * dims.bubble_pitch_mm, y + q * dims.bubble_pitch_mm,
                               dims.bubble_diameter_mm, dims.bubble_diameter_mm))

    # E. cadres de réponse ouverte, pleine largeur
    y += n_qcm_questions * dims.bubble_pitch_mm + 10
    width = dims.page_width_mm - 2 * m
    height = dims.open_frame_line_height_mm * 3
    for o in range(n_open_questions):
        zones.append(Zone(f"ouverte-{o}", "cadre_ouvert", m, y + o * height, width, height))

    return Template(version=version, zones=tuple(zones))
