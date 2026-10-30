from functools import lru_cache
from pathlib import Path

import rich
import typer


@lru_cache(maxsize=1)
def get_project_root(start: Path | None = None) -> Path:
    "Recursively search for the project root directory by searching `.vbuild.meta.json` file."

    current = start or Path.cwd().resolve()

    for directory in (current, *current.parents):
        if (directory / ".vbuild.meta.json").is_file():
            # print(f"Project root found in {directory}.")
            return directory

    rich.print("Not inside a vbuild project.")
    raise typer.Exit(1)
