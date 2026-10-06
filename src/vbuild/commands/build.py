from collections import defaultdict, deque
from pathlib import Path

import typer
from rich.progress import (
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from src.vbuild.api.client import APIClient
from src.vbuild.utils._shared import SUCCESS_RETURN_CODES, get_jcl
from src.vbuild.utils.config import load_config_file
from src.vbuild.utils.meta import SourceFileMeta, load_files_metadata


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


@build_app.command(name="build")
def build():
    "Build the programs files"

    # NOTE Assume the target folder is scanned and metadata extracted by one method/service
    # and put it in the `.vbuild.meta.json` We use that file to build.

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

    with APIClient(host=config.host, port=config.port, verify=config.verify) as client:  # noqa: SIM117
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
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
    typer.echo(f"Build successful in {total_time_taken:.2f}s.🚀")
