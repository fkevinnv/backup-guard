"""Interfaz de línea de comandos de backup-guard."""

import argparse
import logging
import os
import sys
import time

from backupguard import archiver, rotation
from backupguard.config import ConfigError, load_config
from backupguard.notifier import send_failure_email

logger = logging.getLogger("backupguard")


def setup_logging(log_file):
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def _human_size(size_bytes):
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def run_backups(config, dry_run=False):
    """Ejecuta todos los trabajos definidos en la configuración.

    Devuelve la lista de fallos como tuplas (nombre_trabajo, error).
    """
    failures = []

    for job in config["jobs"]:
        name = job["name"]
        try:
            archive_path = archiver.create_backup(
                job["source"], job["destination"], name, dry_run=dry_run
            )
            suffix = " [dry-run]" if dry_run else f" ({_human_size(os.path.getsize(archive_path))})"
            logger.info("Copia creada: %s%s", archive_path, suffix)

            deleted = rotation.apply_rotation(job["destination"], name, job["keep"], dry_run=dry_run)
            for path in deleted:
                logger.info("Copia antigua eliminada: %s%s", path, " [dry-run]" if dry_run else "")

        except Exception as error:
            logger.error("Fallo en el trabajo '%s': %s", name, error)
            failures.append((name, str(error)))

    if failures and config.get("notify_email") and not dry_run:
        try:
            send_failure_email(config["notify_email"], failures)
            logger.info("Aviso de fallo enviado por correo.")
        except Exception as error:
            logger.error("No se pudo enviar el aviso por correo: %s", error)

    return failures


def _report(failures):
    if failures:
        print(f"\n{len(failures)} trabajo(s) con errores. Revisa el log para más detalles.")
    else:
        print("\nTodos los trabajos se completaron correctamente.")


def cmd_run(args):
    config = load_config(args.config)
    setup_logging(args.log_file)

    if args.interval:
        logger.info("Modo continuo: copia cada %s segundos. Pulsa Ctrl+C para detener.", args.interval)
        try:
            while True:
                failures = run_backups(config, dry_run=args.dry_run)
                _report(failures)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Detenido por el usuario.")
            sys.exit(0)
    else:
        failures = run_backups(config, dry_run=args.dry_run)
        _report(failures)
        sys.exit(1 if failures else 0)


def cmd_list(args):
    config = load_config(args.config)
    for job in config["jobs"]:
        backups = rotation.list_backups(job["destination"], job["name"])
        print(f"\n{job['name']} ({len(backups)} copia(s)):")
        if not backups:
            print("  (sin copias todavía)")
        for path in backups:
            print(f"  {path}")


def cmd_restore(args):
    destination = archiver.restore_backup(args.archive, args.destination)
    print(f"Copia restaurada en: {destination}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="backup-guard",
        description="Automatiza copias de seguridad: comprime, rota copias antiguas y avisa de fallos.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Ejecuta los trabajos de copia definidos en la configuración")
    run_parser.add_argument("--config", default="config.json", help="Ruta al archivo de configuración (por defecto config.json)")
    run_parser.add_argument("--log-file", default="backup-guard.log", help="Ruta del archivo de log (por defecto backup-guard.log)")
    run_parser.add_argument("--interval", type=int, help="Repetir cada N segundos en lugar de ejecutar una sola vez")
    run_parser.add_argument("--dry-run", action="store_true", help="Simula la ejecución sin copiar ni borrar nada")
    run_parser.set_defaults(func=cmd_run)

    list_parser = subparsers.add_parser("list", help="Lista las copias de seguridad existentes por trabajo")
    list_parser.add_argument("--config", default="config.json", help="Ruta al archivo de configuración")
    list_parser.set_defaults(func=cmd_list)

    restore_parser = subparsers.add_parser("restore", help="Restaura una copia de seguridad concreta")
    restore_parser.add_argument("archive", help="Ruta del archivo .zip de la copia a restaurar")
    restore_parser.add_argument("destination", help="Carpeta donde extraer la copia")
    restore_parser.set_defaults(func=cmd_restore)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except ConfigError as error:
        print(f"Error de configuración: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
