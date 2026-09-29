from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from src.vbuild.api.client import APIClient
from src.vbuild.utils.cli import get_rich_toolkit
from src.vbuild.utils.config import config
from src.vbuild.utils.jcl_templates import (
    CompileBMSJClTemplate,
    CompileCICSCobolJCLTemplate,
    CompileCobolJCLTemplate,
)

compile_app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)


class SourceCodeType(StrEnum):
    cobol = "cobol"
    bms = "bms"
    cics = "cics"


def _get_jcl(source_code_type: SourceCodeType, member_name: str) -> str:
    match source_code_type:
        case SourceCodeType.cobol:
            return CompileCobolJCLTemplate(
                copy_library_pds=config.copy_library_pds,
                source_library_pds=config.source_library_pds,
                load_library_pds=config.load_library_pds,
                source_library_member=member_name,
            ).get_jcl()
        case SourceCodeType.cics:
            return CompileCICSCobolJCLTemplate(
                source_library_pds=config.source_library_pds,
                source_library_member=member_name,
                symbolic_map_pds=config.symbolic_map_pds,
            ).get_jcl()
        case SourceCodeType.bms:
            return CompileBMSJClTemplate(
                source_library_pds=config.source_library_pds,
                source_library_member=member_name,
                symbolic_map_pds=config.symbolic_map_pds,
            ).get_jcl()


def _read_symbolic_map(client: APIClient, member_name: str) -> str:
    return client.read_dataset(f"{config.symbolic_map_pds}({member_name})")


def _write_symbolic_map(member_name: str, content: str) -> None:
    with open(Path(config.symbolic_map_path) / f"{member_name.lower()}.cpy", "w") as f:
        f.write(content)


SUCCESS_RETURN_CODES = ("CC 0000", "CC 0004")


@compile_app.command(name="compile")
def compile(
    file_path: Annotated[Path, typer.Argument(help="File path to compile.")],
    source_code_type: Annotated[
        SourceCodeType,
        typer.Option("--source-code-type", "-sct", help="Source code type."),
    ] = SourceCodeType.cobol,
):
    """Compile Cobol/BMS/CICS programs."""
    toolkit = get_rich_toolkit()
    if not file_path.is_file():
        toolkit.print("No such file exist.")
        raise typer.Exit(1)

    source_code = file_path.read_text()
    member_name = file_path.stem.upper()

    jcl = _get_jcl(source_code_type, member_name)

    with get_rich_toolkit() as toolkit, APIClient() as client:  # noqa: SIM117
        with toolkit.progress("Compiling...", transient=True) as progress:
            with client.handle_http_error(progress):
                client.write_dataset(
                    f"{config.source_library_pds}({member_name})", content=source_code
                )
                job = client.submit_job(jcl)

            # TODO: Need to Handle TimeoutError.
            job_output = client.poll_job(job_name=job.job_name, job_id=job.job_id)
            toolkit.print(
                f"Return code: {job_output.return_code} ",
                emoji="😀" if job_output.return_code in SUCCESS_RETURN_CODES else "😔",
            )
            if (
                source_code_type == SourceCodeType.bms
                and job_output.return_code in SUCCESS_RETURN_CODES
            ):
                generated_symbolic_map = _read_symbolic_map(client, member_name)
                _write_symbolic_map(member_name, generated_symbolic_map)
