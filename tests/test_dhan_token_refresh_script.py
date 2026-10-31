from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "refresh_dhan_token.py"
SPEC = importlib.util.spec_from_file_location("refresh_dhan_token", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_token_refresh_uses_post_and_exports_only_to_github_env(monkeypatch, tmp_path, capsys):
    env_file = tmp_path / "github_env"
    monkeypatch.setenv("DHAN_CLIENT_ID", "test-client")
    monkeypatch.setenv("DHAN_PIN", "123456")
    monkeypatch.setenv("DHAN_TOTP_SECRET", "TEST_TOTP_SECRET")
    monkeypatch.setenv("GITHUB_ENV", str(env_file))
    monkeypatch.setattr(
        MODULE.pyotp,
        "TOTP",
        lambda secret: SimpleNamespace(now=lambda: "123456"),
    )

    captured = {}

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"accessToken": "x" * 48}

    def fake_post(url, *, params, timeout):
        captured.update(url=url, params=params, timeout=timeout)
        return Response()

    monkeypatch.setattr(MODULE.requests, "post", fake_post)

    assert MODULE.main() == 0
    output = capsys.readouterr().out
    exported = env_file.read_text(encoding="utf-8")

    assert captured["url"] == "https://auth.dhan.co/app/generateAccessToken"
    assert captured["params"] == {
        "dhanClientId": "test-client",
        "pin": "123456",
        "totp": "123456",
    }
    assert captured["timeout"] == 30
    assert "DHAN_JOB_ACCESS_TOKEN=" + "x" * 48 in exported
    mask_lines = [line for line in output.splitlines() if line.startswith("::add-mask::")]
    non_mask_lines = [line for line in output.splitlines() if not line.startswith("::add-mask::")]
    assert mask_lines == ["::add-mask::" + "x" * 48]
    assert "x" * 48 not in "\n".join(non_mask_lines)
    assert "TEST_TOTP_SECRET" not in output
    assert "123456" not in output


def test_token_refresh_fails_closed_on_http_error(monkeypatch, tmp_path, capsys):
    env_file = tmp_path / "github_env"
    monkeypatch.setenv("DHAN_CLIENT_ID", "test-client")
    monkeypatch.setenv("DHAN_PIN", "123456")
    monkeypatch.setenv("DHAN_TOTP_SECRET", "TEST_TOTP_SECRET")
    monkeypatch.setenv("GITHUB_ENV", str(env_file))
    monkeypatch.setattr(
        MODULE.pyotp,
        "TOTP",
        lambda secret: SimpleNamespace(now=lambda: "123456"),
    )

    class Response:
        ok = False
        status_code = 401

        @staticmethod
        def json():
            return {"error": "sensitive provider detail"}

    monkeypatch.setattr(MODULE.requests, "post", lambda *args, **kwargs: Response())

    assert MODULE.main() == 2
    output = capsys.readouterr().err
    assert "HTTP 401" in output
    assert "sensitive provider detail" not in output
    assert not env_file.exists()


def test_token_refresh_rejects_token_line_breaks(monkeypatch, tmp_path, capsys):
    env_file = tmp_path / "github_env"
    monkeypatch.setenv("DHAN_CLIENT_ID", "test-client")
    monkeypatch.setenv("DHAN_PIN", "123456")
    monkeypatch.setenv("DHAN_TOTP_SECRET", "TEST_TOTP_SECRET")
    monkeypatch.setenv("GITHUB_ENV", str(env_file))
    monkeypatch.setattr(
        MODULE.pyotp,
        "TOTP",
        lambda secret: SimpleNamespace(now=lambda: "123456"),
    )

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"accessToken": "x" * 30 + "\nBAD_ENV=1"}

    monkeypatch.setattr(MODULE.requests, "post", lambda *args, **kwargs: Response())

    assert MODULE.main() == 2
    output = capsys.readouterr().err
    assert "line breaks" in output
    assert not env_file.exists()
