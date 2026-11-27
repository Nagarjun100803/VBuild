import typer

from vbuild.utils.project import get_project_root
from vbuild.utils.test import validate

test_app = typer.Typer(rich_markup_mode="rich")


@test_app.command(name="test")
def validate_source_code():
    """Run sanity check on COBOL source code."""
    cobol_folder = get_project_root() / "cobol"
    raise typer.Exit(validate(cobol_folder))
