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
BRANCH = os.environ.get("GITHUB_REF_NAME", "phase/constituent-weekly-outcomes-c2-panel")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "manual")
TEST_OUTCOME = os.environ.get("C2_TEST_OUTCOME", "unknown")
PANEL_OUTCOME = os.environ.get("C2_PANEL_OUTCOME", "unknown")
RESULTS = [
    "research/constituent_weekly/C2_PANEL_BUILD.json",
    "research/constituent_weekly/C2_PANEL_BUILD.md",
]
STATUS_PATH = "research/constituent_weekly/STATUS.md"
README_PATH = "README.md"
RESEARCH_LOG = "logs/RESEARCH_LOG.md"
ERROR_LOG = "logs/ERROR_LOG.md"
CONVERSATION_LOG = "logs/CONVERSATION_LOG.md"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check)


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


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="c2-panel-publish-") as tmp:
        snapshot = Path(tmp)
        for rel in RESULTS:
            source = ROOT / rel
            if source.is_file():
                shutil.copy2(source, snapshot / Path(rel).name)
        for attempt in range(1, 6):
            git("fetch", "origin", BRANCH)
            git("reset", "--hard", f"origin/{BRANCH}")
            for rel in RESULTS:
                source = snapshot / Path(rel).name
                destination = ROOT / rel
                if source.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                else:
                    destination.unlink(missing_ok=True)

            result = read_result()
            status = str(result.get("status", "NO_RESULT_ARTIFACT"))
            acceptance = result.get("acceptance", {})
            panel = result.get("panel", {})
            summary = (
                f"**Formal C2 panel run {RUN_ID}:** {status}; "
                f"{acceptance.get('scheduled_cycles', 0)} scheduled cycles; "
                f"{acceptance.get('valid_index_target_cycles', 0)} valid NIFTY targets "
                f"({acceptance.get('valid_index_target_fraction', 0):.2%}); "
                f"{acceptance.get('primary_eligible_cycles', 0)} cycles pass the 47/94% stock rule; "
                f"{panel.get('constituent_rows', 0)} constituent-cycle rows."
            )
            if status == "COMPLETED":
                summary += " Full panel stored in encrypted Actions cache; no model fitting in C2."
            else:
                summary += " C2 is not accepted; see the workflow run and error log."

            stamp = datetime.now(timezone.utc).isoformat()
            status_path = ROOT / STATUS_PATH
            status_text = status_path.read_text(encoding="utf-8") if status_path.exists() else "# Research Status\n"
            start, end = "<!-- BUP01_C2_PANEL_START -->", "<!-- BUP01_C2_PANEL_END -->"
            status_block = (
                f"{start}\n## Formal C2 panel update\n\n{summary}\n\n"
                "See [C2 panel report](C2_PANEL_BUILD.md) and [panel manifest](C2_PANEL_BUILD.json).\n"
                f"{end}"
            )
            status_path.parent.mkdir(parents=True, exist_ok=True)
            status_path.write_text(replace_block(status_text, start, end, status_block), encoding="utf-8")

            readme_path = ROOT / README_PATH
            if readme_path.exists():
                readme_text = readme_path.read_text(encoding="utf-8")
                readme_block = (
                    "<!-- BUP01_C2_PANEL_STATUS_START -->\n"
                    f"> **BUP-01 C2:** {summary} "
                    "[panel report](research/constituent_weekly/C2_PANEL_BUILD.md) · "
                    "[research status](research/constituent_weekly/STATUS.md)\n"
                    "<!-- BUP01_C2_PANEL_STATUS_END -->"
                )
                readme_path.write_text(
                    replace_block(readme_text, "<!-- BUP01_C2_PANEL_STATUS_START -->",
                                  "<!-- BUP01_C2_PANEL_STATUS_END -->", readme_block),
                    encoding="utf-8",
                )

            log_path = ROOT / RESEARCH_LOG
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Research Log\n"
            marker = f"<!-- C2_PANEL_RUN_{RUN_ID} -->"
            if marker not in log:
                log += (
                    f"\n\n{marker}\n## {stamp} — formal C2 panel run {RUN_ID}\n\n"
                    f"- Status: {status}.\n- Summary: {summary}\n"
                    f"- Input manifest: {result.get('input_manifest', {}).get('hash', 'not available')}.\n"
                    f"- Encrypted panel cache metadata: {result.get('encrypted_panel_cache', {})}.\n"
                    "- C2 is panel-only; stock models belong to C3 and index meta-models belong to C4.\n"
                )
                log_path.write_text(log, encoding="utf-8")

            error_path = ROOT / ERROR_LOG
            if status != "COMPLETED" or TEST_OUTCOME != "success" or PANEL_OUTCOME != "success":
                error_path.parent.mkdir(parents=True, exist_ok=True)
                error_log = error_path.read_text(encoding="utf-8") if error_path.exists() else "# Error Log\n"
                err_marker = f"<!-- C2_PANEL_ERROR_{RUN_ID} -->"
                if err_marker not in error_log:
                    error_log += (
                        f"\n\n{err_marker}\n## C2 panel workflow {RUN_ID} — {status}\n\n"
                        f"- Offline tests: {TEST_OUTCOME}; panel step: {PANEL_OUTCOME}.\n"
                        f"- Error category: {result.get('fatal_error_category', 'pre-panel workflow failure')}.\n"
                        f"- Source location: {result.get('fatal_error_location', {})}.\n"
                        "- No panel acceptance is claimed for this run.\n"
                    )
                    error_path.write_text(error_log, encoding="utf-8")

            conv_path = ROOT / CONVERSATION_LOG
            if conv_path.exists():
                conv = conv_path.read_text(encoding="utf-8")
                conv_marker = f"<!-- C2_PANEL_CONVERSATION_{RUN_ID} -->"
                if conv_marker not in conv:
                    conv += (
                        f"\n\n{conv_marker}\n## {stamp} — formal C2 panel run {RUN_ID}\n\n"
                        "- Formal panel-only workflow executed on the plan-defined C2 branch.\n"
                        f"- Offline tests: {TEST_OUTCOME}; panel step: {PANEL_OUTCOME}; result: {status}.\n"
                        "- The bundled pilot remains diagnostic only; C3/C4 model gates remain separate.\n"
                    )
                    conv_path.write_text(conv, encoding="utf-8")

            git("add", "-f", *RESULTS, STATUS_PATH, README_PATH, RESEARCH_LOG, ERROR_LOG, CONVERSATION_LOG, check=False)
            staged = git("diff", "--cached", "--quiet", check=False)
            if staged.returncode == 0:
                print(f"C2_PANEL_NO_CHANGES run={RUN_ID} status={status}")
                return 0
            git("config", "user.name", "github-actions[bot]")
            git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
            git("commit", "-m", f"Publish C2 panel run {RUN_ID}")
            pushed = git("push", "origin", f"HEAD:refs/heads/{BRANCH}", check=False)
            if pushed.returncode == 0:
                print(f"C2_PANEL_PUBLISH_SUCCESS run={RUN_ID} status={status}")
                return 0
            print(f"C2_PANEL_PUBLISH_RETRY {attempt}/5: {pushed.stderr[-500:]}")
            time.sleep(2)
        raise RuntimeError("Could not publish C2 panel result after five fetch-reset-publish attempts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
