import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Annotated

import rich
import typer
from pydantic import BaseModel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from vbuild.api.client import APIClient
from vbuild.utils._shared import SUCCESS_RETURN_CODES, get_jcl
from vbuild.utils.authentication import resolve_credentials
from vbuild.utils.config import load_config_file, load_config_from_env
from vbuild.utils.diff import get_last_merge
from vbuild.utils.meta import SourceFileMeta, load_files_metadata
from vbuild.utils.project import get_project_root


class CircularDependencyError(Exception): ...


class ResolvedProgramFiles(BaseModel):
    copybooks: list[str]
    program_files: dict[str, SourceFileMeta]


def get_build_order(
    affected_program_files: set[Path] | None = None,
) -> ResolvedProgramFiles:
    """Returns the build order by performing topological sort using Kahn's algorithm."""

    # TODO Need to get affected files using commit hash. get all affected files.
    # - Bring all copy books. Take their dependencies first.
    # - Recursively get all their dependencies also.
    # - Solve it using kahn's algorithm.

    files_metadata = load_files_metadata()

    if affected_program_files:
        # Ignore copybook files from here. and only compile program files.
        copy_books: list[str] = []
        files_to_build: dict[str, SourceFileMeta] = {}

        for file in affected_program_files:
            if file.suffix == ".cpy":
                copy_books.append(file.as_posix())
            else:
                files_to_build.update(
                    {file.as_posix(): files_metadata.program_files[file.as_posix()]}
                )
    else:
        files_to_build = files_metadata.program_files
        copy_books = [Path(cp).as_posix() for cp in files_metadata.copy_books]

    dependency_map = defaultdict(list)

    # Initialize in-degree as 0 for all files.
    in_degree = {file_path: 0 for file_path in files_to_build}

    dependencies: set[tuple[str, str]] = set()
    for caller_file_path in files_to_build:
        for callee_file_metadata in files_to_build[caller_file_path].static_calls:
            dependencies.add((callee_file_metadata.path.as_posix(), caller_file_path))

    # Populate in-degree value.
    for callee_file, caller_file in dependencies:
        dependency_map[callee_file].append(caller_file)
        in_degree[caller_file] += 1

    # Initialize the queue with nodes has 0 in degree right now.
    queue = deque(
        file_path for file_path in files_to_build if in_degree[file_path] == 0
    )
    topological_order: list[str] = []

    while queue:
        top_node = queue.popleft()
        topological_order.append(top_node)

        for dependent_file in dependency_map[top_node]:
            in_degree[dependent_file] -= 1

            if in_degree[dependent_file] == 0:
                queue.append(dependent_file)

    if len(topological_order) != len(files_to_build):
        raise CircularDependencyError("Circular dependency exist.")

    return ResolvedProgramFiles(
        program_files={
            file_path: files_to_build[file_path] for file_path in topological_order
        },
        copybooks=copy_books,
    )


def get_affected_files_by_last_merge() -> ResolvedProgramFiles:

    commit = get_last_merge()
    if not commit:
        raise typer.Exit(1)

    project_root = get_project_root()

    files_metadata = load_files_metadata()

    affected_files = {project_root / file[1] for file in commit.affected_files}

    program_files: set[Path] = set()

    for file in affected_files:
        if file.suffix.lower() == ".cpy":
            program_files.add(file)
            # Add all copy book dependency program to build.
            program_files.update(
                (project_root / pf).resolve()
                for pf in files_metadata.copy_books[file.as_posix()]
            )
        elif file.suffix.lower() in (".cbl", ".asm"):
            program_files.add(file)
        else:
            print(f"Omitted file {file}.")

    return get_build_order(program_files)


build_app = typer.Typer(rich_markup_mode="rich")


@build_app.command(name="build")
def build_programs(
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch", "-b", help="Get latest merge from the branch to build."
        ),
    ] = None,
):
    credentials = resolve_credentials()

    if branch is not None:
        programs_to_build = get_affected_files_by_last_merge()
    else:
        programs_to_build = get_build_order()

    print("List of program files to build.")
    print("Copy books")
    print(programs_to_build.copybooks)
    print("Program files")
    print(programs_to_build.program_files)

    if not sys.stdin.isatty():
        config = load_config_from_env()
    else:
        rich.print(
            "Warning: Running pipeline build command in an interactive terminal."
        )
        config = load_config_file()

    with APIClient(  # noqa: SIM117
        host=config.host,
        port=config.port,
        verify=config.verify,
        auth=(credentials.username, credentials.password.get_secret_value()),
    ) as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            for copybook in programs_to_build.copybooks:
                content = Path(copybook).read_text(encoding="utf-8")
                client.write_dataset(
                    name=f"{config.copy_library_pds}({Path(copybook).stem.upper()})",
                    content=content,
                )
            task_id = progress.add_task(
                "Building...🛠️", total=len(programs_to_build.program_files)
            )
            for file_path in programs_to_build.program_files:
                file_path = Path(file_path)
                progress.update(
                    task_id,
                    description=f"Compiling {Path(*file_path.parts[-3:]).as_posix()}.",
                )
                jcl = get_jcl(
                    source_code_type=programs_to_build.program_files[
                        file_path.as_posix()
                    ].source_code_type,  # pyright: ignore[reportArgumentType]
                    # NOTE: Here it won't get .cpy file so I add pyright: ignore[reportArgumentType]
                    member_name=file_path.stem.upper(),
                    config=config,
                )
                source_code = file_path.read_text()

                client.write_dataset(
                    name=f"{config.source_library_pds}({file_path.stem.upper()})",
                    content=source_code,
                )

                job = client.submit_job(jcl)
                job_output = client.poll_job(job_id=job.job_id, job_name=job.job_name)

                if job_output.return_code in SUCCESS_RETURN_CODES:
                    progress.update(task_id, advance=1)
                else:
                    progress.stop()
                    typer.secho(
                        f"Build error occurred...😥\nError occurred while compiling {file_path} with rc {job_output.return_code}.",
                        err=True,
                    )
                    # TODO: Fetch spool for that particular job and display the error from mainframe.
                    raise typer.Exit(1)
            total_time_taken = progress.tasks[task_id].elapsed
    rich.print(f"Build successful in '{total_time_taken:.2f}s'.")
    rich.print("List of programs build.")
    for program in programs_to_build.program_files:
        rich.print(program)
