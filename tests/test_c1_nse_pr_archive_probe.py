from __future__ import annotations
import io, zipfile
from datetime import date
from scripts.constituent_weekly.probe_c1_nse_pr_archives import cache_helpers, candidate_urls, parse_bundle


def test_candidate_url_uses_legacy_and_new_names_across_transition():
    before = candidate_urls(date(2024, 4, 17))
    after = candidate_urls(date(2025, 10, 14))
    assert any("/nupr170424.zip" in url for url in before)
    assert any("/PR141025.zip" in url for url in after)
    assert all("/content/historical/EQUITIES/2024/APR/" in url for url in before if "/content/historical/" in url)
    assert all("/content/historical/EQUITIES/2025/OCT/" in url for url in after if "/content/historical/" in url)


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
