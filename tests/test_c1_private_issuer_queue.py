from __future__ import annotations
import base64, json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from scripts.constituent_weekly.build_c1_private_issuer_queue import AAD, encrypt_manifest

def _decrypt(data, private_key):
    envelope=json.loads(data)
    wrapped=base64.b64decode(envelope["wrapped_key_b64"])
    key=private_key.decrypt(wrapped,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    nonce=base64.b64decode(envelope["nonce_b64"])
    ciphertext=base64.b64decode(envelope["ciphertext_b64"])
    return json.loads(AESGCM(key).decrypt(nonce,ciphertext,AAD))

def test_encrypted_manifest_roundtrip_and_no_plaintext_leak():
    private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public=private.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    summary={"total_matched_unique_candidates":1}
    items=[{"symbol":"PRIVATE_SAMPLE","ex_date":"2024-01-02","ratio_num":"1"}]
    encrypted=encrypt_manifest(summary,items,public)
    assert b"PRIVATE_SAMPLE" not in encrypted and b"2024-01-02" not in encrypted
    assert _decrypt(encrypted,private)=={"items":items,"summary":summary}

def test_encrypted_manifest_uses_fresh_random_nonce():
    private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public=private.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    assert encrypt_manifest({"x":1},[{"symbol":"A"}],public) != encrypt_manifest({"x":1},[{"symbol":"A"}],public)
