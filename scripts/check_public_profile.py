#!/usr/bin/env python3
"""Validate the public profile without printing matched secret values."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".kdbx", ".sqlite", ".db"}
SENSITIVE_NAMES = {".env", "id_dsa", "id_ed25519", "id_rsa"}
PLACEHOLDER_PATH_USERS = {"user", "username", "example", "runner"}

SECRET_RULES = {
    "private key": re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "OpenAI API key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "private IPv4 address": re.compile(
        r"(?<![0-9.])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![0-9.])"
    ),
    "internal URL": re.compile(r"https?://[^\s)>\]]*(?:\.internal|\.lan|\.local)(?:[/:]|\b)", re.IGNORECASE),
}

LOCAL_PATH = re.compile(r"/home/([A-Za-z0-9._-]+)/")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\((https?://[^)\s]+)\)")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout


def tracked_files() -> list[Path]:
    output = git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    return [ROOT / item for item in output.split("\0") if item]


def scan_text(text: str) -> set[str]:
    findings = {name for name, pattern in SECRET_RULES.items() if pattern.search(text)}
    for match in LOCAL_PATH.finditer(text):
        if match.group(1).lower() not in PLACEHOLDER_PATH_USERS:
            findings.add("local home path")
    return findings


def scan_current_tree() -> list[str]:
    findings: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT)
        if path.name in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            findings.append(f"{relative}: sensitive filename")
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for rule in sorted(scan_text(text)):
            findings.append(f"{relative}: {rule}")
        merge_markers = ("<" * 7 + " ", "=" * 7 + "\n", ">" * 7 + " ")
        if any(marker in text for marker in merge_markers):
            findings.append(f"{relative}: unresolved merge marker")
    return findings


def scan_history() -> list[str]:
    findings: set[str] = set()
    blobs: dict[str, str] = {}
    for revision in git("rev-list", "--all").splitlines():
        for row in git("ls-tree", "-r", "--full-tree", revision).splitlines():
            metadata, path = row.split("\t", 1)
            blob = metadata.split()[2]
            blobs.setdefault(blob, path)

    for blob, path in blobs.items():
        data = subprocess.run(
            ["git", "cat-file", "blob", blob], cwd=ROOT, check=True, capture_output=True
        ).stdout
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for rule in scan_text(text):
            findings.add(f"history:{path}: {rule}")
    return sorted(findings)


def check_readme_contract() -> list[str]:
    text = README.read_text(encoding="utf-8")
    findings: list[str] = []
    required = (
        "# Markus Silvo",
        "## Avoin lähdekoodi",
        "## Yhteys",
        "<summary><strong>In English</strong></summary>",
        "### Open source",
        "### Contact",
    )
    for marker in required:
        if marker not in text:
            findings.append(f"README.md: missing required section: {marker}")
    if text.count("<details>") != text.count("</details>"):
        findings.append("README.md: unbalanced details element")
    return findings


def extract_links(text: str) -> list[str]:
    return sorted(set(MARKDOWN_LINK.findall(text)))


def check_link(url: str) -> tuple[bool, str]:
    headers = {"User-Agent": "Markus-web-profile-check/1.0"}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return 200 <= response.status < 400, str(response.status)
        except urllib.error.HTTPError as error:
            if error.code in {401, 403, 405, 429, 999}:
                if method == "HEAD" and error.code == 405:
                    continue
                return True, f"protected ({error.code})"
            if method == "HEAD":
                continue
            return False, str(error.code)
        except urllib.error.URLError as error:
            if method == "HEAD":
                continue
            return False, error.reason.__class__.__name__
    return False, "unreachable"


def check_links() -> list[str]:
    findings: list[str] = []
    for url in extract_links(README.read_text(encoding="utf-8")):
        ok, status = check_link(url)
        print(f"link {status}: {url}")
        if not ok:
            findings.append(f"README.md: broken link ({status}): {url}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true", help="scan all reachable Git blobs")
    parser.add_argument("--links", action="store_true", help="check external README links")
    args = parser.parse_args()

    findings = scan_current_tree() + check_readme_contract()
    if args.history:
        findings.extend(scan_history())
    if args.links:
        findings.extend(check_links())

    if findings:
        print("Public profile validation failed:", file=sys.stderr)
        for finding in sorted(set(findings)):
            print(f"- {finding}", file=sys.stderr)
        return 1

    print("Public profile validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
