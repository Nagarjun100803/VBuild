import typer

from src.vbuild.commands.compile import compile_app
from src.vbuild.commands.init import init_app
from src.vbuild.commands.run import run_app

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="[bold]VBuild[/], Our next generation build tool for mainframe applications.",
)

app.add_typer(init_app)
app.add_typer(compile_app)
app.add_typer(run_app)

if __name__ == "__main__":
    app()
