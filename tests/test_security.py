from app.core.security import (
    API_KEY_PREFIX,
    KEY_PREFIX_LENGTH,
    generate_api_key,
    get_key_prefix,
    hash_api_key,
    verify_api_key,
)


def test_generate_api_key_has_prefix_and_is_unique():
    first = generate_api_key()
    second = generate_api_key()

    assert first.startswith(API_KEY_PREFIX)
    assert len(first) > 40
    assert first != second


def test_hash_api_key_is_deterministic_sha256():
    key = generate_api_key()

    key_hash = hash_api_key(key)

    assert key_hash == hash_api_key(key)
    assert len(key_hash) == 64
    assert key not in key_hash


def test_verify_api_key_accepts_matching_key():
    key = generate_api_key()

    assert verify_api_key(key, hash_api_key(key))


def test_verify_api_key_rejects_other_key():
    key = generate_api_key()

    assert not verify_api_key(generate_api_key(), hash_api_key(key))


def test_get_key_prefix_returns_leading_characters():
    key = generate_api_key()

    assert get_key_prefix(key) == key[:KEY_PREFIX_LENGTH]
    assert get_key_prefix(key).startswith(API_KEY_PREFIX)
