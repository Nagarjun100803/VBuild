import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    verify: bool

    source_library_pds: str
    copy_library_pds: str
    load_library_pds: str
    symbolic_map_pds: str

    source_library_path: Path
    copy_library_path: Path
    symbolic_map_path: Path


def load_config_file() -> Config:
    project_root = Path(__file__).parents[3]
    config_file = project_root / "vbuild.toml"

    if not config_file.is_file():
        raise FileNotFoundError(
            "Error: No `vbuild.toml` is found in a project directory."
        )

    with open(config_file, "rb") as f:
        content = tomllib.load(f)
        zosmf = content["zosmf"]
        remote_datasets = content["remote_datasets"]
        local_files = content["local_files"]
        return Config(
            **zosmf,  # type: ignore
            **remote_datasets,
            **{key: Path(val).absolute() for key, val in local_files.items()},
        )


config = load_config_file()
