"""
menu.py
-------
Menu interactivo principal de Modgest (modo no-CLI). Muestra las opciones
al usuario y despacha a la función correspondiente según su elección.
"""

import os
import time

from config import ModgestConfig, update_config_value
from ui import cls, jilog, winput
from modrinth_api import download_mod
from search_flow import interactive_search_and_download
from batch import download_from_file


def _show_menu_header(config: ModgestConfig) -> None:
    cls()
    jilog(f"""[ {config.loader.capitalize()} {config.user_version} ]  [ {config.mod_type.capitalize()} ]

[1] Buscar y descargar un mod
[2] Descargar con un nombre preciso
[3] Usar un archivo con nombres de mods
[4] Usar un archivo con nombres precisos
[5] Configuracion
[x] Salir
""")


def _handle_search_and_download(config: ModgestConfig) -> None:
    cls()
    mod_name = winput("Ingresa el nombre del mod > ")
    if mod_name == "":
        return
    if interactive_search_and_download(mod_name, config) is None:
        cls()
        jilog("No se encontraron/seleccionaron mods.")
        time.sleep(3)


def _handle_precise_download(config: ModgestConfig) -> None:
    cls()
    slug = winput("Ingresa el slug/id > ")
    jilog(download_mod(slug, config))
    time.sleep(3)
    cls()


def _handle_file_with_names(config: ModgestConfig) -> None:
    cls()
    filename = winput("Ingresa la ruta del archivo > ")
    download_from_file(filename, config, precise=False)


def _handle_file_with_precise_names(config: ModgestConfig) -> None:
    cls()
    filename = winput("Ingresa la ruta del archivo > ")
    download_from_file(filename, config, precise=True)


def _handle_configuration(config: ModgestConfig) -> ModgestConfig:
    cls()
    update_config_value(config, "user_version", winput("Ingresa la version de tu juego > "))
    update_config_value(config, "mod_type", winput("Buscar mods para (cliente/servidor/ambos) > ").lower())
    update_config_value(config, "loader", winput("Ingresa tu modloader (forge/fabric/neoforge) > ").lower())
    jilog("Configuracion modificada.")
    time.sleep(3)
    return config


def _handle_exit() -> None:
    cls()
    jilog("Gracias por usar Modgest!")
    os._exit(0)


MENU_ACTIONS = {
    "1": _handle_search_and_download,
    "2": _handle_precise_download,
    "3": _handle_file_with_names,
    "4": _handle_file_with_precise_names,
}


def run_menu_once(config: ModgestConfig) -> ModgestConfig:
    """
    Muestra el menu principal una vez, lee la opcion del usuario y la ejecuta.
    Devuelve la configuracion (sin cambios o actualizada, segun la opcion elegida).
    """
    _show_menu_header(config)
    option = winput("Opcion > ")

    if option in MENU_ACTIONS:
        MENU_ACTIONS[option](config)
    elif option == "5":
        config = _handle_configuration(config)
    elif option == "x":
        _handle_exit()
    else:
        print("Opcion invalida.")
        time.sleep(3)

    return config


def run_menu_loop(config: ModgestConfig) -> None:
    """Ejecuta el menu interactivo indefinidamente hasta que el usuario salga."""
    while True:
        config = run_menu_once(config)
