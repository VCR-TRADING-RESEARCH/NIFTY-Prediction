from scripts.constituent_weekly.probe_c1_dhan_intraday_response_shape import classify_provider_text, response_shape


class FakeResponse:
    def __init__(self, status_code, body, headers=None):
        import json
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.headers = headers or {"Content-Type": "application/json"}
        self.content = json.dumps(body).encode()
        self.text = self.content.decode()

    def json(self):
        import json
        return json.loads(self.content)


def test_provider_message_classification_does_not_retain_message_text():
    assert classify_provider_text("Your data plan does not permit this request") == "ENTITLEMENT_OR_PLAN"
    assert classify_provider_text("Rate limit exceeded") == "RATE_LIMIT"
    assert classify_provider_text("No data found for date range") == "DATE_RANGE_OR_HISTORY"
    assert classify_provider_text(None) == "NO_PROVIDER_MESSAGE"


def test_response_shape_records_keys_types_and_array_lengths_only():
    fake = FakeResponse(200, {
        "status": "failure",
        "remarks": "No data found for this requested date range",
        "data": None,
        "errorCode": "X",
    })
    shape = response_shape(fake)
    assert shape["http_status"] == 200
    assert shape["provider_status_value"] == "failure"
    assert shape["provider_message_category"] == "DATE_RANGE_OR_HISTORY"
    assert shape["data_field_type"] == "NoneType"
    assert shape["payload_container"] == "top_level"
    assert shape["payload_keys"] == ["data", "errorCode", "remarks", "status"]
    assert "No data found" not in str(shape)
    assert "errorCode" in shape["top_level_keys"]


def test_response_shape_handles_successful_top_level_arrays_without_recording_values():
    fake = FakeResponse(200, {
        "status": "success",
        "open": [100, 101],
        "high": [102, 103],
        "low": [99, 100],
        "close": [101, 102],
        "volume": [1000, 1200],
        "timestamp": [1, 2],
    })
    shape = response_shape(fake)
    assert shape["data_field_type"] == "TOP_LEVEL_ARRAYS"
    assert shape["payload_container"] == "top_level"
    assert shape["payload_keys"] == ["close", "high", "low", "open", "status", "timestamp", "volume"]
    assert shape["open_length"] == 2
    assert shape["timestamp_length"] == 2
    assert "100" not in str(shape)


def test_index_parser_accepts_valid_ohlc_without_volume():
    from datetime import datetime
    from zoneinfo import ZoneInfo

    timestamps = [
        int(datetime.fromisoformat("2023-05-11T10:00:00").replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp()),
        int(datetime.fromisoformat("2023-05-11T15:14:00").replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp()),
    ]
    fake = FakeResponse(200, {
        "open": [100.0, 101.0],
        "high": [101.0, 102.0],
        "low": [99.0, 100.0],
        "close": [100.5, 101.5],
        "timestamp": timestamps,
    })
    shape = response_shape(fake, "2023-05-11", require_volume=False)
    assert shape["parser_response_status"] == "PASS_RESPONSE"
    assert shape["target_anchor_ok"] is True
    assert shape["target_expiry_ok"] is True
    assert shape["target_anchor_time_ist"] == "10:00"
    assert shape["target_expiry_time_ist"] == "15:14"


def test_stock_parser_still_requires_valid_volume_when_checked():
    from datetime import datetime
    from zoneinfo import ZoneInfo

    timestamps = [
        int(datetime.fromisoformat("2023-05-11T10:00:00").replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp()),
        int(datetime.fromisoformat("2023-05-11T15:14:00").replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp()),
    ]
    fake = FakeResponse(200, {
        "open": [100.0, 101.0],
        "high": [101.0, 102.0],
        "low": [99.0, 100.0],
        "close": [100.5, 101.5],
        "volume": [],
        "timestamp": timestamps,
    })
    shape = response_shape(fake, "2023-05-11", require_volume=True)
    assert shape["parser_response_status"] == "INVALID_RESPONSE"
    assert shape["target_anchor_ok"] is False
    assert shape["target_expiry_ok"] is False
