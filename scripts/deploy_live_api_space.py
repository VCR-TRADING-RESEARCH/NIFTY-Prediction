#!/usr/bin/env python3
"""Deploy the live inference API to a Hugging Face Docker Space.

GitHub Actions secrets are copied into Space runtime secrets by the Hugging Face
management API. They never enter the Space source files or GitHub Pages bundle.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import requests
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
SPACE_SLUG = "nifty-prediction-live-api"
PAGE_ORIGIN = "https://vcr-trading-research.github.io"


def need_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError("Required deployment configuration is missing: " + name)
    return value


def main() -> int:
    stage = "validating deployment configuration"
    try:
        hf_token = need_env("HF_TOKEN")
        dhan_client = need_env("DHAN_CLIENT_ID")
        dhan_pin = need_env("DHAN_PIN")
        dhan_totp = need_env("DHAN_TOTP_SECRET")
        api = HfApi(token=hf_token)
        stage = "checking Hugging Face token identity and permissions"

        explicit_id = os.getenv("HF_SPACE_ID", "").strip()
        if explicit_id:
            repo_id = explicit_id
            if "/" not in repo_id:
                raise RuntimeError("HF_SPACE_ID must have the format namespace/space-name.")
        else:
            identity = api.whoami()
            owner = str(identity.get("name", "")).strip()
            if not owner:
                raise RuntimeError("Hugging Face identity did not return an account namespace.")
            repo_id = owner + "/" + SPACE_SLUG

        stage = "creating or opening the Hugging Face Docker Space"
        with tempfile.TemporaryDirectory(prefix="nifty-live-api-") as tmp:
            stage = Path(tmp)
            shutil.copy2(ROOT / "live_api" / "app.py", stage / "app.py")
            shutil.copy2(ROOT / "live_api" / "Dockerfile", stage / "Dockerfile")
            shutil.copy2(ROOT / "live_api" / "requirements.txt", stage / "requirements.txt")
            shutil.copy2(ROOT / "scripts" / "research_core.py", stage / "research_core.py")
            for relative in (
                "data/reconciliation/nifty50_official_daily.csv",
                "data/reconciliation/expiry_verification.csv",
            ):
                destination = stage / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)

            api.create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="docker",
                private=False,
                exist_ok=True,
            )
            stage = "uploading backend source and research data to the Space"
            api.upload_folder(
                folder_path=str(stage),
                repo_id=repo_id,
                repo_type="space",
                commit_message="Deploy Dhan-backed NIFTY ExtraTrees inference API",
            )

        # Secrets are installed only as runtime settings, after source upload.
        stage = "installing Dhan credentials as Space runtime secrets"
        api.add_space_secret(repo_id=repo_id, key="DHAN_CLIENT_ID", value=dhan_client)
        api.add_space_secret(repo_id=repo_id, key="DHAN_PIN", value=dhan_pin)
        api.add_space_secret(repo_id=repo_id, key="DHAN_TOTP_SECRET", value=dhan_totp)
        api.add_space_secret(repo_id=repo_id, key="ALLOWED_ORIGIN", value=PAGE_ORIGIN)

        endpoint = "https://" + repo_id.replace("/", "-").lower() + ".hf.space"
        config_path = ROOT / "docs" / "assets" / "live-api-config.json"
        config_path.write_text(
            json.dumps({
                "api_base_url": endpoint,
                "status": "DEPLOYED_BY_GITHUB_ACTIONS",
                "space_id": repo_id,
                "health_path": "/health",
                "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        print("LIVE_API_SPACE_ID:", repo_id)
        print("LIVE_API_ENDPOINT:", endpoint)
        print("Dhan credentials were installed as private Space runtime secrets; values withheld.")

        # A new Space may need several minutes to build. Do not block publishing
        # the endpoint config forever; GitHub Pages reports service health at use.
        ready = False
        for _ in range(24):
            try:
                response = requests.get(endpoint + "/health", timeout=8)
                if response.ok:
                    body = response.json()
                    if body.get("status") == "ready":
                        ready = True
                        print("LIVE_API_HEALTH: ready")
                        break
            except Exception:
                pass
            time.sleep(15)
        if not ready:
            print("LIVE_API_HEALTH: Space created and endpoint published; startup is still warming or health check timed out.")
        return 0
    except Exception as exc:
        # Report only failed stage/status, never response body or secret values.
        status = getattr(getattr(exc, "response", None), "status_code", None)
        print("LIVE_API_DEPLOY_ERROR_STAGE:", stage, file=sys.stderr)
        print("LIVE_API_DEPLOY_ERROR_TYPE:", type(exc).__name__, file=sys.stderr)
        if status is not None:
            print("LIVE_API_DEPLOY_HTTP_STATUS:", int(status), file=sys.stderr)
        if status in (401, 403):
            print("ACTION_NEEDED: HF_TOKEN is unauthenticated or lacks permission to create/update Spaces or change Space secrets.", file=sys.stderr)
        elif status == 404:
            print("ACTION_NEEDED: Confirm the Hugging Face account/Space namespace and whether the repository exists.", file=sys.stderr)
        else:
            print("Check the failed deployment stage and GitHub Actions secret/variable names; secret values are withheld.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
