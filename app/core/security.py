import hashlib
import hmac
import secrets

API_KEY_PREFIX = "lgw_"
KEY_PREFIX_LENGTH = 12


def generate_api_key() -> str:
    """클라이언트에게 한 번만 보여줄 API 키 원문을 만든다."""
    return API_KEY_PREFIX + secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """키 원문 대신 저장할 SHA-256 해시. 키가 충분히 무작위라 느린 해시는 필요 없다."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_key_prefix(api_key: str) -> str:
    """목록에서 키를 구분할 수 있게 보여줄 앞자리."""
    return api_key[:KEY_PREFIX_LENGTH]


def verify_api_key(api_key: str, key_hash: str) -> bool:
    return hmac.compare_digest(hash_api_key(api_key), key_hash)
