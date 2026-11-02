import os
import tomllib
from dataclasses import dataclass
from functools import lru_cache

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
    batch_load_library_pds: str
    online_load_library_pds: str

    # symbolic_map_pds: str

    # source_library_path: Path
    # copy_library_path: Path
    # symbolic_map_path: Path

    @property
    def _username(self) -> str:
        return self.user_id.lower()


# TODO: Need to pass the toolkit here to handle json output option.


def load_config_from_env() -> Config:
    """Load configuration from env variable for CI/CD orchestration."""

    env_names = {
        "host": "ZOSMF_HOST",
        "port": "ZOSMF_PORT",
        "verify": "ZOSMF_VERIFY",
        "source_library_pds": "SRCLIB",
        "copy_library_pds": "COPYLIB",
        "batch_load_library_pds": "BATCH_LOADLIB",
        "online_load_library_pds": "ONLINE_LOADLIB",
    }

    config = {
        "host": os.getenv("ZOSMF_HOST"),
        "port": os.getenv("ZOSMF_PORT"),
        "verify": os.getenv("ZOSMF_VERIFY", None) or False,
        "source_library_pds": os.getenv("SRCLIB"),
        "copy_library_pds": os.getenv("COPYLIB"),
        "batch_load_library_pds": os.getenv("BATCH_LOADLIB"),
        "online_load_library_pds": os.getenv("ONLINE_LOADLIB"),
    }

    missing_env = [env_names[env] for env in config if config[env] is None]
    if missing_env:
        print(f"Missing env variables {missing_env}.")
        raise typer.Exit(1)

    return Config(
        **config, user_id=""
    )  # NOTE: Set user_id as empty string. will set by resolve_credentials in build.


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
        return Config(
            **zosmf,  # type: ignore
            **remote_datasets,
        )
