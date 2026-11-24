import socket

import pytest

from app.core.config import settings


@pytest.fixture(scope="session", autouse=True)
def require_firestore_emulator():
    """Evita correr las pruebas contra Firestore real o sin emulador."""
    host = settings.FIRESTORE_EMULATOR_HOST
    if not host:
        pytest.exit(
            "FIRESTORE_EMULATOR_HOST no está definido en .env: las pruebas solo "
            "deben correr contra el emulador.",
            returncode=2,
        )
    hostname, _, port = host.partition(":")
    try:
        socket.create_connection((hostname, int(port or 8080)), timeout=2).close()
    except OSError:
        pytest.exit(
            f"No se pudo conectar al emulador de Firestore en {host}. "
            "Inícialo con: firebase emulators:start --only firestore",
            returncode=2,
        )
