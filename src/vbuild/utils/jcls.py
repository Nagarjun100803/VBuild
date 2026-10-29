import typing
from dataclasses import dataclass
from enum import StrEnum


class SourceCodeType(StrEnum):
    APA_PREFIX = "apa"
    APB_PREFIX = "apb"
    APC_PREFIX = "apc"
    ONL_ONLY = "onl"
    BMS = "bms"
    ASM = "asm"


@dataclass(frozen=True, kw_only=True)
class JCLTemplate(typing.Protocol):
    def get_jcl(self) -> str:
        """Returns the formatted `jcl` that are ready to submit."""
        ...


@dataclass(frozen=True, kw_only=True)
class CompileAPAPrefixProgramJCLTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    load_library_pds: str

    def get_jcl(self) -> str:
        return """
        //IU280APA JOB (SD,IDV101,SGN,P),
        //            'GEN SRC API',
        //            CLASS=J,
        //            MSGCLASS=Q,
        //            NOTIFY=&SYSUID,
        //            REGION=0M
        //*
        //****CHANGE HISTORY: IU280    ON 03/26/18 AT 15.19.03 ****************C
        //* DATE     RSEC OR REASON FOR CHANGE                                *C
        //*          PROJECT                                                  *C
        //* -------- --182-- -------------------------------------------------*C
        //* 03/26/18 GN7359  FILTER FOR CONDITIONAL COBOL                     *C
        //* 12/12/17 GN7313  MODIFIED TO ACCEPT 44 CHARACTER DSN              *C
        //* -------- --181-- -------------------------------------------------*C
        //* 07/25/17 GN7234  MODIFY FOR MQ FROM CICSLOD                       *C
        //* 01/31/17 GN7151  JSON REQUIREMENTS                                *C
        //* -------- --171-- -------------------------------------------------*C
        //* 06/14/16 GN7072  FILTER FOR CONDITIONAL COBOL                     *C
        //* -------- --162-- -------------------------------------------------*C
        //* 01/15/16 GN6973  ADD SYMBOLICS TO SKIP BINDING                    *C
        //* -------- --161-- -------------------------------------------------*C
        //* 08/18/15 GN6892  ADD TEMPORARY DBRM                               *C
        //* 03/19/15 GN6795  ADD CRYPTOGRAPHY SUPPORT                         *C
        //* -------- --152-- -------------------------------------------------*C
        //* 11/11/14 GN6738  COBOL V5 CHANGES                                 *C
        //* -------- --143-- -------------------------------------------------*C
        //* 07/11/14 GN6560  DB2 CHANGES                                      *C
        //* -------- --131-- -------------------------------------------------*C
        //* 06/05/12 GN6282  DB2 CHANGES                                      *C
        //*********************************************************************C
        //*
        //* *******************************************************************
        //* * RUN JCL: APPLICATION INSTALL GENERATE FOR APA/APB/APC SECTIONS
        //* *
        //* * CHANGE:  CNTLDSK TO APPLICATION SOURCE CONTROL FILE DATASET NAME
        //* * CHANGE:  EN1SCF TO APPLICATION SOURCE CONTROL FILE DATASET NAME
        //* *
        //* * PARM USAGE:   STEP NAME         PARM NAME  ACTION
        //* *               N/A               NONE       NONE
        //* *******************************************************************
        //* *******************************************************************
        //* * NOTE   :
        //* *
        //* * THE AUXILIARY DATA DICTIONARY USED IN THIS JOB IS NOT THE SAME
        //* * WITH WHAT IS USED ONLINE. UNEXPECTED RESULTS MAY OCCUR IF
        //* * PROGRAM COMPILED WITH THIS JOB IS TESTED ONLINE
        //* * DEV CICS: SPH1CICS
        //* * SAAUX USED BY THIS JOB: SPHVON.SA.SA.P000.SAAUX.V
        //* * SAAUX USED BY SPH1CICS: SPHVON.SA.SA.P000.SAAUX.V
        //* *
        //* *******************************************************************
        //*
        //JOBLIB   DD DSN=SIBASE.IU.LOADLIB,DISP=SHR
        //*
        /*JOBPARM ROOM=6
        //IU280II  EXEC PGM=IUJCLGEN
        //SYSOUT   DD SYSOUT=Z
        //SYSPRINT DD SYSOUT=A
        //SYSUDUMP DD SYSOUT=Z
        //CNTLDSK  DD DSN=SCOVBN.IU.IU.BASE.SCF,DISP=SHR
        //MIGDSK DD DISP=SHR,
        // DSN=SPHVBN.SA.SA.P000.SAMIG.V
        //SYSUT2   DD SYSOUT=(J,INTRDR)
        //SYSIN    DD *
        NODATA
        SELECT SECTION=APA
        SELECT LANG=COBII
        SELECT NAME={source_library_member}
        SELECT ERROR=YES
        EXCLUDE SRCONLY
        DSLIMIT 1
        APASH    //&NAME JOB (SD,IDV101,SGN,U),'PNB.DEV',
        APASH    // CLASS=J,MSGCLASS=Q,REGION=0M
        APASH    //*NOTIFY AP62790
        APASH    //PROCS JCLLIB ORDER=(SIBASE.IU.PROCLIB)
        APASH    //JOBLIB   DD DISP=SHR,
        APASH    // DSN=SIBASE.IU.LOADLIB
        APASH    // DD DISP=SHR,
        APASH    // DSN=IGY640.SIGYCOMP
        APASH    //*
        APASH    /*JOBPARM ROOM=6
        APADH    //&BATNAME EXEC PROC=IUP2READ,
        APADH    // EN1QUAL='SPHSDN',
        APADH    // SOUT='Z',
        APADH    // DOUT='Z',
        APADH    // EN1SGMT='{source_library_pds}',
        APADH    // EN1CSRC='{source_library_pds}',
        APADH    // MEMBER=&NAME,
        APADH    // WORKDA='3390'
        APADH    //WORKFIL.SYSIN DD *
        APADH    FILTER=NO
        APADH    SINGLE MEMBER=&NAME,APB,COBII
        APADH    /*
        APADH    //&ONLNAME EXEC PROC=IUP2READ,
        APADH    // EN1QUAL='SPHSDN',
        APADH    // SOUT='Z',
        APADH    // DOUT='Z',
        APADH    // EN1SGMT='{source_library_pds}',
        APADH    // EN1CSRC='{source_library_pds}',
        APADH    // MEMBER=&ONLNAME,
        APADH    // WORKDA='3390'
        APADH    //WORKFIL.SYSIN DD *
        APADH    FILTER=NO
        APADH    $SET SYSPARM  CICS
        APADH    SINGLE MEMBER=&NAME,APB,COBII
        APADH    /*
        APADH    //*
        APADH    //&BATNAME EXEC PROC=IUP2APB,
        APADH    // COBREG='0M',
        APADH    // APIBAT='COB3,GEN,CMNT,LCHK',
        APADH    // CB2BP1='NUMPROC(NOPFD),DYN,APOST,NOC(E),ARCH(14),OPT(2)',
        APADH    // CB2BP2=',RULES(NOLAXPERF,NOSLACKBYTES,NOLAXREDEF)',
        APADH    // IULINKB='REUS,XREF,LET,LIST,MAP',
        APADH    // SPNM=',',
        APADH    // ASMBLR='ASMA90',
        APADH    // COMPILR='IGYCRCTL',
        APADH    // LNKEDT='HEWL',
        APADH    // MEMBER=&BATNAME,
        APADH    // DOUT='Z',
        APADH    // SOUT='Z',
        APADH    // IUPARM='SIBASE.IU.PARMLIB',
        APADH    // REG=200M,
        APADH    // LSTNAME=&NAME,
        APADH    // EN1QUAL='SPHSDN',
        APADH    // EN1AUX='SPHVON.SA.SA.P000.SAAUX.V',
        APADH    // EN1LOAD='{load_library_pds}',
        APADH    // TEMPDA='3390',
        APADH    // WORKDA='3390'
        APADH    //*
        APADH    //API121.STEPLIB DD DISP=SHR,
        APADH    // DSN={load_library_pds}
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DSN=CEE.SCEERUN,
        APADH    //* DISP=SHR
        APADH    //API121.SAPDSIN DD DISP=SHR,
        APADH    // DSN=SCON.COPYLIB
        APADH    //  DD DISP=SHR,
        APADH    //  DSN=SCON.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=CEE.SCEESAMP
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //ASM.SYSLIB DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.MACLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=SYS1.MACLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=SYS1.MODGEN
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=SPHN.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=SCON.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=PPSN.PROD.INT3.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=SPHN.COPYLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=SCON.COPYLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //COB.SYSIN DD *
        APADH     CBL INVDATA,S,MAP,FLAG(I,E),TRUNC(BIN)
        APADH     CBL XREF(SHORT),LANG(UE),NODBCS,NONC,IC
        APADH     CBL SSR,DATA(31)
        APADH    /*
        APADH    //COB.SYSLIB DD DISP=SHR,
        APADH    // DSN=SPHN.COPYLIB
        APADH    //  DD DISP=SHR,
        APADH    //  DSN=SCON.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=CEE.SCEESAMP
        APADH    // DD DISP=SHR,
        APADH    // DSN=SYS1.MACLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=SPHN.COPYLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=SCON.COPYLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //LKED.SYSLIB DD DISP=SHR,
        APADH    // DSN={load_library_pds}
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.LOADLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.LOADLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=CEE.SCEELKED
        APADH    // DD DISP=SHR,
        APADH    // DSN=SYS1.CSSLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=CSF.SCSFMOD0
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR* DD DISP=SHR,
        APADH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    &VNDR DD DISP=SHR,
        APADH    &VNDR DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //IUSCRN.SYSIN DD *
        APADH               COPYMOD OUTDD=TESTLIB,INDD=((TEMPLIB,R))
        APADH               SELECT  MEMBER=&BATNAME
        APADH    /*
        APADH    //*
        APADH    //&ONLNAME EXEC PROC=IUP2APC,
        APADH    // APIONL='COB3,CICS,GEN,CMNT,LIST,SP',
        APADH    // COBREG='0M',
        APADH    // CB2OP1='NUMPROC(NOPFD),NODYN,APOST,NOC(E),ARCH(14),OPT(2)',
        APADH    // CB2OP2=',RULES(NOLAXPERF,NOSLACKBYTES,NOLAXREDEF)',
        APADH    // TRNOPT='',
        APADH    // CB2CTRN='COBOL3,CICS,OP,DEBUG,SOURCE,SP',
        APADH    // IULINKO='XREF,LET,LIST,MAP,RENT',
        APADH    // SPNM=',',
        APADH    // ASMBLR='ASMA90',
        APADH    // COMPILR='IGYCRCTL',
        APADH    // IUPARM='SIBASE.IU.PARMLIB',
        APADH    // LNKEDT='HEWL',
        APADH    // MEMBER=&ONLNAME,
        APADH    // REG=200M,
        APADH    // DOUT='Z',
        APADH    // SOUT='Z',
        APADH    // LSTNAME=&NAME,
        APADH    // SYSMAC='SYS1.MACLIB',
        APADH    // SYSMOD='SYS1.MODGEN',
        APADH    // EN1QUAL='SPHSDN',
        APADH    // EN1AUX='SPHVON.SA.SA.P000.SAAUX.V',
        APADH    // EN1COPY='SCON.COPYLIB',
        APADH    // EN1CICS='SCON.CICSLIB',
        APADH    // EN1MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN2COPY='SCON.COPYLIB',
        APADH    // EN2MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN3COPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // EN3MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN4COPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // EN4MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN5COPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // EN5MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN6COPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // EN6MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN7COPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // EN7MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN8COPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // EN8MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // EN9COPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // EN9MAC='PPSN.PROD.INT3.MACLIB',
        APADH    // CICSLOD='CICSTS56.CICS.SDFHLOAD',
        APADH    // CICSCOB='CICSTS56.CICS.SDFHCOB',
        APADH    // GNLOAD='PPSN.PROD.INT3.LOADLIB',
        APADH    // GNCOPY='PPSN.PROD.INT3.COPYLIB',
        APADH    // GNMAC='PPSN.PROD.INT3.MACLIB',
        APADH    // LESAMP='CEE.SCEESAMP',
        APADH    // TEMPDA='3390',
        APADH    // WORKDA='3390'
        APADH    //API121.STEPLIB DD DISP=SHR,
        APADH    // DSN={load_library_pds}
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APADH    //* DD DSN=CEE.SCEERUN,
        APADH    //* DISP=SHR
        APADH    //TRN.STEPLIB DD DISP=SHR,
        APADH    // DSN=CICSTS56.CICS.SDFHLOAD
        APADH    //*
        APADH    //COB.SYSLIB DD DISP=SHR,
        APADH    // DSN=CICSTS56.CICS.SDFHCOB
        APADH    // DD DISP=SHR,
        APADH    // DSN=SCON.COPYLIB
        APADH    //  DD DISP=SHR,
        APADH    //  DSN=SCON.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.COPYLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=CEE.SCEESAMP
        APADH    // DD DISP=SHR,
        APADH    // DSN=SYS1.MACLIB
        APADH    //COB.SYSIN DD *
        APADH     CBL INVDATA,S,MAP,FLAG(I,E),TRUNC(BIN)
        APADH     CBL XREF(SHORT),LANG(UE),NODBCS,NONC,IC,DEF(ONLINE)
        APADH     CBL SSR,DATA(31),RENT,NOWORD,LIST
        APADH    /*
        APADH    //LKED.SYSLIN DD *
        APADH     INCLUDE IUPARM(IU2LE&LEEXIT)
        APADH     INCLUDE CICSLOD(DFHELII)
        APADH     INCLUDE LOADSET
        APADH    /*
        APADH    //LKED.SYSLIB DD DISP=SHR,
        APADH    // DSN=SCON.CICSLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.CICSLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=SPHN.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    //* DD DISP=SHR,
        APADH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.LOADLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.CICSLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=PPSN.PROD.INT3.LOADLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=CEE.SCEELKED
        APADH    // DD DISP=SHR,
        APADH    // DSN=SYS1.CSSLIB
        APADH    // DD DISP=SHR,
        APADH    // DSN=CICSTS56.CICS.SDFHLOAD
        APADH    // DD DISP=SHR,
        APADH    // DSN=TCPIP.SEZATCP
        APADH    // DD DISP=SHR,
        APADH    // DSN=CSF.SCSFMOD0
        APADH    //IUSCRN.SYSIN DD *
        APADH               COPYMOD OUTDD=TESTLIB,INDD=((TEMPLIB,R))
        APADH               SELECT  MEMBER=&ONLNAME
        APADH    /*
        APADH    //&NAME EXEC PROC=IUP2SET,
        APADH    // EN1QUAL='SPHSDN',
        APADH    // SOUT='Z',
        APADH    // UOUT='A',
        APADH    // DOUT='Z',
        APADH    // EN1SCF='SCOVBN.IU.IU.BASE.SCF',
        APADH    // MEMBER=&NAME,
        APADH    // PARM.SETCOMP='ERRCODE=4',
        APADH    // WORKDA='3390'
        APADH    //SETERR.SYSIN DD *
        APADH    CTLUPDT=YES
        APADH    ERRCODE=9
        APADH    PRINT=YES
        APADH    MEMBER=&NAME
        APADH    /*
        APADH    //SETCOMP.SYSIN DD *
        APADH    CTLUPDT=YES
        APADH    PRINT=YES
        APADH    MEMBER=&NAME
        APADH    /*
        APAST    //
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class CompileAPBPrefixProgramJCLTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    load_library_pds: str

    def get_jcl(self) -> str:
        return """
        //IU280APB JOB (SD,IDV101,SGN,P),
        //            'GEN SRC API',
        //            CLASS=J,
        //            MSGCLASS=Q,
        //            NOTIFY=&SYSUID,
        //            REGION=0M
        //*
        //****CHANGE HISTORY: IU280    ON 03/26/18 AT 15.19.03 ****************C
        //* DATE     RSEC OR REASON FOR CHANGE                                *C
        //*          PROJECT                                                  *C
        //* -------- --182-- -------------------------------------------------*C
        //* 03/26/18 GN7359  FILTER FOR CONDITIONAL COBOL                     *C
        //* 12/12/17 GN7313  MODIFIED TO ACCEPT 44 CHARACTER DSN              *C
        //* -------- --181-- -------------------------------------------------*C
        //* 07/25/17 GN7234  MODIFY FOR MQ FROM CICSLOD                       *C
        //* 01/31/17 GN7151  JSON REQUIREMENTS                                *C
        //* -------- --171-- -------------------------------------------------*C
        //* 06/14/16 GN7072  FILTER FOR CONDITIONAL COBOL                     *C
        //* -------- --162-- -------------------------------------------------*C
        //* 01/15/16 GN6973  ADD SYMBOLICS TO SKIP BINDING                    *C
        //* -------- --161-- -------------------------------------------------*C
        //* 08/18/15 GN6892  ADD TEMPORARY DBRM                               *C
        //* 03/19/15 GN6795  ADD CRYPTOGRAPHY SUPPORT                         *C
        //* -------- --152-- -------------------------------------------------*C
        //* 11/11/14 GN6738  COBOL V5 CHANGES                                 *C
        //* -------- --143-- -------------------------------------------------*C
        //* 07/11/14 GN6560  DB2 CHANGES                                      *C
        //* -------- --131-- -------------------------------------------------*C
        //* 06/05/12 GN6282  DB2 CHANGES                                      *C
        //*********************************************************************C
        //*
        //* *******************************************************************
        //* * RUN JCL: APPLICATION INSTALL GENERATE FOR APA/APB/APC SECTIONS
        //* *
        //* * CHANGE:  CNTLDSK TO APPLICATION SOURCE CONTROL FILE DATASET NAME
        //* * CHANGE:  EN1SCF TO APPLICATION SOURCE CONTROL FILE DATASET NAME
        //* *
        //* * PARM USAGE:   STEP NAME         PARM NAME  ACTION
        //* *               N/A               NONE       NONE
        //* *******************************************************************
        //*
        //JOBLIB   DD DSN=SIBASE.IU.LOADLIB,DISP=SHR
        //*
        /*JOBPARM ROOM=6
        //IU280II  EXEC PGM=IUJCLGEN
        //SYSOUT   DD SYSOUT=Z
        //SYSPRINT DD SYSOUT=A
        //SYSUDUMP DD SYSOUT=Z
        //CNTLDSK  DD DSN=SCOVBN.IU.IU.BASE.SCF,DISP=SHR
        //MIGDSK DD DISP=SHR,
        // DSN=SCOVBN.SA.SA.P000.SAMIG.V
        //SYSUT2   DD SYSOUT=(J,INTRDR)
        //SYSIN    DD *
        NODATA
        SELECT SECTION=APB
        SELECT LANG=COBII
        SELECT NAME={source_library_member}
        SELECT DISTCTL=ALL
        SELECT ERROR=YES
        EXCLUDE SRCONLY
        DSLIMIT 1
        APBSH    //&NAME JOB (SD,IDV101,SGN,U),'PNB.DEV',
        APBSH    // CLASS=J,MSGCLASS=Q,REGION=0M
        APBSH    //*NOTIFY AP62790
        APBSH    //PROCS JCLLIB ORDER=(SIBASE.IU.PROCLIB)
        APBSH    //JOBLIB   DD DISP=SHR,
        APBSH    // DSN=SIBASE.IU.LOADLIB
        APBSH    // DD DISP=SHR,
        APBSH    // DSN=IGY640.SIGYCOMP
        APBSH    //*
        APBSH    /*JOBPARM ROOM=6
        APBDH    //&NAME EXEC PROC=IUP2READ,
        APBDH    // EN1QUAL='SCOSDN',
        APBDH    // SOUT='Z',
        APBDH    // DOUT='Z',
        APBDH    // EN1SGMT='{source_library_pds}',
        APBDH    // EN1CSRC='{source_library_pds}',
        APBDH    // MEMBER=&NAME,
        APBDH    // WORKDA='3390'
        APBDH    //WORKFIL.SYSIN DD *
        APBDH    FILTER=NO
        APBDH    SINGLE MEMBER=&NAME,APB,COBII
        APBDH    /*
        APBDH    //*
        APBDH    //&NAME EXEC PROC=IUP2APB,
        APBDH    // APIBAT='COB3,GEN,CMNT,LCHK',
        APBDH    // COBREG='0M',
        APBDH    // CB2BP1='NUMPROC(NOPFD),DYN,APOST,NOC(E),ARCH(14),OPT(2)',
        APBDH    // CB2BP2=',RULES(NOLAXPERF,NOSLACKBYTES,NOLAXREDEF)',
        APBDH    // IULINKB='REUS,XREF,LET,LIST,MAP',
        APBDH    // SPNM=',',
        APBDH    // ASMBLR='ASMA90',
        APBDH    // COMPILR='IGYCRCTL',
        APBDH    // LNKEDT='HEWL',
        APBDH    // MEMBER=&NAME,
        APBDH    // DOUT='Z',
        APBDH    // SOUT='Z',
        APBDH    // IUPARM='SIBASE.IU.PARMLIB',
        APBDH    // REG=200M,
        APBDH    // LSTNAME=&NAME,
        APBDH    // EN1QUAL='SCOSDN',
        APBDH    // EN1AUX='SPHVON.SA.SA.P000.SAAUX.V',
        APBDH    // EN1LOAD='{load_library_pds}',
        APBDH    // TEMPDA='3390',
        APBDH    // WORKDA='3390'
        APBDH    //API121.STEPLIB DD DISP=SHR,
        APBDH    // DSN={load_library_pds}
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DSN=CEE.SCEERUN,
        APBDH    //* DISP=SHR
        APBDH    //API121.SAPDSIN DD DISP=SHR,
        APBDH    // DSN=SCON.COPYLIB
        APBDH    //  DD DISP=SHR,
        APBDH    //  DSN=SCON.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=CEE.SCEESAMP
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR DD DISP=SHR,
        APBDH    &VNDR DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //ASM.SYSLIB DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=SYS1.MACLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=SYS1.MODGEN
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=SCON.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=SCON.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR DD DISP=SHR,
        APBDH    &VNDR DSN=PPSN.PROD.INT3.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR DD DISP=SHR,
        APBDH    &VNDR DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //COB.SYSIN DD *
        APBDH     CBL INVDATA,S,MAP,FLAG(I,E),TRUNC(BIN)
        APBDH     CBL XREF(SHORT),LANG(UE),NODBCS,NONC,IC
        APBDH     CBL SSR,DATA(31)
        APBDH    /*
        APBDH    //COB.SYSLIB DD DISP=SHR,
        APBDH    // DSN=SCON.COPYLIB
        APBDH    //  DD DISP=SHR,
        APBDH    //  DSN=SCON.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=CEE.SCEESAMP
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=SYS1.MACLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    &VNDR DD DISP=SHR,
        APBDH    &VNDR DSN=PPSN.PROD.INT3.COPYLIB
        APBDH    //LKED.SYSLIB DD DISP=SHR,
        APBDH    // DSN={load_library_pds}
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //* DD DISP=SHR,
        APBDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=CEE.SCEELKED
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=SYS1.CSSLIB
        APBDH    // DD DISP=SHR,
        APBDH    // DSN=CSF.SCSFMOD0
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR* DD DISP=SHR,
        APBDH    &VNDR* DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    &VNDR DD DISP=SHR,
        APBDH    &VNDR DSN=PPSN.PROD.INT3.LOADLIB
        APBDH    //IUSCRN.SYSIN DD *
        APBDH               COPYMOD OUTDD=TESTLIB,INDD=((TEMPLIB,R))
        APBDH               SELECT  MEMBER=&NAME
        APBDH    /*
        APBDH    //*
        APBDH    //&NAME EXEC PROC=IUP2SET,
        APBDH    // EN1QUAL='SCOSDN',
        APBDH    // SOUT='Z',
        APBDH    // UOUT='A',
        APBDH    // DOUT='Z',
        APBDH    // EN1SCF='SCOVBN.IU.IU.BASE.SCF',
        APBDH    // MEMBER='&NAME',
        APBDH    // PARM.SETCOMP='ERRCODE=4',
        APBDH    // WORKDA='3390'
        APBDH    //SETERR.SYSIN DD *
        APBDH    CTLUPDT=YES
        APBDH    ERRCODE=9
        APBDH    PRINT=YES
        APBDH    MEMBER=&NAME
        APBDH    /*
        APBDH    //SETCOMP.SYSIN DD *
        APBDH    CTLUPDT=YES
        APBDH    PRINT=NO
        APBDH    MEMBER=&NAME
        APBDH    /*
        APBST    //
        /*
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class CompileAPCPrefixProgramJCLTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    load_library_pds: str

    def get_jcl(self) -> str:
        return """
        //IU280APC JOB (SD,IDV101,SGN,P),
        //            'GEN SRC API',
        //            CLASS=A,
        //            MSGCLASS=Q,
        //            NOTIFY=&SYSUID,
        //            REGION=0M
        //*
        //*********************************************************************C
        //*
        //* *******************************************************************
        //* * RUN JCL: APPLICATION INSTALL GENERATE FOR APA/APB/APC SECTIONS
        //* *
        //* * CHANGE:  CNTLDSK TO APPLICATION SOURCE CONTROL FILE DATASET NAME
        //* * CHANGE:  EN1SCF TO APPLICATION SOURCE CONTROL FILE DATASET NAME
        //* *
        //* * PARM USAGE:   STEP NAME         PARM NAME  ACTION
        //* *               N/A               NONE       NONE
        //* *******************************************************************
        //* *******************************************************************
        //* * NOTE   :
        //* *
        //* * THE AUXILIARY DATA DICTIONARY USED IN THIS JOB IS NOT THE SAME
        //* * WITH WHAT IS USED ONLINE. UNEXPECTED RESULTS MAY OCCUR IF
        //* * PROGRAM COMPILED WITH THIS JOB IS TESTED ONLINE
        //* * DEV CICS: SCO1CICS
        //* * SAAUX USED BY THIS JOB: SPHVON.SA.SA.P000.SAAUX.V
        //* * SAAUX USED BY SPH#CICS: SPHVON.SA.SA.P000.SAAUX.V
        //* *
        //* *******************************************************************
        //*
        //JOBLIB   DD DSN=SIBASE.IU.LOADLIB,DISP=SHR
        //*
        /*JOBPARM ROOM=6
        //IU280II  EXEC PGM=IUJCLGEN
        //SYSOUT   DD SYSOUT=Z
        //SYSPRINT DD SYSOUT=A
        //SYSUDUMP DD SYSOUT=Z
        //CNTLDSK  DD DSN=SCOVBN.IU.IU.BASE.SCF,DISP=SHR
        //MIGDSK DD DISP=SHR,
        // DSN=SCOVBN.SA.SA.P000.SAMIG.V
        //SYSUT2   DD SYSOUT=(J,INTRDR)
        //SYSIN    DD *
        NODATA
        SELECT SECTION=APC
        SELECT NAME={source_library_member}
        SELECT ERROR=YES
        EXCLUDE SRCONLY
        DSLIMIT 1
        APCSH    //&NAME JOB (SD,IDV101,SGN,U),'PNB.DEV',
        APCSH    // CLASS=A,MSGCLASS=Q,REGION=0M
        APCSH    //*NOTIFY AP62790
        APCSH    //PROCS JCLLIB ORDER=(SIBASE.IU.PROCLIB)
        APCSH    //JOBLIB   DD DISP=SHR,
        APCSH    // DSN=SIBASE.IU.LOADLIB
        APCSH    // DD DISP=SHR,
        APCSH    // DSN=IGY640.SIGYCOMP
        APCSH    //*
        APCSH    /*JOBPARM ROOM=6
        APCDH    //&NAME EXEC PROC=IUP2READ,
        APCDH    // EN1QUAL='SCOSDN',
        APCDH    // SOUT='Z',
        APCDH    // DOUT='Z',
        APCDH    // EN1SGMT='{source_library_pds}',
        APCDH    // EN1CSRC='{source_library_pds}',
        APCDH    // MEMBER=&NAME,
        APCDH    // WORKDA='3390'
        APCDH    //WORKFIL.SYSIN DD *
        APCDH    FILTER=NO
        APCDH    SINGLE MEMBER=&NAME,APC,COBII
        APCDH    /*
        APCDH    //*
        APCDH    //&NAME EXEC PROC=IUP2APC,
        APCDH    // APIONL='COB3,CICS,GEN,CMNT,LIST,SP',
        APCDH    // COBREG='0M',
        APCDH    // CB2OP1='NUMPROC(NOPFD),NODYN,APOST,NOC(E),ARCH(12),OPT(2)',
        APCDH    // CB2OP2=',RULES(NOLAXPERF,NOSLACKBYTES,NOLAXREDEF)',
        APCDH    // TRNOPT='',
        APCDH    // CB2CTRN='COBOL3,CICS,OP,DEBUG,SOURCE,SP',
        APCDH    // IULINKO='XREF,LET,LIST,MAP,RENT',
        APCDH    // SPNM=',',
        APCDH    // ASMBLR='ASMA90',
        APCDH    // COMPILR='IGYCRCTL',
        APCDH    // LNKEDT='HEWL',
        APCDH    // MEMBER=&NAME,
        APCDH    // DOUT='Z',
        APCDH    // SOUT='Z',
        APCDH    // IUPARM='SIBASE.IU.PARMLIB',
        APCDH    // REG=200M,
        APCDH    // LSTNAME=&NAME,
        APCDH    // EN1QUAL='SCOSDN',
        APCDH    // EN1AUX='SPHVON.SA.SA.P000.SAAUX.V',
        APCDH    // EN1COPY='SCON.COPYLIB',
        APCDH    // EN1CICS='{load_library_pds}',
        APCDH    // EN1MAC='SCON.MACLIB',
        APCDH    // EN2COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN2MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // EN3COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN3MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // EN4COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN4MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // EN5COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN5MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // EN6COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN6MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // EN7COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN7MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // EN8COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN8MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // EN9COPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // EN9MAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // SYSMAC='SYS1.MACLIB',
        APCDH    // SYSMOD='SYS1.MODGEN',
        APCDH    // CICSLOD='CICSTS56.CICS.SDFHLOAD',
        APCDH    // CICSCOB='CICSTS56.CICS.SDFHCOB',
        APCDH    // GNLOAD='PPSN.PROD.INT3.LOADLIB',
        APCDH    // GNCOPY='PPSN.PROD.INT3.COPYLIB',
        APCDH    // GNMAC='PPSN.PROD.INT3.MACLIB',
        APCDH    // LESAMP='CEE.SCEESAMP',
        APCDH    // TEMPDA='3390',
        APCDH    // WORKDA='3390'
        APCDH    //API121.STEPLIB DD DISP=SHR,
        APCDH    // DSN={load_library_pds}
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    // DD DSN=PPSN.PROD.INT3.LOADLIB,DISP=SHR
        APCDH    //* DD DSN=CEE.SCEERUN,
        APCDH    //* DISP=SHR
        APCDH    //TRN.STEPLIB DD DISP=SHR,
        APCDH    // DSN=CICSTS56.CICS.SDFHLOAD
        APCDH    //*
        APCDH    //COB.SYSLIB DD DISP=SHR,
        APCDH    // DSN=CICSTS56.CICS.SDFHCOB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=SCON.COPYLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=PPSN.PROD.INT3.COPYLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=CEE.SCEESAMP
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=SYS1.MACLIB
        APCDH    //COB.SYSIN DD *
        APCDH     CBL INVDATA,S,MAP,FLAG(I,E),TRUNC(BIN)
        APCDH     CBL XREF(SHORT),LANG(UE),NODBCS,NC(ZON,PAC),IC,DEF(ONLINE)
        APCDH     CBL SSR,DATA(31),RENT,NOWORD
        APCDH    /*
        APCDH    //LKED.SYSLIN DD *
        APCDH     INCLUDE IUPARM(IU2LE&LEEXIT)
        APCDH     INCLUDE CICSLOD(DFHELII)
        APCDH     INCLUDE LOADSET
        APCDH    /*
        APCDH    //LKED.SYSLIB DD DISP=SHR,
        APCDH    // DSN={load_library_pds}
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN={load_library_pds}
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    //* DD DISP=SHR,
        APCDH    //* DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=PPSN.PROD.INT3.CICSLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=PPSN.PROD.INT3.LOADLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=CEE.SCEELKED
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=SYS1.CSSLIB
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=CICSTS56.CICS.SDFHLOAD
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=TCPIP.SEZATCP
        APCDH    // DD DISP=SHR,
        APCDH    // DSN=CSF.SCSFMOD0
        APCDH    //IUSCRN.SYSIN DD *
        APCDH               COPYMOD OUTDD=TESTLIB,INDD=((TEMPLIB,R))
        APCDH               SELECT  MEMBER=&NAME
        APCDH    /*
        APCDH    //&NAME EXEC PROC=IUP2SET,
        APCDH    // EN1QUAL='SCOSDN',
        APCDH    // SOUT='Z',
        APCDH    // UOUT='A',
        APCDH    // DOUT='Z',
        APCDH    // EN1SCF='SCOVBN.IU.IU.BASE.SCF',
        APCDH    // MEMBER='&NAME',
        APCDH    // PARM.SETCOMP='ERRCODE=4',
        APCDH    // WORKDA='3390'
        APCDH    //SETERR.SYSIN DD *
        APCDH    CTLUPDT=YES
        APCDH    ERRCODE=9
        APCDH    PRINT=YES
        APCDH    MEMBER=&NAME
        APCDH    /*
        APCDH    //SETCOMP.SYSIN DD *
        APCDH    CTLUPDT=YES
        APCDH    PRINT=YES
        APCDH    MEMBER=&NAME
        APCDH    /*
        APCST    //
        /*
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class CompilePureCICSProgramJCLTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    load_library_pds: str

    def get_jcl(self) -> str:
        return """
        //COMPCICS JOB ACCT,'ASDWSPC',CLASS=A,MSGCLASS=X,
        //             MSGLEVEL=(1,1),NOTIFY=&SYSUID TYPRUN=HOLD
        //************************************************************
        //* ORIGINAL COMPILER NAME: CCMPLJCL
        //* THIS COMPILES COBOL CICS FOR ZOS
        //************************************************************
        //COB    EXEC PGM=IGYCRCTL,REGION=0M,
        //        PARM='OBJECT,RENT,APOST,MAP,OFFSET,XREF,CICS("SP")'
        //SYSIN     DD DISP=SHR,DSN={source_library_pds}({source_library_member})
        //STEPLIB  DD  DSNAME=IGY640.SIGYCOMP,DISP=SHR
        //         DD  DSNAME=CEE.SCEERUN,DISP=SHR
        //         DD  DSNAME=CEE.SCEERUN2,DISP=SHR
        //          DD DSN=CICSTS56.CICS.SDFHCOB,DISP=SHR
        //          DD DSN=CICSTS56.CICS.SDFHLOAD,DISP=SHR
        //SYSLIB    DD DSN=SCON.COPYLIB,DISP=SHR
        //          DD DSN=CICSTS56.CICS.SDFHCOB,DISP=SHR
        //          DD DSN=CICSTS56.CICS.SDFHMAC,DISP=SHR
        //          DD DSN=CICSTS56.CICS.SDFHSAMP,DISP=SHR
        //SYSPRINT  DD SYSOUT=*
        //SYSOUT    DD SYSOUT=*
        //*YSIN     DD DSN=&&SYSCIN,DISP=(OLD,DELETE)
        //SYSLIN    DD DSN=&&LOADSET,DISP=(MOD,PASS),
        //             UNIT=SYSDA,SPACE=(80,(250,100))
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
        //************************************************************
        //*OPYLNK EXEC PGM=IEBGENER,COND=(7,LT,COB)
        //*YSUT1    DD DSN=CICSTS56.CICS.SDFHSAMP(DFHEILID),DISP=SHR
        //*YSUT2    DD DSN=&&COPYLINK,DISP=(NEW,PASS),
        //*            DCB=(LRECL=80,BLKSIZE=400,RECFM=FB),
        //*            UNIT=SYSDA,SPACE=(400,(20,20))
        //*YSPRINT  DD SYSOUT=A
        //*YSIN     DD DUMMY
        //************************************************************
        //LKED    EXEC PGM=HEWL,REGION=4M,
        //             PARM='LIST,XREF',COND=(5,LT,COB)
        //SYSLIB    DD DSN=CICSTS56.CICS.SDFHLOAD,DISP=SHR
        //          DD DSN=CEE.SCEELKED,DISP=SHR
        //          DD DSN=CICSTS56.CICS.SDFHCOB,DISP=SHR
        //          DD DSN=TCPIP.SEZATCP,DISP=SHR
        //SYSLMOD   DD DSN={load_library_pds},DISP=SHR
        //SYSUT1    DD UNIT=SYSDA,DCB=BLKSIZE=1024,
        //             SPACE=(1024,(200,20))
        //SYSPRINT  DD SYSOUT=*
        //SYSOUT    DD SYSOUT=*
        //SYSUDUMP  DD SYSOUT=*
        //SYSABOUT  DD SYSOUT=*
        //SYSDBOUT  DD SYSOUT=*
        //*YSLIN    DD DSN=&&COPYLINK,DISP=(OLD,DELETE)
        //SYSLIN    DD DSN=&&LOADSET,DISP=(OLD,DELETE)
        //          DD DDNAME=SYSIN
        //SYSIN DD *
         NAME {source_library_member}(R)
        /*
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class CompileBMSProgramJCLTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    load_library_pds: str

    def get_jcl(self) -> str:
        return """
        //COMPBMS JOB (ACCT),'MAP COMPILE',
        //            CLASS=A,MSGCLASS=H,NOTIFY=&SYSUID,REGION=0M
        //*OBPARM SYSAFF=TSG1
        //SETA SET LIBPRFX=CEE
        //*********************************************************************
        //* ORIGINAL COMPILER NAME: COMPMAP
        //* COMPILES TW MAP
        //*********************************************************************
        //*
        //    JCLLIB ORDER=CICSTS56.CICS.SDFHPROC
        //RUNIVP EXEC DFHMAPS,REGION=0M,
        //    MAPLIB='{load_library_pds}',
        //    DSCTLIB='SCON.COPYLIB',
        //    MAPNAME={source_library_member},
        //    WORK=SYSALLDA
        //COPY.SYSUT1 DD DSN={source_library_pds}({source_library_member}),
        //       DISP=SHR
        """.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class CompileASMProgramJCLTemplate(JCLTemplate):
    source_library_pds: str
    source_library_member: str
    load_library_pds: str

    def get_jcl(self) -> str:
        return """
        //COMPASM JOB (ACCT),'ZOS 2.5',CLASS=A,
        //            MSGCLASS=H,NOTIFY=&SYSUID,REGION=0M
        //*********************************************************************
        //* ORIGINAL COMPILER NAME: COMPASM
        //* ASSEMBLE THE SOURCE
        //*********************************************************************
        //ASMH     EXEC  PGM=ASMA90,PARM=(NODECK,OBJECT)
        //SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
        //*        DD  DSN=SYS1.MODGEN,DISP=SHR
        //SYSUT1   DD  UNIT=(3390,SEP=SYSLIB),SPACE=(CYL,(10,5)),DSN=&SYSUT1,
        //         VOL=SER=Z1SYSB
        //SYSPUNCH DD  DUMMY
        //SYSPRINT DD  SYSOUT=*
        //SYSLIN   DD  DISP=(,PASS),SPACE=(CYL,(5,5,0)),
        //             DCB=(BLKSIZE=400),DSN=&&LOADSET,
        //             UNIT=SYSDA
        //SYSIN    DD  DISP=SHR,DSN={source_library_pds}({source_library_member})
        //*********************************************************************
        //* LINKEDIT THE OBJECT TO A TEMPORARY LOAD LIBRARY
        //*********************************************************************
        //LKED     EXEC  PGM=IEWL,PARM='LET,LIST,XREF,AMODE(31),RMODE(ANY)',
        //        COND=(4,LT,ASMH)
        //*            RMODE(ANY)),COND=(4,LT,ASMH)
        //SYSLIN   DD  DSN=&&LOADSET,DISP=(OLD,DELETE)
        //         DD  DDNAME=SYSIN
        //SYSLMOD  DD  DISP=SHR,DSN={load_library_pds}
        //SYSUT1   DD  SPACE=(CYL,(3,2)),DSN=&SYSUT1,
        //         UNIT=SYSDA
        //SYSPRINT DD  SYSOUT=*
        //SYSIN    DD  *
          NAME {source_library_member}(R)
        /*
        """.format(**self.__dict__)
