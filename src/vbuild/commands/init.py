from pathlib import Path

import typer

from src.vbuild.utils.cli import get_rich_toolkit

init_app = typer.Typer(rich_markup_mode="rich")

project_root = Path(__file__).parents[3]
config_file = project_root / "vbuild.toml"


config_template = """[zosmf]
host=
port=
verify=
user_id=

[remote_datasets]
source_library_pds=
copy_library_pds=
symbolic_map_pds=
load_library_pds=

[local_files]
source_library_path
copy_library_path=
symbolic_map_path=
"""


def _create_config_file():
    with open(config_file, "w") as f:
        f.write(config_template)


@init_app.command(name="init")
def initialize():
    "Initialize the project configuration."
    toolkit = get_rich_toolkit()
    if config_file.is_file():
        toolkit.print("`vbuild.toml` file already exists.")
    else:
        _create_config_file()
        toolkit.print(
            "`vbuild.toml` file created, complete configuration and start building.🚀"
        )
