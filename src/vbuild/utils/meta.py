import json
from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

import rich
import typer
from pydantic import BaseModel, ConfigDict, Field, model_validator

from vbuild.utils.jcls import SourceCodeType
from vbuild.utils.project import get_project_root


class StaticCallMeta(BaseModel):
    name: str
    path: Path

    # FIXME When we add static call dependencies we need to change the self.path resolve.
    # FIXME Cause we need to resolve it based on project_root.

    @model_validator(mode="after")
    def validate_path(self) -> Self:
        self.path = self.path.resolve()
        return self


class SourceFileMeta(BaseModel):
    source_code_type: SourceCodeType
    static_calls: list[StaticCallMeta] = Field(default_factory=list)
    has_dynamic_calls: bool = False
    load_type: Literal["batch", "online"]

    model_config = ConfigDict(extra="ignore")


class FilesMetadata(BaseModel):
    copy_books: dict[str, list[Path]]
    program_files: dict[str, SourceFileMeta]


@lru_cache(maxsize=1)
def load_files_metadata() -> FilesMetadata:
    """Loads the files metadata file defined from project root directory."""

    project_root = get_project_root()
    if not (project_root / ".vbuild.meta.json").is_file():
        rich.print("metadata file is missing.")
        raise typer.Exit(1)

    with open(project_root / ".vbuild.meta.json", "rb") as f:
        content = json.load(f)

    return FilesMetadata(
        program_files={
            (project_root / file_path).resolve().as_posix(): SourceFileMeta(**metadata)
            for file_path, metadata in content["program_files"].items()
        },
        copy_books={
            (project_root / copy_book).resolve().as_posix(): program_dependencies
            for (copy_book, program_dependencies) in content["copybook_files"].items()
        },
    )
