"""
modgest.py
----------
Punto de entrada de Modgest: une los modulos de configuracion, CLI y menu
interactivo. La logica especifica de cada parte vive en su propio modulo:

    config.py        -> configuracion persistente
    ui.py             -> impresion/input con estilo de consola
    modrinth_api.py   -> llamadas a la API de Modrinth
    search_flow.py    -> busqueda interactiva + seleccion + descarga
    batch.py          -> descargas desde archivos de lista de mods
    cli.py            -> parseo de argumentos y comandos no interactivos
    menu.py           -> menu interactivo principal
"""

import os
import time

from config import load_config
from ui import cls, jilog
from cli import build_arg_parser, run_cli
from menu import run_menu_loop

MODGEST_VERSION = "1.3.3"


def set_terminal_title(version):
    """En Windows, establece el titulo de la ventana de la terminal."""
    if os.name == "nt":
        os.system(f"title Modgest {version}")


def run_interactive_mode():
    """Inicializa la configuracion y arranca el menu interactivo en bucle."""
    config = load_config()
    cls()
    jilog(f"ModGest {MODGEST_VERSION}")
    time.sleep(1)
    run_menu_loop(config)


def main():
    set_terminal_title(MODGEST_VERSION)

    parser = build_arg_parser()
    args = parser.parse_args()

    if run_cli(args):
        return

    run_interactive_mode()


if __name__ == "__main__":
    main()
