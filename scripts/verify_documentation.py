#!/usr/bin/env python3
"""
QuantyCoin Documentation & Link Integrity Validator
Validates markdown links, llms.txt, and CITATION.cff formatting.
"""
import os
import sys
import re
from pathlib import Path

def validate_markdown_links(repo_root: Path) -> int:
    md_files = []
    # Collect root markdown files
    for item in repo_root.iterdir():
        if item.is_file() and item.suffix == ".md":
            md_files.append(item)
    # Collect docs and .github markdown files
    for subdir in ["docs", ".github"]:
        target_dir = repo_root / subdir
        if target_dir.exists():
            for p in target_dir.rglob("*.md"):
                md_files.append(p)

    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    errors = 0
    total_checked = 0

    print(f"Scanning {len(md_files)} markdown files for link integrity...")
    for mdf in sorted(md_files):
        try:
            content = mdf.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[ERROR] Failed to read {mdf}: {e}")
            errors += 1
            continue

        links = link_pattern.findall(content)
        for text, link in links:
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            total_checked += 1
            clean_link = link.split("#")[0]
            if not clean_link:
                continue

            target = (mdf.parent / clean_link).resolve()
            if not target.exists():
                rel_source = mdf.relative_to(repo_root)
                print(f"[BROKEN LINK] in {rel_source}: {link} -> target not found ({clean_link})")
                errors += 1

    print(f"Validated {total_checked} local relative links across repository.")
    if errors == 0:
        print("[PASS] All markdown links resolve successfully.")
    else:
        print(f"[FAIL] Found {errors} broken link(s).")
    return errors

def validate_llms_txt(repo_root: Path) -> int:
    llms_file = repo_root / "llms.txt"
    if not llms_file.exists():
        print("[FAIL] llms.txt does not exist in repository root.")
        return 1
    content = llms_file.read_text(encoding="utf-8", errors="ignore")
    if "QuantyCoin" not in content or "SHA-256D" not in content:
        print("[FAIL] llms.txt missing expected project identifiers.")
        return 1
    print("[PASS] llms.txt validated.")
    return 0

def validate_citation(repo_root: Path) -> int:
    cff_file = repo_root / "CITATION.cff"
    if not cff_file.exists():
        print("[FAIL] CITATION.cff does not exist in repository root.")
        return 1
    content = cff_file.read_text(encoding="utf-8", errors="ignore")
    if "cff-version:" not in content or ("version: 4.0.0" not in content and "version: 3.0.0" not in content and "version: 2.0.0" not in content):
        print("[FAIL] CITATION.cff missing expected version (4.0.0).")
        return 1
    print("[PASS] CITATION.cff validated.")
    return 0

def main():
    repo_root = Path(__file__).resolve().parent.parent
    errors = 0
    errors += validate_markdown_links(repo_root)
    errors += validate_llms_txt(repo_root)
    errors += validate_citation(repo_root)

    if errors > 0:
        print(f"\n[FAIL] Documentation validation encountered {errors} error(s).")
        sys.exit(1)
    print("\n==================================================")
    print("ALL DOCUMENTATION VALIDATION CHECKS PASSED (100%)")
    print("==================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
