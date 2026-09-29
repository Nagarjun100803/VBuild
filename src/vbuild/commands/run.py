from pathlib import Path
from typing import Annotated

import typer

from src.vbuild.api.client import APIClient
from src.vbuild.utils.cli import get_rich_toolkit
from src.vbuild.utils.config import config
from src.vbuild.utils.jcl_templates import RunCobolJCLTemplate

run_app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)


def _get_jcl(member_name: str) -> str:
    return RunCobolJCLTemplate(
        load_library_pds=config.load_library_pds, load_library_member=member_name
    ).get_jcl()


SUCCESS_RETURN_CODES = ("CC 0000", "CC 0004")


@run_app.command(name="run")
def run(file_path: Annotated[Path, typer.Argument(help="File path to run.")]):
    """Run the Cobol program."""
    toolkit = get_rich_toolkit()
    if not file_path.is_file():
        toolkit.print("No such file exist.")
        raise typer.Exit(1)

    member_name = file_path.stem.upper()
    jcl = _get_jcl(member_name)

    with APIClient() as client:  # noqa: SIM117
        with toolkit.progress("Running...", transient=True) as progress:
            with client.handle_http_error(progress):
                job = client.submit_job(jcl)

            # TODO: Need to handle TimeOutError.
            job_output = client.poll_job(job_name=job.job_name, job_id=job.job_id)
            if job_output.return_code in SUCCESS_RETURN_CODES:
                output_content = client.get_job_output(
                    job_name=job_output.job_name, job_id=job_output.job_id
                )
                toolkit.print(f"😀 Return Code: {job_output.return_code}")
                toolkit.print(f"[bold]{output_content}[/]")
            else:
                toolkit.print(f"😔 Return Code : {job_output.return_code}")
