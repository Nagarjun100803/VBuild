from typing import Literal

from vbuild.utils.config import Config
from vbuild.utils.jcls import (
    CompileAPAPrefixProgramJCLTemplate,
    CompileAPBPrefixProgramJCLTemplate,
    CompileAPCPrefixProgramJCLTemplate,
    CompileASMProgramJCLTemplate,
    CompileBMSProgramJCLTemplate,
    CompilePureCICSProgramJCLTemplate,
    JCLTemplate,
    SourceCodeType,
)

APP_NAME = "vbuild"

SUCCESS_RETURN_CODES = ("CC 0000", "CC 0004")


def get_jcl(
    source_code_type: SourceCodeType,
    member_name: str,
    load_type: Literal["batch", "online"],
    config: Config,
) -> str:

    if source_code_type not in SourceCodeType:
        raise ValueError(f"Invalid source code type {source_code_type}.")

    load_library_pds = (
        config.batch_load_library_pds
        if load_type == "batch"
        else config.online_load_library_pds
    )

    template_mapper: dict[str, JCLTemplate] = {
        SourceCodeType.APA_PREFIX: CompileAPAPrefixProgramJCLTemplate(
            source_library_pds=config.source_library_pds,
            source_library_member=member_name,
            load_library_pds=load_library_pds,
        ),
        SourceCodeType.APB_PREFIX: CompileAPBPrefixProgramJCLTemplate(
            source_library_pds=config.source_library_pds,
            source_library_member=member_name,
            load_library_pds=load_library_pds,
        ),
        SourceCodeType.APC_PREFIX: CompileAPCPrefixProgramJCLTemplate(
            source_library_pds=config.source_library_pds,
            source_library_member=member_name,
            load_library_pds=load_library_pds,
        ),
        SourceCodeType.ONL_ONLY: CompilePureCICSProgramJCLTemplate(
            source_library_pds=config.source_library_pds,
            source_library_member=member_name,
            load_library_pds=load_library_pds,
        ),
        SourceCodeType.BMS: CompileBMSProgramJCLTemplate(
            source_library_pds=config.source_library_pds,
            source_library_member=member_name,
            load_library_pds=load_library_pds,
        ),
        SourceCodeType.ASM: CompileASMProgramJCLTemplate(
            source_library_pds=config.source_library_pds,
            source_library_member=member_name,
            load_library_pds=load_library_pds,
        ),
    }

    return template_mapper[source_code_type].get_jcl()
