from collections.abc import Generator
from contextlib import contextmanager
from datetime import timedelta
from textwrap import dedent
from time import monotonic, sleep
from urllib.parse import quote

import httpx
import typer
from rich_toolkit.progress import Progress

from src.vbuild.api._models import Job, JobFile

POLL_TIMEOUT = timedelta(seconds=60)
POLL_INTERVAL = 1


class APIClient(httpx.Client):
    def __init__(
        self,
        host: str,
        port: int,
        verify: bool = False,
        auth: tuple[str, str] | None = None,
    ) -> None:
        super().__init__(
            base_url=f"https://{host}:{port}/zosmf",
            timeout=httpx.Timeout(5),
            headers={"X-CSRF-ZOSMF-HEADER": "*"},
            verify=verify,
            auth=auth or ("vrex006", "shiva"),  # TODO Need to come from OS Keyring.
        )

    @contextmanager
    def handle_http_error(
        self,
        progress: Progress,
    ) -> Generator[None]:

        try:
            yield
        except httpx.ReadTimeout:
            progress.set_error("Failed to connect `ZOSMF`, Please try again later.")
            raise typer.Exit(1)
        except httpx.HTTPError:  # TODO: Need to get the error and display it as json.
            progress.set_error("HTTP Error Occurred.")
            raise typer.Exit(1)

    def read_dataset(self, name: str) -> str:
        response = self.get(f"/restfiles/ds/{quote(name, safe='')}")
        response.raise_for_status()
        return response.text

    def write_dataset(self, name: str, content: str) -> None:
        response = self.put(
            f"/restfiles/ds/{quote(name, safe='')}",
            content=content,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "X-IBM-Data-Type": "text",
            },
        )
        response.raise_for_status()

    def _process_jcl(self, jcl: str) -> str:
        return dedent(jcl).strip().replace("\r\n", "\n")

    def submit_job(self, jcl: str) -> Job:
        jcl = self._process_jcl(jcl)
        response = self.put(
            url="/restjobs/jobs", content=jcl, headers={"Content-Type": "text/plain"}
        )
        response.raise_for_status()
        return Job.model_validate(response.json())

    def get_job(self, job_name: str, job_id: str) -> Job:
        response = self.get(
            f"/restjobs/jobs/{quote(job_name, safe='')}/{quote(job_id, safe='')}"
        )
        response.raise_for_status()
        return Job.model_validate(response.json())

    def get_job_files(self, job_name: str, job_id: str) -> list[JobFile]:
        response = self.get(
            f"/restjobs/jobs/{quote(job_name, safe='')}/{quote(job_id, safe='')}/files"
        )
        response.raise_for_status()
        return [JobFile.model_validate(file) for file in response.json()]

    def get_job_output(self, job_name: str, job_id: str) -> str:
        response = self.get(
            f"/restjobs/jobs/{quote(job_name, safe='')}/{quote(job_id, safe='')}/files/101/records"
        )
        response.raise_for_status()
        return response.text

    def poll_job(self, job_name: str, job_id: str) -> Job:
        start = monotonic()
        while True:
            if monotonic() - start > POLL_TIMEOUT.total_seconds():
                raise TimeoutError()
            job = self.get_job(job_id=job_id, job_name=job_name)
            if job.return_code:
                return job
            sleep(POLL_INTERVAL)
