from unittest.mock import MagicMock, patch

from backupguard.notifier import send_failure_email


SMTP_CONFIG = {
    "host": "smtp.example.com",
    "port": 587,
    "user": "alertas@example.com",
    "password": "secreto",
    "to": "kevin@example.com",
}


def test_send_failure_email_sends_when_failures_exist():
    failures = [("documentos", "Permiso denegado")]

    with patch("backupguard.notifier.smtplib.SMTP") as mock_smtp:
        server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = server

        result = send_failure_email(SMTP_CONFIG, failures)

    assert result is True
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("alertas@example.com", "secreto")
    server.send_message.assert_called_once()


def test_send_failure_email_does_nothing_without_failures():
    with patch("backupguard.notifier.smtplib.SMTP") as mock_smtp:
        result = send_failure_email(SMTP_CONFIG, [])

    assert result is False
    mock_smtp.assert_not_called()


def test_send_failure_email_does_nothing_without_config():
    with patch("backupguard.notifier.smtplib.SMTP") as mock_smtp:
        result = send_failure_email(None, [("job", "error")])

    assert result is False
    mock_smtp.assert_not_called()
