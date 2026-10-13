import subprocess
from pathlib import Path

from pydantic import BaseModel, Field


class FileChange(BaseModel):
    status: str
    filename: str


class Commit(BaseModel):
    hash: str
    author: str
    date: str
    message: str
    changes: list[FileChange] = Field(default_factory=list)

    @property
    def affected_files(self):
        return [Path(file.filename).resolve() for file in self.changes]


def get_last_commit() -> Commit:
    """Returns commit details"""

    try:
        commit_message = subprocess.run(
            [
                "git",
                "show",
                "--name-status",
                "--format=fuller",
                "HEAD",
            ],
            check=True,
            capture_output=True,
        ).stdout.decode("utf-8")
        lines = commit_message.splitlines()
        hash = lines[0].split(" ")[1]
        author = lines[1].removeprefix("Author:").strip()
        date = lines[2].removeprefix("AuthorDate:").strip()
        message = "\n".join(l.strip() for l in lines[5:] if l.startswith("    "))
        changes = []

        for l in lines[5:]:
            if l and l[0] in {"M", "A", "D", "R", "C", "U", "T"}:
                _, filename = l.split(l[0], maxsplit=1)
                changes.append(FileChange(status=l[0], filename=filename.strip()))

        return Commit(
            author=author, date=date, message=message, hash=hash, changes=changes
        )

    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise
