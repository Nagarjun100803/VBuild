from src.vbuild.utils.config import Config
from src.vbuild.utils.jcl_templates import (
    CompileBMSJClTemplate,
    CompileCICSCobolJCLTemplate,
    CompileCobolJCLTemplate,
)
from src.vbuild.utils.meta import SourceCodeType

SUCCESS_RETURN_CODES = ("CC 0000", "CC 0004")


def get_jcl(source_code_type: SourceCodeType, member_name: str, config: Config) -> str:
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
