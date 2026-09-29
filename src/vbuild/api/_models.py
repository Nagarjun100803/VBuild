from typing import Annotated

from pydantic import BaseModel, Field

# Types
JobId = Annotated[str, Field(alias="jobid")]
JobName = Annotated[str, Field(alias="jobname")]
SubSystem = Annotated[str, Field(alias="subsystem")]
JobCorrelator = Annotated[str, Field(alias="job-correlator")]
Class = Annotated[str, Field(alias="class")]


class Job(BaseModel):
    owner: str
    phase: int
    sub_system: SubSystem
    phase_name: str = Field(alias="phase-name")
    job_correlator: JobCorrelator
    type: str
    url: str
    job_id: JobId
    class_: Class
    files_url: str = Field(alias="files-url")
    job_name: JobName
    status: str
    return_code: Annotated[str | None, Field(alias="retcode")]


class JobFile(BaseModel):
    id: int
    record_format: Annotated[str, Field(alias="recfm")]
    records_url: Annotated[str, Field(alias="records-url")]
    step_name: Annotated[str, Field(alias="stepname")]
    sub_system: SubSystem
    job_correlator: JobCorrelator
    byte_count: Annotated[int, Field(alias="byte-count")]
    logical_record_length: Annotated[int, Field(alias="lrecl")]
    job_id: JobId
    dd_name: Annotated[str, Field(alias="ddname")]
    record_count: Annotated[int, Field(alias="record-count")]
    class_: Class
    job_name: JobName
    procedure_step: Annotated[str | None, Field(alias="procstep")]
