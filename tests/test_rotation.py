import os

from backupguard import rotation


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("contenido")


def test_list_backups_returns_matching_files_sorted(tmp_path):
    _touch(tmp_path / "prueba_20260101-000000-000000.zip")
    _touch(tmp_path / "prueba_20260103-000000-000000.zip")
    _touch(tmp_path / "prueba_20260102-000000-000000.zip")
    _touch(tmp_path / "otro_20260101-000000-000000.zip")

    backups = rotation.list_backups(str(tmp_path), "prueba")

    assert [os.path.basename(b) for b in backups] == [
        "prueba_20260101-000000-000000.zip",
        "prueba_20260102-000000-000000.zip",
        "prueba_20260103-000000-000000.zip",
    ]


def test_backups_to_delete_keeps_most_recent(tmp_path):
    for i in range(1, 6):
        _touch(tmp_path / f"prueba_2026010{i}-000000-000000.zip")

    to_delete = rotation.backups_to_delete(str(tmp_path), "prueba", keep=2)

    assert [os.path.basename(p) for p in to_delete] == [
        "prueba_20260101-000000-000000.zip",
        "prueba_20260102-000000-000000.zip",
        "prueba_20260103-000000-000000.zip",
    ]


def test_backups_to_delete_returns_empty_when_under_limit(tmp_path):
    _touch(tmp_path / "prueba_20260101-000000-000000.zip")

    to_delete = rotation.backups_to_delete(str(tmp_path), "prueba", keep=5)

    assert to_delete == []


def test_apply_rotation_removes_old_files(tmp_path):
    for i in range(1, 4):
        _touch(tmp_path / f"prueba_2026010{i}-000000-000000.zip")

    deleted = rotation.apply_rotation(str(tmp_path), "prueba", keep=1)

    assert len(deleted) == 2
    remaining = rotation.list_backups(str(tmp_path), "prueba")
    assert len(remaining) == 1
    for path in deleted:
        assert not os.path.exists(path)


def test_apply_rotation_dry_run_does_not_delete(tmp_path):
    for i in range(1, 4):
        _touch(tmp_path / f"prueba_2026010{i}-000000-000000.zip")

    deleted = rotation.apply_rotation(str(tmp_path), "prueba", keep=1, dry_run=True)

    assert len(deleted) == 2
    remaining = rotation.list_backups(str(tmp_path), "prueba")
    assert len(remaining) == 3
