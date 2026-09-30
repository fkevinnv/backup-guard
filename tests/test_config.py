import json

import pytest

from backupguard.config import ConfigError, load_config


def test_load_config_applies_defaults(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({
        "jobs": [{"name": "docs", "source": "/tmp/docs", "destination": "/tmp/backups"}]
    }))

    config = load_config(str(config_path))

    assert config["jobs"][0]["keep"] == 5
    assert config["notify_email"] is None


def test_load_config_keeps_explicit_keep_value(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({
        "jobs": [{"name": "docs", "source": "/tmp/docs", "destination": "/tmp/backups", "keep": 10}]
    }))

    config = load_config(str(config_path))

    assert config["jobs"][0]["keep"] == 10


def test_load_config_missing_file_raises():
    with pytest.raises(ConfigError):
        load_config("/ruta/que/no/existe.json")


def test_load_config_invalid_json_raises(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{ esto no es json valido")

    with pytest.raises(ConfigError):
        load_config(str(config_path))


def test_load_config_requires_jobs(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({}))

    with pytest.raises(ConfigError):
        load_config(str(config_path))


def test_load_config_requires_fields_per_job(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"jobs": [{"name": "docs"}]}))

    with pytest.raises(ConfigError):
        load_config(str(config_path))
