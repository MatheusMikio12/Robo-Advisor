import base64
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings
from app.models.wealth import WealthRecord


def security_record(db, user):
    row = db.query(WealthRecord).filter_by(user_id=user.id, kind="security", external_id="account").first()
    if not row:
        row = WealthRecord(user_id=user.id, kind="security", external_id="account", data={"version": 0, "mfa": False})
        db.add(row)
        db.flush()
    return row


def version(db, user):
    row = db.query(WealthRecord).filter_by(user_id=user.id, kind="security", external_id="account").first()
    return row.data.get("version", 0) if row else 0


def cipher():
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(settings.secret_key.encode()).digest()))
