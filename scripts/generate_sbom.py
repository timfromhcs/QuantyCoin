#!/usr/bin/env python3
"""Generate a minimal CycloneDX-style SBOM + SHA256 manifest for QTY4 source.

Stdlib only. Scans tracked .py/.c/.h sources + spec/vectors, records
sha256, sizes, and pip freeze. Writes sbom/sbom.json + sbom/SHA256SUMS.
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "sbom"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, cwd=str(REPO)).stdout.strip()
    except Exception:
        commit = "unknown"
    try:
        freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                                capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:
        freeze = f"# pip freeze unavailable: {e}"

    exts = {".py", ".c", ".h", ".json", ".yml", ".yaml", ".sh", ".ps1"}
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "dist", "build",
                 "bitcoin knots reference don't push with repo in the end"}
    components = []
    sums = []
    for p in sorted(REPO.rglob("*")):
        if not p.is_file():
            continue
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.suffix.lower() not in exts:
            continue
        if OUT in p.parents:
            continue
        rel = p.relative_to(REPO).as_posix()
        digest = sha256_file(p)
        components.append({"name": rel, "sha256": digest, "size": p.stat().st_size})
        sums.append(f"{digest}  {rel}")

    sbom = {
        "bomFormat": "QuantyCoin-SBOM",
        "specVersion": "1.0",
        "project": "QuantyCoin-QTY4",
        "commit": commit,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "pip_freeze": freeze.splitlines(),
        "components": components,
    }
    (OUT / "sbom.json").write_text(json.dumps(sbom, indent=2), encoding="utf-8")
    (OUT / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"SBOM: {len(components)} components, commit {commit[:12]}")
    print(f"Wrote {OUT / 'sbom.json'} and {OUT / 'SHA256SUMS'}")


if __name__ == "__main__":
    main()
