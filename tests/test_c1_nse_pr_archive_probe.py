from __future__ import annotations
import io, zipfile
from datetime import date
from scripts.constituent_weekly.probe_c1_nse_pr_archives import cache_helpers, candidate_urls, parse_bundle


def test_candidate_url_uses_canonical_pr_archive_path():
    urls = candidate_urls(date(2024, 4, 16))
    assert urls == ["https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR160424.zip"]


def test_parse_bundle_extracts_only_schema_metadata():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("bcd17042024.csv", "SYMBOL,SERIES,EX-DATE,PURPOSE\nABC,EQ,17-Apr-2024,DIVIDEND\n")
        archive.writestr("and17042024.txt", "private announcement body")
        archive.writestr("bmd17042024.txt", "private board meeting body")
    result = parse_bundle(stream.getvalue(), date(2024, 4, 17))
    assert result["corporate_action_member"] == "bcd17042024.csv"
    assert result["corporate_action_header"] == ["SYMBOL", "SERIES", "EX-DATE", "PURPOSE"]
    assert result["announcement_member_present"] and result["board_meeting_member_present"]
    assert "ABC" not in str(result)


def test_parse_bundle_rejects_missing_corporate_action_member():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("readme.txt", "not a corporate action report")
    try:
        parse_bundle(stream.getvalue(), date(2024, 4, 17))
    except ValueError as exc:
        assert "no documented corporate-action" in str(exc).lower()
    else:
        raise AssertionError("Missing corporate-action CSV must not pass.")



def test_shared_encrypted_cache_helpers_import_in_actions_environment():
    decrypt, encrypt = cache_helpers()
    assert callable(decrypt)
    assert callable(encrypt)
