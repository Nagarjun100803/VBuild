import os
import sys
from typing import Literal

import keyring
import typer
from pydantic import BaseModel, SecretStr

from src.vbuild.utils.config import load_config_file

SERVICE_NAME = "vbuild"


class Credentials(BaseModel):
    username: str
    password: SecretStr
    type: Literal["os", "env"]


def resolve_credentials() -> Credentials:
    """Resolve the authenticated user credentials."""

    # NOTE: `user_id` field must be specified in `vbuild.toml` file for developer workflow and ci/cd automation.
    # * Only the password come from OS keyring or env variable[VBUILD_PASSWORD].
    # * Prefer keyring for secure local developer workflow and env for ci/cd automation.
    # * env works for both local developer workflow but not recommended.

    config = load_config_file()

    # 1. Priority for env variable.
    password_env = os.getenv("VBUILD_PASSWORD")

    if password_env:
        if sys.stdin.isatty():
            typer.echo("Warning: Using environment variables for local dev workflow.")
        return Credentials(
            username=config._username, password=SecretStr(password_env), type="env"
        )

    # 2. Fallback for os keyring.
    password = keyring.get_password(
        service_name=SERVICE_NAME, username=config._username
    )
    if not password:
        typer.echo("Error: Not authenticated, Run 'vbuild login'.")
        raise typer.Exit(1)

    return Credentials(
        username=config._username, password=SecretStr(password), type="os"
    )


def set_password(username: str, password: str) -> None:
    keyring.set_password(
        service_name=SERVICE_NAME, username=username, password=password
    )


def get_password(username: str) -> str | None:
    return keyring.get_password(service_name=SERVICE_NAME, username=username)


def delete_password(username: str) -> None:
    keyring.delete_password(service_name=SERVICE_NAME, username=username)
