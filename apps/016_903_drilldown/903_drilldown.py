####
# Notes
####

# Dropdown to choose stability type
# Some descriptive statistics about instability types (which years is it bad in etc.)
# Allow slicing instability by year

# change plot time to start of first year of data

import pandas as pd
import numpy as np
import datetime as dt
import calendar
from math import asin, cos, radians, sin, sqrt
import matplotlib.pyplot as plt


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

postcodes_url = open_url(
    "https://raw.githubusercontent.com/data-to-insight/patch/refs/heads/main/apps/016_903_drilldown/full_postcode_list_v2%201.csv"
)
postcodes = pd.read_csv(postcodes_url)

journey_events = {
    "decom": {"episodes": "DECOM"},
    "dec": {"episodes": "DEC"},
    "mis_start": {"missing": "MIS_START"},
    "mis_end": {"missing": "MIS_END"},
    "review": {"reviews": "REVIEW"},
}


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
    _F5 = (
        "Young person engaged full time in training or employment (not apprenticeship)"
    )
    _G4 = "Young person not in education, employment or training because of illness or disability"
    _G5 = "Young person not in education, employment or training: other circumstances"
    _G6 = "Young person not in education, employment or training due to pregnancy or parenting"
    _P1 = "Young person engaged part time in higher education (for example studies beyond A level)"
    _P2 = "Young person engaged part time in education other than higher education"
    _P3 = "Young person engaged part time in training or employment"
    _P4 = "Young person engaged part time in an apprenticeship"
    _P5 = (
        "Young person engaged part time in training or employment (not apprenticeship)"
    )


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
############################
def apply_filters(
    df,
    sex_selected,
    age_selected,
    ethnicity_selected,
):
    """Used to apply all filters to enriched tables"""
    df = df[
        df["SEX"].isin(sex_selected)
        & (df["Age (on return date)"] >= age_selected[0])
        & (df["Age (on return date)"] <= age_selected[1])
        & (df["EthnicityGroup"].isin(ethnicity_selected))
    ]

    return df


def make_bar(
    df,
    column,
    title,
    x_label="test",
    color_column="SEX",
    buckets=None,
    total_cohort=None,
    color_sequence=px.colors.qualitative.G10,
):
    """Used to make and format all bar charts in dashboard. Allows users to force 0
    counts on columns if needed. Also overlays data labels by adding a scatter trace as
    text."""
    # TODO refactor
    if (buckets != None) & ("Timeliness" not in color_column):
        # Makes an empty dataframe with column names according to specified buckets
        # to merge groupby to, in order to have rows for counts of zero which are then filled.
        values_df = pd.DataFrame({column: buckets})

        df_counts = (
            df.groupby([column, color_column])
            .size()
            .to_frame("Number of children")
            .reset_index()
        )
        df_counts = df_counts.merge(values_df, how="outer", on=column)
        df_counts["Number of children"] = (
            df_counts["Number of children"].fillna(0).astype("int")
        )
        df_counts[color_column].fillna("", inplace=True)
        df_sum = df_counts.groupby(column).sum()
        bar = px.bar(
            df_counts,
            x=column,
            y="Number of children",
            title=title,
            color=color_column,
            category_orders={"Sex": ["M", "F"], column: buckets},
            labels={column: x_label},
            color_discrete_sequence=color_sequence,
        )

        # Needed to add total stacked bar heights where we are using sex to split bars
        # Makes a scatter using text lined up with the top of the bar chart
        bar.add_trace(
            go.Scatter(
                mode="text",
                x=df_sum.index,
                y=df_sum["Number of children"].tolist(),
                text=[str(x) for x in df_sum["Number of children"].tolist()],
                textposition="bottom center",
                showlegend=False,
            )
        )

    elif "Timeliness" in color_column:
        # Makes an empty dataframe with column names according to specified buckets
        # to merge groupby to, in order to have rows for counts of zero which are then filled.
        values_df = pd.DataFrame({column: buckets})

        count_df = (
            timeliness_df.groupby([color_column, column])
            .size()
            .to_frame("Number of children")
            .reset_index()
        )
        count_df = values_df.merge(count_df, how="outer", on=column)
        count_df["Number of children"] = count_df["Number of children"].fillna(0)

        bar = go.Figure(
            px.bar(
                title=title,
                barmode="group",
                color_discrete_sequence=color_sequence,
            )
        )
        bar.add_trace(
            go.Bar(
                x=pd.Series(count_df[column][count_df[color_column] == "Timely"]),
                y=pd.Series(
                    count_df["Number of children"][count_df[color_column] == "Timely"]
                ),
                name="Timely",
                marker_color="#DC3912",
                text=pd.Series(
                    count_df["Number of children"][count_df[color_column] == "Timely"]
                ),
            )
        )
        bar.add_trace(
            go.Bar(
                x=pd.Series(count_df[column][count_df[color_column] == "Not timely"]),
                y=pd.Series(
                    count_df["Number of children"][
                        count_df[color_column] == "Not timely"
                    ]
                ),
                name="Not timely",
                marker_color="#3366CC",
                text=pd.Series(
                    count_df["Number of children"][
                        count_df[color_column] == "Not timely"
                    ]
                ),
            )
        )
        bar.update_xaxes(categoryorder="array", categoryarray=months)
        bar.update_layout(
            xaxis={"title": {"text": "Month"}},
            yaxis={"title": {"text": "Number of children"}},
        )

    elif not color_column:
        # Used to make charts not split by Sex, and without specified x-buckets
        df_counts = (
            df.groupby([column]).size().to_frame("Number of children").reset_index()
        )

        # Needed to add total stacked bar heights where we are using sex to split bars
        # Makes a scatter using text lined up with the top of the bar chart
        bar = px.bar(
            df_counts,
            x=column,
            y="Number of children",
            title=title,
            color=color_column,
            text="Number of children",
            category_orders={"Sex": ["M", "F"]},
            labels={column: x_label},
            color_discrete_sequence=color_sequence,
        )

    else:
        # Used to make charts with a specified sex value but no need to specify buckets.
        df_counts = (
            df.groupby([column]).size().to_frame("Number of children").reset_index()
        )
        df_counts["Percentage of children"] = (
            df_counts["Number of children"] / len(df) * 100
        )
        df_counts["Percentage of children"] = df_counts[
            "Percentage of children"
        ].astype("int")
        df_counts["Cohort"] = "Stability cohort"

        total_cohort_counts = (
            total_cohort.groupby([column])
            .size()
            .to_frame("Number of children")
            .reset_index()
        )
        total_cohort_counts["Percentage of children"] = (
            total_cohort_counts["Number of children"] / len(total_cohort) * 100
        )
        total_cohort_counts["Percentage of children"] = total_cohort_counts[
            "Percentage of children"
        ].astype("int")
        total_cohort_counts["Cohort"] = "All 903"

        # Needed to add total stacked bar heights where we are using sex to split bars
        # Makes a scatter using text lined up with the top of the bar chart above
        # df_sum = df_counts.groupby(column).sum()
        # cohort_sum = total_cohort_counts.groupby(column).sum()

        all_counts = pd.concat([df_counts, total_cohort_counts])
        # all_sum = pd.concat([df_sum, cohort_sum])

        bar = px.bar(
            all_counts,
            x=column,
            y="Percentage of children",
            # y="Number of children",
            title=title,
            color="Cohort",
            barmode="group",
            # category_orders={"Sex": ["M", "F"]},
            labels={column: x_label},
            color_discrete_sequence=color_sequence,
        )
        # bar.add_trace(
        #     go.Scatter(
        #         mode="text",
        #         x=all_sum.index,
        #         #y=df_sum["Number of children"].tolist(),
        #         y=all_sum["Percentage of children"].tolist(),
        #         # text=[str(x) for x in df_sum["Number of children"].tolist()],
        #         text=[str(x) for x in df_sum["Percentage of children"].tolist()],
        #         textposition="bottom center",
        #         showlegend=False,
        #     )
        # )

    bar.update_layout(
        template="seaborn",
        plot_bgcolor="lightgrey",
        paper_bgcolor="lightgrey",
        font_color="black",
        title_font_color="black",
        legend_font_color="black",
        legend_title_font_color="black",
    )
    return bar


def make_indicator(df, title):
    """Used to make and format indicators to display overall, male, and female counts for given columns.
    Will return no number if there are none of a given sex."""
    indicator = make_subplots(
        rows=3,
        cols=1,
        specs=[
            [{"type": "indicator"}],
            [{"type": "indicator"}],
            [{"type": "indicator"}],
        ],
    )

    indicator.update_layout(
        paper_bgcolor="lightgray", font=dict(size=18, color="black")
    )

    indicator.add_trace(
        go.Indicator(
            mode="number",
            value=len(df),
            title={"text": title},
        ),
        row=1,
        col=1,
    )

    if len(df[df["SEX"] == "Male"]) > 0:
        indicator.add_trace(
            go.Indicator(
                mode="number",
                value=len(df[df["SEX"] == "Male"]),
                title={"text": f"{title} - Male"},
            ),
            row=2,
            col=1,
        )
    if len(df[df["SEX"] == "Female"]) > 0:
        indicator.add_trace(
            go.Indicator(
                mode="number",
                value=len(df[df["SEX"] == "Female"]),
                title={"text": f"{title} - Female"},
            ),
            row=3,
            col=1,
        )

    return indicator


# @st.cache_data
def read_903(df):
    dfs = pd.read_excel(df, sheet_name=None)

    return dfs


def convert_dates(column):
    column_dt = pd.to_datetime(column, format="%d/%m/%Y", errors="coerce")  # .dt.date
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


def haversine(row):

    # Haversine formula for determining distance between two coordinates given by latitude and longitude. Calculates great circle distance between two points.
    # Imagine an isosceles triangle with one vertex on the centre of the Earth, two sides of length R (radius of Earth) and the other two vertices at the two
    # lat/long coordinates. This formula calculates the spherical distance between these two points on the arc described by the Earth's surface.
    # Probably overkill for this as we can approximate the UK to a flat plane (and postcode lat/long are approximate) but why not be accurate?
    # (Open to moving this function to somewhere more sensible if required)

    lat1 = row["LAT_HOME"]
    lon1 = row["LONG_HOME"]
    lat2 = row["LAT_PLACE"]
    lon2 = row["LONG_PLACE"]

    # Earth's radius in miles. For Earth radius in kilometers use 6372.8 km
    R = 3959.87433
    # Convert latitude and longitude values to radians
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Returns distance between points in miles (or km if R changed above)

    return R * c


def match_postcodes(df, postcodes):
    episodes = df
    # Match postcode to home and placement postcodes and calculate distance between them. Precision is probably no more than +/- 1 mile
    # as only uses first 4 or 5 characters of postcode.
    # Adds LAD and LA codes to each postcode.
    # Important metrics are:
    # placements > or < 20 miles from home
    # in/out of home LA (**not LAD**)

    # Merge in details for home postcode:
    # pcd8_TRIM : first 4/5 characters of postcode
    # lad25cd : Local Authority District (LAD) code
    # lat : approximate postcode latitude
    # long : approximate postcode longitude
    # CTYUA24CD : Local Authority (LA) code
    episodes_home = episodes.merge(
        postcodes[["pcd8_TRIM", "lad25cd", "lat", "long", "CTYUA24CD"]],
        how="left",
        left_on="HOME_POST",
        right_on="pcd8_TRIM",
    )

    # Rename merged columns
    episodes_home = episodes_home.rename(
        columns={
            "pcd8_TRIM": "HOME_POSTCODE",
            "lad25cd": "LAD_CODE_HOME",
            "lat": "LAT_HOME",
            "long": "LONG_HOME",
            "CTYUA24CD": "LA_CODE_HOME",
        }
    )

    # Repeats the above merge for placement postcode
    episodes_home_and_placement = episodes_home.merge(
        postcodes[["pcd8_TRIM", "lad25cd", "lat", "long", "CTYUA24CD"]],
        how="left",
        left_on="PL_POST",
        right_on="pcd8_TRIM",
    )

    episodes_home_and_placement = episodes_home_and_placement.rename(
        columns={
            "pcd8_TRIM": "PLACE_POSTCODE",
            "lad25cd": "LAD_CODE_PLACE",
            "lat": "LAT_PLACE",
            "long": "LONG_PLACE",
            "CTYUA24CD": "LA_CODE_PLACE",
        }
    )

    return episodes_home_and_placement


def build_903record(dfs_dict, events=journey_events):
    """
    Based on open source work by Social Finance for the AnnexA here:
    https://github.com/CSCDP/child-event-journeys/blob/master/functions/__init__.py
    Creates a flat file with three columns:
    1) child unique id
    2) Date
    3) Type
    Based on events in 903 lists defined in the events argument
    """

    # Create empty dataframe in which we'll drop our events
    df_list = []

    # Loop over our dictionary to populate the log
    for event in events:
        contents = events[event]
        list_number = list(contents.keys())[0]
        date_column = contents[list_number]

        # Load Annex A list
        df = dfs_dict[list_number]

        # Get date column information
        df.columns = [col.lower().strip() for col in df.columns]
        date_column_lower = date_column.lower()
        if date_column_lower in df.columns:
            df = df[df[date_column_lower].notnull()]
            df["Type"] = event
            df["Date"] = df[date_column_lower]
            df_list.append(df)
        else:
            print(
                ">>>>>  Could not find column {} in {}".format(date_column, list_number)
            )

    # Pull all events into a unique dataframe annexarecord
    ssda903record = pd.concat(df_list, sort=False)

    # Clean annexarecord
    # Define categories to be able to sort events
    ordered_categories = [
        "decom",
        "dec",
        "mis_start",
        "mis_end",
        "review",
    ]
    ssda903record.Type = ssda903record.Type.astype("category")
    ssda903record.Type.cat.set_categories(
        [c for c in ordered_categories if c in ssda903record.Type.unique()],
        inplace=True,
        ordered=True,
    )
    # Ensure dates are in the correct format
    ssda903record.Date = pd.to_datetime(ssda903record.Date)

    return ssda903record


def joined_string(series):
    """
    Based on open source work by Social Finance for the AnnexA here:
    https://github.com/CSCDP/child-event-journeys/blob/master/functions/__init__.py
    Turns all elements from a series into a string, joining elements with "->"
    """
    list_elements = series.tolist()
    return " -> ".join(list_elements)


def create_journeys(df):
    """
    Based on open source work by Social Finance for the AnnexA here:
    https://github.com/CSCDP/child-event-journeys/blob/master/functions/__init__.py
    """
    df = df[~df["Date"].isnull()]
    df = df[~df["Type"].isnull()]
    df = df.sort_values(["Date", "Type"])

    # Add new column showing each event in format [00-00-0000/event]
    df["TimeEvent"] = df.Date.astype(str) + "/" + df.Type.astype(str)

    # Create both long and reduced journeys
    grouped = df.groupby("child")
    journey_long = grouped["TimeEvent"].apply(joined_string)

    # Create new dataframe with both long and reduced journeys
    journeys_df = pd.DataFrame(
        {"Child journey": journey_long}, index=journey_long.index
    )

    # # Save to Excel
    # writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    # # Journeys
    # journeys_df.to_excel(writer, sheet_name='Child journeys')
    # # Events abbreviation
    # pd.DataFrame({'Event': list(events_map.keys()), 'Reduced': list(events_map.values())}).to_excel(writer, sheet_name='Legend', index=None)
    # writer.save()

    return journeys_df


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
    def end_of_latest_return(self):
        df = self.data["header"].copy()

        latest_year = df["YEAR"].max()

        end_of_latest_return = pd.to_datetime(f"{latest_year}/03/31")

        return end_of_latest_return

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
            lambda x: (
                UPNCodes[x].value
                if x in ["UN1", "UN2", "UN3", "UN4", "UN5"]
                else ("Has UPN" if pd.notnull(x) else "N/A")
            )
        )

        enriched_df["MC_DOB_dt"] = convert_dates(enriched_df["MC_DOB"])

        enriched_df["Age (on return date)"] = enriched_df.apply(
            lambda x: relativedelta(
                dt1=pd.to_datetime(x["YEAR"], format="%Y"), dt2=x["DOB_dt"]
            )
            .normalized()
            .years,
            axis=1,
        )
        enriched_df["AgeBuckets"] = enriched_df["Age (on return date)"].apply(
            calculate_age_buckets
        )

        return enriched_df

    @property
    def enriched_episodes(self):
        enriched_df = self.data["episodes"].copy()

        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year
        enriched_df["DECOM_dt"] = convert_dates(enriched_df["DECOM"])
        enriched_df["DEC_dt"] = convert_dates(enriched_df["DEC"])

        enriched_df.sort_values(["CHILD", "DECOM_dt"], inplace=True)
        enriched_df = enriched_df.merge(
            self.enriched_header[
                [
                    "CHILD",
                    "YEAR",
                    "DOB_dt",
                    "Age (on return date)",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "SEX",
                ]
            ],
            how="left",
            on=["CHILD", "YEAR"],
        )
        enriched_df.bfill(inplace=True)

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

        # Number of episodes
        enriched_df["Number of Episodes"] = enriched_df.groupby("CHILD").cumcount()
        enriched_df["Number of Episodes"] = enriched_df["Number of Episodes"] + 1

        enriched_df["Number of placements in following 12 months"] = enriched_df.apply(
            lambda x: len(
                enriched_df[
                    (enriched_df["CHILD"] == x["CHILD"])
                    & (
                        enriched_df["DECOM_dt"]
                        <= x["DECOM_dt"] + pd.DateOffset(months=12)
                    )
                    & (enriched_df["DECOM_dt"] >= x["DECOM_dt"])
                ]
            ),
            axis=1,
        )

        return enriched_df

    @property
    def enriched_missing(self):
        enriched_df = self.data["missing"].copy()

        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year
        enriched_df = enriched_df.merge(
            self.enriched_header[
                [
                    "CHILD",
                    "YEAR",
                    "Age (on return date)",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "SEX",
                ]
            ],
            how="left",
            on=["CHILD", "YEAR"],
        )

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["MIS_START_dt"] = convert_dates(enriched_df["MIS_START"])
        enriched_df["MIS_END_dt"] = convert_dates(enriched_df["MIS_END"])

        enriched_df["MISSING"] = enriched_df["MISSING"].apply(
            lambda x: MISSINGCodes[x].value if pd.notnull(x) else "N/A"
        )

        return enriched_df

    @property
    def enriched_oc2(self):
        enriched_df = self.data["oc2"].copy()

        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year
        enriched_df = enriched_df.merge(
            self.enriched_header[
                [
                    "CHILD",
                    "YEAR",
                    "Age (on return date)",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "SEX",
                ]
            ],
            how="left",
            on=["CHILD", "YEAR"],
        )

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])

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

        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year
        enriched_df = enriched_df.merge(
            self.enriched_header[
                [
                    "CHILD",
                    "YEAR",
                    "Age (on return date)",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "SEX",
                ]
            ],
            how="left",
            on=["CHILD", "YEAR"],
        )

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])

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

        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year
        enriched_df = enriched_df.merge(
            self.enriched_header[
                [
                    "CHILD",
                    "YEAR",
                    "Age (on return date)",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "SEX",
                ]
            ],
            how="left",
            on=["CHILD", "YEAR"],
        )

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])

        enriched_df["PREV_PERM"] = enriched_df["PREV_PERM"].apply(
            lambda x: PREVPERMCodes[x].value if pd.notnull(x) else "N/A"
        )

        enriched_df["LA_PERM"] = (
            enriched_df["LA_PERM"].astype("str").str.split(".", expand=True)[0]
        )
        enriched_df["LA_PERM"] = enriched_df["LA_PERM"].apply(
            lambda x: (
                x
                if x.isnumeric()
                else (LAPERMCodes[f"_{x}"].value if pd.notnull(x) else "N/A")
            )
        )

        return enriched_df

    @property
    def enriched_reviews(self):
        enriched_df = self.data["reviews"].copy()

        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year
        enriched_df = enriched_df.merge(
            self.enriched_header[
                [
                    "CHILD",
                    "YEAR",
                    "Age (on return date)",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "SEX",
                ]
            ],
            how="left",
            on=["CHILD", "YEAR"],
        )

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["REVIEW_dt"] = convert_dates(enriched_df["REVIEW"])

        enriched_df["REVIEW_CODE"] = enriched_df["REVIEW_CODE"].apply(
            lambda x: REVIEWCODECodes[x].value if pd.notnull(x) else "N/A"
        )

        return enriched_df

    @property
    def enriched_uasc(self):
        enriched_df = self.data["uasc"].copy()

        enriched_df["YEAR"] = pd.to_datetime(enriched_df["YEAR"], format="%Y").dt.year
        enriched_df = enriched_df.merge(
            self.enriched_header[
                [
                    "CHILD",
                    "YEAR",
                    "Age (on return date)",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "SEX",
                ]
            ],
            how="left",
            on=["CHILD", "YEAR"],
        )

        enriched_df["DOB_dt"] = convert_dates(enriched_df["DOB"])
        enriched_df["DUC_dt"] = convert_dates(enriched_df["DUC"])

        return enriched_df

    @property
    def gapminder_df(self):
        all_child_df = pd.DataFrame()

        head = self.enriched_header.copy()
        epis = self.data["episodes"].copy()
        df = epis.merge(head, on=["CHILD"], how="left")
        children = df["CHILD"].unique()

        df["DECOM_dt"] = convert_dates(df["DECOM"])
        df["DEC_dt"] = convert_dates(df["DEC"])

        df["DEC_cleaned"] = df["DEC_dt"].apply(
            lambda x: x if pd.notnull(x) else self.end_of_latest_return
        )

        df.sort_values("DECOM_dt", inplace=True, ascending=True)
        df["Number of Episodes"] = df.groupby("CHILD").cumcount()
        df["Number of Episodes"] = df["Number of Episodes"] + 1

        df["First DECOM"] = df.apply(
            lambda x: df[df["CHILD"] == x["CHILD"]]["DECOM_dt"].iloc[0], axis=1
        )
        df["Last DEC"] = df.apply(
            lambda x: df.sort_values("DEC_cleaned", ascending=False)[
                df["CHILD"] == x["CHILD"]
            ]["DEC_cleaned"].iloc[0],
            axis=1,
        )

        val = 0
        dfs_dict = {}
        for child in children:
            val += 1
            child_df = df[df["CHILD"] == child]
            dates = pd.date_range(
                start=child_df["First DECOM"].iloc[0],
                end=child_df["Last DEC"].iloc[0],
                freq="M",
            )
            dates_df = pd.DataFrame({"Days": dates, "CHILD": [child for date in dates]})
            # dates_df["Days_string"] = [
            #     str(str(x).split(" ")[0]).replace("-", "") for x in dates_df["Days"]
            # ]

            child_df = child_df.merge(dates_df, on=["CHILD"], how="outer").ffill()

            # child_df = child_df[(child_df["Days"] >= child_df["DECOM_dt"]) & (child_df["Days"] <= child_df["DEC_dt"])].copy()
            dfs_dict[val] = child_df

            # all_child_df = pd.concat([all_child_df, child_df])

        all_child_df = pd.concat(dfs_dict.values())
        all_child_df["Days_string"] = [
            str(str(x).split(" ")[0]).replace("-", "") for x in all_child_df["Days"]
        ]
        all_child_df = all_child_df[
            (all_child_df["Days"] >= all_child_df["DECOM_dt"])
            & (all_child_df["Days"] <= all_child_df["DEC_dt"])
        ].copy()
        all_child_df["Age (on day)"] = all_child_df.apply(
            lambda x: (x["Days"] - x["DOB_dt"]) / pd.Timedelta(days=365.25), axis=1
        )
        all_child_df["Time in care (on day)"] = all_child_df.apply(
            lambda x: (x["Days"] - x["First DECOM"]) / pd.Timedelta(days=1), axis=1
        )
        return all_child_df


# @st.cache_data
def convert_data(_dfs: pd.DataFrame):
    """Used to make input data python readable and to enable caching.
    Runs Datacontainer to read in SSDA903 as an object containing enriched and cleaned data.
    """
    datafiles = Datacontainer(_dfs)

    return datafiles


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

    ssda903 = convert_data(dfs)
    # ssda903 = Datacontainer(dfs)

    with st.sidebar:
        st.write("Make selections here:")

        sex_selected = st.sidebar.multiselect(
            "Select Sex",
            (ssda903.enriched_header["SEX"].unique()),
            default=(ssda903.enriched_header["SEX"].unique()),
        )

        age_selected = st.sidebar.slider(
            "Select age range (on day of census)",
            min_value=int(ssda903.enriched_header["Age (on return date)"].min()),
            max_value=int(ssda903.enriched_header["Age (on return date)"].max()),
            value=[0, int(ssda903.enriched_header["Age (on return date)"].max())],
        )

        ethnicity_selected = st.sidebar.multiselect(
            "Select ethnicities",
            (ssda903.enriched_header["EthnicityGroup"].unique()),
            default=(ssda903.enriched_header["EthnicityGroup"].unique()),
        )

    sliced_enriched_header = apply_filters(
        ssda903.enriched_header, sex_selected, age_selected, ethnicity_selected
    )

    sliced_enriched_episodes = ssda903.enriched_episodes  # apply_filters(
    #     ssda903.enriched_episodes,
    #     sex_selected,
    #     age_selected,
    #     ethnicity_selected
    # )

    # with st.expander("Gapminder"):
    #     test_df = ssda903.gapminder_df.sort_values("Days_string")

    #     plot = px.scatter(
    #         test_df,
    #         x="Age (on day)",
    #         y="Time in care (on day)",
    #         size="Number of Episodes",
    #         animation_frame="Days_string",
    #         animation_group="CHILD",
    #         range_y=[0, 5000],
    #         range_x=[0, 25],
    #         hover_name="CHILD",
    #         color="EthnicityGroup"
    #     )
    #     st.plotly_chart(plot)

    #     # st.table(test_df[test_df["CHILD"] == "L10197839"])

    # with st.expander("Journeys visualisation"):
    #     child = st.selectbox(
    #         "Select child by ID", options=list(sliced_enriched_header["CHILD"].unique())
    #     )

    #     record_dfs = {
    #         "episodes": ssda903.enriched_episodes[
    #             ssda903.enriched_episodes["CHILD"] == child
    #         ],
    #         "missing": ssda903.enriched_missing[
    #             ssda903.enriched_missing["CHILD"] == child
    #         ],
    #         "reviews": ssda903.enriched_reviews[
    #             ssda903.enriched_reviews["CHILD"] == child
    #         ],
    #         "uasc": ssda903.enriched_uasc[ssda903.enriched_uasc["CHILD"] == child],
    #         "header": sliced_enriched_header[sliced_enriched_header["CHILD"] == child],
    #     }

    #     record_dfs["episodes"]["DEC"].fillna(ssda903.end_of_latest_return, inplace=True)
    #     record_dfs["missing"]["MIS_END"].fillna(
    #         ssda903.end_of_latest_return, inplace=True
    #     )

    #     episodes_data = record_dfs["episodes"].copy()
    #     episodes_data.rename(
    #         columns={
    #             "DECOM": "Start",
    #             "DEC": "Finish",
    #         },
    #         inplace=True,
    #     )
    #     episodes_data["Task"] = "Episodes"

    #     missing_data = record_dfs["missing"].copy()
    #     missing_data.rename(
    #         columns={
    #             "MIS_START": "Start",
    #             "MIS_END": "Finish",
    #         },
    #         inplace=True,
    #     )
    #     missing_data["Task"] = "Missing"

    #     review_data = record_dfs["reviews"][["REVIEW", "REVIEW_CODE"]].copy()
    #     review_data["Finish"] = record_dfs["reviews"]["REVIEW"].copy()
    #     review_data["Finish"] = review_data["Finish"] + pd.DateOffset(days=1)
    #     review_data.rename(
    #         columns={
    #             "REVIEW": "Start",
    #         },
    #         inplace=True,
    #     )
    #     review_data["Task"] = "Reviews"

    #     uasc_data = record_dfs["uasc"].copy()
    #     uasc_data.rename(
    #         columns={
    #             "DUC": "Finish",
    #         },
    #         inplace=True,
    #     )
    #     uasc_data["Start"] = review_data["Finish"] - pd.DateOffset(days=1)
    #     missing_data["Task"] = "Missing"

    #     timelines_data = pd.concat([episodes_data, missing_data, review_data])

    #     fig = px.timeline(
    #         timelines_data,
    #         x_start="Start",
    #         x_end="Finish",
    #         y="Task",
    #         color="Task",
    #         hover_data=[
    #             "RNE",
    #             "LS",
    #             "PLACE",
    #             "PLACE_PROVIDER",
    #             "MISSING",
    #             "REVIEW_CODE",
    #         ],
    #     )
    #     st.plotly_chart(fig)

    #     st.table(
    #         record_dfs["header"][
    #             ["CHILD", "SEX", "ETHNIC", "UPN", "Age (on return date)"]
    #         ]
    #     )

    with st.expander("High Instability"):
        st.write(
            "All breakdowns shown for instability cohorts are the value for the first placement in a CYP's most unstable 12 month period. For example, if a child's CIN code before hteir most unstable 12 month period is 'neglect' that will be their value in the CIN chart below."
        )
        instability_df = ssda903.enriched_episodes.copy()

        highly_unstable_df = instability_df[
            (instability_df["Number of placements in following 12 months"] >= 5)
            & instability_df["DEC_dt"].notna()
        ]
        # most_unstbale placement is the one that preceeds a child's most unstable period
        most_unstable_placement = highly_unstable_df.sort_values(
            "Number of placements in following 12 months"
        ).drop_duplicates("CHILD", keep="first")

        highly_unstable_col1, highly_unstable_col2 = st.columns(2)

        with highly_unstable_col1:
            total_highly_unstable = make_indicator(
                most_unstable_placement,
                "Total children with at least one highly unstable 12 month period",
            )
            st.plotly_chart(total_highly_unstable, use_container_width=True)

            # Age
            highly_unstable_age = make_bar(
                most_unstable_placement,
                "AgeBuckets",
                title="Children still in care who have had highly unstable placements",
                x_label="Age group",
                total_cohort=instability_df,
            )
            st.plotly_chart(highly_unstable_age, use_container_width=True, theme=None)

            # Sex
            highly_unstable_sex = make_bar(
                most_unstable_placement,
                "SEX",
                title="Children still in care who have had highly unstable placements",
                x_label="Sex",
                total_cohort=instability_df,
            )
            st.plotly_chart(highly_unstable_sex, use_container_width=True, theme=None)

            # RNE
            highly_unstable_rne = make_bar(
                most_unstable_placement,
                "RNE",
                title="Children still in care who have had highly unstable placements",
                x_label="RNE",
                total_cohort=instability_df,
            )
            st.plotly_chart(highly_unstable_rne, use_container_width=True, theme=None)

        with highly_unstable_col2:
            highly_unstable_ethnicity = make_bar(
                most_unstable_placement,
                "EthnicityGroup",
                title="Children still in care who have had highly unstable placements",
                x_label="Ethnicity",
                total_cohort=instability_df,
            )
            st.plotly_chart(
                highly_unstable_ethnicity, use_container_width=True, theme=None
            )

            # LS
            highly_unstable_ls = make_bar(
                most_unstable_placement,
                "LS",
                title="Children still in care who have had highly unstable placements",
                x_label="LS",
                total_cohort=instability_df,
            )
            st.plotly_chart(highly_unstable_ls, use_container_width=True, theme=None)

            # CIN
            highly_unstable_cin = make_bar(
                most_unstable_placement,
                "CIN",
                title="Children still in care who have had highly unstable placements",
                x_label="CIN",
                total_cohort=instability_df,
                # buckets=[
                #     "M - maintain the EHC plan",
                #     "C - cease the EHC plan",
                #     "A - Amend the EHC plan",
                # ],
            )
            st.plotly_chart(highly_unstable_cin, use_container_width=True, theme=None)

            # Place
            highly_unstable_place = make_bar(
                most_unstable_placement,
                "PLACE",
                title="Children still in care who have had highly unstable placements",
                x_label="Place",
                total_cohort=instability_df,
                # buckets=[
                #     "M - maintain the EHC plan",
                #     "C - cease the EHC plan",
                #     "A - Amend the EHC plan",
                # ],
            )
            st.plotly_chart(highly_unstable_place, use_container_width=True, theme=None)
