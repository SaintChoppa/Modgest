"""
modrinth_api.py
----------------
Toda la lógica de comunicación con la API de Modrinth: búsqueda de mods,
verificación de compatibilidad, descarga de archivos y resolución de
dependencias.

Estas funciones no imprimen directamente en pantalla (salvo logs puntuales
mediante `ui.jilog`, igual que el original) y devuelven datos o mensajes de
resultado, dejando la presentación al módulo de CLI/menú.
"""

import os
from glob import glob
from urllib.parse import unquote

import requests

from config import ModgestConfig, WORKING_DIRECTORY
from ui import jilog

MODRINTH_API_BASE = "https://api.modrinth.com/v2"


# ---------------------------------------------------------------------------
# Compatibilidad
# ---------------------------------------------------------------------------

def is_compatible(mod_data: dict, config: ModgestConfig, search_result: bool = False) -> bool:
    """
    Verifica si un mod es compatible con la versión del juego y el tipo
    (cliente/servidor/ambos) configurados por el usuario.

    `search_result` indica si `mod_data` viene de un resultado de búsqueda
    (campo "versions") o de los datos completos de un proyecto (campo "game_versions").
    """
    try:
        versions_field = "versions" if search_result else "game_versions"
        if config.user_version not in mod_data[versions_field]:
            return False
    except Exception as e:
        jilog(f"Error: {e}")
        return False

    client_support = mod_data["client_side"]
    server_support = mod_data["server_side"]

    if config.mod_type == "cliente":
        return client_support in ("optional", "required")
    elif config.mod_type == "servidor":
        return server_support in ("optional", "required")
    else:
        return True


# ---------------------------------------------------------------------------
# Búsqueda
# ---------------------------------------------------------------------------

def search_mods(mod_name: str, config: ModgestConfig) -> list[dict] | None:
    """
    Busca mods en Modrinth por nombre, filtrando por loader y versión del juego.
    Devuelve una lista de hits normalizados (o None si no hay resultados).
    """
    url = (
        f'{MODRINTH_API_BASE}/search?query={mod_name}'
        f'&facets=[["categories:{config.loader}"],["versions:{config.user_version}"]]'
    )
    response = requests.get(url)

    if response.status_code != 200:
        return None

    mod_data = response.json()
    if mod_data["total_hits"] < 1:
        return None

    return _build_hit_list(mod_data["hits"], config)


def _build_hit_list(hits: list[dict], config: ModgestConfig) -> list[dict] | None:
    """Filtra y normaliza los resultados crudos de búsqueda de Modrinth."""
    final_hits = []
    shown_count = 0

    for index, mod in enumerate(hits):
        if not is_compatible(mod, config, search_result=True):
            continue

        shown_count += 1
        final_hits.append({
            "name": mod["title"],
            "description": mod["description"],
            "author": mod["author"],
            "slug": mod["slug"],
            "client_side": mod["client_side"],
            "server_side": mod["server_side"],
            "game_versions": mod["versions"],
            "internal_mod_id": index,
            "show_mod_id": shown_count,
            "external_mod_id": mod["project_id"],
        })

    return final_hits if final_hits else None


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------

def _ensure_mod_folder(modfolder: str = "") -> str:
    """Crea (si no existen) la carpeta `mods` y, opcionalmente, una subcarpeta dentro de ella."""
    base_mods_folder = os.path.join(WORKING_DIRECTORY, "mods")
    os.makedirs(base_mods_folder, exist_ok=True)

    if modfolder:
        target_folder = os.path.join(base_mods_folder, modfolder)
        os.makedirs(target_folder, exist_ok=True)
        return target_folder

    return base_mods_folder


def _mod_already_downloaded(file_url: str) -> bool:
    """Comprueba si el archivo de un mod ya existe en la carpeta `mods` (en cualquier subcarpeta)."""
    file_name = unquote(file_url.split('/')[-1])
    mods_glob_pattern = os.path.join(WORKING_DIRECTORY, "mods", "*.*")
    existing_files = glob(mods_glob_pattern)
    return any(file_name in path for path in existing_files)


def _download_dependencies(dependencies: list[dict], config: ModgestConfig, modfolder: str) -> None:
    """Descarga recursivamente las dependencias obligatorias de un mod."""
    if not dependencies:
        return
    jilog("Descargando dependencias...")
    for dependency in dependencies:
        if dependency["dependency_type"] == "optional":
            continue
        jilog(download_mod(dependency["project_id"], config, modfolder=modfolder))


def download_mod(slug: str, config: ModgestConfig, modfolder: str = "") -> str:
    """
    Descarga un mod de Modrinth por su slug/ID, incluyendo sus dependencias
    no opcionales. Devuelve un mensaje de resultado para mostrar al usuario.
    """
    project = requests.get(f"{MODRINTH_API_BASE}/project/{slug}").json()
    if not is_compatible(project, config):
        return "Error, ese mod no es compatible"

    versions_url = (
        f'{MODRINTH_API_BASE}/project/{slug}/version'
        f'?loaders=["{config.loader}"]&game_versions=["{config.user_version}"]'
    )
    versions = requests.get(versions_url).json()

    if not versions:
        return "Mod no disponible"

    latest_version = versions[0]
    file_info = latest_version["files"][0]
    file_name = file_info["filename"]
    file_url = file_info["url"]

    target_folder = _ensure_mod_folder(modfolder)
    file_path = os.path.join(target_folder, file_name)

    if _mod_already_downloaded(file_url):
        downloaded_name = unquote(file_url.split('/')[-1])
        return f"Mod ya existente: {downloaded_name}"

    file_contents = requests.get(file_url, stream=True).content
    with open(file_path, "wb") as f:
        f.write(file_contents)

    _download_dependencies(latest_version.get("dependencies", []), config, modfolder)

    return f"{file_name} descargado!"


# Alias retrocompatible con el nombre de función original.
def get_modrinth(slug: str, config: ModgestConfig, modfolder: str = "") -> str:
    """Alias de `download_mod`, por compatibilidad con el nombre usado en versiones previas."""
    return download_mod(slug, config, modfolder=modfolder)
