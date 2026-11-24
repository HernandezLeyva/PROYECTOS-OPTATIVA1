import os
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings


def get_firestore_client():
    if settings.FIRESTORE_EMULATOR_HOST:
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST
        print(f"[Firestore] EMULADOR en {settings.FIRESTORE_EMULATOR_HOST}")
        return firestore.Client(project=settings.FIREBASE_PROJECT_ID)

    print(f"[Firestore] NUBE, proyecto {settings.FIREBASE_PROJECT_ID}")
    
    # Firestore real (usa la llave de la cuenta de servicio)
    if not settings.FIREBASE_CREDENTIALS_PATH:
        raise RuntimeError("Define FIREBASE_CREDENTIALS_PATH en .env para usar Firestore real")
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
    
    return firestore.client(database_id=settings.FIRESTORE_DATABASE)

db = get_firestore_client()