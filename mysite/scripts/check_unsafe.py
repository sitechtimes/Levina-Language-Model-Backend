import subprocess
import sys


def run(*args):
    print("\n=== Running Ruff Format ===\n")
    format_result = subprocess.run(
        ["ruff", "format", "."],
        text=True,
    )

    if format_result.returncode != 0:
        print("Ruff format failed")
        sys.exit(format_result.returncode)

    print("\n=== Running Ruff Check (with fix and unsafe-fixes) ===\n")
    check_result = subprocess.run(
        ["ruff", "check", ".", "--fix", "--unsafe-fixes"],
        text=True,
    )

    if check_result.returncode != 0:
        print("Ruff check failed")
        sys.exit(check_result.returncode)

    print("\nFormatting and linting complete!\n")
