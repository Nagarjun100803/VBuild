from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import rich
import typer
from rich.progress import (
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from vbuild.api.client import APIClient
from vbuild.utils._shared import APP_NAME, SUCCESS_RETURN_CODES, get_jcl
from vbuild.utils.authentication import resolve_credentials
from vbuild.utils.config import load_config_file
from vbuild.utils.diff import Commit, get_last_commit
from vbuild.utils.meta import SourceFileMeta, load_files_metadata


class CircularDependencyError(Exception): ...


def get_build_order() -> dict[str, SourceFileMeta]:
    """Returns the build order by performing topological sort using Kahn's algorithm."""

    files_metadata = load_files_metadata()
    dependency_map = defaultdict(list)

    # Initialize in-degree as 0 for all files.
    in_degree = {file_path: 0 for file_path in files_metadata}

    dependencies: set[tuple[str, str]] = set()
    for caller_file_path in files_metadata:
        for callee_file_metadata in files_metadata[caller_file_path].static_calls:
            dependencies.add((callee_file_metadata.path.as_posix(), caller_file_path))

    # Populate in-degree value.
    for callee_file, caller_file in dependencies:
        dependency_map[callee_file].append(caller_file)
        in_degree[caller_file] += 1

    # Initialize the queue with nodes has 0 in degree right now.
    queue = deque(
        file_path for file_path in files_metadata if in_degree[file_path] == 0
    )
    topological_order: list[str] = []

    while queue:
        top_node = queue.popleft()
        topological_order.append(top_node)

        for dependent_file in dependency_map[top_node]:
            in_degree[dependent_file] -= 1

            if in_degree[dependent_file] == 0:
                queue.append(dependent_file)

    if len(topological_order) != len(files_metadata):
        raise CircularDependencyError("Circular dependency exist.")
    return {file_path: files_metadata[file_path] for file_path in topological_order}


build_app = typer.Typer(rich_markup_mode="rich")


def write_build_log(commit: Commit, elapsed_time: float):

    build_id = uuid4()
    current_datetime = datetime.now(tz=UTC)

    build_log_template = """
Build id: {build_id}
Build date: {build_date}
Elapsed time: {elapsed_time} seconds
Build status: {build_status}

Commit: {commit_hash}
Author: {commit_author}
Commit Date: {commit_date}
Description: {commit_description}

Number of files affected: {num_of_files_affected}
Files:
{affected_files}
    """.format(
        build_id=uuid4(),
        build_date=current_datetime,
        elapsed_time=elapsed_time,
        commit_hash=commit.hash,
        commit_description=commit.message,
        commit_author=commit.author,
        commit_date=commit.date,
        num_of_files_affected=len(commit.affected_files),
        build_status="Success",
        affected_files="\n".join(
            [
                f"{i}. {f.as_posix()}"
                for i, f in enumerate(commit.affected_files, start=1)
            ]
        ),
    )
    app_directory = Path(typer.get_app_dir(APP_NAME))
    naming_convention = f"{current_datetime.strftime('%d-%m-%Y')}-{str(build_id)[-6:]}"
    build_directory = app_directory / naming_convention
    build_directory.mkdir(exist_ok=True, parents=True)

    # Write the content.
    with open(build_directory / "log.txt", "w", encoding="utf-8") as f:
        f.write(build_log_template)


@build_app.command(name="build")
def build():
    "Build the programs files"

    # NOTE Assume the target folder is scanned and metadata extracted by one method/service
    # * and put it in the `.vbuild.meta.json` We use that file to build.

    credentials = resolve_credentials()

    config = load_config_file()
    all_program_files: dict[str, SourceFileMeta] = get_build_order()

    # Separate cobol files and cobol copybooks.
    copy_books: list[str] = []
    program_files: list[str] = []
    for file_path in all_program_files:
        if file_path.endswith(".cpy"):
            copy_books.append(file_path)
        else:
            program_files.append(file_path)

    with APIClient(
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
            for copy_book in copy_books:
                content = Path(copy_book).read_text(encoding="utf-8")
                client.write_dataset(
                    name=f"{config.copy_library_pds}({Path(copy_book).stem.upper()})",
                    content=content,
                )
            task_id = progress.add_task("Building...🛠️", total=len(program_files))
            for file_path in program_files:
                file_path = Path(file_path)
                progress.update(
                    task_id,
                    description=f"Compiling {Path(*file_path.parts[-3:]).as_posix()}.",
                )
                jcl = get_jcl(
                    source_code_type=all_program_files[
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
        write_build_log(get_last_commit(), elapsed_time=total_time_taken)  # pyright: ignore[reportArgumentType]
    rich.print(f"Build successful in {total_time_taken:.2f}s.")
