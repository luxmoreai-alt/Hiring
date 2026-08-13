from django.core import signing
from rest_framework.exceptions import AuthenticationFailed

SALT = "campus-hire-token"


def make_token(subject, kind="candidate"):
    return signing.dumps({"sub": str(subject), "kind": kind}, salt=SALT, compress=True)


def read_token(request, expected="candidate"):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise AuthenticationFailed("Authentication required")
    try:
        data = signing.loads(header[7:], salt=SALT, max_age=60 * 60 * 12)
    except signing.BadSignature as exc:
        raise AuthenticationFailed("Invalid or expired session") from exc
    if data.get("kind") != expected:
        raise AuthenticationFailed("Invalid session type")
    return data["sub"]
