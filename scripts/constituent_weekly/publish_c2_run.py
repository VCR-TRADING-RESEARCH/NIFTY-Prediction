from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRANCH = os.environ.get("GITHUB_REF_NAME", "phase/constituent-weekly-outcomes-c2-models")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "manual")
TEST_OUTCOME = os.environ.get("C2_TEST_OUTCOME", "unknown")
MODEL_OUTCOME = os.environ.get("C2_MODEL_OUTCOME", "unknown")
RESULTS = [
    "research/constituent_weekly/C2_MODEL_RESULTS.json",
    "research/constituent_weekly/C2_MODEL_RESULTS.md",
    "research/constituent_weekly/C2_INDEX_OOF_FORECASTS.csv",
    "research/constituent_weekly/C2_STOCK_OOF_FORECASTS.csv",
    "research/constituent_weekly/C2_CYCLE_FEATURE_SUMMARIES.csv",
]
STATUS_PATH = "research/constituent_weekly/STATUS.md"
README_PATH = "README.md"
RESEARCH_LOG = "logs/RESEARCH_LOG.md"
ERROR_LOG = "logs/ERROR_LOG.md"
CONVERSATION_LOG = "logs/CONVERSATION_LOG.md"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=check
    )


def read_result() -> dict:
    path = ROOT / RESULTS[0]
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"status": "INVALID_RESULT_JSON"}
    return {"status": "NO_RESULT_ARTIFACT"}


def replace_block(text: str, start: str, end: str, block: str) -> str:
    if start in text and end in text:
        left = text.index(start)
        right = text.index(end, left) + len(end)
        return text[:left] + block + text[right:]
    return text.rstrip() + "\n\n" + block + "\n"


def restore_outputs(snapshot: Path) -> None:
    for rel in RESULTS:
        source = snapshot / Path(rel).name
        destination = ROOT / rel
        if source.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def snapshot_outputs(snapshot: Path) -> None:
    for rel in RESULTS:
        source = ROOT / rel
        if source.is_file():
            shutil.copy2(source, snapshot / Path(rel).name)


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="c2-publish-") as tmp:
        snapshot = Path(tmp)
        snapshot_outputs(snapshot)
        for attempt in range(1, 6):
            git("fetch", "origin", BRANCH)
            git("reset", "--hard", f"origin/{BRANCH}")
            restore_outputs(snapshot)
            result = read_result()
            model_status = str(result.get("status", "NO_RESULT_ARTIFACT"))
            panel = result.get("panel", {})
            summary = (
                f"**C2 latest run {RUN_ID}:** {model_status}; "
                f"{panel.get('primary_eligible_cycles', 0)} eligible cycles; "
                f"{panel.get('stock_oof_cycles', 0)} stock OOF cycles; "
                f"{panel.get('meta_oof_cycles', 0)} index meta OOF cycles."
            )
            if model_status == "COMPLETED_EXPLORATORY":
                summary += f" Final holdout results are in [C2 report](C2_MODEL_RESULTS.md)."
            else:
                summary += " No accepted forecast is claimed; see the workflow run and error log."

            stamp = datetime.now(timezone.utc).isoformat()
            status_file = ROOT / STATUS_PATH
            status_text = status_file.read_text(encoding="utf-8") if status_file.exists() else "# Research Status\n"
            start, end = "<!-- BUP01_C2_LATEST_START -->", "<!-- BUP01_C2_LATEST_END -->"
            status_block = (
                f"{start}\n## C2 modelling update\n\n{summary}\n\n"
                "See [C2 results](C2_MODEL_RESULTS.md) and [C2 machine results](C2_MODEL_RESULTS.json).\n"
                f"{end}"
            )
            status_file.parent.mkdir(parents=True, exist_ok=True)
            status_file.write_text(replace_block(status_text, start, end, status_block), encoding="utf-8")

            readme = ROOT / README_PATH
            if readme.exists():
                readme_text = readme.read_text(encoding="utf-8")
                readme_block = (
                    "<!-- BUP01_C2_STATUS_START -->\n"
                    f"> **BUP-01 C2 update:** {summary} "
                    "[C2 report](research/constituent_weekly/C2_MODEL_RESULTS.md) · "
                    "[C2 phase status](research/constituent_weekly/STATUS.md)\n"
                    "<!-- BUP01_C2_STATUS_END -->"
                )
                readme.write_text(
                    replace_block(readme_text, "<!-- BUP01_C2_STATUS_START -->",
                                  "<!-- BUP01_C2_STATUS_END -->", readme_block),
                    encoding="utf-8",
                )

            log_path = ROOT / RESEARCH_LOG
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Research Log\n"
            run_marker = f"<!-- C2_RESEARCH_RUN_{RUN_ID} -->"
            if run_marker not in log_text:
                metrics = result.get("index_models", {}).get("meta_models", {})
                log_text += (
                    f"\n\n{run_marker}\n## {stamp} — C2 automated run {RUN_ID}\n\n"
                    f"- Status: {model_status}.\n- Summary: {summary}\n"
                    f"- Dhan auth method: {result.get('auth_method', 'not recorded')}; "
                    f"token refresh: {result.get('token_refresh_status', 'not recorded')}.\n"
                    f"- Data acquisition: {result.get('data_acquisition', {})}.\n"
                    f"- NIFTY model metric keys: {list(metrics)}.\n"
                    "- Raw input values are retained only in the encrypted Actions cache; public outputs contain labels, probabilities and aggregate metrics.\n"
                )
                log_path.write_text(log_text, encoding="utf-8")

            error_path = ROOT / ERROR_LOG
            if model_status != "COMPLETED_EXPLORATORY" or TEST_OUTCOME != "success":
                error_path.parent.mkdir(parents=True, exist_ok=True)
                error_text = error_path.read_text(encoding="utf-8") if error_path.exists() else "# Error Log\n"
                error_marker = f"<!-- C2_ERROR_RUN_{RUN_ID} -->"
                if error_marker not in error_text:
                    error_text += (
                        f"\n\n{error_marker}\n## C2 run {RUN_ID} — {model_status}\n\n"
                        f"- Offline regression outcome: {TEST_OUTCOME}.\n"
                        f"- Model step outcome: {MODEL_OUTCOME}.\n"
                        f"- Error category: {result.get('fatal_error_category', 'pre-model workflow gate')}.\n"
                        f"- Failure location: {result.get('fatal_error_location', {})}.\n"
                        "- No model or strategy acceptance is claimed for this failed run.\n"
                    )
                    error_path.write_text(error_text, encoding="utf-8")

            conv_path = ROOT / CONVERSATION_LOG
            if conv_path.exists():
                conv_text = conv_path.read_text(encoding="utf-8")
                conv_marker = f"<!-- C2_CONVERSATION_RUN_{RUN_ID} -->"
                if conv_marker not in conv_text:
                    conv_text += (
                        f"\n\n{conv_marker}\n## {stamp} — C2 run {RUN_ID}\n\n"
                        "- User authorized progression to C2.\n"
                        f"- Offline tests: {TEST_OUTCOME}; model step: {MODEL_OUTCOME}; recorded result: {model_status}.\n"
                        "- Remaining C1 identity/action checks remain recorded limitations, not passed checks.\n"
                    )
                    conv_path.write_text(conv_text, encoding="utf-8")

            git("add", "-f", *RESULTS, STATUS_PATH, README_PATH, RESEARCH_LOG, ERROR_LOG, CONVERSATION_LOG, check=False)
            staged = git("diff", "--cached", "--quiet", check=False)
            if staged.returncode == 0:
                print(f"C2_PUBLISH_NO_CHANGES run={RUN_ID} result={model_status}")
                return 0
            git("config", "user.name", "github-actions[bot]")
            git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
            git("commit", "-m", f"Publish C2 research run {RUN_ID}")
            pushed = git("push", "origin", f"HEAD:refs/heads/{BRANCH}", check=False)
            if pushed.returncode == 0:
                print(f"C2_PUBLISH_SUCCESS run={RUN_ID} result={model_status}")
                return 0
            print(f"C2_PUBLISH_RETRY {attempt}/5: {pushed.stderr[-500:]}")
            time.sleep(2)
        raise RuntimeError("Could not publish C2 outputs after five fetch-reset-republish attempts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
