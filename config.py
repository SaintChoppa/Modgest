"""
config.py
---------
Carga, guarda y modifica la configuración de Modgest (versión del juego,
tipo de mod buscado y modloader). La configuración se persiste como JSON
en `modgest_config.json`, dentro del directorio desde el que se ejecuta el programa.
"""

import json
import os
from dataclasses import dataclass, asdict

from ui import winput

WORKING_DIRECTORY = os.getcwd()
CONFIG_FILE_PATH = os.path.join(WORKING_DIRECTORY, "modgest_config.json")

DEFAULT_CONFIG = {
    "user_version": "1.20.1",
    "loader": "forge",
    "mod_type": "ambos",
}


@dataclass
class ModgestConfig:
    """Representa la configuración activa de Modgest."""
    user_version: str = DEFAULT_CONFIG["user_version"]
    mod_type: str = DEFAULT_CONFIG["mod_type"]
    loader: str = DEFAULT_CONFIG["loader"]

    def to_dict(self) -> dict:
        return asdict(self)


def _prompt_initial_config() -> dict:
    """Pregunta al usuario los valores iniciales de configuración (primer uso)."""
    return {
        "user_version": winput("Ingresa la versión de tu juego > ", torep="1.20.1"),
        "mod_type": winput("Buscar mods para (cliente/servidor/ambos) > ", torep="any").lower(),
        "loader": winput("Ingresa tu modloader (forge/fabric/neoforge) > ", torep="forge").lower(),
    }


def load_config() -> ModgestConfig:
    """
    Carga la configuración desde disco. Si no existe el archivo, pide los datos
    al usuario interactivamente y los guarda. Devuelve un ModgestConfig.
    """
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            raw = json.load(config_file)
    else:
        raw = _prompt_initial_config()
        save_config_dict(raw)

    return ModgestConfig(
        user_version=raw.get("user_version", DEFAULT_CONFIG["user_version"]),
        mod_type=raw.get("mod_type", DEFAULT_CONFIG["mod_type"]),
        loader=raw.get("loader", DEFAULT_CONFIG["loader"]),
    )


def save_config_dict(raw: dict) -> None:
    """Escribe un diccionario de configuración directamente a disco como JSON."""
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config_file.write(json.dumps(raw))


def save_config(config: ModgestConfig) -> None:
    """Persiste un ModgestConfig a disco."""
    save_config_dict(config.to_dict())


def update_config_value(config: ModgestConfig, key: str, value: str) -> ModgestConfig:
    """
    Actualiza un único campo de la configuración (por nombre de atributo) y lo guarda.
    Devuelve la configuración actualizada.
    """
    if not hasattr(config, key):
        raise ValueError(f"Clave de configuración inválida: {key}")
    setattr(config, key, value)
    save_config(config)
    return config
