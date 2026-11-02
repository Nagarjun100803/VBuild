from pathlib import Path
from typing import Annotated

import rich
import typer

from vbuild.utils.project import get_project_root

init_app = typer.Typer(rich_markup_mode="rich")


config_template = """[zosmf]
host=
port=
verify=
user_id=

[remote_datasets]
source_library_pds=
copy_library_pds=
load_library_pds=

"""


@init_app.command(name="init")
def initialize(
    start: Annotated[
        Path | None, typer.Argument(help="Path to initialize the project.")
    ] = None,
):
    "Initialize the project configuration."
    project_root = get_project_root()
    if (project_root / "vbuild.toml").is_file():
        rich.print("'vbuild.toml' file already exists.")
    else:
        Path(project_root / "vbuild.toml").write_text(
            data=config_template,
            encoding="utf-8",
        )
        rich.print(
            "'vbuild.toml' file created, complete configuration and start building.🚀"
        )
