"""
cli.py
------
Parseo de argumentos de linea de comandos y ejecucion de los comandos
no interactivos de Modgest (descarga directa y configuracion via flags).
"""

import argparse
import os

from config import ModgestConfig, load_config, update_config_value
from search_flow import interactive_search_and_download
from batch import download_from_file


def build_arg_parser() -> argparse.ArgumentParser:
    """Construye el parser de argparse con todas las opciones soportadas."""
    parser = argparse.ArgumentParser(
        description="Usa la API de Modrinth para descargar archivos mas rapido."
    )
    parser.add_argument("-d", action="store_true", help="Descarga un mod")
    parser.add_argument("--name", type=str, help="El nombre del mod a descargar")
    parser.add_argument(
        "--filename", type=str,
        help="El nombre del archivo que contiene los nombres de mods",
    )
    parser.add_argument("-c", action="store_true", help="Configurar")
    parser.add_argument("--key", type=str, help="Clave a configurar")
    parser.add_argument("--value", type=str, help="Valor configurado")
    return parser


def handle_config_command(args: argparse.Namespace) -> bool:
    """
    Maneja el flag `-c` (configuracion via CLI). Devuelve True si el
    programa debe terminar despues de esta llamada.
    """
    if not args.c:
        return False

    if args.key is None or args.value is None:
        os._exit(0)

    config = load_config()
    update_config_value(config, args.key, args.value)
    print("Configuracion modificada.")
    os._exit(0)


def handle_download_command(args: argparse.Namespace) -> bool:
    """
    Maneja el flag `-d` (descarga via CLI), ya sea por nombre o por archivo.
    Devuelve True si el programa debe terminar despues de esta llamada.
    """
    if not args.d:
        return False

    config = load_config()

    if args.name is None and args.filename is None:
        os._exit(0)

    if args.name is not None:
        interactive_search_and_download(args.name, config, iterating=True)

    if args.filename is not None:
        download_from_file(args.filename, config)

    os._exit(0)


def run_cli(args: argparse.Namespace) -> bool:
    """
    Ejecuta los comandos de CLI segun los flags recibidos.
    Devuelve True si alguno de los comandos manejo la ejecucion (y por lo
    tanto el programa ya termino), False si se debe continuar al modo interactivo.
    """
    if handle_config_command(args):
        return True
    if handle_download_command(args):
        return True
    return False
