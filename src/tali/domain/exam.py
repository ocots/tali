"""Les objets d'un examen.

Purs : aucune entrée/sortie, aucune connaissance d'un format de fichier. La lecture
d'`exam.toml` est dans `tali.codecs`. Cette séparation permet de construire un examen
en mémoire dans les tests, sans fichier.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import blake2b


class ExamError(ValueError):
    """Donnée d'examen invalide.

    Le message nomme toujours le champ fautif : `exam.toml` est écrit à la main, et
    la faute de frappe est le cas courant, pas le cas rare.
    """


@dataclass(frozen=True)
class AnswerSheet:
    """Feuille de réponses détachée (cahier des charges §6)."""

    separate: bool
    pages: int


@dataclass(frozen=True)
class Identity:
    """Rapprochement copie → étudiant (décision `0003`).

    Seulement le roster : la géométrie des grilles `NOM` / `PRÉNOM` appartient au
    gabarit (décision `0001`), pas à la configuration de l'examen.
    """

    roster: str


@dataclass(frozen=True)
class Shuffle:
    """Mélange des sujets (cahier des charges §8)."""

    exercises: bool
    questions: str  # "none" | "within_exercise"
    answers: bool

    QUESTIONS_VALUES = ("none", "within_exercise")


@dataclass(frozen=True)
class Phases:
    """Divulgation en trois temps (cahier des charges §3.2)."""

    note: datetime
    correction: datetime
    claims_deadline: datetime


@dataclass(frozen=True)
class CorrectionKey:
    """Clé de correction **d'une copie**.

    Il n'existe pas de clé d'examen : chaque copie porte sa propre permutation
    (cahier des charges §8.3). Le mélange n'est pas encore implémenté, mais la clé
    est adressée par copie dès maintenant — rétro-adapter coûterait cher.
    """

    copy_id: int
    seed: int


@dataclass(frozen=True)
class Exam:
    """Un examen, tel que le décrit `exam.toml`."""

    id: str
    title: str
    seed: int
    copies: int
    answer_sheet: AnswerSheet
    identity: Identity
    shuffle: Shuffle
    phases: Phases

    def __post_init__(self) -> None:
        if self.copies < 1:
            raise ExamError(f"exam.copies doit être au moins 1, reçu {self.copies}")
        if self.answer_sheet.pages < 1:
            raise ExamError(
                f"answer_sheet.pages doit être au moins 1, reçu {self.answer_sheet.pages}"
            )
        if self.shuffle.questions not in Shuffle.QUESTIONS_VALUES:
            raise ExamError(
                f"shuffle.questions vaut {self.shuffle.questions!r} ; "
                f"valeurs admises : {', '.join(Shuffle.QUESTIONS_VALUES)}"
            )
        p = self.phases
        if not (p.note <= p.correction <= p.claims_deadline):
            raise ExamError(
                "les phases doivent être croissantes : "
                "phases.note ≤ phases.correction ≤ phases.claims_deadline"
            )

    def correction_key(self, copy_id: int) -> CorrectionKey:
        """La clé de la copie `copy_id`, dérivée de la graine de l'examen.

        Déterministe entre exécutions et entre machines — `hash()` ne l'est pas.
        C'est ce qui rend les copies rejouables à l'identique.
        """
        if not 1 <= copy_id <= self.copies:
            raise ExamError(
                f"copy_id doit être entre 1 et {self.copies} (exam.copies), reçu {copy_id}"
            )
        material = f"{self.id}:{self.seed}:{copy_id}".encode()
        digest = blake2b(material, digest_size=8).digest()
        return CorrectionKey(copy_id=copy_id, seed=int.from_bytes(digest, "big"))
