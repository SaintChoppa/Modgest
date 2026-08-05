"""
ui.py
-----
Funciones de interfaz de consola: impresión animada, entrada de usuario,
limpieza de pantalla y construcción de tablas ASCII para mostrar resultados.

Mantiene pystyle/colorama como motor visual, igual que el código original.
"""

import os
from pystyle import Write, Colors
from colorama import Fore

# Color principal usado en toda la UI
MAIN_COLOR = Fore.LIGHTGREEN_EX
DEFAULT_GRADIENT = Colors.white_to_green

# Ancho fijo usado por las tablas (se mantiene igual al original)
TABLE_WIDTH = 33


def jilog(text: str) -> None:
    """Imprime texto con el efecto de escritura animada y un salto de línea extra."""
    Write.Print(text, DEFAULT_GRADIENT, 0.005)
    print()


def winput(text: str = "", torep: str = "") -> str:
    """
    Pide un input al usuario con estilo animado.
    Si el usuario no escribe nada, devuelve `torep` (valor por defecto).
    """
    respuesta = Write.Input(text, DEFAULT_GRADIENT, 0.005)
    return torep if respuesta == "" else respuesta


def cls() -> None:
    """Limpia la pantalla de la terminal (compatible con Windows y Unix)."""
    os.system("cls" if os.name == "nt" else "clear")


def remake_string(text: str, max_length: int = TABLE_WIDTH) -> list[str]:
    """
    Divide un texto largo en una lista de líneas que no exceden `max_length`,
    respetando los espacios para no cortar palabras a la mitad cuando es posible.
    """
    lines = []
    while len(text) > max_length:
        split_pos = text.rfind(' ', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        lines.append(text[:split_pos].strip())
        text = text[split_pos:].strip()
    lines.append(text)
    return lines


def make_table(table_data: list[str], table_header="", show: bool = False) -> int:
    """
    Construye (y opcionalmente imprime) una tabla ASCII con bordes,
    un encabezado opcional y las líneas de `table_data` como contenido.

    Devuelve el ancho usado para la tabla (constante, igual al original).
    """
    lines = table_data
    if isinstance(table_header, str) and len(table_header) > TABLE_WIDTH:
        table_header = remake_string(table_header)

    width = TABLE_WIDTH

    if show:
        print(f'{MAIN_COLOR}╔{"═" * (width + 2)}╗{Fore.RESET}')

    if table_header != "":
        if isinstance(table_header, list):
            for line in table_header:
                if show:
                    print(f"{MAIN_COLOR}║{Fore.RESET} {line} {' ' * (width - len(line) - 1)} {MAIN_COLOR}║")
        else:
            if show:
                print(f"{MAIN_COLOR}║{Fore.RESET} {table_header} {' ' * (width - len(table_header) - 1)} {MAIN_COLOR}║")
        if show:
            print(f"{MAIN_COLOR}╠{'═' * (width + 2)}╣{Fore.RESET}")

    for line in lines:
        if line.strip() == "":
            continue
        padding = width - len(line)
        if show:
            print(f'{MAIN_COLOR}║{Fore.RESET} {line}{" " * padding} {MAIN_COLOR}║')

    if show:
        print(f'{MAIN_COLOR}╚{"═" * (width + 2)}╝{Fore.RESET}')

    return width


if __name__ == "__main__":
    print("Testing tables...")
    longer = make_table(
        remake_string("Adds plenty of blocks and items to defend and secure your base with."),
        table_header="[4] security breach objects, blocks, & more open beta",
        show=True,
    )
    print(f"Longest line: {longer}")
