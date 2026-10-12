from pathlib import Path
from typing import Annotated

import rich
import typer

init_app = typer.Typer(rich_markup_mode="rich")


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
source_library_path=
copy_library_path=
symbolic_map_path=
"""


@init_app.command(name="init")
def initialize(
    start: Annotated[
        Path | None, typer.Argument(help="Path to initialize the project.")
    ] = None,
):
    "Initialize the project configuration."
    current_directory = (start or Path.cwd()).resolve()
    if (current_directory / "vbuild.toml").is_file():
        rich.print("'vbuild.toml' file already exists.")
    else:
        Path(current_directory / "vbuild.toml").write_text(
            data=config_template,
            encoding="utf-8",
        )
        rich.print(
            "'vbuild.toml' file created, complete configuration and start building.🚀"
        )
