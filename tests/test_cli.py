import json

from backupguard import rotation
from backupguard.cli import run_backups
from backupguard.config import load_config


def _make_config(tmp_path, keep=2):
    source = tmp_path / "origen"
    source.mkdir()
    (source / "archivo.txt").write_text("hola")

    destination = tmp_path / "destino"

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({
        "jobs": [
            {
                "name": "prueba",
                "source": str(source),
                "destination": str(destination),
                "keep": keep,
            }
        ]
    }))

    return load_config(str(config_path)), destination


def test_run_backups_creates_archive(tmp_path):
    config, destination = _make_config(tmp_path)

    failures = run_backups(config)

    assert failures == []
    backups = rotation.list_backups(str(destination), "prueba")
    assert len(backups) == 1


def test_run_backups_rotates_old_archives(tmp_path):
    config, destination = _make_config(tmp_path, keep=2)

    for _ in range(4):
        run_backups(config)

    backups = rotation.list_backups(str(destination), "prueba")
    assert len(backups) == 2


def test_run_backups_reports_failure_for_missing_source(tmp_path):
    destination = tmp_path / "destino"
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({
        "jobs": [
            {
                "name": "prueba",
                "source": str(tmp_path / "no-existe"),
                "destination": str(destination),
            }
        ]
    }))
    config = load_config(str(config_path))

    failures = run_backups(config)

    assert len(failures) == 1
    assert failures[0][0] == "prueba"


def test_run_backups_dry_run_creates_nothing(tmp_path):
    config, destination = _make_config(tmp_path)

    failures = run_backups(config, dry_run=True)

    assert failures == []
    assert not destination.exists()
