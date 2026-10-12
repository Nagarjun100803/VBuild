import json
from enum import StrEnum
from pathlib import Path
from typing import Literal

import rich
import typer
from pydantic import BaseModel, Field


class SourceCodeType(StrEnum):
    cobol = "cobol"
    bms = "bms"
    cics = "cics"


class StaticCallMeta(BaseModel):
    name: str
    path: Path


class SourceFileMeta(BaseModel):
    source_code_type: SourceCodeType | Literal["cpy"]
    static_calls: list[StaticCallMeta] = Field(default_factory=list)
    has_dynamic_calls: bool = False


def load_files_metadata(start: Path | None = None) -> dict[str, SourceFileMeta]:
    current = (start or Path.cwd()).resolve()

    target_file: Path | None = None
    for directory in (current, *current.parents):
        metadata_file = directory / ".vbuild" / ".vbuild.meta.json"
        if metadata_file.is_file():
            target_file = metadata_file

    if target_file is None:
        rich.print("metadata file is missing.")
        raise typer.Exit(1)

    with open(target_file, "rb") as f:
        content = json.load(f)

    return {
        file_path: SourceFileMeta(**metadata)
        for file_path, metadata in content["program_files"].items()
    }
