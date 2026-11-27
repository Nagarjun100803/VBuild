import sys
from typing import Annotated

import rich
import typer

from vbuild.commands import (
    auth_app,
    build_app,
    compile_app,
    init_app,
    test_app,
)
from vbuild.logger import setup_logging

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="[bold]VBuild[/], Our next generation build tool for mainframe applications.",
)


def version_callback(value: bool) -> None:
    """Display the version and exit if value = True."""
    if value:
        from vbuild import __version__

        rich.print(f"VBuild CLI Version: {__version__}")
        raise typer.Exit(0)  # Early exit to avoid empty subcommand execution.


@app.callback()
def verbosity(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version", help="Show the version of vbuild.", callback=version_callback
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose output.")
    ] = False,
):
    if verbose:
        setup_logging(level="debug")
    else:
        setup_logging(level="info")


app.add_typer(init_app)
app.add_typer(auth_app)
app.add_typer(compile_app)
app.add_typer(build_app)
app.add_typer(test_app)


def compile_shortcut():
    "Shortcut for executing `vbuild compile` command."
    args = sys.argv[1:]
    verbose = False
    if "-v" in args:
        args.remove("-v")
        verbose = True
    if "--verbose" in args:
        args.remove("--verbose")
        verbose = True

    cli_args = ["compile", *args]
    if verbose:
        cli_args.insert(0, "--verbose")

    app(cli_args)


def main() -> None:
    """Main entry point of the vbuild cli."""
    app()
