from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.constituent_weekly import build_c1_private_issuer_queue as base

SECONDARY_CLASSES = {"buyback", "agm_or_other"}
REFERENCE_COUNT = 49


def build_secondary_private_queue(token: str, cache_dir: Path):
    """Build only the remaining 20 buyback and 29 AGM/other candidates."""
    original_classes = base.REVIEW_CLASSES
    try:
        base.REVIEW_CLASSES = set(SECONDARY_CLASSES)
        summary, items = base.build_private_candidate_queue(token, cache_dir)
    finally:
        base.REVIEW_CLASSES = original_classes
    summary["catalogue_reference_count"] = REFERENCE_COUNT
    summary["matches_reference_count"] = len(items) == REFERENCE_COUNT
    summary["event_classes"] = sorted(SECONDARY_CLASSES)
    return summary, items


def main() -> int:
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise SystemExit("HF_TOKEN is required.")
    if not base.personal_use_fallback_authorized(os.environ.get("TEJHQ_PERSONAL_USE_ONLY")):
        raise SystemExit("Personal-use-only handling was not confirmed.")
    cache = base.resolve_tejhq_encrypted_cache_dir(os.environ.get("TEJHQ_ENCRYPTED_CACHE_DIR"))
    summary, items = build_secondary_private_queue(token, cache)
    payload = base.encrypt_manifest(summary, items, base.PUBLIC_KEY_PEM)
    output = Path(os.environ.get("C1_SECONDARY_QUEUE_PATH", "/tmp/c1-secondary-issuer-review-queue.enc.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    print("C1_SECONDARY_QUEUE_SUMMARY", json.dumps({
        "total_matched_unique_candidates": summary["total_matched_unique_candidates"],
        "matches_reference_count": summary["matches_reference_count"],
        "counts": summary["counts"],
        "partition_cache_hits": sum(x["encrypted_cache_hit"] for x in summary["partition_metadata"]),
        "partition_count": len(summary["partition_metadata"]),
        "cleartext_rows_published": False,
        "recipient_public_key_fingerprint_sha256": base.PUBLIC_KEY_FINGERPRINT_SHA256,
    }, sort_keys=True))
    print("C1_SECONDARY_QUEUE_ENCRYPTED_SHA256", hashlib.sha256(payload).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
