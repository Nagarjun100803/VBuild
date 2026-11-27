import re
from pathlib import Path

GREEN, RED, RESET = "\033[32m", "\033[31m", "\033[0m"
COBOL_SUFFIXES = {".cbl", ".cob", ".cobol"}

CHECKS = {
    "program_id_present": lambda src: re.search(r"\bPROGRAM-ID\b", src, re.IGNORECASE),
    "author_present": lambda src: re.search(r"\bAUTHOR\b", src, re.IGNORECASE),
}


def validate(path: Path) -> int:
    files = sorted(f for f in path.iterdir() if f.suffix.lower() in COBOL_SUFFIXES)
    if not files:
        print(f"{RED}FAILED{RESET} no COBOL source files found in {path}")
        return 1

    passed = failed = 0
    for f in files:
        src = f.read_text(encoding="utf-8", errors="ignore")
        for name, check in CHECKS.items():
            if check(src):
                passed += 1
                print(f"{f.name}::{name:<20} {GREEN}PASSED{RESET}")
            else:
                failed += 1
                print(f"{f.name}::{name:<20} {RED}FAILED{RESET}")

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0
