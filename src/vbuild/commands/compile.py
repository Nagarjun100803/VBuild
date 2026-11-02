import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.logging import RichHandler

from vbuild.api.client import APIClient
from vbuild.utils._shared import SUCCESS_RETURN_CODES, get_jcl
from vbuild.utils.authentication import resolve_credentials
from vbuild.utils.config import load_config_file
from vbuild.utils.jcls import SourceCodeType
from vbuild.utils.meta import load_files_metadata
from vbuild.utils.project import get_project_root

compile_app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)

logger = logging.getLogger("compiler")
logger.propagate = False


def set_up_logging(verbose: bool):
    """Setup the logger for compile command."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logger.handlers.clear()
    logger.setLevel(log_level)
    rich_handler = RichHandler(
        rich_tracebacks=True, show_path=False, show_time=False, show_level=False
    )
    logger.addHandler(rich_handler)


def write_job_logs(job_id: str, job_name: str, logs: dict[str, str]):
    """Write all the compile log in logs directory."""

    logs_folder = get_project_root() / "logs"

    # Create a folder inside of logs for this job.
    folder_naming_convention = (
        datetime.now(tz=UTC).strftime("%d-%m-%Y") + f"({job_id})-({job_name})"
    )
    target_folder = logs_folder / folder_naming_convention
    target_folder.mkdir(parents=True, exist_ok=True)

    for ddname, log in logs.items():
        with open(target_folder / ddname, "w") as f:
            f.write(log)

    logger.info(f"Logs written successfully in '{target_folder.as_posix()}' ")


@compile_app.command(name="compile")
def compile(
    file_path: Annotated[Path, typer.Argument(help="File path to compile.")],
    source_code_type: Annotated[
        SourceCodeType | None,
        typer.Option(
            "--source-code-type",
            "-sct",
            help="Source code type. If not provided, it will load from the metadata file.",
        ),
    ] = None,
    write_logs: Annotated[
        bool,
        typer.Option(
            "--write-logs",
            "-wl",
            help="Write logs to a file instead of displaying them in the terminal when compilation fails (return code > 4).",
        ),
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose output.")
    ] = False,
):
    """Compile APA/APB/APC/ONL/BMS/ASM programs."""

    set_up_logging(verbose=verbose)
    credentials = resolve_credentials()

    if not file_path.is_file():
        logger.error("No such file exist.")
        raise typer.Exit(1)

    target_source_code_type: SourceCodeType

    if source_code_type is None:
        logger.debug("Source code type is empty, loading from metadata file.")
        files_metadata = load_files_metadata().program_files

        file_metadata = files_metadata.get(file_path.resolve().as_posix(), None)
        if file_metadata is None:
            logger.error(f"No metadata for file {file_path.resolve().as_posix()}")
            raise typer.Exit(1)

        target_source_code_type = file_metadata.source_code_type

    else:
        target_source_code_type = source_code_type

    logger.debug(f"Target source code type is {target_source_code_type.value}")

    config = load_config_file()
    source_code = file_path.read_text()
    member_name = file_path.stem.upper()
    jcl = get_jcl(target_source_code_type, member_name, config)

    with APIClient(
        host=config.host,
        port=config.port,
        verify=config.verify,
        auth=(credentials.username, credentials.password.get_secret_value()),
    ) as client:
        logger.debug("Write source code to remote dataset.")
        client.write_dataset(
            f"{config.source_library_pds}({member_name})", content=source_code
        )
        logger.debug("Submit a job to compile.")
        job = client.submit_job(jcl)

        # TODO: Need to Handle TimeoutError.
        job_output = client.poll_job(job_name=job.job_name, job_id=job.job_id)
        if job_output.return_code in SUCCESS_RETURN_CODES:
            logger.info(f"Compilation success with {job_output.return_code}")
        else:
            logger.error(f"Compilation failed with {job_output.return_code}")
            logger.debug("Fetching spool logs.")
            logs = client.get_job_logs(
                job_id=job_output.job_id, job_name=job_output.job_name
            )
            if write_logs:
                write_job_logs(
                    job_name=job_output.job_name, job_id=job_output.job_id, logs=logs
                )
            else:
                for ddname, log in logs.items():
                    logger.info(ddname)
                    logger.info(log)
            raise typer.Exit(1)
