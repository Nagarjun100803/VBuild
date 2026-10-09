import typer
from keyring.errors import PasswordDeleteError

from src.vbuild.api.client import APIClient
from src.vbuild.utils.authentication import (
    delete_password,
    get_password,
    resolve_credentials,
    set_password,
)
from src.vbuild.utils.config import Config, load_config_file

auth_app = typer.Typer(rich_markup_mode="rich")


def _is_valid_cred(username: str, password: str, config: Config) -> bool:
    """Returns `True` if the given credentials are valid else `False`."""
    with APIClient(
        host=config.host,
        port=config.port,
        verify=config.verify,
        auth=(username, password),
    ) as client:
        response = client.get("/restjobs/jobs", params={"max_jobs": 1})
        return response.status_code == 200


@auth_app.command(name="login")
def login():
    """Login to the system."""

    config = load_config_file()
    existing_password = get_password(username=config._username)
    if existing_password:
        typer.echo("Already logged in.")
        want_to_login_as_different_user = typer.confirm(
            "Want to login as different user"
        )
        if want_to_login_as_different_user:
            typer.echo(
                "Follow the steps to login as different user.\n"
                "1.Change the [bold]user_id[/] field in [bold]vbuild.toml[/]\n"
                "2.Run [bold]vbuild logout[/]\n"
                "3.Run [bold]vbuild login[/]"
            )
        raise typer.Exit(0)

    typer.echo(f"Logging in as [bold]{config.user_id}[/]")
    password: str = typer.prompt("Password", hide_input=True)
    if _is_valid_cred(config._username, password, config):
        set_password(config._username, password)
        del password  # Remove from the memory.
        typer.echo("Login success.🚀")
    else:
        typer.echo("Invalid user_id or password.")


@auth_app.command(name="logout")
def logout():
    """Logout from the system."""

    config = load_config_file()
    try:
        delete_password(config._username)
    except PasswordDeleteError:
        ...
    typer.echo("Logged out.")


@auth_app.command(name="ping")
def ping():
    """If the server is reachable, it responds with [bold]pong[/]."""

    config = load_config_file()
    credentials = resolve_credentials()
    if credentials.type == "env" and not _is_valid_cred(
        username=credentials.username,
        password=credentials.password.get_secret_value(),
        config=config,
    ):
        typer.echo("Invalid credentials.")
    else:
        typer.echo("pong")
