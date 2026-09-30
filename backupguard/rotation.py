"""Decide qué copias de seguridad antiguas eliminar según la política de
retención de cada trabajo.
"""

import glob
import os


def list_backups(destination, job_name):
    """Devuelve las rutas de las copias de un trabajo, de más antigua a más
    reciente. El formato del nombre de archivo (timestamp) hace que el orden
    alfabético coincida con el orden cronológico.
    """
    pattern = os.path.join(destination, f"{job_name}_*.zip")
    return sorted(glob.glob(pattern))


def backups_to_delete(destination, job_name, keep):
    """Devuelve las copias que sobran según cuántas se quieren conservar."""
    backups = list_backups(destination, job_name)
    if len(backups) <= keep:
        return []
    return backups[: len(backups) - keep]


def apply_rotation(destination, job_name, keep, dry_run=False):
    """Elimina las copias más antiguas que sobrepasen la política de
    retención. Devuelve la lista de archivos eliminados (o que se habrían
    eliminado, si dry_run es True).
    """
    to_delete = backups_to_delete(destination, job_name, keep)
    if not dry_run:
        for path in to_delete:
            os.remove(path)
    return to_delete
