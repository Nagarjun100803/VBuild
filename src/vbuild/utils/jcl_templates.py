from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, kw_only=True)
class JCLTemplate(Protocol):
    def get_jcl(self) -> str:
        """Returns the formatted `JCL` that are ready to submit."""
        ...


@dataclass(frozen=True, kw_only=True)
class CompileCobolJCLTemplate(JCLTemplate):
    copy_library_pds: str
    source_library_pds: str
    source_library_member: str
    load_library_pds: str

    def get_jcl(self) -> str:
        return """
        //COMPCOB JOB REGION=0M,NOTIFY=&SYSUID,COND=(4,LT),TIME=2
        //**********************************************************************
        //*                           INPUT AREA                               *
        //**********************************************************************
        //  SET MEMBER={source_library_member}                 <== YOUR MEMBER NAME
        //  SET SOURCE={source_library_pds}            <== YOUR COBOL LIBRARY
        //  SET COPYLIB={copy_library_pds}             <== YOUR COPY LIBRARY
        //  SET LOADLIB={load_library_pds}             <== YOUR LOAD LIBRARY
        //  SET LNGPRFX='IGY640'
        //  SET LIBPRFX='CEE'
        //**********************************************************************
        //*                   COMPILE THE COBOL PROGRAM                        *
        //**********************************************************************
        //COBCOMP EXEC PGM=IGYCRCTL,REGION=0M,PARM='DYNAM'
        //STEPLIB  DD  DSNAME=&LNGPRFX..SIGYCOMP,DISP=SHR
        //         DD  DSNAME=&LIBPRFX..SCEERUN,DISP=SHR
        //         DD  DSNAME=&LIBPRFX..SCEERUN2,DISP=SHR
        //SYSIN    DD  DSNAME=&SOURCE(&MEMBER),DISP=SHR
        //SYSLIB   DD  DSNAME=&COPYLIB,DISP=SHR
        //SYSPRINT DD  SYSOUT=*
        //SYSLIN   DD  DSNAME=&&LOADSET,UNIT=SYSALLDA,
        //             DISP=(MOD,PASS),SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT1   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT2   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT3   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT4   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT5   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT6   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT7   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT8   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT9   DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT10  DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT11  DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT12  DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT13  DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT14  DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSUT15  DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //SYSMDECK DD  UNIT=SYSALLDA,SPACE=(CYL,(1,1)),VOL=(,,,1)
        //**********************************************************************
        //*                   LINK EDIT THE COBOL PROGRAM                      *
        //**********************************************************************
        //LINKEDIT EXEC PGM=IEWL,COND=(4,LT,COBCOMP)
        //SYSLIB   DD  DSNAME=&LIBPRFX..SCEELKEX,DISP=SHR
        //         DD  DSNAME=&LIBPRFX..SCEELKED,DISP=SHR
        //SYSLIN   DD DSN=&&LOADSET,DISP=(OLD,DELETE)
        //         DD DDNAME=SYSIN
        //SYSLMOD  DD DISP=SHR,DSN=&LOADLIB(&MEMBER)
        //SYSPRINT DD SYSOUT=*
        //SYSUDUMP DD SYSOUT=*
        //SYSUT1   DD SPACE=(1043,(50,50)),UNIT=SYSDA
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class RunCobolJCLTemplate(JCLTemplate):
    load_library_pds: str
    load_library_member: str

    def get_jcl(self) -> str:
        return """
        //RUNCOB JOB NOTIFY=&SYSUID,TIME=2
        //*
        //* RUN COBOL PROGRAM
        //*
        //STEP1    EXEC PGM={load_library_member}      <== YOUR LOAD LIBRARY
        //STEPLIB  DD DISP=SHR,DSN={load_library_pds}  <== YOUR PROGRAM
        //SYSOUT   DD SYSOUT=*
        //OUTDD    DD SYSOUT=*
        //*
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class CompileCICSCobolJCLTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    symbolic_map_pds: str

    def get_jcl(self) -> str:
        return """
        //COMPCICS JOB REGION=0M,NOTIFY=&SYSUID
        //*---------------------------------------------------------------------
        //  SET  SRCLIB={source_library_pds}
        //  SET  MEMBER={source_library_member}
        //  SET  SYMMAP={symbolic_map_pds}
        //*---------------------------------------------------------------------
        //*
        //  SET  SUFFIX='1$'
        //  SET  INDEX='DFH610.CICS'         QUALIFIER(S) FOR CICS LIBRARIES
        //  SET  COMPHLQ='IGY640'            QUALIFIER(S) FOR COBOL COMPILER
        //  SET  REG=2M                      REGION SIZE FOR ALL STEPS
        //  SET  LNKPARM='LIST,XREF'         LINK EDIT PARAMETERS
        //  SET  STUB='DFHEILIC'             LINK EDIT INCLUDE FOR DFHECI
        //  SET  LIB='SDFHCOB'               LIBRARY
        //  SET  WORK='SYDA'                 UNIT FOR WORK DATASETS
        //*---------------------------------------------------------------------
        //*      THIS PROCEDURE CONTAINS 4 STEPS
        //*      1.   EXEC THE COBOL TRANSLATOR
        //*           (USING THE SUPPLIED SUFFIX 1$)
        //*      2.   EXEC THE VS COBOL II COMPILER
        //*      3.   REBLOCK &LIB(&STUB) FOR USE BY THE LINKEDIT STEP
        //*      4.   LINKEDIT THE OUTPUT INTO DATASET &PROGLIB
        //*---------------------------------------------------------------------
        //* PRECOMPILER STEP
        //PRCOM  EXEC PGM=DFHECP1$
        //STEPLIB  DD DSN=&INDEX..SDFHLOAD,DISP=SHR
        //SYSPRINT DD SYSOUT=*
        //SYSIN    DD DSN=&SRCLIB(&MEMBER),DISP=SHR
        //SYSPUNCH DD DSN=&&SYSCIN,
        //            DISP=(,PASS),SPACE=(TRK,(5,5))
        //* COMPILER STEP
        //COMP   EXEC PGM=IGYCRCTL,REGION=&REG
        //STEPLIB  DD DSN=&COMPHLQ..SIGYCOMP,DISP=SHR
        //SYSLIB   DD DSN=&INDEX..SDFHCOB,DISP=SHR
        //         DD DSN=&INDEX..SDFHMAC,DISP=SHR
        //         DD DSN=&INDEX..SDFHSAMP,DISP=SHR
        //         DD DSN=&INDEX..SDFHPARM,DISP=SHR
        //         DD DSN=&SYMMAP,DISP=SHR
        //SYSPRINT DD SYSOUT=*
        //SYSIN    DD DSN=&&SYSCIN,DISP=(OLD,DELETE)
        //SYSLIN   DD DSN=&&LOADSET,DISP=(MOD,PASS),
        //            UNIT=&WORK,SPACE=(80,(250,100))
        //SYSMDECK DD DSN=&&OBJ,
        //             DISP=(MOD,PASS),
        //             UNIT=SYSDA,
        //             SPACE=(TRK,(5,5)),
        //             DCB=(RECFM=FB,LRECL=80)
        //SYSUT1   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT2   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT3   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT4   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT5   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT6   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT7   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT8   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT9   DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT10  DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT11  DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT12  DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT13  DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT14  DD UNIT=&WORK,SPACE=(460,(350,100))
        //SYSUT15  DD UNIT=&WORK,SPACE=(460,(350,100))
        //*
        //COPYLINK EXEC PGM=IEBGENER,COND=(7,LT,COMP)
        //SYSUT1   DD DSN=&INDEX..&LIB(&STUB),DISP=SHR
        //SYSUT2   DD DSN=&&COPYLINK,DISP=(NEW,PASS),
        //            DCB=(LRECL=80,BLKSIZE=400,RECFM=FB),
        //            UNIT=&WORK,SPACE=(400,(20,20))
        //SYSPRINT DD SYSOUT=*
        //SYSIN    DD DUMMY
        //*
        //LKED     EXEC PGM=IEWL,REGION=&REG,
        //            PARM='&LNKPARM',COND=(5,LT,COMP)
        //SYSLIB   DD DSN=&INDEX..SDFHLOAD,DISP=SHR
        //         DD DSN=CEE.SCEELKED,DISP=SHR
        //         DD DSN=TCPIP.SEZATCP,DISP=SHR
        //         DD DSN=IGY640.AIGYMOD1,DISP=SHR
        //SYSUT1   DD UNIT=&WORK,DCB=BLKSIZE=1024,
        //            SPACE=(1024,(200,20))
        //SYSPRINT DD SYSOUT=*
        //SYSLIN   DD DSN=&&COPYLINK,DISP=(OLD,DELETE)
        //         DD DSN=&&LOADSET,DISP=(OLD,DELETE)
        //         DD DDNAME=SYSIN
        //SYSLMOD  DD DISP=SHR,DSN=&INDEX..APPLLOAD(&MEMBER)
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class CompileBMSJClTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    symbolic_map_pds: str

    def get_jcl(self) -> str:
        return """
        //COMPBMS JOB NOTIFY=&SYSUID
        //         JCLLIB ORDER=VREX006.POC.PROCLIB
        //*----------------------------------------------------------------
        //         SET MEMBER={source_library_member}
        //         SET SRCLIB={source_library_pds}
        //         SET SYMMAP={symbolic_map_pds}
        //*----------------------------------------------------------------
        //STEP01      EXEC PROC=BMSPROC
        //C.SYSIN     DD DSN=&SRCLIB(&MEMBER),DISP=SHR
        //L.SYSLMOD   DD DSN=DFH610.CICS.APPLLOAD(&MEMBER),DISP=SHR
        //CSYM.SYSIN  DD DSN=&SRCLIB(&MEMBER),DISP=SHR
        //CSYM.SYSLIN DD DSN=&SYMMAP(&MEMBER),DISP=SHR
        """.format(**self.__dict__)


if __name__ == "__main__":
    import textwrap

    print(
        textwrap.dedent(
            CompileBMSJClTemplate(
                source_library_pds="VREX006.POC.SRCLIB1",
                source_library_member="CUSTMAP",
                symbolic_map_pds="VREX006.POC.SYMMAP",
            ).get_jcl()
        )
    )
