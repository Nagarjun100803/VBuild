import subprocess as sp
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class Commit(BaseModel):
    type: Literal["merge", "push"]
    hash_: str
    author: str
    date: str
    affected_files: list[tuple[str, Path]]
    message: str
    parents: tuple[str, str] | None = None


def get_last_merge() -> Commit | None:
    git_switch_to_dev_branch_cmd: sp.CompletedProcess = sp.run(
        args=["git", "switch", "dev"], check=False, capture_output=True, text=True
    )
    if git_switch_to_dev_branch_cmd.returncode != 0:
        print("Error occur while switching the branch to 'dev'")
        print(git_switch_to_dev_branch_cmd)
        return

    git_diff_cmd: sp.CompletedProcess = sp.run(
        args=["git", "diff", "--name-status", "HEAD^1", "HEAD^2"],
        text=True,
        capture_output=True,
        check=False,
    )
    if git_diff_cmd.returncode != 0:
        print("Error occur while performing 'git diff'.")
        print(git_diff_cmd)
        return

    git_diff_cmd_output: str = git_diff_cmd.stdout
    affected_files: list[tuple[str, Path]] = []
    for line in git_diff_cmd_output.splitlines():
        mode, filename = line.split("\t")
        affected_files.append((mode, Path(filename)))

    git_show_cmd: sp.CompletedProcess = sp.run(
        args=["git", "show", "HEAD"], text=True, check=False, capture_output=True
    )

    if git_show_cmd.returncode != 0:
        print("Error occur while performing 'git show HEAD'.")
        print(git_show_cmd)
        return

    git_show_cmd_output: str = git_show_cmd.stdout
    git_show_cmd_output_lines = git_show_cmd_output.splitlines()

    commit_hash = git_show_cmd_output_lines[0].split()[1]
    parents: tuple[str, str] = (
        git_show_cmd_output_lines[1].split()[1],
        git_show_cmd_output_lines[1].split()[2],
    )
    author = git_show_cmd_output_lines[2].split()[1]
    date = git_show_cmd_output_lines[3].split()[1]
    message = "\n".join(git_show_cmd_output_lines[4:])

    return Commit(
        hash_=commit_hash,
        parents=parents,
        author=author,
        date=date,
        message=message,
        affected_files=affected_files,
        type="merge",
    )
