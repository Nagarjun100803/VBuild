from pathlib import Path
from typing import Annotated

import typer

from vbuild.api.client import APIClient
from vbuild.utils._shared import SUCCESS_RETURN_CODES, get_jcl
from vbuild.utils.authentication import resolve_credentials
from vbuild.utils.cli import get_rich_toolkit
from vbuild.utils.config import load_config_file
from vbuild.utils.jcls import SourceCodeType

compile_app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)


@compile_app.command(name="compile")
def compile(
    file_path: Annotated[Path, typer.Argument(help="File path to compile.")],
    source_code_type: Annotated[
        SourceCodeType,
        typer.Option("--source-code-type", "-sct", help="Source code type."),
    ],
):
    """Compile APA/APB/APC/ONL/BMS/ASM programs."""

    credentials = resolve_credentials()
    config = load_config_file()
    toolkit = get_rich_toolkit()

    if not file_path.is_file():
        toolkit.print("No such file exist.")
        raise typer.Exit(1)

    source_code = file_path.read_text()
    member_name = file_path.stem.upper()

    jcl = get_jcl(source_code_type, member_name, config)

    with (  # noqa: SIM117
        get_rich_toolkit() as toolkit,
        APIClient(
            host=config.host,
            port=config.port,
            verify=config.verify,
            auth=(credentials.username, credentials.password.get_secret_value()),
        ) as client,
    ):
        with toolkit.progress("Compiling...", transient=True) as progress:
            with client.handle_http_error(progress):
                client.write_dataset(
                    f"{config.source_library_pds}({member_name})", content=source_code
                )
                job = client.submit_job(jcl)

            # TODO: Need to Handle TimeoutError.
            job_output = client.poll_job(job_name=job.job_name, job_id=job.job_id)
            if job_output.return_code in SUCCESS_RETURN_CODES:
                toolkit.print(f"Return Code: {job_output.return_code}")
            else:
                logs = client.get_job_logs(
                    job_name=job_output.job_name, job_id=job_output.job_id
                )
                for log in logs:
                    print(logs[log])
