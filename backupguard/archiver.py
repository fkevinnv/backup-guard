"""Crea y restaura copias de seguridad comprimidas de una carpeta."""

import os
import zipfile
from datetime import datetime


def build_archive_name(job_name, timestamp=None):
    """Construye el nombre del archivo de copia, con precisión de
    microsegundos para evitar colisiones entre copias creadas muy seguidas.
    """
    timestamp = timestamp or datetime.now()
    return f"{job_name}_{timestamp.strftime('%Y%m%d-%H%M%S-%f')}.zip"


def create_backup(source, destination, job_name, dry_run=False):
    """Comprime el contenido de 'source' en un .zip dentro de 'destination'.

    Devuelve la ruta del archivo creado (o la que se habría creado, si
    dry_run es True, sin escribir nada en disco).
    """
    if not os.path.isdir(source):
        raise FileNotFoundError(f"La carpeta de origen no existe: {source}")

    archive_name = build_archive_name(job_name)
    archive_path = os.path.join(destination, archive_name)

    if dry_run:
        return archive_path

    os.makedirs(destination, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for root, _dirs, files in os.walk(source):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                arcname = os.path.relpath(file_path, source)
                archive.write(file_path, arcname)

    return archive_path


def restore_backup(archive_path, destination):
    """Extrae un archivo de copia de seguridad en la carpeta indicada."""
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(f"No se encuentra el archivo de copia: {archive_path}")

    os.makedirs(destination, exist_ok=True)
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(destination)

    return destination
