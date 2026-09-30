"""Carga y valida el archivo de configuración de los trabajos de copia de
seguridad.
"""

import json


class ConfigError(Exception):
    """Se lanza cuando el archivo de configuración no es válido."""


def load_config(path):
    """Lee el archivo JSON de configuración y aplica valores por defecto.

    Cada elemento de "jobs" debe incluir al menos: name, source y
    destination. "keep" es opcional (por defecto 5). "notify_email" es
    opcional a nivel global.
    """
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise ConfigError(f"No se encuentra el archivo de configuración: {path}")
    except json.JSONDecodeError as error:
        raise ConfigError(f"El archivo de configuración no es un JSON válido: {error}")

    jobs = data.get("jobs")
    if not jobs:
        raise ConfigError("La configuración debe incluir al menos un trabajo en 'jobs'.")

    for job in jobs:
        for field in ("name", "source", "destination"):
            if field not in job:
                raise ConfigError(f"Cada trabajo debe incluir '{field}'.")
        job.setdefault("keep", 5)

    data.setdefault("notify_email", None)
    return data
