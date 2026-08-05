"""
search_flow.py
---------------
Flujo interactivo de búsqueda: muestra resultados de Modrinth en tablas,
permite al usuario elegir uno y dispara la descarga. Separado de
`modrinth_api.py` porque mezcla lógica de presentación con la de datos.
"""

import time

from config import ModgestConfig
from ui import cls, jilog, winput, remake_string, make_table
from modrinth_api import search_mods, download_mod


def _print_search_results(hits: list[dict]) -> None:
    """Imprime cada resultado de búsqueda como una tabla individual, en orden inverso (igual al original)."""
    for mod in hits[::-1]:
        header = f"[{mod['show_mod_id']}] {mod['name']}"
        description_lines = remake_string(mod["description"])
        make_table(description_lines, table_header=header, show=True)


def _prompt_selection(hits: list[dict], iterating: bool) -> int | None:
    """
    Pide al usuario que elija un resultado por número. Si `iterating` es True
    (modo no interactivo, p. ej. batch), se elige automáticamente el primero.
    Devuelve el índice (1-based) elegido, o None si la selección es inválida.
    """
    if iterating:
        return 1

    jilog("Enter para volver...")
    print()
    selection = winput("Selecciona un mod > ", torep="RETRN")

    if selection == 1:
        return 1
    if not str(selection).isdigit():
        return None
    return int(selection)


def interactive_search_and_download(mod_name: str, config: ModgestConfig, iterating: bool = False) -> bool | None:
    """
    Busca un mod por nombre, muestra los resultados y descarga el seleccionado.

    Devuelve True si se descargó algo, o None si no hubo resultados o el
    usuario canceló la selección.
    """
    if not iterating:
        cls()

    if mod_name == "":
        return None

    hits = search_mods(mod_name, config)
    if not hits:
        return None

    _print_search_results(hits)

    selected_index = _prompt_selection(hits, iterating)
    if selected_index is None:
        return None

    selected_mod = hits[selected_index - 1]
    jilog(download_mod(selected_mod["slug"], config))
    time.sleep(3)
    return True
