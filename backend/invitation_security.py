
import secrets
import hashlib
from datetime import datetime, timedelta, timezone


# Generate a cryptographically secure invitation token
def generate_invitation_token():
    return secrets.token_urlsafe(32)


# Hash the token before storing it in the database
def hash_invitation_token(token: str):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# Set invitation expiry time (24 hours)
def get_invitation_expiry():
    return datetime.now(timezone.utc).replace(
        tzinfo=None
    ) + timedelta(hours=24)


# Check whether invitation has expired
def is_invitation_expired(expires_at: datetime):
    return datetime.now(timezone.utc).replace(
        tzinfo=None
    ) >= expires_at


import os
import jwt
from dotenv import load_dotenv

load_dotenv()

CANDIDATE_SESSION_SECRET = os.getenv("CANDIDATE_SESSION_SECRET")


def create_candidate_session_token(
    screening_id: int,
    candidate_id: int
):
    if not CANDIDATE_SESSION_SECRET:
        raise RuntimeError(
            "CANDIDATE_SESSION_SECRET is not configured"
        )

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(candidate_id),
        "screening_id": screening_id,
        "type": "candidate_interview",
        "iat": now,
        "exp": now + timedelta(minutes=30)
    }

    return jwt.encode(
        payload,
        CANDIDATE_SESSION_SECRET,
        algorithm="HS256"
    )


def verify_candidate_session_token(token: str):
    if not CANDIDATE_SESSION_SECRET:
        raise RuntimeError(
            "CANDIDATE_SESSION_SECRET is not configured"
        )

    payload = jwt.decode(
        token,
        CANDIDATE_SESSION_SECRET,
        algorithms=["HS256"],
        options={"require": ["sub", "screening_id", "type", "iat", "exp"]}
    )

    if payload.get("type") != "candidate_interview":
        raise jwt.InvalidTokenError("Invalid session type")

    return payload
