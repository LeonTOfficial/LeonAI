#!/usr/bin/env python3
"""Release readiness checks for LEON AI.

The doctor is intentionally lightweight: it uses only the Python standard
library, so it can run locally and inside GitHub Actions before dependencies
or optional services such as Ollama are available.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ".env.example",
    ".github/workflows/test.yml",
    ".gitignore",
    "app.py",
    "config.py",
    "requirements.txt",
    "README.md",
    "SECURITY.md",
    "TESTING.md",
    "STRUKTUR.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "LICENSE",
]

REQUIRED_DIRS = [
    "docs/screenshots",
    "models",
    "routes",
    "scripts",
    "services",
    "static/js",
    "templates",
    "tests",
    "utils",
]

PUBLIC_DOCS = [
    "README.md",
    "SECURITY.md",
    "TESTING.md",
    "STRUKTUR.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
]

SENSITIVE_EXACT = {
    ".env",
    "data/chats.db",
    "data/logs/leon.log",
    "data/logs/server.out",
}

SENSITIVE_PREFIXES = (
    "data/",
    "backup/",
    "venv/",
    "env/",
    "ENV/",
)

SENSITIVE_SUFFIXES = (
    ".db",
    ".log",
    ".pyc",
    ".pyo",
)


@dataclass
class CheckResult:
    ok: bool
    message: str


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def ok(message: str) -> CheckResult:
    return CheckResult(True, message)


def fail(message: str) -> CheckResult:
    return CheckResult(False, message)


def warn(message: str) -> CheckResult:
    return CheckResult(True, f"Warning: {message}")


def run_git_ls_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def test_python_executable() -> str:
    mac_linux = ROOT / "venv" / "bin" / "python"
    windows = ROOT / "venv" / "Scripts" / "python.exe"
    if mac_linux.exists():
        return str(mac_linux)
    if windows.exists():
        return str(windows)
    return sys.executable


def is_sensitive_tracked(path: str) -> bool:
    if path in SENSITIVE_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in SENSITIVE_PREFIXES):
        return True
    if any(path.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        return True
    if "__pycache__/" in path or path.endswith(".DS_Store"):
        return True
    return False


def markdown_links(text: str) -> list[str]:
    image_links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    normal_links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)
    return image_links + normal_links


def is_external_link(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "#"))


def strip_anchor(link: str) -> str:
    return link.split("#", 1)[0]


def check_python_version() -> CheckResult:
    if sys.version_info < (3, 10):
        return fail("Python 3.10 or newer is required. Python 3.11/3.12 is recommended.")
    return ok(f"Python version looks good: {sys.version.split()[0]}")


def check_required_files() -> list[CheckResult]:
    results: list[CheckResult] = []
    for item in REQUIRED_FILES:
        path = ROOT / item
        results.append(ok(f"Found {item}") if path.is_file() else fail(f"Missing required file: {item}"))
    for item in REQUIRED_DIRS:
        path = ROOT / item
        results.append(ok(f"Found {item}/") if path.is_dir() else fail(f"Missing required folder: {item}/"))
    return results


def check_sensitive_git_files() -> CheckResult:
    tracked = run_git_ls_files()
    if not tracked:
        return warn("Could not inspect tracked files with git ls-files.")
    sensitive = [path for path in tracked if is_sensitive_tracked(path)]
    if sensitive:
        joined = ", ".join(sensitive[:12])
        suffix = " ..." if len(sensitive) > 12 else ""
        return fail(f"Sensitive runtime files are tracked by Git: {joined}{suffix}")
    return ok("No tracked runtime secrets, logs, databases, caches, or virtual environments found.")


def check_public_docs() -> list[CheckResult]:
    results: list[CheckResult] = []
    for doc in PUBLIC_DOCS:
        path = ROOT / doc
        if not path.exists():
            results.append(fail(f"Cannot check missing doc: {doc}"))
            continue
        text = path.read_text(encoding="utf-8")
        if "Mobile Documents/com~apple~CloudDocs" in text:
            results.append(fail(f"{doc} contains a private local iCloud path."))
        if doc == "README.md":
            if "https://github.com/LeonTOfficial/LeonAI-DE" not in text:
                results.append(fail("README.md does not link the German documentation repository."))
            if "README_SICHERHEIT" in text:
                results.append(fail("README.md still links the legacy README_SICHERHEIT bridge."))
            if "UPDATES.md" in text:
                results.append(fail("README.md should link CHANGELOG.md publicly, not UPDATES.md."))
        for link in markdown_links(text):
            clean = strip_anchor(link).strip()
            if not clean or is_external_link(clean):
                continue
            if not (ROOT / clean).exists():
                results.append(fail(f"{doc} has a broken local link: {link}"))
    if not any(not result.ok for result in results):
        results.append(ok("Public documentation links and release notes look consistent."))
    return results


def check_ci_workflows() -> list[CheckResult]:
    results: list[CheckResult] = []
    test_workflow = ROOT / ".github/workflows/test.yml"
    legacy_workflow = ROOT / ".github/workflows/main.yml"
    if not test_workflow.exists():
        results.append(fail("Missing .github/workflows/test.yml"))
    else:
        text = test_workflow.read_text(encoding="utf-8")
        for needle in (
            "python -m unittest discover -s tests -q",
            "node --check static/js/api.js",
            "python scripts/leon_doctor.py",
        ):
            if needle not in text:
                results.append(fail(f"CI workflow is missing: {needle}"))
    if legacy_workflow.exists():
        results.append(fail("Duplicate legacy workflow still exists: .github/workflows/main.yml"))
    if not any(not result.ok for result in results):
        results.append(ok("CI workflow is focused and includes tests, JS checks, and release doctor."))
    return results


def run_tests() -> CheckResult:
    python = test_python_executable()
    result = subprocess.run(
        [python, "-m", "unittest", "discover", "-s", "tests", "-q"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        return fail("Automated tests failed:\n" + result.stdout.strip())
    first_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "OK"
    return ok(f"Automated tests passed with {rel(Path(python)) if Path(python).is_relative_to(ROOT) else python}: {first_line}")


def collect_results(run_full_tests: bool) -> list[CheckResult]:
    results = [check_python_version()]
    results.extend(check_required_files())
    results.append(check_sensitive_git_files())
    results.extend(check_public_docs())
    results.extend(check_ci_workflows())
    if run_full_tests:
        results.append(run_tests())
    return results


def print_results(results: list[CheckResult]) -> None:
    print("LEON AI Release Doctor")
    print("=" * 22)
    for result in results:
        marker = "OK" if result.ok else "FAIL"
        print(f"[{marker}] {result.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether LEON AI is ready for a clean public release.")
    parser.add_argument("--run-tests", action="store_true", help="Also run the full Python unittest suite.")
    args = parser.parse_args()

    os.chdir(ROOT)
    results = collect_results(run_full_tests=args.run_tests)
    print_results(results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
