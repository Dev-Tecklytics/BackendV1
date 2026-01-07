import secrets
import hashlib

def generate_api_key():
    raw_key = "sk_live_"+secrets.token_hex(32)
    prefix = raw_key[:8]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, prefix, key_hash
    