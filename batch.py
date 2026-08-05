"""
batch.py
--------
Lógica para procesar archivos de texto que contienen listas de mods a
descargar (uno por línea), con soporte para indicar una subcarpeta de
destino mediante líneas que empiezan con "--".
"""

import os
import time

from config import ModgestConfig
from ui import jilog
from modrinth_api import download_mod
from search_flow import interactive_search_and_download

FOLDER_MARKER_PREFIX = "--"


def _resolve_file_path(filename: str) -> str | None:
    """
    Resuelve la ruta de un archivo de lista de mods, probando también con
    extensión `.txt` si la ruta original no existe. Devuelve None si no se encuentra.
    """
    if os.path.exists(filename):
        return filename
    if os.path.exists(f"{filename}.txt"):
        return f"{filename}.txt"
    return None


def _is_folder_marker(line: str) -> bool:
    return line.startswith(FOLDER_MARKER_PREFIX)


def _extract_folder_name(line: str) -> str:
    return line.replace("-- ", "").strip()


def download_from_file(filename: str, config: ModgestConfig, precise: bool = False) -> None:
    """
    Lee un archivo con nombres de mods (uno por línea) y los descarga.

    - Si `precise` es False, cada línea se trata como un término de búsqueda
      y se descarga automáticamente el primer resultado.
    - Si `precise` es True, cada línea se trata como el slug/ID exacto del mod.
    - Las líneas que empiezan con "--" definen la subcarpeta donde se
      guardarán los mods siguientes hasta la próxima marca.
    """
    resolved_path = _resolve_file_path(filename)
    if resolved_path is None:
        print(f"Archivo no encontrado: {filename}")
        time.sleep(3)
        return

    current_folder = ""

    with open(resolved_path, "r") as file:
        for raw_line in file.readlines():
            line = raw_line.strip()
            if line == "":
                continue

            if _is_folder_marker(line):
                current_folder = _extract_folder_name(line)
                continue

            jilog(f"---\nDescargando: {line}")
            if precise:
                jilog(download_mod(line, config, modfolder=current_folder))
            else:
                interactive_search_and_download(line, config, iterating=True)
            jilog("---")
