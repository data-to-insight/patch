import pandas as pd
import numpy as np
import datetime as dt
import calendar

import streamlit as st

import xml.etree.ElementTree as ET
import time

from enum import Enum
from dateutil.relativedelta import relativedelta

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from pyodide.http import open_url

###################
# Config
###################

st.set_page_config(layout="wide")


class EthnicSubcategories(Enum):
    """Used to map ethnicity codes to main groups, uses long GIAS code-set"""

    WBRI = "White British"
    WIRI = "White Irish"
    WOTH = "Any other White background"
    WIRT = "Traveller of Irish Heritage"
    WROM = "Gypsy/Roma"
    MWBC = "White and Black Caribbean"
    MWBA = "White and Black African"
    MWAS = "White and Asian"
    MOTH = "Any other Mixed background"
    AIND = "Indian"
    APKN = "Pakistani"
    ABAN = "Bangladeshi"
    AOTH = "Any other Asian background"
    BCRB = "Caribbean"
    BAFR = "African"
    BOTH = "Any other Black background"
    CHNE = "Chinese"
    OOTH = "Any other ethnic group"
    REFU = "Refused"
    NOBT = "Information not yet obtained"


class UPNCodes(Enum):
    UN1 = "Child looked-after is not of school age and has not yet been assigned a unique pupil number (UPN)."
    UN2 = "Child looked-after has never attended a maintained school in England (for example, some unaccompanied asylum-seeking children (UASC))."
    UN3 = "Child looked-after is educated outside England."
    UN4 = "Child is newly looked-after (from one week before end of collection period) and the unique pupil number (UPN) was not yet known at the time of the looked-after children data collection return."
    UN5 = "Sources collating unique pupil numbers (UPNs) reflect discrepancy(ies) for the child's name and/or surname and/or date of birth therefore preventing reliable matching (for example, duplicated unique pupil numbers (UPNs)"


class CINCodes(Enum):
    N1 = "Abuse or neglect"
    N2 = "Child's disability"
    N3 = "Parental illness or disability"
    N4 = "Family in acute stress"
    N5 = "Family dysfunction"
    N6 = "Socially unacceptable behaviour"
    N7 = "Low income"
    N8 = "Absent parenting"


class LSCodes(Enum):
    C1 = "Interim care order"
    C2 = "Full care order"
    D1 = "Freeing order granted"
    E1 = "Placement order granted"
    V2 = "Single period of accommodation under section 20 (Children Act 1989)"
    V3 = "Accommodated under an agreed series of short-term breaks, when individual episodes of care are recorded"
    V4 = "Accommodated under an agreed series of short-term breaks, when agreements are recorded (NOT individual episodes of care)"
    L1 = "Under police protection and in local authority accommodation"
    L2 = "Emergency protection order (EPO)"
    L3 = "Under child assessment order and in local authority accommodation"
    J1 = "Remanded to local authority accommodation or to youth detention accommodation"
    J2 = "Placed in local authority accommodation under the Police and Criminal Evidence Act 1984, including secure accommodation, not necessarily where child would be detained."
    J3 = "Sentenced to Youth Rehabilitation Order (Criminal Justice and Immigration Act 2008 as amended by Legal Aid, Sentencing and Punishment of Offenders Act 2012 with residence or intensive fostering requirement)"


class PLACECodes(Enum):
    U4 = "Foster placement with other foster carer(s) – long term fostering"
    U5 = "Foster placement with other foster carer(s) who is/are also an approved adopter(s) –fostering for adoption /concurrent planning"
    U6 = "Foster placement with other foster carer(s) – not long term or fostering for adoption /concurrent planning"
    U1 = "Foster placement with relative(s) or friend(s) – long term fostering"
    U2 = "Fostering placement with relative(s) or friend(s) who is/are also an approved adopter(s) – fostering for adoption /concurrent planning"
    U3 = "Fostering placement with relative(s) or friend(s) who is/are not long-term or fostering for adoption /concurrent plannin"
    H5 = "Semi-independent living accommodation not subject to children’s homes regulations"
    K3 = "Registered supported accommodation"
    P2 = "Independent living for example in a flat, lodgings, bedsit, bed and breakfast (B&B) or with friends, with or without formal support"
    K2 = "Children’s Homes subject to Children’s Homes Regulations"
    K1 = "Secure children’s homes"
    R1 = "Residential care home"
    R2 = "National Health Service (NHS)/health trust or other establishment providing medical or nursing care"
    R5 = "Young offender institution (YOI)"
    S1 = "All residential schools, except where dual-registered as a school and children’s home"
    P1 = "Placed with own parent(s) or other person(s) with parental responsibility"
    A3 = "Placed for adoption with parental/guardian consent with current foster carer(s) (under Section 19 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent has been given (under Section 18(1)(a) of the Adoption Act 1976)"
    A4 = "Placed for adoption with parental/guardian consent not with current foster carer(s) (under Section 19 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent has been given under Section 18(1)(a) of the  Adoption Act 1976"
    A5 = "Placed for adoption with placement order with current foster carer(s) (under Section Placed for adoption with placement order with current foster carer(s) (under Section 21 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent was dispensed with (under Section 18(1)(b) the Adoption Act 1976)"
    A6 = "Placed for adoption with placement order not with current foster carer(s) (under Section 21 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent was dispensed with (under Section 18(1)(b) of the Adoption Act 1976)"
    P3 = "Residential employment"
    R3 = "Family centre or mother and baby unit"
    T0 = "All types of temporary move (see paragraphs above for further details)"
    T1 = "Temporary periods in hospital"
    T2 = "Temporary absences of the child on holiday"
    T3 = "Temporary accommodation whilst normal foster carer(s) is/are on holiday"
    Z1 = "Other placements (must be listed on a schedule sent to DfE with annual submission)"
    T4 = "Temporary accommodation of seven days or less, for any reason, not covered by codes T1 to T3"


class PLACEPROVIDERCodes(Enum):
    PR1 = "Own provision (by the local authority) including a regional adoption agency where the child’s responsible local authority is the host authority"
    PR2 = "Other local authority provision, including a regional adoption agency where another local authority is the host authority"
    PR3 = "Other public provision (for example, a primary care trust)"
    PR0 = "Parent(s) or other person(s) with parental responsibility"
    PR4 = "Private provision"
    PR5 = "Voluntary/third sector provision"


class REASONPLACECHANGECodes(Enum):
    CARPL = "Change to/Implementation of Care Plan"
    ALLEG = "Allegation (s47)"
    STAND = "Standards of care concern"
    APPRR = "Approval removed"
    CUSTOD = "Custody arrangement"
    OTHER = "other"
    CLOSE = "Resignation/ closure of provision"
    CREQB = "Carer(s) requests placement end due to child’s behaviour"
    CREQO = "Carer(s) requests placement end other than due to child’s behaviour"
    CHILD = "Child requests placement end"
    LAREQ = "Responsible/area authority requests placement end"
    PLACE = "Change in the status of placement only"
    LIIAF = "CONSULT LIIA FOR CODE"


class RECCodes(Enum):
    E11 = "Adopted - application for an adoption order unopposed"
    E12 = "Adopted – consent dispensed with by the court"
    E45 = "Special guardianship order made to former foster carer(s), who was/are a relative(s) or friend(s)"
    E46 = "Special guardianship order made to former foster carer(s), other than relative(s) or friend(s)"
    E47 = "Special guardianship order made to carer(s), other than former foster carer(s), who was/are a relative(s) or friend(s)"
    E48 = "Special guardianship order made to carer(s), other than former foster carer(s), other than relative(s) or friend(s)"
    E5 = "Moved into independent living arrangement and no longer looked-after: supportive accommodation providing formalised advice/support arrangements (such as most hostels, young men’s Christian association, foyers, staying close and care leavers projects). Includes both children leaving care before and at age 18"
    E6 = "Moved into independent living arrangement and no longer looked-after : accommodation providing no formalised advice/support arrangements (such as bedsit, own flat, living with friend(s)). Includes both children leaving care before and at age 18"
    E9 = "Sentenced to custody"
    E14 = "Accommodation on remand ended"
    E7 = "Transferred to residential care funded by adult social care services"
    E17 = "Aged 18 (or over) and remained with current carers (inc under staying put arrangements)"
    E13 = "Left care to live with parent(s), relative(s), or other person(s) with no parental responsibility."
    E2 = "Died"
    E3 = "Care taken over by another local authority in the UK"
    E15 = "Age assessment determined child is aged 18 or over and E5, E6 and E7 do not apply, such as an unaccompanied asylum-seeking child (UASC) whose age has been disputed"
    E16 = "Child moved abroad"
    E8 = "Period of being looked-after ceased for any other reason (where none of the other reasons apply)"
    E4B = "Returned home to live with parent(s), relative(s), or other person(s) with parental responsibility which was not part of the current care planning process (not under a special guardianship order or residence order or (from 22 April 2014) a child arrangement order)."
    E4A = "Returned home to live with parent(s), relative(s), or other person(s) with parental responsibility as part of the care planning process (not under a special guardianship order or residence order or (from 22 April 2014) a child arrangement order)."
    X1 = "Episode ceases, and new episode begins on same day, for any reason"
    E41 = "Residence order (or, from 22 April 2014, a child arrangement order which sets out with whom the child is to live) granted"
    E43 = "Special guardianship made to former foster carers"
    E44 = "Special guardianship made to carers other than former foster carers"
    E99 = "Not recorded (rule-fixed episode)"


class RNECodes(Enum):
    S = "Started to be looked-after"
    L = "Change of legal status only"
    P = "Change of placement and carer(s) only"
    T = "Change of placement (but same carer(s)) only"
    B = "Change of legal status and placement and carer(s) at the same time"
    U = "Change of legal status and change of placement (but same carer(s)) at the same time"


class MISSINGCodes(Enum):
    A = "Away from placement without authorisation: a looked-after child whose whereabouts is known but who is not at their placement or place they are expected to be and the carer has concerns or the incident has been notified to the local authority or the police"
    M = "Missing from care: a looked-after child who is not at their placement or the place they are expected to be (for example school) and their whereabouts is not known"


class SDQREASONCodes(Enum):
    SDQ1 = "No form returned as child was aged under 4 or over 16 at date of latest assessment"
    SDQ2 = "Carer(s) refused to complete and return questionnaire"
    SDQ3 = "Not possible to complete the questionnaire due to severity of the child’s disability"
    SDQ4 = "Other"
    SDQ5 = "Child or young person refuses to allow a strengths and difficulties questionnaire (SDQ) to be completed"


class SUBSTANCECodes(Enum):
    _0 = "Child was not identified as having a substance misuse problem"
    _1 = "Child was identified as having a substance misuse problem"


class TEETHCodes(Enum):
    _0 = "Child did not have their teeth checked by a dentist"
    _1 = "Child did have their teeth checked by a dentist"


class INTERVENTIONOFFEREDCodes(Enum):
    _0 = "Child was not offered an intervention for their substance misuse problem"
    _1 = "Child was offered an intervention for their substance misuse problem but refused it"


class INTERVENTIONRECEIVEDCodes(Enum):
    _0 = "Child did not receive an intervention for their substance misuse problem"
    _1 = "Child received an intervention for their substance misuse problem"


class CONVICTEDCodes(Enum):
    _0 = "Child has not been convicted or subject to a youth caution (including youth conditional caution) during the year"
    _1 = "Child has been convicted or subject to a youth caution (including youth conditional caution) during the year"


class IMMUNISATIONCodes(Enum):
    _0 = "Child’s immunisations were not up to date"
    _1 = "Child’s immunisations were up to date"


class HEALTHCHECKCodes(Enum):
    _0 = "Child’s health surveillance or health promotion checks were not up to date"
    _1 = "Child’s health surveillance or health promotion checks were up to date"


class HEALTHASSESSMENTCodes(Enum):
    _0 = "Child did not have their annual health assessment"
    _1 = "Child had their annual health assessment"

class ACCOMCodes(Enum):
    _0 = "Not in touch with the young person and do not know their accommodation, or the young person has died, or returned home to live with parents or someone with parental responsibility for a continuous period of 6 months or more."
    _B1 = "With parent(s) or relative(s)"
    _B2 = "With parent(s) or relative(s)"
    _C1 = "Community home or other form of residential care such as an National Health Service (NHS) establishment"
    _C2 = "Community home or other form of residential care such as an National Health Service (NHS) establishment"
    _D1 = "Semi-independent, transitional accommodation (like a supported hostel, trainer flats); self contained accommodation with specialist personal assistance support (for example, for young people with disabilities, pregnant young women and single parents); and self-contained accommodation with floating support"
    _D2 = "Semi-independent, transitional accommodation (like a supported hostel, trainer flats); selfcontained accommodation with specialist personal assistance support (for example, for young people with disabilities, pregnant young women and single parents); and self-contained accommodation with floating support"
    _E1 = "Supported lodgings (accommodation, usually in a family home, where adult(s) in the “host family” provide formal advice and support)"
    _E2 = "Supported lodgings (accommodation, usually in a family home, where adult(s) in the “host family” provide formal advice and support)"
    _G1 = "Gone abroad"
    _G2 = "Gone abroad"
    _H1 = "Deported"
    _H2 = "Deported"
    _K1 = "Ordinary lodgings, without formal support"
    _K2 = "Ordinary lodgings, without formal support"
    _R1 = "Residence not known"
    _R2 = "Residence not known"
    _S1 = "No fixed abode / homeless"
    _S2 = "No fixed abode / homeless"
    _T1 = "Foyers and similar supported accommodation which combines the accommodation with opportunities for education, training or employment"
    _T2 = "Foyers and similar supported accommodation which combines the accommodation with opportunities for education, training or employment"
    _U1 = "Independent living, for example independent tenancy of flat, house or bedsit, including local authority or housing association tenancy, or accommodation provided by a college or university. Includes flat sharing"
    _U2 = "Independent living, for example independent tenancy of flat, house or bedsit, including local authority or housing association tenancy, or accommodation provided by a college or university. Includes flat sharing"
    _V1 = "Emergency accommodation (like a night shelter, direct access or emergency hostel)"
    _V2 = "Emergency accommodation (like a night shelter, direct access or emergency hostel)"
    _W1 = "Bed and breakfast"
    _W2 = "Bed and breakfast"
    _X1 = "In custody"
    _X2 = "In custody"
    _Y1 = "Other accommodation"
    _Y2 = "Other accommodation"
    _Z1 = "With former foster carer(s) - where the young person has been fostered and on turning 18 continues to remain with the same carer(s) who had fostered them immediately prior to their reaching legal adulthood, and where the plan for their care involves their remaining with this former foster family for the future. This code should not be used for 17-year-old care leavers. If the foster carer is also a relative this code should be used rather than ‘B - with parents or relatives’."
    _Z2 = "With former foster carer(s) - where the young person has been fostered and on turning 18 continues to remain with the same carer(s) who had fostered them immediately prior to their reaching legal adulthood, and where the plan for their care involves their remaining with this former foster family for the future. This code should not be used for 17-year-old care leavers. If the foster carer is also a relative this code should be used rather than ‘B - with parents or relatives’."

class ACTIVCodes(Enum):
    _0 = "Not in touch with the young person and do not know their activity, or the young person has died, or returned home to live with parents or someone with parental responsibility for a continuous period of 6 months or more."
    _F1 = "Young person engaged full time in higher education (for example studies beyond A level)"
    _F2 = "Young person engaged full time in education other than higher education"
    _F4 = "Young person engaged full time in an apprenticeship"
    _F3 = "Young person engaged full time in training or employment"
    _F5 = "Young person engaged full time in training or employment (not apprenticeship)"
    _G4 = "Young person not in education, employment or training because of illness or disability"
    _G5 = "Young person not in education, employment or training: other circumstances"
    _G6 = "Young person not in education, employment or training due to pregnancy or parenting"
    _P1 = "Young person engaged part time in higher education (for example studies beyond A level)"
    _P2 = "Young person engaged part time in education other than higher education"
    _P3 = "Young person engaged part time in training or employment"
    _P4 = "Young person engaged part time in an apprenticeship"
    _P5 = "Young person engaged part time in training or employment (not apprenticeship)"

class INTOUCHCodes(Enum):
    DIED = "Died after leaving care"
    NO = "No – not in touch"
    NREQ = "Young person no longer requires children’s social care services"
    REFU = "Young person refuses contact"
    RHOM = "Young person returned to live with parents or someone with parental responsibility for a continuous period of 6 months or more"
    YES = "Yes – in touch"

class LAPERMCodes(Enum):
    _999 = "Information not available"
    _NIR = "Northern Ireland"
    _nnn = "A valid local authority code, or 999"
    _NUK = "Outside of the UK"
    _SCO = "Scotland"
    _WAL = "Wales"
    _nan = "N/A"

class PREVPERMCodes(Enum):
    P1 = "Adoption"
    P2 = "Special guardianship order (SGO)"
    P3 = "Residence order (RO) or child arrangements order (CAO) which sets out with whom the child is to live."
    P4 = "Unknown"
    Z1 = "Child has not previously had a permanence option"

class REVIEWCODECodes(Enum):
    PN0 = "Child aged under 4 at the time of the review"
    PN1 = "Child physically attends and speaks for him or herself (Attendance)."
    PN2 = "Child physically attends and an advocate speaks on his or her behalf. (Attendance views represented by advocate or independent reviewing officer (IRO))"
    PN3 = "Child attends and conveys his or her view symbolically (non-verbally) (Attendance symbols)"
    PN4 = "Child physically attends but does not speak for him or herself, does not convey his or her view symbolically (non-verbally) and does not ask an advocate to speak for him or her (Attendance without contribution)"
    PN7 = "Child does not attend nor are his or her views conveyed to the review"
    PN5 = "Child does not attend physically but briefs an advocate to speak for him or her (Views represented by advocate or independent reviewing officer (IRO) through texting, written format, phone, audio/video, viewpoint"
    PN6 = "Child does not attend but conveys his or her feelings to the review by a facilitative medium (Texting the chair, written format, phone, audio/video, viewpoint)"


###########################
# Util Functions
###########################
def read_903(df):
    dfs = pd.read_excel(df, sheet_name=None)

    return dfs


def convert_dates(column):
    column_dt = pd.to_datetime(column, format="%d/%m/%Y", errors="coerce").dt.date
    return column_dt


def calculate_age_buckets(age):
    """Used to calculate age buckets for calculated ages in DataContainer"""
    if age < 5:
        return "a) Under 5 years"
    elif age < 11:
        return "b) 5 to 10 years"
    elif age < 16:
        return "c) 11 to 15 years"
    elif age < 20:
        return "d) 16 to 19 years"
    elif age >= 20:
        return "e) 20 years and over"
    else:
        return "f) Age error"


def make_year_buckets(years):
    """Used to make buckets for open plan lengths for named plans"""
    if years < 1:
        return "a) Less than 1 year"
    elif years < 2:
        return "b) 1-2 years"
    elif years < 3:
        return "c) 2-3 years"
    elif years < 4:
        return "d) 13-4 years"
    elif years < 5:
        return "e) 4-5 years"
    elif years < 6:
        return "f) 5-6 years"
    elif years < 7:
        return "g) 6-7 years"
    elif years < 8:
        return "h) 7-8 years"
    elif years < 9:
        return "i) 8-9 years"
    elif years < 10:
        return "j) 9-10 years"
    elif years < 11:
        return "k) 10-11 years"
    elif years < 12:
        return "l) 11-12 years"
    else:
        return "m) 12+ years"


###########################
# Datacontainer
###########################
class Datacontainer:
    """
    A container for 903data. Indexes data by table type. Provieds methods to extract key info,
    and returns each table as a property, enriched with key info for slicing and calculations.
    Enrichment includes mapping codes to descriptions, and adding columns necessary to work slicers to all tables.
    """

    def __init__(self, data_dict: dict):
        self.data = data_dict

    @property
    def enriched_header(self):
        enriched_df = self.data["header"].copy()

        enriched_df["SEX"] = [
            (
                "Male"
                if x in ["1", "M"]
                else ("Female" if x in ["2", "F"] else "SEX code error")
            )
            for x in enriched_df["SEX"].astype("str")
        ]

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["EthnicityGroup"] = enriched_df["ETHNIC"].apply(
            lambda x: EthnicSubcategories[x].value
        )

        enriched_df["UPN"] = enriched_df["UPN"].apply(
            lambda x: UPNCodes[x].value if pd.notnull(x) else "N/A"
        )

        enriched_df["MC_DOB_dt"] = convert_dates(enriched_df["MC_DOB"])

        return enriched_df

    @property
    def enriched_episodes(self):
        enriched_df = self.data["episodes"].copy()

        enriched_df["DECOM_dt"] = convert_dates(enriched_df["DECOM"])
        enriched_df["DEC_dt"] = convert_dates(enriched_df["DEC"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["RNE"] = enriched_df["RNE"].apply(
            lambda x: RNECodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["LS"] = enriched_df["LS"].apply(
            lambda x: LSCodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["CIN"] = enriched_df["CIN"].apply(
            lambda x: CINCodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["PLACE"] = enriched_df["PLACE"].apply(
            lambda x: PLACECodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["PLACE_PROVIDER"] = enriched_df["PLACE_PROVIDER"].apply(
            lambda x: PLACEPROVIDERCodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["REC"] = enriched_df["REC"].apply(
            lambda x: RECCodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["REASON_PLACE_CHANGE"] = enriched_df["REASON_PLACE_CHANGE"].apply(
            lambda x: REASONPLACECHANGECodes[x].value if pd.notnull(x) else "N/A"
        )

        return enriched_df

    @property
    def enriched_missing(self):
        enriched_df = self.data["missing"].copy()

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["MIS_START_dt"] = convert_dates(enriched_df["MIS_START"])
        enriched_df["MIS_END_dt"] = convert_dates(enriched_df["MIS_END"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["MISSING"] = enriched_df["MISSING"].apply(
            lambda x: MISSINGCodes[x].value if pd.notnull(x) else "N/A"
        )

        return enriched_df

    @property
    def enriched_oc2(self):
        enriched_df = self.data["oc2"].copy()

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["SDQ_REASON"] = enriched_df["SDQ_REASON"].apply(
            lambda x: SDQREASONCodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["CONVICTED"] = enriched_df["CONVICTED"].apply(
            lambda x: CONVICTEDCodes[f"_{int(x)}"].value if pd.notnull(x) else "N/A"
        )
        enriched_df["HEALTH_CHECK"] = enriched_df["HEALTH_CHECK"].apply(
            lambda x: HEALTHCHECKCodes[f"_{int(x)}"].value if pd.notnull(x) else "N/A"
        )
        enriched_df["IMMUNISATIONS"] = enriched_df["IMMUNISATIONS"].apply(
            lambda x: IMMUNISATIONCodes[f"_{int(x)}"].value if pd.notnull(x) else "N/A"
        )
        enriched_df["TEETH_CHECK"] = enriched_df["TEETH_CHECK"].apply(
            lambda x: TEETHCodes[f"_{int(x)}"].value if pd.notnull(x) else "N/A"
        )
        enriched_df["HEALTH_ASSESSMENT"] = enriched_df["HEALTH_ASSESSMENT"].apply(
            lambda x: (
                HEALTHASSESSMENTCodes[f"_{int(x)}"].value if pd.notnull(x) else "N/A"
            )
        )
        enriched_df["SUBSTANCE_MISUSE"] = enriched_df["SUBSTANCE_MISUSE"].apply(
            lambda x: SUBSTANCECodes[f"_{int(x)}"].value if pd.notnull(x) else "N/A"
        )
        enriched_df["INTERVENTION_RECEIVED"] = enriched_df[
            "INTERVENTION_RECEIVED"
        ].apply(
            lambda x: (
                INTERVENTIONRECEIVEDCodes[f"_{int(x)}"].value
                if pd.notnull(x)
                else "N/A"
            )
        )
        enriched_df["INTERVENTION_OFFERED"] = enriched_df["INTERVENTION_OFFERED"].apply(
            lambda x: (
                INTERVENTIONOFFEREDCodes[f"_{int(x)}"].value if pd.notnull(x) else "N/A"
            )
        )

        return enriched_df

    @property
    def enriched_oc3(self):
        enriched_df = self.data["oc3"].copy()

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["IN_TOUCH"] = enriched_df["IN_TOUCH"].apply(
            lambda x: INTOUCHCodes[x].value if pd.notnull(x) else "N/A"
        )
        enriched_df["ACTIV"] = enriched_df["ACTIV"].apply(
            lambda x: ACTIVCodes[f"_{x}"].value if pd.notnull(x) else "N/A"
        )
        enriched_df["ACCOM"] = enriched_df["ACCOM"].apply(
            lambda x: ACCOMCodes[f"_{x}"].value if pd.notnull(x) else "N/A"
        )
        return enriched_df

    @property
    def enriched_prev_perm(self):
        enriched_df = self.data["prev_perm"].copy()

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["PREV_PERM"] = enriched_df["PREV_PERM"].apply(
            lambda x: PREVPERMCodes[x].value if pd.notnull(x) else "N/A"
        )

        enriched_df["LA_PERM"] = enriched_df["LA_PERM"].astype("str").str.split(".", expand=True)[0]
        enriched_df["LA_PERM"] = enriched_df["LA_PERM"].apply(
            lambda x: x if x.isnumeric() else (LAPERMCodes[f"_{x}"].value if pd.notnull(x) else "N/A")
        )

        return enriched_df

    @property
    def enriched_reviews(self):
        enriched_df = self.data["reviews"].copy()

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["REVIEW_dt"] = convert_dates(enriched_df["REVIEW"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["REVIEW_CODE"] = enriched_df["REVIEW_CODE"].apply(
            lambda x: REVIEWCODECodes[x].value if pd.notnull(x) else "N/A"
        )

        return enriched_df

    @property
    def enriched_uasc(self):
        enriched_df = self.data["uasc"].copy()

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["DUC_dt"] = convert_dates(enriched_df["DUC"])
        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year

        enriched_df["SEX"] = [
            (
                "Male"
                if x in ["1", "M"]
                else ("Female" if x in ["2", "F"] else "SEX code error")
            )
            for x in enriched_df["SEX"].astype("str")
        ]


        return enriched_df


###########################
# Main App
###########################
st.title("903 drilldown tool")
st.markdown(
    "See an [explanation of why the tool is safe to use](https://www.datatoinsight.org/patch) on D2I's website."
)
st.markdown(
    "After file upload the page may take a few minutes to update whilst processing the data. \
    Even after the file upload bar finishes it will still take some time to process. \
    Refresh the page if uploading a new file."
)
st.markdown(
    "[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/015_SEN2_app/sen2_app.py)"
)

with st.expander("Instructions"):
    st.write("Instructions")

input_file = st.file_uploader("Upload processed 903 .xlsx here")


if input_file:
    dfs = read_903(input_file)

    ssda903 = Datacontainer(dfs)

    st.table(ssda903.enriched_uasc.head())
