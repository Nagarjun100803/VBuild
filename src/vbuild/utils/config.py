import tomllib
from dataclasses import dataclass
from pathlib import Path

import rich
import typer


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    verify: bool
    user_id: str

    source_library_pds: str
    copy_library_pds: str
    load_library_pds: str
    symbolic_map_pds: str

    source_library_path: Path
    copy_library_path: Path
    symbolic_map_path: Path

    @property
    def _username(self) -> str:
        return self.user_id.lower()


# TODO: Need to pass the toolkit here to handle json output option.


def load_config_file(start: Path | None = None) -> Config:
    current = (start or Path.cwd()).resolve()

    target_directory: Path | None = None
    for directory in (current, *current.parents):
        if (directory / "vbuild.toml").is_file():
            target_directory = directory

    if target_directory is None:
        rich.print(
            "Error: No `vbuild.toml` is found in a project directory. Run 'vbuild init' to initialize it.",
        )
        raise typer.Exit(1)

    with open(target_directory / "vbuild.toml", "rb") as f:
        content = tomllib.load(f)
        zosmf = content["zosmf"]
        remote_datasets = content["remote_datasets"]
        local_files = content["local_files"]
        return Config(
            **zosmf,  # type: ignore
            **remote_datasets,
            **{key: Path(val).absolute() for key, val in local_files.items()},
        )
