from firebase_admin import credentials, firestore, initialize_app
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def init_firebase():
    try:
        cred = credentials.Certificate(settings.firebase_credentials)
        initialize_app(cred)
        return firestore.client()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise

db = init_firebase()