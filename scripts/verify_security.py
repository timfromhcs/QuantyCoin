"""
QuantyCoin Zero-Leak Pre-Push and Pre-Commit Security Scanner
Enforces strict secret isolation and detects forbidden patterns/credentials.
"""
import sys
import os
import re
import subprocess
from pathlib import Path

# Patterns indicating potential sensitive material
FORBIDDEN_NAME_PATTERNS = [
    r"quantysecrets",
    r"\.secret$",
    r"\.secrets$",
    r"\.private$",
    r"\.pem$",
    r"\.key$",
    r"\.priv$",
    r"\.wallet$",
    r"\.seed$",
    r"\.mnemonic$",
    r"_secret",
    r"_secrets",
    r"id_ed25519",
    r"id_rsa",
]

# Sensitive content signatures (regex)
FORBIDDEN_CONTENT_PATTERNS = [
    (r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "Private key marker"),
    (r"\bghp_[0-9a-zA-Z]{36}\b", "GitHub personal access token"),
    (r"\b(?:xprv|qprv)[0-9a-zA-Z]{100,}\b", "BIP32 Extended Private Key"),
    (r"CREATOR MASTER PRIVATE KEY", "Genesis Creator private key leak"),
    (r"24-WORD BIP39 MNEMONIC SEED", "Mnemonic seed header leak"),
    (r"QuantySecrets[\\/]", "QuantySecrets vault path reference in source"),
]

# Allowed files that may mention patterns purely for detection/documentation
WHITELISTED_FILES = {
    "AGENTS.md",
    "docs/agent/STATE.md",
    "docs/agent/NEXT_ACTIONS.md",
    "docs/agent/EVIDENCE.md",
    "docs/agent/FAILURES.md",
    "docs/agent/DECISIONS.md",
    "docs/agent/OPEN_QUESTIONS.md",
    "scripts/verify_security.py",
    "scripts/generate_and_verify_genesis.py",
    ".gitignore",
}

def scan_file_path(path_str: str) -> bool:
    clean_path = path_str.replace("\\", "/")
    # Ignore whitelisted directories/files
    for pattern in FORBIDDEN_NAME_PATTERNS:
        if re.search(pattern, clean_path, re.IGNORECASE):
            # Check if this exact file is whitelisted
            norm_name = Path(clean_path).name
            if clean_path in WHITELISTED_FILES or norm_name in WHITELISTED_FILES:
                continue
            print(f"[SECURITY ALERT] Forbidden file path detected: {clean_path} (matches {pattern})")
            return False
    return True

def scan_content(content: str, file_path: str) -> bool:
    clean_path = file_path.replace("\\", "/")
    if clean_path in WHITELISTED_FILES:
        return True

    for pattern, desc in FORBIDDEN_CONTENT_PATTERNS:
        if re.search(pattern, content):
            print(f"[SECURITY ALERT] Secret content pattern detected in {file_path}: {desc}")
            return False
    return True

def check_git_status() -> bool:
    passed = True
    try:
        # Get list of staged and unstaged modified files
        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        lines = res.stdout.strip().splitlines()
        for line in lines:
            if not line:
                continue
            status_code = line[:2]
            filename = line[3:].strip()
            if not scan_file_path(filename):
                passed = False

            if os.path.isfile(filename):
                try:
                    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if not scan_content(content, filename):
                        passed = False
                except Exception as e:
                    print(f"Warning: Could not read {filename}: {e}")
    except Exception as e:
        print(f"Error checking git status: {e}")
        return False

    return passed

def main():
    print("==================================================")
    print("QUANTYCOIN ZERO-LEAK SECURITY SCANNER")
    print("==================================================")
    clean = check_git_status()
    if clean:
        print("[PASS] No secrets, private credentials or forbidden files detected.")
        sys.exit(0)
    else:
        print("[FAIL] Security scan FAILED. Commit/Push blocked.")
        sys.exit(1)

if __name__ == "__main__":
    main()
