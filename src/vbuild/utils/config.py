import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import rich
import typer

from vbuild.utils.project import get_project_root


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    verify: bool
    user_id: str

    source_library_pds: str
    copy_library_pds: str
    load_library_pds: str
    # symbolic_map_pds: str

    source_library_path: Path
    # copy_library_path: Path
    # symbolic_map_path: Path

    @property
    def _username(self) -> str:
        return self.user_id.lower()


# TODO: Need to pass the toolkit here to handle json output option.


@lru_cache(maxsize=1)
def load_config_file() -> Config:
    """Loads local dev configuration file named `vbuild.toml` from project root directory."""

    project_root = get_project_root()

    if not (project_root / "vbuild.toml").is_file():
        rich.print(
            "Error: No `vbuild.toml` is found in a project directory. Run 'vbuild init' to initialize it.",
        )
        raise typer.Exit(1)

    with open(project_root / "vbuild.toml", "rb") as f:
        content = tomllib.load(f)
        zosmf = content["zosmf"]
        remote_datasets = content["remote_datasets"]
        local_files = content["local_files"]
        return Config(
            **zosmf,  # type: ignore
            **remote_datasets,
            **{key: Path(val).absolute() for key, val in local_files.items()},
        )
