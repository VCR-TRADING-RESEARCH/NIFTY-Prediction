from __future__ import annotations
import base64, hashlib, json, os
from datetime import date, datetime
from pathlib import Path
import pandas as pd
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from scripts.constituent_weekly.audit_c1_corporate_actions import (
    START, END, load_action_year, load_member_intervals, match_member_keys, normalise_type
)
from scripts.constituent_weekly.audit_c1_daily_history import (
    personal_use_fallback_authorized, resolve_tejhq_encrypted_cache_dir
)

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAt1cWfCvy3poaLuNOA1i9
ybvQPWUOaqZSTbCHFju15LsHMwBZU2Ui9y/tmMoIhxPbWStgIiiRwi8FnbI/y69V
3bQjnz6V3ZnLIR93YJyfZjfL2bGQYjqkMVlL0MnZ0OCoyK6QtYufUvCV2l3PJukq
CmJFxNgrpK3FLyKKxHDGbMiEOW00tcNypI2Raqik6SkUSzNC6O5rij4ReS5Ix5sx
jYDHieEd/Y8iZjQ0voc1LmlKezNxIPffbHsH0Dg7/kcE7072aFeQYvt6FVwCizHw
+0UL7TvTKtG9wRF7c1vyRDfdhvOiaEChfixZ66Q5eihwT86mK3mA8MzVKz3TRj9X
a2xRlv88xrwq1A7TMLq7DyksSvY15VKVpFUYLIXGW3WfW23NbhYUtz189wgAOWMp
PyEkZ/XPuaA67POyfg3WC7meX4HmM3YuTW1Gl3F7YLmPcfONxATnLkiuTGEHUUS1
EnyK/OhRnZJnDcy5m/aFJ+fCY+kSTpsxHwtEc76bjYfNAgMBAAE=
-----END PUBLIC KEY-----"""
REVIEW_CLASSES = {"bonus", "split", "rights", "merger_demerger"}
AAD = b"BUP-01-C1-ISSUER-REVIEW-QUEUE-v1"
YEARS = range(2018, 2027)
FIELDS = ("exchange","symbol","isin","company","ex_date","record_date","type","ratio_num","ratio_den","cash_amount","face_value_from","face_value_to","raw_subject")

def clean_scalar(value):
    if value is None: return None
    if isinstance(value, (pd.Timestamp, datetime, date)): return value.isoformat()[:10]
    try:
        if pd.isna(value): return None
    except (TypeError, ValueError): pass
    if hasattr(value, "item"):
        try: value = value.item()
        except (TypeError, ValueError): pass
    return value if isinstance(value, (str,int,float,bool)) else str(value)

def build_private_candidate_queue(token: str, cache_dir: Path):
    intervals = load_member_intervals()
    queue = []
    counts = {k: {"matched":0,"ambiguous":0,"unmatched":0} for k in sorted(REVIEW_CLASSES)}
    metadata = []
    for year in YEARS:
        partition, meta = load_action_year(year, token, cache_dir)
        metadata.append({"year":int(meta["year"]),"partition_sha256":str(meta["sha256"]),
                         "encrypted_cache_hit":bool(meta["encrypted_cache_hit"])})
        frame = partition.copy()
        frame["exchange"] = frame["exchange"].astype("string").str.upper().str.strip()
        frame["ex_date_parsed"] = pd.to_datetime(frame["ex_date"], errors="coerce")
        frame = frame.loc[frame["exchange"].eq("NSE") &
                          frame["ex_date_parsed"].between(START, END, inclusive="both")]
        frame = frame.drop_duplicates(["exchange","symbol","isin","ex_date","type"])
        for row in frame.itertuples(index=False):
            kind = normalise_type(getattr(row,"type"))
            if kind not in REVIEW_CLASSES: continue
            ex_date = pd.Timestamp(getattr(row,"ex_date_parsed")).strftime("%Y-%m-%d")
            symbol = str(getattr(row,"symbol","")).strip().upper()
            matches = match_member_keys(symbol, ex_date, intervals)
            if len(matches) != 1:
                counts[kind]["ambiguous" if len(matches)>1 else "unmatched"] += 1
                continue
            counts[kind]["matched"] += 1
            item = {"point_in_time_member_key":matches[0],"ex_date":ex_date,"event_class":kind}
            for field in FIELDS: item[field] = clean_scalar(getattr(row,field,None))
            queue.append(item)
    keys = ("exchange","symbol","isin","ex_date","type")
    unique = {"|".join(str(item.get(k) or "") for k in keys):item for item in queue}
    items = sorted(unique.values(), key=lambda x:(x["event_class"],x["ex_date"],x["symbol"]))
    summary = {"window":{"start":START,"end":END},"event_classes":sorted(REVIEW_CLASSES),
               "counts":counts,"total_matched_unique_candidates":len(items),
               "catalogue_reference_count":37,"matches_reference_count":len(items)==37,
               "partition_metadata":metadata,"cleartext_rows_written_to_disk":False,
               "cleartext_rows_or_identifiers_published":False,
               "source_terms":"TEJHQ_PERSONAL_USE_ONLY; recipient-encrypted private queue; no redistribution"}
    return summary, items

def encrypt_manifest(summary: dict, items: list[dict], public_key_pem: bytes | str) -> bytes:
    pem = public_key_pem.encode("utf-8") if isinstance(public_key_pem,str) else public_key_pem
    public_key = serialization.load_pem_public_key(pem)
    plaintext = json.dumps({"summary":summary,"items":items},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce,plaintext,AAD)
    wrapped = public_key.encrypt(key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),label=None))
    envelope = {"format":"RSA-OAEP-SHA256+AES-256-GCM-v1",
        "aad_b64":base64.b64encode(AAD).decode(),
        "wrapped_key_b64":base64.b64encode(wrapped).decode(),
        "nonce_b64":base64.b64encode(nonce).decode(),
        "ciphertext_b64":base64.b64encode(ciphertext).decode()}
    return (json.dumps(envelope,sort_keys=True,separators=(",",":"))+"\n").encode()

def main():
    token=os.environ.get("HF_TOKEN","").strip()
    if not token: raise SystemExit("HF_TOKEN is required.")
    if not personal_use_fallback_authorized(os.environ.get("TEJHQ_PERSONAL_USE_ONLY")):
        raise SystemExit("Personal-use-only handling was not confirmed.")
    cache=resolve_tejhq_encrypted_cache_dir(os.environ.get("TEJHQ_ENCRYPTED_CACHE_DIR"))
    summary,items=build_private_candidate_queue(token,cache)
    payload=encrypt_manifest(summary,items,PUBLIC_KEY_PEM)
    output=Path(os.environ.get("C1_PRIVATE_QUEUE_PATH","/tmp/c1-issuer-review-queue.enc.json"))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(payload)
    print("C1_ISSUER_REVIEW_QUEUE_SUMMARY",json.dumps({
        "total_matched_unique_candidates":summary["total_matched_unique_candidates"],
        "matches_reference_count":summary["matches_reference_count"],
        "counts":summary["counts"],
        "partition_cache_hits":sum(x["encrypted_cache_hit"] for x in summary["partition_metadata"]),
        "partition_count":len(summary["partition_metadata"]),
        "cleartext_rows_published":False},sort_keys=True))
    print("C1_ISSUER_REVIEW_QUEUE_ENCRYPTED_SHA256",hashlib.sha256(payload).hexdigest())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
