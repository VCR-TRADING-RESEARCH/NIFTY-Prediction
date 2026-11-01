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
    assert "No data found" not in str(shape)
    assert "errorCode" in shape["top_level_keys"]


def test_response_shape_handles_successful_arrays_without_recording_values():
    fake = FakeResponse(200, {
        "status": "success",
        "data": {
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [1000, 1200],
            "start_Time": [1, 2],
        },
    })
    shape = response_shape(fake)
    assert shape["data_keys"] == ["close", "high", "low", "open", "start_Time", "volume"]
    assert shape["open_length"] == 2
    assert shape["start_Time_length"] == 2
    assert "100" not in str(shape)
