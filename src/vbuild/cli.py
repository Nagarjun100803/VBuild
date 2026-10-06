import typer

from src.vbuild.commands import (
    auth_app,
    build_app,
    compile_app,
    init_app,
    run_app,
)

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="[bold]VBuild[/], Our next generation build tool for mainframe applications.",
)

app.add_typer(init_app)
app.add_typer(auth_app)
app.add_typer(compile_app)
app.add_typer(run_app)
app.add_typer(build_app)

if __name__ == "__main__":
    app()
