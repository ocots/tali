"""Le socle est vert. Point de départ pour que le premier critère `done` ait une base."""

import tali


def test_le_paquet_s_importe():
    assert tali.__version__
