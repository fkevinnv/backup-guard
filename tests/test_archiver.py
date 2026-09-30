import os
import zipfile

import pytest

from backupguard import archiver


def test_create_backup_compresses_all_files(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("contenido a")
    (source / "sub").mkdir()
    (source / "sub" / "b.txt").write_text("contenido b")

    destination = tmp_path / "backups"

    archive_path = archiver.create_backup(str(source), str(destination), "prueba")

    assert archive_path.endswith(".zip")
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())

    assert "a.txt" in names
    assert os.path.join("sub", "b.txt") in names


def test_create_backup_raises_if_source_missing(tmp_path):
    destination = tmp_path / "backups"

    with pytest.raises(FileNotFoundError):
        archiver.create_backup(str(tmp_path / "no-existe"), str(destination), "prueba")


def test_dry_run_does_not_create_file(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("contenido")
    destination = tmp_path / "backups"

    archive_path = archiver.create_backup(str(source), str(destination), "prueba", dry_run=True)

    assert not os.path.exists(archive_path)


def test_restore_backup_extracts_files(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("contenido original")
    destination = tmp_path / "backups"

    archive_path = archiver.create_backup(str(source), str(destination), "prueba")

    restore_to = tmp_path / "restaurado"
    archiver.restore_backup(archive_path, str(restore_to))

    assert (restore_to / "a.txt").read_text() == "contenido original"


def test_restore_backup_raises_if_archive_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        archiver.restore_backup(str(tmp_path / "no-existe.zip"), str(tmp_path / "destino"))
