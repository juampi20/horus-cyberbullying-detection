"""Demo temporal: verifica que un test rojo bloquea el merge en main.

Este archivo se agrega en un branch de demo para probar la proteccion de
rama. NO debe mergearse.
"""


def test_demo_intentional_failure() -> None:
    assert 1 == 2, "Falla intencional para demostrar el bloqueo del merge"
