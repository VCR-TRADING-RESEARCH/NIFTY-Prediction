import pandas as pd

from scripts.reconcile_archive_closes import compare_archive_to_official


def test_archive_close_audit_uses_preserved_archive_close_not_overridden_close():
    archive = pd.DataFrame({
        "session_date": ["2024-01-02", "2024-01-03"],
        "session_open": [100.0, 101.0],
        "session_high": [105.0, 106.0],
        "session_low": [99.0, 100.0],
        "session_close_archive": [103.0, 104.0],
        "session_close": [103.5, 104.5],
    })
    official = pd.DataFrame({
        "session_date": ["2024-01-02", "2024-01-03"],
        "official_open": [100.0, 101.0],
        "official_high": [105.0, 106.0],
        "official_low": [99.0, 100.0],
        "official_close": [103.5, 104.5],
    })
    merged, metrics = compare_archive_to_official(archive, official)
    assert merged["archive_close"].tolist() == [103.0, 104.0]
    assert metrics["minute_vs_official_mismatches_over_1_point"] == 0
    assert metrics["minute_vs_official_abs_difference_median_points"] == 0.5
    assert metrics["daily_source_rows_compared"] == 2
