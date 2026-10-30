"""Combine verification, hash v3 artifacts, and package the branch snapshot."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def write(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    verification = json.loads((HERE / "verification.json").read_text())
    browser = json.loads((HERE / "browser_verification.json").read_text())
    verification["browser_ui"] = {
        "status": "PASS" if browser["pass"] else "FAIL",
        "browser": browser["browser"],
        "mode": browser["mode"],
        "checks": browser["checks"],
        "console_errors": browser["console_errors"],
        "remote_requests": browser["remote_requests"],
    }
    verification["overall_status"] = (
        "PASS" if verification["status"] == "PASS" and browser["pass"] else "FAIL"
    )
    write(HERE / "verification.json", verification)

    manifest = json.loads((HERE / "run_manifest.json").read_text())
    manifest["finalized_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["verification_status"] = verification["overall_status"]
    manifest["technical_verdict"] = (
        "VALIDATED" if verification["overall_status"] == "PASS" else "PARTIAL"
    )
    manifest["branch_parent_commit"] = "3fcd5ae"
    manifest["spike_lineage"] = (
        "Versioned sensitivity experiment descending from GSD spike 001; "
        "v3 was executed on its own Git branch."
    )
    files = sorted(
        p for p in HERE.iterdir()
        if p.is_file() and p.name != "run_manifest.json"
    )
    files += [
        ROOT / "DEFERENCE_GSD_SPIKE_PROMPT.md",
        ROOT / ".planning/spikes/MANIFEST.md",
        ROOT / ".planning/spikes/CONVENTIONS.md",
    ]
    files = sorted(files, key=lambda p: str(p.relative_to(ROOT)))
    manifest["sha256"] = {str(p.relative_to(ROOT)): digest(p) for p in files}
    write(HERE / "run_manifest.json", manifest)

    archive = ROOT / "v3_time_coupled_copying.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files + [HERE / "run_manifest.json"]:
            z.write(p, arcname=str(p.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt archive member: {bad}")
    print(json.dumps({
        "status": verification["overall_status"],
        "numerical_checks": len(verification["checks"]),
        "browser_checks": len(browser["checks"]),
        "archive": str(archive),
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": digest(archive),
    }, indent=2))


if __name__ == "__main__":
    main()
