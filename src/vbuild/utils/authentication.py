import keyring

SERVICE_NAME = "vbuild"


def set_password(username: str, password: str) -> None:
    keyring.set_password(
        service_name=SERVICE_NAME, username=username, password=password
    )


def get_password(username: str) -> str | None:
    return keyring.get_password(service_name=SERVICE_NAME, username=username)


def delete_password(username: str) -> None:
    keyring.delete_password(service_name=SERVICE_NAME, username=username)
