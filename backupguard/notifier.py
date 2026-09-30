"""Envía un aviso por correo cuando uno o varios trabajos de copia de
seguridad fallan.
"""

import smtplib
from email.message import EmailMessage


def send_failure_email(smtp_config, failures):
    """smtp_config: diccionario con host, port, user, password y to.
    failures: lista de tuplas (nombre_trabajo, mensaje_error).

    No hace nada (y devuelve False) si falta la configuración de correo o si
    no hay fallos que notificar.
    """
    if not smtp_config or not failures:
        return False

    body_lines = [f"- {name}: {error}" for name, error in failures]
    body = "Los siguientes trabajos de copia de seguridad han fallado:\n\n" + "\n".join(body_lines)

    message = EmailMessage()
    message["Subject"] = f"[backup-guard] {len(failures)} trabajo(s) con errores"
    message["From"] = smtp_config["user"]
    message["To"] = smtp_config["to"]
    message.set_content(body)

    with smtplib.SMTP(smtp_config["host"], smtp_config.get("port", 587)) as server:
        server.starttls()
        server.login(smtp_config["user"], smtp_config["password"])
        server.send_message(message)

    return True
