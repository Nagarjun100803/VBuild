import logging
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel

from vbuild.api.client import APIClient
from vbuild.utils._shared import SUCCESS_RETURN_CODES, get_jcl
from vbuild.utils.authentication import resolve_credentials
from vbuild.utils.config import load_config_file, load_config_from_env
from vbuild.utils.diff import get_last_merge
from vbuild.utils.meta import SourceFileMeta, load_files_metadata
from vbuild.utils.project import get_project_root

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception): ...


class ResolvedProgramFiles(BaseModel):
    copybooks: list[str]
    program_files: dict[str, SourceFileMeta]


def get_build_order(
    affected_files: set[Path] | None = None,
) -> ResolvedProgramFiles:
    """Returns the build order by performing topological sort using Kahn's algorithm."""

    # TODO Need to get affected files using commit hash. get all affected files.
    # - Bring all copy books. Take their dependencies first.
    # - Recursively get all their dependencies also.
    # - Solve it using kahn's algorithm.

    logger.debug("Loading 'vbuild.meta.json' file to get dependency map.")
    files_metadata = load_files_metadata()

    if affected_files is not None:
        if len(affected_files) == 0:
            logger.info("No copybook or program file have changed.")
            return ResolvedProgramFiles(copybooks=[], program_files={})

        # NOTE: May be no program files will affect.
        # * In that scenario they just change metadata/readme.md file.

        # Ignore copybook files from here. and only compile program files.
        logger.info("Resolving dependency for affected files.")
        copy_books: list[str] = []
        files_to_build: dict[str, SourceFileMeta] = {}

        for file in affected_files:
            if file.suffix == ".cpy":
                copy_books.append(file.as_posix())
            else:
                files_to_build.update(
                    {file.as_posix(): files_metadata.program_files[file.as_posix()]}
                )
    else:
        logger.info("Resolving dependency.")
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
        logger.error(
            "Error: Failed to resolve the dependency, may be due to circular dependency!."
        )
        raise CircularDependencyError("Circular dependency exist.")

    logger.info("Dependencies resolved successfully.")
    return ResolvedProgramFiles(
        program_files={
            file_path: files_to_build[file_path] for file_path in topological_order
        },
        copybooks=copy_books,
    )


def get_affected_files_by_last_merge() -> ResolvedProgramFiles:

    logger.debug("Fetch latest merge.")
    commit = get_last_merge()
    if not commit:
        raise typer.Exit(1)

    project_root = get_project_root()

    files_metadata = load_files_metadata()

    changed_files = {project_root / file[1] for file in commit.affected_files}

    logger.debug("Files changed in the latest merge: ")
    for file in changed_files:
        logger.debug(f"'{_get_absolute_path(file.as_posix())}'")

    affected_files: set[Path] = set()

    for file in changed_files:
        if file.suffix.lower() == ".cpy":
            affected_files.add(file)
            # Add all copy book dependency program to build.
            affected_files.update(
                (project_root / pf).resolve()
                for pf in files_metadata.copy_books[file.as_posix()]
            )
        elif file.suffix.lower() in (".cbl", ".asm"):
            affected_files.add(file)
        else:
            # print(f"Omitted file {file}.")
            ...

    return get_build_order(affected_files)


build_app = typer.Typer(rich_markup_mode="rich")


def _get_absolute_path(path: Path | str) -> Path:
    project_root = get_project_root()
    return Path(path).relative_to(project_root)


@build_app.command(name="build")
def build_programs(
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch", "-b", help="Get latest merge from the branch to build."
        ),
    ] = None,
):
    """Build the program files."""

    credentials = resolve_credentials()

    if not sys.stdin.isatty():
        logger.debug("Loading config from env variables.")
        config = load_config_from_env()
    else:
        logger.warning(
            "Warning: Running pipeline build command in an interactive terminal."
        )
        config = load_config_file()

    if branch is not None:
        programs_to_build = get_affected_files_by_last_merge()
    else:
        programs_to_build = get_build_order()

    logger.info("Affected files are:")
    logger.info(
        "\n".join(f"'{_get_absolute_path(cp)}'" for cp in programs_to_build.copybooks)
    )
    logger.info(
        "\n".join(f"'{_get_absolute_path(p)}'" for p in programs_to_build.program_files)
    )

    with APIClient(
        host=config.host,
        port=config.port,
        verify=config.verify,
        auth=(credentials.username, credentials.password.get_secret_value()),
    ) as client:
        for copybook in programs_to_build.copybooks:
            logger.info(
                f"Sync copy book '{_get_absolute_path(copybook)}' to remote system."
            )
            content = Path(copybook).read_text(encoding="utf-8")
            client.write_dataset(
                name=f"{config.copy_library_pds}({Path(copybook).stem.upper()})",
                content=content,
            )

        logger.info("Building programs")
        for file_path in programs_to_build.program_files:
            logger.info(f"Building '{_get_absolute_path(file_path)}'")
            file_path = Path(file_path)
            metadata = programs_to_build.program_files[file_path.as_posix()]
            jcl = get_jcl(
                source_code_type=metadata.source_code_type,
                member_name=file_path.stem.upper(),
                config=config,
                load_type=metadata.load_type,
            )
            source_code = file_path.read_text()
            client.write_dataset(
                name=f"{config.source_library_pds}({file_path.stem.upper()})",
                content=source_code,
            )
            job = client.submit_job(jcl)
            job_output = client.poll_job(job_id=job.job_id, job_name=job.job_name)

            if job_output.return_code in SUCCESS_RETURN_CODES:
                logger.info(
                    f"'{_get_absolute_path(file_path)}' built successfully with return code: {job_output.return_code}."
                )
            else:
                logger.error(
                    f"Error occurs while building '{_get_absolute_path(file_path)}'."
                )
                logger.info("Fetch the error from the spool.")
                compile_listing = client.get_job_logs(
                    job_id=job_output.job_id, job_name=job_output.job_name
                )
                logger.info(compile_listing)
                raise typer.Exit(1)
