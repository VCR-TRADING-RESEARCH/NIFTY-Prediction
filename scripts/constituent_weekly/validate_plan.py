from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "constituent_weekly"

REQUIRED_FILES = (
    "RESEARCH_PLAN.md",
    "LITERATURE_REVIEW.md",
    "DATA_SOURCE_REGISTER.md",
    "STATUS.md",
    "MANUSCRIPT_OUTLINE.md",
)
REQUIRED_PHASES = (
    "C0", "C1", "C2", "C3", "C4", "C5", "C6",
)
REQUIRED_PLAN_HEADINGS = (
    "## 2. Research questions",
    "## 3. Aim and objectives",
    "## 4. Frozen target and mathematical construction",
    "## 5. Data requirements and source hierarchy",
    "## 7. Bounded models and aggregation candidates",
    "## 8. Validation and statistics",
    "## 10. Phases, branches and gates",
    "## 11. Stop rules",
    "## 12. Final manuscript requirements",
)

def validate() -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (BASE / name).is_file():
            errors.append(f"Missing required research file: {name}")

    plan_path = BASE / "RESEARCH_PLAN.md"
    if plan_path.exists():
        plan = plan_path.read_text(encoding="utf-8")
        for heading in REQUIRED_PLAN_HEADINGS:
            if heading not in plan:
                errors.append(f"Missing plan section: {heading}")
        version_match = re.search(r"^\\*\\*Plan version:\\*\\* (\\d+\\.\\d+)\\s*$", plan, re.MULTILINE)
        if not version_match:
            errors.append("Plan version registration marker missing or malformed")
        else:
            registered_version = version_match.group(1)
            history_marker = f"- **v{registered_version} —"
            if history_marker not in plan:
                errors.append(f"Plan version {registered_version} has no matching version-history entry")
        for token in ("15:00 through 15:14 IST", "15:15 expiry proxy", "official 15:30 close"):
            if token not in plan:
                errors.append(f"Missing controlled expiry-target definition: {token}")
        for phase in REQUIRED_PHASES:
            if f"| {phase} —" not in plan:
                errors.append(f"Missing phase definition: {phase}")
        if "Pre-registered hypotheses" not in plan:
            errors.append("Pre-registered hypotheses section missing")
        for token in ("98%", "104", "20261031", "Paytm Money", "free-float"):
            if token not in plan:
                errors.append(f"Missing mandatory protocol item: {token}")

    status_path = BASE / "STATUS.md"
    if status_path.exists():
        status = status_path.read_text(encoding="utf-8")
        for phase in REQUIRED_PHASES:
            if f"{phase} —" not in status:
                errors.append(f"Missing phase status row: {phase}")
        if "No constituent panel" not in status:
            errors.append("Initial no-results disclosure missing from status")

    if errors:
        return errors

    report = [
        "# C0 Registration Validation",
        "",
        "Result: PASS",
        "",
        "Validated required plan, literature, source register, status and manuscript outline files.",
        "Checked research questions, objectives, formal target, data hierarchy, model scope, validation, stop rules, all seven phases, free-float coverage, minimum history, fixed bootstrap seed and transaction-cost requirements.",
        "",
        "This is a structural governance check only. It does not validate market data, historical constituents, stock prices, weights, models or trading performance.",
        "",
        "Run locally: python scripts/constituent_weekly/validate_plan.py",
    ]
    (BASE / "C0_VALIDATION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return []

def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("BUP-01 C0 registration structure: PASS")
    print("Important: empirical C1 data gate remains pending.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
