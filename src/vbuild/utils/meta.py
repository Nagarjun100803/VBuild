import json
from enum import StrEnum
from pathlib import Path
from typing import Literal

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


def load_files_metadata() -> dict[str, SourceFileMeta]:
    project_root = Path(__file__).parents[3]
    metadata_file = project_root / ".vbuild" / ".vbuild.meta.json"

    with open(metadata_file, "rb") as f:
        content = json.load(f)

    return {
        file_path: SourceFileMeta(**metadata)
        for file_path, metadata in content["program_files"].items()
    }
