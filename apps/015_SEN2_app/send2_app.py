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

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


class SENTypes(Enum):
    """Used to map SENtype codes to descriptions"""

    SPLD = "Specific learning difficulty"
    MLD = "Moderate learning difficulty"
    SLD = "Severe learning difficulty"
    PMLD = "Profound and multiple learning difficulty"
    SEMH = "Social, emotional and mental health"
    SLCN = "Speech, language and communication needs"
    HI = "Hearing impairment"
    VI = "Vision impairment"
    MSI = "Multi-sensory impairment"
    PD = "Physical disability"
    ASD = "Autistic spectrum disorder"
    DS = "Down Syndrome"
    OTH = "Other difficulty"


class SENSettings(Enum):
    """Used to map SEN setting codes to descriptions"""

    OLA = "Other (OLA)"
    OPA = "Other (OPA)"
    EHE = "Elective home education (EHE)"
    EYP = "Early years provider (EYP)"
    OTH = "Other (OTH)"
    NEET = "Not in education, employment, or training"
    NIEC = "Not in education or training - notice issued"
    NIEO = "Not in education or training - other"


class EthnicMaincategories(Enum):
    """Used to map ethnicity codes to main groups, uses long GIAS code-set"""

    WBRI = "White"
    WCOR = "White"
    WENG = "White"
    WNIR = "White"
    WSCO = "White"
    WWEL = "White"
    WOWB = "White"
    WIRI = "White"
    WIRT = "White"
    WOTH = "White"
    WALB = "White"
    WBOS = "White"
    WCRO = "White"
    WGRE = "White"
    WGRK = "White"
    WGRC = "White"
    WITA = "White"
    WKOS = "White"
    WPOR = "White"
    WSER = "White"
    WTUR = "White"
    WTUK = "White"
    WTUC = "White"
    WEUR = "White"
    WEEU = "White"
    WWEU = "White"
    WOTW = "White"
    WROM = "White"
    WROG = "White"
    WROR = "White"
    WROO = "White"
    MWBC = "Mixed"
    MWBA = "Mixed"
    MWAS = "Mixed"
    MWAP = "Mixed"
    MWAI = "Mixed"
    MWAO = "Mixed"
    ABRI = "Asian"
    AWEL = "Asian"
    MOTH = "Asian"
    MAOE = "Asian"
    MABL = "Asian"
    MACH = "Asian"
    MBOE = "Asian"
    MBCH = "Asian"
    MCOE = "Asian"
    MWOE = "Asian"
    MWCH = "Asian"
    MOTM = "Asian"
    AIND = "Asian"
    APKN = "Asian"
    AMPK = "Asian"
    AKPA = "Asian"
    AOPK = "Asian"
    ABAN = "Asian"
    AOTH = "Asian"
    AAFR = "Asian"
    AKAO = "Asian"
    ANEP = "Asian"
    ASNL = "Asian"
    ASLT = "Asian"
    ASRO = "Asian"
    AOTA = "Asian"
    BBRI = "Black"
    BWEL = "Black"
    BCRB = "Black"
    BAFR = "Black"
    BANN = "Black"
    BCON = "Black"
    BGHA = "Black"
    BNGN = "Black"
    BSLN = "Black"
    BSOM = "Black"
    BSUD = "Black"
    BAOF = "Black"
    BOTH = "Black"
    BEUR = "Black"
    BNAM = "Black"
    BOTB = "Black"
    CHNE = "Asian"
    CHKC = "Asian"
    CMAL = "Asian"
    CSNG = "Asian"
    CTWN = "Asian"
    COCH = "Asian"
    OOTH = "Other"
    OAFG = "Other"
    ORAB = "Other"
    OARA = "Other"
    OEGY = "Other"
    OFIL = "Other"
    OIRN = "Other"
    OIRQ = "Other"
    OJPN = "Other"
    OKOR = "Other"
    OKRD = "Other"
    OLAM = "Other"
    OLEB = "Other"
    OLIB = "Other"
    OMAL = "Other"
    OMRC = "Other"
    OPOL = "Other"
    OTHA = "Other"
    OVIE = "Other"
    OYEM = "Other"
    OOEG = "Other"
    NOBT = "Unclassified"
    REFU = "Unclassified"


class EthnicSubcategories(Enum):
    """Used to map ethnicity codes to main groups, uses long GIAS code-set"""

    WBRI = "White - British"
    WCOR = "White - British"
    WENG = "White - British"
    WNIR = "White - British"
    WSCO = "White - British"
    WWEL = "White - British"
    WOWB = "White - British"
    WIRI = "White"
    WIRT = "White"
    WOTH = "Any other white background"
    WALB = "Any other white background"
    WBOS = "Any other white background"
    WCRO = "Any other white background"
    WGRE = "Any other white background"
    WGRK = "Any other white background"
    WGRC = "Any other white background"
    WITA = "Any other white background"
    WKOS = "Any other white background"
    WPOR = "Any other white background"
    WSER = "Any other white background"
    WTUR = "Any other white background"
    WTUK = "Any other white background"
    WTUC = "Any other white background"
    WEUR = "Any other white background"
    WEEU = "Any other white background"
    WWEU = "Any other white background"
    WOTW = "Any other white background"
    WROM = "Gypsy/Roma"
    WROG = "Gypsy/Roma"
    WROR = "Gypsy/Roma"
    WROO = "Gypsy/Roma"
    MWBC = "White and Black Caribbean"
    MWBA = "White and Black African"
    MWAS = "White and Asian"
    MWAP = "White and Asian"
    MWAI = "White and Asian"
    MWAO = "White and Asian"
    ABRI = "Asian - British"
    AWEL = "Asian - Welsh"
    MOTH = "Any other mixed background"
    MAOE = "Any other mixed background"
    MABL = "Any other mixed background"
    MACH = "Any other mixed background"
    MBOE = "Any other mixed background"
    MBCH = "Any other mixed background"
    MCOE = "Any other mixed background"
    MWOE = "Any other mixed background"
    MWCH = "Any other mixed background"
    MOTM = "Any other mixed background"
    AIND = "Indian"
    APKN = "Pakistani"
    AMPK = "Pakistani"
    AKPA = "Pakistani"
    AOPK = "Pakistani"
    ABAN = "Bangladeshi"
    AOTH = "Any other Asian background"
    AAFR = "Any other Asian background"
    AKAO = "Any other Asian background"
    ANEP = "Any other Asian background"
    ASNL = "Any other Asian background"
    ASLT = "Any other Asian background"
    ASRO = "Any other Asian background"
    AOTA = "Any other Asian background"
    BBRI = "Black - British"
    BWEL = "Black - Welsh"
    BCRB = "Black Caribbean"
    BAFR = "Black - African"
    BANN = "Black - African"
    BCON = "Black - African"
    BGHA = "Black - African"
    BNGN = "Black - African"
    BSLN = "Black - African"
    BSOM = "Black - African"
    BSUD = "Black - African"
    BAOF = "Black - African"
    BOTH = "Any other black background"
    BEUR = "Any other black background"
    BNAM = "Any other black background"
    BOTB = "Any other black background"
    CHNE = "Chinese"
    CHKC = "Chinese"
    CMAL = "Chinese"
    CSNG = "Chinese"
    CTWN = "Chinese"
    COCH = "Chinese"
    OOTH = "Any other ethnic group"
    OAFG = "Any other ethnic group"
    ORAB = "Any other ethnic group"
    OARA = "Any other ethnic group"
    OEGY = "Any other ethnic group"
    OFIL = "Any other ethnic group"
    OIRN = "Any other ethnic group"
    OIRQ = "Any other ethnic group"
    OJPN = "Any other ethnic group"
    OKOR = "Any other ethnic group"
    OKRD = "Any other ethnic group"
    OLAM = "Other ethnic group"
    OLEB = "Any other ethnic group"
    OLIB = "Any other ethnic group"
    OMAL = "Any other ethnic group"
    OMRC = "Any other ethnic group"
    OPOL = "Any other ethnic group"
    OTHA = "Any other ethnic group"
    OVIE = "Any other ethnic group"
    OYEM = "Any other ethnic group"
    OOEG = "Any other ethnic group"
    REFU = "Refused"
    NOBT = "Information not yet obtained"


###################
# Util functions
###################
def apply_filters(
    df,
    sex_selected,
    age_selected,
    ethnicity_selected,
    sen_type_selected,
    sen_setting_selected,
    plan_length,
):
    """Used to apply all filters to enriched tables"""
    df = df[
        df["Sex"].isin(sex_selected)
        & (df["Age"] >= age_selected[0])
        & (df["Age"] <= age_selected[1])
        & (df["EthnicitySubGroup"].isin(ethnicity_selected))
        & (df["SENtype"].isin(sen_type_selected))
        & (df["SENSetting_mapped"].isin(sen_setting_selected))
        & (df["NamedPlanLength (days)"] >= plan_length[0])
        & (df["NamedPlanLength (days)"] <= plan_length[1])
    ]

    return df


@st.cache_data
def read_lookups():
    """Reads lookups for the URN, and UKPRNs to map SENsettings, also reads LA names and codes to map transfers.

    Input data will need to be updates as URNs, UKPRNs and LA codes change.

    We need to use open_url from pyodide so we can open https urls.
    """
    urn_url = open_url(
        "https://raw.githubusercontent.com/data-to-insight/patch/refs/heads/main/apps/015_SEN2_app/urn_ukprn_lookups.csv"
    )
    la_names_url = open_url(
        "https://raw.githubusercontent.com/data-to-insight/patch/refs/heads/main/apps/015_SEN2_app/la_names_lookup.csv"
    )
    urn_ukprn_lookups = pd.read_csv(urn_url)
    la_names_lookups = pd.read_csv(la_names_url)

    la_names_lookups["LA code"] = la_names_lookups["LA code"].astype("str")

    # Turn the dfs into dictionaries for easier mapping rather than merging in the
    # relevant function
    urn_lookup = dict(
        zip(
            urn_ukprn_lookups["URN"].astype("float"),
            urn_ukprn_lookups["TypeOfEstablishment (name)"],
        )
    )
    ukprn_lookup = dict(
        zip(
            urn_ukprn_lookups["UKPRN"].astype("float"),
            urn_ukprn_lookups["TypeOfEstablishment (name)"],
        )
    )

    return urn_lookup, ukprn_lookup, la_names_lookups


def map_sen_settings(row):
    """Takes rows of Named and Active plans. Looks at values in URN, UKPRN and then SENSetting
    to determine overall SEN setting according to item 5.7 <PlacementDetail>.

    Tries checks if there is a URN, then UKPRN, then SENSetting to match, in that order of
    priority. Returns error to front end charts if there is no matching code.
    """
    if pd.notnull(row["URN"]):
        try:
            return urn_lookup[float(row["URN"])]
        except:
            return f"URN match not found for {row['URN']}"
    elif pd.notnull(row["UKPRN"]):
        try:
            return ukprn_lookup[float(row["UKPRN"])]
        except:
            return f"UKPRN match not found for {row['UKPRN']}"
    elif pd.notnull(row["SENSetting"]):
        if row["SENSetting"] in [
            "Other (OLA)",
            "Other (OPA)",
            "Elective home education (EHE)",
            "Early years provider (EYP)",
            "Other (OTH)",
            "Not in education, employment, or training",
            "Not in education or training - notice issued",
            "Not in education or training - other",
        ]:
            return SENSettings[row].value
        else:
            return "SEN setting not found"
    else:
        return "SEN setting not found"


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


def request_days_buckets(days):
    """Used to calculate time buckets for time between ReceivedDate and
    OutcomeDate in enriched_requests in DataContainer"""
    if days < 10:
        return "a) Under 10 days"
    elif days < 21:
        return "b) 10 to 20 days"
    elif days < 31:
        return "c) 21 to 30 days"
    elif days < 41:
        return "d) 31 to 40 days"
    elif days < 51:
        return "e) 41 to 50 days"
    elif days < 61:
        return "f) 51 to 60 days"
    elif days >= 61:
        return "g) 61+ days"
    else:
        return "x) Request incomplete"


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


def make_bar(df, column, title, x_label="test", color_column="Sex", buckets=None):
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
            color_discrete_sequence=px.colors.qualitative.G10,
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
                color_discrete_sequence=px.colors.qualitative.G10,
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
            color_discrete_sequence=px.colors.qualitative.G10,
        )

    else:
        # Used to make charts with a specified sex value but no need to specify buckets.
        df_counts = (
            df.groupby([column, color_column])
            .size()
            .to_frame("Number of children")
            .reset_index()
        )

        # Needed to add total stacked bar heights where we are using sex to split bars
        # Makes a scatter using text lined up with the top of the bar chart above
        df_sum = df_counts.groupby(column).sum()
        bar = px.bar(
            df_counts,
            x=column,
            y="Number of children",
            title=title,
            color=color_column,
            category_orders={"Sex": ["M", "F"]},
            labels={column: x_label},
            color_discrete_sequence=px.colors.qualitative.G10,
        )
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

    if len(df[df["Sex"] == "M"]) > 0:
        indicator.add_trace(
            go.Indicator(
                mode="number",
                value=len(df[df["Sex"] == "M"]),
                title={"text": f"{title} - Male"},
            ),
            row=2,
            col=1,
        )
    if len(df[df["Sex"] == "F"]) > 0:
        indicator.add_trace(
            go.Indicator(
                mode="number",
                value=len(df[df["Sex"] == "F"]),
                title={"text": f"{title} - Female"},
            ),
            row=3,
            col=1,
        )

    return indicator


###################
# Ingress
###################


def get_values(xml_elements, table_dict: dict, xml_block):
    """Used to find all values in XML elements/messages to return dicts ready to convert to dfs."""
    for element in xml_elements:
        try:
            table_dict[element] = xml_block.find(element).text
        except:
            table_dict[element] = pd.NA
    return table_dict


class XMLtoDF:
    """Uses Element Tree to read in the XML as tables, flattened when needed. If children have
    multiple of a message, it will appear on multiple rows, which will need to be sliced appropriately for different charts/calculations.
    """

    header = pd.DataFrame(columns=["Collection", "Year", "ReferenceDate"])

    # columns and info can be found:
    # https://assets.publishing.service.gov.uk/media/6937018aa6fc97b81e5743a7/Special_educational_needs_survey_guide_2026.pdf
    persons = pd.DataFrame(
        columns=[
            "Surname",
            "Forename",
            "PersonBirthDate",
            "Sex",
            "Ethnicity",
            "PostCode",
            "UPN",
            "UniqueLearnerNumber",
            "UPNunknown",
        ]
    )

    requests = pd.DataFrame(
        columns=[
            "ReceivedDate",
            "RequestSource",
            "RYA",
            "RequestOutcomeDate",
            "RequestOutcome",
            "RequestMediation",
            "RequestTribunal",
            "Exported",
        ]
    )

    assessments = pd.DataFrame(
        columns=[
            "AssessmentOutcome",
            "AssessmentOutcomeDate",
            "AssessmentMediation",
            "AssessmentTribunal",
            "OtherMediation",
            "OtherTribunal",
            "Week20",
        ]
    )

    named_plan = pd.DataFrame(
        columns=[
            "StartDate",
            "URN",
            "UKPRN",
            "SENSetting",
            "PlacementRank",
            "SENunitIndicator",
            "ResourcedProvisionIndicator",
            "PlanRes",
            "PlanWPB",
            "PB",
            "OA",
            "DP",
            "CeaseDate",
            "CeaseReason",
        ]
    )

    active_plans = pd.DataFrame(
        columns=[
            "TransferLA",
            "URN",
            "UKPRN",
            "SENSetting",
            "SENSettingOther",
            "PlacementRank",
            "EntryDate",
            "LeavingDate",
            "SENunitIndicator",
            "ResourcedProvisionIndicator",
            "RES",
            "WPB",
            "SENtype",
            "SENtypeRank",
            "ReviewMeeting",
            "ReviewOutcome",
            "LastReview",
        ]
    )

    def __init__(self, root):
        self.child_id = 0
        header = root.find("Header")
        self.header = self.create_header(header)
        self.name = None

        children = root.find("Persons")
        self.total_children = len(children)

        for child in children.findall("Person"):
            self.create_child(child)

        self.named_plan = self.named_plan[self.named_plan["StartDate"].notna()].copy()

    def create_header(self, header):
        header_dict = {}
        collection_details = header.find("CollectionDetails")
        collection_elements = ["Collection", "Year", "ReferenceDate"]
        header_dict = get_values(collection_elements, header_dict, collection_details)

        source = header.find("Source")
        source_elements = [
            "SourceLevel",
            "LEA",
            "SoftwareCode",
            "Release",
            "SerialNo",
            "DateTime",
        ]
        header_dict = get_values(source_elements, header_dict, source)

        header_df = pd.DataFrame.from_dict([header_dict])
        return header_df

    def create_child(self, person):
        self.create_person(person)
        self.create_requests(person)

    def create_person(self, child):
        forename = child.find("Forename").text
        surname = child.find("Surname").text
        self.name = f"{forename} {surname}"
        self.child_id += 1
        person_dict = {}
        elements = self.persons.columns
        person_dict = get_values(elements, person_dict, child)
        person_dict["child_id"] = self.child_id

        persons_df = pd.DataFrame.from_dict([person_dict])
        self.persons = pd.concat([self.persons, persons_df], ignore_index=True)

    def create_requests(self, child):
        self.requests_id = 0
        elements = self.requests.columns
        requests_list = []

        requests = child.findall("Requests")
        for request in requests:
            requests_dict = {}
            self.requests_id += 1

            requests_dict = get_values(elements, requests_dict, request)

            requests_dict["child_id"] = self.child_id
            requests_dict["requests_id"] = self.requests_id

            requests_list.append(requests_dict)

            self.create_assessments(request)
            self.create_active_plans(request)

        requests_df = pd.DataFrame(requests_list)
        self.requests = pd.concat([self.requests, requests_df], ignore_index=True)

    def create_assessments(self, request):
        assessment_list = []
        elements = self.assessments.columns
        self.assessment_id = 0

        assessments = request.findall("Assessment")

        for assessment in assessments:

            # assessments
            self.assessment_id += 1
            assessment_dict = {}

            assessment_dict = get_values(elements, assessment_dict, assessment)

            assessment_dict["name"] = self.name
            assessment_dict["child_id"] = self.child_id
            assessment_dict["requests_id"] = self.requests_id
            assessment_dict["assessment_id"] = self.assessment_id

            assessment_list.append(assessment_dict)

            # named_plans
            self.create_named_plan(assessment)

        assessment_df = pd.DataFrame(assessment_list)
        self.assessments = pd.concat(
            [self.assessments, assessment_df], ignore_index=True
        )

    def create_named_plan(self, assessment):

        named_plan_elements = [
            "StartDate",
            "PlanRes",
            "PlanWPB",
            "PB",
            "OA",
            "DP",
            "CeaseDate",
            "CeaseReason",
        ]
        named_plan_dict = {}

        plan_detail_elements = [
            "URN",
            "UKPRN",
            "SENSetting",
            "SENSettingOther",
            "PlacementRank",
            "SENunitIndicator",
            "ResourcedProvisionIndicator",
        ]

        named_plan_locs = assessment.find("NamedPlan")
        plan_detail_list = []

        if named_plan_locs is not None:
            for plan_detail in named_plan_locs.findall("PlanDetail"):
                named_plan_dict = get_values(
                    named_plan_elements, named_plan_dict, named_plan_locs
                )

                named_plan_dict = get_values(
                    plan_detail_elements, named_plan_dict, plan_detail
                )
                named_plan_dict["name"] = self.name
                named_plan_dict["child_id"] = self.child_id
                named_plan_dict["requests_id"] = self.requests_id
                named_plan_dict["assessment_id"] = self.assessment_id

                plan_detail_list.append(named_plan_dict)

            named_plan_df = pd.DataFrame(plan_detail_list)
            self.named_plan = pd.concat(
                [self.named_plan, named_plan_df], ignore_index=True
            )

    def create_active_plans(self, request):
        active_plans_list = []

        active_plan_elements = [
            "TransferLA",
            "RES",
            "WPB",
            "ReviewMeeting",
            "ReviewOutcome",
            "LastReview",
        ]
        placement_detail_elements = [
            "URN",
            "SENSetting",
            "SENSettingOther",
            "PlacementRank",
            "EntryDate",
            "LeavingDate",
            "SENunitIndicator",
            "ResourcedProvisionIndicator",
        ]
        sen_need_elements = ["SENtype", "SENtypeRank"]

        active_plan_locs = request.find("ActivePlans")
        if active_plan_locs is not None:
            placement_detail_locs = active_plan_locs.findall("PlacementDetail")
            sen_need_locs = active_plan_locs.find("SENneed")

            for placement_detail in placement_detail_locs:
                active_plans_dict = {}
                active_plans_dict = get_values(
                    active_plan_elements, active_plans_dict, active_plan_locs
                )
                active_plans_dict = get_values(
                    placement_detail_elements, active_plans_dict, placement_detail
                )
                active_plans_dict = get_values(
                    sen_need_elements, active_plans_dict, sen_need_locs
                )
                active_plans_dict["name"] = self.name
                active_plans_dict["child_id"] = self.child_id
                active_plans_dict["requests_id"] = self.requests_id

                active_plans_list.append(active_plans_dict)

            active_plan_df = pd.DataFrame(active_plans_list)
            self.active_plans = pd.concat(
                [self.active_plans, active_plan_df], ignore_index=True
            )


@st.cache_data
def convert_data(_root: ET.Element):
    """Used to make input data python readable and to enable caching.
    Runs XMLtoDF to read in SEN2 XML as a dictionary of dataframes, ready to be passed to DataContainer for cleaning.
    """
    datafiles = XMLtoDF(_root)

    return datafiles


###########################
# Datacontainer
###########################
class Datacontainer:
    """
    A container for SEN2 data. Indexes data by table type. Provieds methods to extract key info,
    and returns each table as a property, enriched with key info for slicing and calculations.
    Enrichment includes mapping codes to descriptions, and adding columns necessary to work slicers to all tables.
    """

    def __init__(self, data_dict: dict):
        self.data = data_dict

        self.reference_period = self._get_reference_period(self.data.header)

        self.persons = self.data.persons

    def _get_reference_period(self, df):
        """Takes the Year value from the header and uses it to set the reference period start and end dates."""
        year = int(df["Year"].iloc[0])

        start = pd.to_datetime(f"{str(year-1)}-01-01", format=f"%Y-%m-%d")
        end = pd.to_datetime(f"{str(year-1)}-12-31", format=f"%Y-%m-%d")

        reference_period = {"start": start, "end": end}

        return reference_period

    @property
    def enriched_persons(self):
        enriched_df = self.data.persons.copy()
        enriched_df["EthnicityGroup"] = enriched_df["Ethnicity"].apply(
            lambda x: EthnicMaincategories[x].value
        )

        enriched_df["EthnicitySubGroup"] = enriched_df["Ethnicity"].apply(
            lambda x: EthnicSubcategories[x].value
        )

        enriched_df["PersonBirthDate_dt"] = pd.to_datetime(
            enriched_df["PersonBirthDate"], format="%Y-%m-%d"
        )
        enriched_df["Age"] = enriched_df["PersonBirthDate_dt"].apply(
            lambda x: relativedelta(dt1=self.reference_period["end"], dt2=x)
            .normalized()
            .years
        )
        enriched_df["AgeBuckets"] = enriched_df["Age"].apply(calculate_age_buckets)

        # Get just the primary needs and sen settings for slicing and map to descriptions
        sen_types = self.data.active_plans[
            self.data.active_plans["SENtypeRank"].astype("str") == "1"
        ][["child_id", "SENtype", "EntryDate", "URN", "UKPRN", "SENSetting"]]
        sen_types["EntryDate"] = pd.to_datetime(
            sen_types["EntryDate"], format="%Y-%m-%d"
        )
        sen_types.sort_values(["EntryDate"], ascending=False, inplace=True)
        sen_types.drop_duplicates(subset="child_id", keep="first", inplace=True)
        sen_types = sen_types[
            [
                "child_id",
                "SENtype",
                "SENSetting",
                "URN",
                "UKPRN",
            ]
        ]
        enriched_df = enriched_df.merge(sen_types, on="child_id", how="left")

        enriched_df["SENtype"] = enriched_df["SENtype"].apply(
            lambda x: SENTypes[x.upper()].value if pd.notnull(x) else "Not yet determined"
        )
        enriched_df["SENSetting_mapped"] = enriched_df.apply(map_sen_settings, axis=1)

        # Get named plan lengths from named plans
        plan_lengths = self.data.named_plan[
            self.data.named_plan["PlacementRank"].astype("str") == "1"
        ][["child_id", "StartDate", "CeaseDate"]]

        plan_lengths["StartDate"] = pd.to_datetime(
            plan_lengths["StartDate"], format="%Y-%m-%d", errors="coerce"
        )
        plan_lengths["CeaseDate"] = pd.to_datetime(
            plan_lengths["CeaseDate"], format="%Y-%m-%d", errors="coerce"
        )

        plan_lengths["StartDate (month)"] = plan_lengths["StartDate"].dt.month

        plan_lengths["CeaseDate"].fillna(self.reference_period["end"], inplace=True)

        plan_lengths["NamedPlanLength (days)"] = (
            plan_lengths["CeaseDate"] - plan_lengths["StartDate"]
        ) / pd.Timedelta(days=1)

        plan_lengths["NamedPlanLength (years)"] = (
            plan_lengths["NamedPlanLength (days)"] / 365.25
        )

        plan_lengths["NamedPlanLength (years)"] = plan_lengths[
            "NamedPlanLength (years)"
        ].apply(make_year_buckets)
        enriched_df = enriched_df.merge(
            plan_lengths[
                ["child_id", "NamedPlanLength (days)", "NamedPlanLength (years)"]
            ],
            how="left",
            on="child_id",
        )

        return enriched_df

    @property
    def enriched_requests(self):
        enriched_df = self.data.requests[
            self.data.requests["ReceivedDate"].notna()
        ].copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[
                [
                    "Age",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "EthnicitySubGroup",
                    "Sex",
                    "child_id",
                    "SENtype",
                    "SENSetting_mapped",
                    "NamedPlanLength (days)",
                ]
            ],
            how="left",
            on="child_id",
        )

        enriched_df[["RequestSource", "RequestMediation", "RequestTribunal"]] = (
            enriched_df[
                ["RequestSource", "RequestMediation", "RequestTribunal"]
            ].astype("str")
        )
        enriched_df["RequestSource"] = enriched_df["RequestSource"].map(
            {
                "1": "Young person or parent",
                "2": "School or other education setting",
                "3": "Health care professionals",
                "4": "Social care professionals",
                "5": "Other",
            }
        )
        enriched_df["RequestSource"] = enriched_df["RequestSource"].astype("str")

        enriched_df["MediationOrTribunal"] = enriched_df.apply(
            lambda x: (
                "Mediation"
                if (x["RequestMediation"] == "1")
                else "Tribunal" if (x["RequestTribunal"] == "1") else "No"
            ),
            axis=1,
        )

        enriched_df["ReceivedDate"] = pd.to_datetime(
            enriched_df["ReceivedDate"], format="%Y-%m-%d", errors="coerce"
        )
        enriched_df["RequestOutcomeDate"] = pd.to_datetime(
            enriched_df["RequestOutcomeDate"], format="%Y-%m-%d", errors="coerce"
        )

        enriched_df["RequestLength"] = (
            enriched_df["RequestOutcomeDate"] - enriched_df["ReceivedDate"]
        ).dt.days.to_list()

        enriched_df["RequestLengthBucket"] = enriched_df["RequestLength"].apply(
            request_days_buckets
        )

        enriched_df["RYA"] = (
            enriched_df["RYA"].astype("str").map({"0": "No", "1": "Yes"})
        )

        enriched_df["Exported"] = [
            "No" if pd.isnull(col) else "Yes" for col in enriched_df["Exported"]
        ]

        enriched_df["ReceivedDate_month"] = enriched_df["ReceivedDate"].apply(
            lambda x: calendar.month_name[x.month] if pd.notnull(x) else pd.NaT
        )

        return enriched_df

    @property
    def enriched_assessments(self):
        enriched_df = self.data.assessments.copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[
                [
                    "Age",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "EthnicitySubGroup",
                    "Sex",
                    "child_id",
                    "SENtype",
                    "SENSetting_mapped",
                    "NamedPlanLength (days)",
                ]
            ],
            how="left",
            on="child_id",
        )

        enriched_df["AssessmentOutcomeDate"] = pd.to_datetime(
            enriched_df["AssessmentOutcomeDate"], format="%Y-%m-%d", errors="coerce"
        )

        enriched_df["AssessmentOutcomeDate_month"] = enriched_df[
            "AssessmentOutcomeDate"
        ].apply(lambda x: calendar.month_name[x.month] if pd.notnull(x) else pd.NaT)

        enriched_df["MediationOrTribunal"] = enriched_df.apply(
            lambda x: (
                "Assessment Mediation"
                if (x["AssessmentOutcome"] != "H") & (x["AssessmentMediation"] == "1")
                else (
                    "Assessment Tribunal"
                    if (x["AssessmentOutcome"] != "H")
                    & (x["AssessmentTribunal"] == "1")
                    else (
                        "Other Mediation"
                        if (x["AssessmentOutcome"] != "H")
                        & (x["OtherMediation"] == "1")
                        else (
                            "Other Tribunal"
                            if (x["AssessmentOutcome"] != "H")
                            & (x["OtherTribunal"] == "1")
                            else "No"
                        )
                    )
                )
            ),
            axis=1,
        )

        enriched_df["Week20"] = enriched_df.apply(
            lambda x: (
                "Yes"
                if (x["AssessmentOutcome"] != "H") & (x["Week20"] == "1")
                else "No"
            ),
            axis=1,
        )

        return enriched_df

    @property
    def enriched_named_plan(self):
        enriched_df = self.data.named_plan.copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[
                [
                    "Age",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "EthnicitySubGroup",
                    "Sex",
                    "child_id",
                    "SENtype",
                    "SENSetting_mapped",
                    "NamedPlanLength (years)",
                    "NamedPlanLength (days)",
                ]
            ],
            how="left",
            on="child_id",
        )

        enriched_df["CeaseReason"] = enriched_df["CeaseReason"].astype("str")
        enriched_df["CeaseReason"] = enriched_df["CeaseReason"].map(
            {
                "1": "1) Reached maximum age",
                "2": "2) Need met w/o EHC",
                "3": "3) Moved to HE",
                "4": "4) Moved to paid employment/apprenticeships",
                "5": "5) Transferred",
                "6": "6) No longer wishes to engage",
                "7": "7) Moved outside of England",
                "8": "8) Deceased",
                "9": "9) Other",
            }
        )

        enriched_df["StartDate"] = pd.to_datetime(
            enriched_df["StartDate"], format="%Y-%m-%d", errors="coerce"
        )

        enriched_df["StartDate_year"] = enriched_df["StartDate"].dt.year
        enriched_df["StartDate_month"] = enriched_df["StartDate"].apply(
            lambda x: calendar.month_name[x.month] if pd.notnull(x) else pd.NaT
        )

        enriched_df["CeaseDate"] = pd.to_datetime(
            enriched_df["CeaseDate"], format="%Y-%m-%d", errors="coerce"
        )

        enriched_df["CeaseDate_year"] = enriched_df["CeaseDate"].dt.year
        enriched_df["CeaseDate_month"] = enriched_df["CeaseDate"].apply(
            lambda x: calendar.month_name[x.month] if pd.notnull(x) else pd.NaT
        )

        enriched_df["PlanRes"].fillna("Non-residential", inplace=True)
        enriched_df["PlanRes"] = enriched_df["PlanRes"].map(
            {"A": "38 to 51 weeks", "B": "52 weeks"}
        )

        enriched_df["PlacementRank"] = enriched_df["PlacementRank"].astype("str")

        enriched_df["SENSetting_np"] = enriched_df.apply(map_sen_settings, axis=1)

        return enriched_df

    @property
    def enriched_active_plans(self):
        enriched_df = self.data.active_plans.copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[
                [
                    "Age",
                    "AgeBuckets",
                    "EthnicityGroup",
                    "EthnicitySubGroup",
                    "Sex",
                    "child_id",
                    "SENSetting_mapped",
                    "NamedPlanLength (days)",
                ]
            ],
            how="left",
            on="child_id",
        )

        enriched_df["PlanOpen"] = enriched_df["LeavingDate"].apply(
            lambda x: "Closed" if pd.isnull(x) else "Open"
        )

        enriched_df["RES"].fillna("Not applicable", inplace=True)
        enriched_df["WPB"].fillna("Not applicable", inplace=True)

        enriched_df["ReviewMeeting"].fillna("Not applicable", inplace=True)
        enriched_df["ReviewOutcome"] = enriched_df["ReviewOutcome"].map({                    
                    "M":"M - maintain the EHC plan",
                    "C":"C - cease the EHC plan",
                    "A":"A - Amend the EHC plan",})
        enriched_df["LastReview"] = pd.to_datetime(enriched_df["LastReview"], format="%Y-%m-%d", errors="coerce")

        enriched_df["TransferLA"] = enriched_df["TransferLA"].fillna("Not transferred")

        enriched_df = enriched_df.merge(
            la_codes, how="left", left_on="TransferLA", right_on="LA code"
        )
        enriched_df["LA name"].fillna("Not transferred", inplace=True)

        enriched_df["SENtype"] = enriched_df["SENtype"].apply(
            lambda x: SENTypes[x.upper()].value if pd.notnull(x) else "Not yet determined"
        )

        enriched_df["SENunitIndicator"] = enriched_df["SENunitIndicator"].apply(
            lambda x: (
                "Yes" if str(x) == "1" else ("No" if str(x) == "0" else "Undefined")
            )
        )

        enriched_df["ResourcedProvisionIndicator"] = enriched_df[
            "ResourcedProvisionIndicator"
        ].apply(
            lambda x: (
                "Yes" if str(x) == "1" else ("No" if str(x) == "0" else "Undefined")
            )
        )

        return enriched_df


###########################
# Main App
###########################
st.title("SEN2 drilldown tool")
st.markdown(
    "[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/015_SEN2_app/sen2_app.py)"
)

with st.expander("Instructions"):
    st.write(
        "Upload your clean SEN2 XML as it is downloaded from COLLECT. Use the slicers on the "
        "left to further select down for data views. Use the bottom expander to view remaining children."
        "If you need to upload a different data set, you'll need to reload the page."
        "Some numbers may be cut off on bar charts, to overcome this, expand the chart using"
        "the button on the top right"
    )

input_file = st.file_uploader("Upload SEN2 XML here")

urn_lookup, ukprn_lookup, la_codes = read_lookups()

if input_file:
    tree = ET.parse(input_file)
    root = tree.getroot()
    data_files = convert_data(root)

    @st.cache_data
    def get_datacontainer(_data_files):
        """This function exists to create a datacontainer object for the sen2 so we can cache it
        with the st.cache_data decorator, this cant be done with the class directly."""
        sen2_object = Datacontainer(_data_files)
        return sen2_object

    sen2 = get_datacontainer(data_files)

    with st.sidebar:
        st.write("Make selections here:")

        sex_selected = st.sidebar.multiselect(
            "Select Sex",
            (sen2.enriched_persons["Sex"].unique()),
            default=(sen2.enriched_persons["Sex"].unique()),
        )

        age_selected = st.sidebar.slider(
            "Select age range (on day of census)",
            min_value=int(sen2.enriched_persons["Age"].min()),
            max_value=int(sen2.enriched_persons["Age"].max()),
            value=[0, int(sen2.enriched_persons["Age"].max())],
        )

        sen_type_selected = st.sidebar.multiselect(
            "Select SEN types",
            (sen2.enriched_persons["SENtype"].unique()),
            default=(sen2.enriched_persons["SENtype"].unique()),
        )

        ethnicity_selected = st.sidebar.multiselect(
            "Select ethnicities",
            (sen2.enriched_persons["EthnicitySubGroup"].unique()),
            default=(sen2.enriched_persons["EthnicitySubGroup"].unique()),
        )

        sen_setting_selected = st.sidebar.multiselect(
            "Select SEN settings (active plans)",
            (sen2.enriched_persons["SENSetting_mapped"].unique()),
            default=(sen2.enriched_persons["SENSetting_mapped"].unique()),
        )

        plan_length = st.sidebar.slider(
            "Select named plan length (includes closed plans)",
            min_value=int(sen2.enriched_persons["NamedPlanLength (days)"].min()),
            max_value=int(sen2.enriched_persons["NamedPlanLength (days)"].max()),
            value=[0, int(sen2.enriched_persons["NamedPlanLength (days)"].max())],
        )

    sliced_enriched_persons = apply_filters(
        sen2.enriched_persons,
        sex_selected,
        age_selected,
        ethnicity_selected,
        sen_type_selected,
        sen_setting_selected,
        plan_length,
    )
    sliced_enriched_requests = apply_filters(
        sen2.enriched_requests,
        sex_selected,
        age_selected,
        ethnicity_selected,
        sen_type_selected,
        sen_setting_selected,
        plan_length,
    )
    sliced_enriched_assessments = apply_filters(
        sen2.enriched_assessments,
        sex_selected,
        age_selected,
        ethnicity_selected,
        sen_type_selected,
        sen_setting_selected,
        plan_length,
    )
    sliced_enriched_np = apply_filters(
        sen2.enriched_named_plan,
        sex_selected,
        age_selected,
        ethnicity_selected,
        sen_type_selected,
        sen_setting_selected,
        plan_length,
    )
    sliced_enriched_ap = apply_filters(
        sen2.enriched_active_plans,
        sex_selected,
        age_selected,
        ethnicity_selected,
        sen_type_selected,
        sen_setting_selected,
        plan_length,
    )

    with st.expander("All children in data (every child with a persons block)"):
        col1, col2, col3 = st.columns(3)

        with col1:
            gender_all = make_indicator(sliced_enriched_persons, "Total children")
            st.plotly_chart(gender_all, use_container_width=True)

        with col2:
            age_chart = make_bar(
                sliced_enriched_persons,
                "AgeBuckets",
                title="Age group - all children",
                x_label="Age groups",
                buckets=[
                    "a) Under 5 years",
                    "b) 5 to 10 years",
                    "c) 11 to 15 years",
                    "d) 16 to 19 years",
                    "e) 20 years and over",
                ],
            )
            st.plotly_chart(age_chart, use_container_width=True, theme=None)

        with col3:
            ethnicity_chart = make_bar(
                sliced_enriched_persons,
                "EthnicityGroup",
                title="Ethnicity - all children",
                x_label="Ethnicity",
            )
            st.plotly_chart(ethnicity_chart, use_container_width=True, theme=None)

        ethnicity_subgroups_chart = make_bar(
            sliced_enriched_persons,
            "EthnicitySubGroup",
            "Ethnicity Subgroups - all children",
            x_label="Ethnicity",
        )
        st.plotly_chart(ethnicity_subgroups_chart, use_container_width=True, theme=None)

    with st.expander("Requests"):
        req_col1, req_col2, req_col3 = st.columns(3)

        with req_col1:
            total_requests = make_indicator(sliced_enriched_requests, "Total Requests")
            st.plotly_chart(total_requests, use_container_width=True, theme=None)

            requests_exported = px.pie(
                sliced_enriched_requests,
                names="Exported",
                title="Requests exported",
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            requests_exported.update_traces(textinfo="value+percent")
            requests_exported.update_layout(
                template="seaborn",
                plot_bgcolor="lightgrey",
                paper_bgcolor="lightgrey",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                legend_title_font_color="black",
            )
            st.plotly_chart(requests_exported, use_container_width=True, theme=None)

        with req_col2:
            requests_by_age = make_bar(
                sliced_enriched_requests,
                "AgeBuckets",
                x_label="Age groups",
                title="Requests by age",
                buckets=[
                    "a) Under 5 years",
                    "b) 5 to 10 years",
                    "c) 11 to 15 years",
                    "d) 16 to 19 years",
                    "e) 20 years and over",
                ],
            )
            requests_by_age.update_layout(yaxis_title="Number of children")
            st.plotly_chart(requests_by_age, use_container_width=True, theme=None)

            requests_rya = px.pie(
                sliced_enriched_requests,
                names="RYA",
                title="Registered youth accomodation",
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            requests_rya.update_traces(textinfo="value+percent")
            requests_rya.update_layout(
                template="seaborn",
                plot_bgcolor="lightgrey",
                paper_bgcolor="lightgrey",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                legend_title_font_color="black",
            )
            st.plotly_chart(requests_rya, use_container_width=True, theme=None)

        with req_col3:
            request_outcomes = make_bar(
                sliced_enriched_requests,
                "RequestOutcome",
                "Request outcomes",
                x_label="Outcomes",
            )
            st.plotly_chart(request_outcomes, use_container_width=True, theme=None)

            request_tribunal = make_bar(
                sliced_enriched_requests,
                "MediationOrTribunal",
                "Requests - mediation or tribunal",
                x_label="Challenge to request outcome",
                buckets=["Mediation", "Tribunal", "No"],
            )
            st.plotly_chart(request_tribunal, use_container_width=True, theme=None)

        requests_months_bar = make_bar(
            sliced_enriched_requests,
            "ReceivedDate_month",
            title="Requests per month",
            x_label="Month",
            buckets=months,
        )
        st.plotly_chart(requests_months_bar, use_container_width=True, theme=None)

        request_lengths = make_bar(
            sliced_enriched_requests,
            "RequestLengthBucket",
            "Request timeframe (received to outcome)",
            x_label="Request length (days)",
            buckets=[
                "a) Under 10 days",
                "b) 10 to 20 days",
                "c) 21 to 30 days",
                "d) 31 to 40 days",
                "e) 41 to 50 days",
                "f) 51 to 60 days",
                "g) 61+ days",
                "x) Request incomplete",
            ],
        )
        st.plotly_chart(request_lengths, use_container_width=True, theme=None)

        request_sources = make_bar(
            sliced_enriched_requests,
            "RequestSource",
            "Request sources",
            x_label="Sources",
            buckets=[
                "Young person or parent",
                "School or other education setting",
                "Health care professionals",
                "Social care professionals",
                "Other",
            ],
        )
        st.plotly_chart(request_sources, use_container_width=True, theme=None)

    with st.expander("Assessments"):
        ass_col1, ass_col2 = st.columns(2)

        with ass_col1:
            total_assessments = make_indicator(
                sliced_enriched_assessments, "Total assessments"
            )
            st.plotly_chart(total_assessments, use_container_width=True, theme=None)

            assessment_tribunal = make_bar(
                sliced_enriched_assessments,
                "MediationOrTribunal",
                "Assessments - mediation or tribunal",
                x_label="Challenge to assessment outcome",
                buckets=[
                    "Assessment Mediation",
                    "Assessment Tribunal",
                    "Other Mediation",
                    "Other Tribunal",
                    "No",
                ],
            )
            st.plotly_chart(assessment_tribunal, use_container_width=True, theme=None)

        with ass_col2:
            assessments_by_age = make_bar(
                sliced_enriched_assessments,
                "AgeBuckets",
                title="Assessments by age",
                x_label="Age group",
                buckets=[
                    "a) Under 5 years",
                    "b) 5 to 10 years",
                    "c) 11 to 15 years",
                    "d) 16 to 19 years",
                    "e) 20 years and over",
                ],
            )
            st.plotly_chart(assessments_by_age, use_container_width=True, theme=None)

            assessment_outcomes = make_bar(
                sliced_enriched_assessments,
                "AssessmentOutcome",
                "Assessment outcomes",
                x_label="Outcomes",
            )
            st.plotly_chart(assessment_outcomes, use_container_width=True, theme=None)

        assessments_months_bar = make_bar(
            sliced_enriched_assessments,
            "AssessmentOutcomeDate_month",
            title="Assessments per month",
            x_label="Month",
            buckets=months,
        )
        st.plotly_chart(assessments_months_bar, use_container_width=True, theme=None)

    with st.expander("Named Plans"):
        np_c1r1, np_c2r1, np_c3r1 = st.columns(3)
        np_c1r2, np_c2r2 = st.columns(2)

        with np_c1r1:
            plans_starting = make_indicator(
                sliced_enriched_np[
                    (sliced_enriched_np["StartDate"] > sen2.reference_period["start"])
                ],
                "Plans starting (year)",
            )
            st.plotly_chart(plans_starting, use_container_width=True, theme=None)

        with np_c2r1:
            plans_ending = make_indicator(
                sliced_enriched_np[
                    (sliced_enriched_np["CeaseDate"] > sen2.reference_period["start"])
                ],
                "Plans ending (year)",
            )
            st.plotly_chart(plans_ending, use_container_width=True, theme=None)

        with np_c3r1:
            active_census_day = make_indicator(
                sliced_enriched_np[sliced_enriched_np["CeaseDate"].isna()],
                "Plans active on census day",
            )
            st.plotly_chart(active_census_day, use_container_width=True, theme=None)

        with np_c1r2:
            # Children with multiple placements
            placements_df = (
                sliced_enriched_np.groupby(["child_id"])
                .size()
                .to_frame("Number of plans")
                .reset_index()
            )
            multiple_placements = px.pie(
                placements_df,
                names="Number of plans",
                title="Number of plans per child",
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            multiple_placements.update_traces(textinfo="value+percent")
            multiple_placements.update_layout(
                template="seaborn",
                plot_bgcolor="lightgrey",
                paper_bgcolor="lightgrey",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                legend_title_font_color="black",
            )
            st.plotly_chart(multiple_placements, use_container_width=True, theme=None)

            open_plan_lengths = make_bar(
                sliced_enriched_np[sliced_enriched_np["CeaseDate"].isna()],
                "NamedPlanLength (years)",
                x_label="Named plan lengths (years)",
                title="Plans active on census day - length",
                buckets=[
                    "a) Less than 1 year",
                    "b) 1-2 years",
                    "c) 2-3 years",
                    "d) 13-4 years",
                    "e) 4-5 years",
                    "f) 5-6 years",
                    "g) 6-7 years",
                    "h) 7-8 years",
                    "i) 8-9 years",
                    "j) 9-10 years",
                    "k) 10-11 years",
                    "l) 11-12 years",
                    "m) 12+ years",
                ],
            )
            st.plotly_chart(open_plan_lengths, use_container_width=True, theme=None)

        with np_c2r2:
            residential_setting = px.pie(
                sliced_enriched_np[
                    sliced_enriched_np["CeaseDate"].isna()
                    & sliced_enriched_np["PlanRes"].notna()
                ],
                names="PlanRes",
                title="Residential Setting",
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            residential_setting.update_traces(textinfo="value+percent")
            residential_setting.update_layout(
                template="seaborn",
                plot_bgcolor="lightgrey",
                paper_bgcolor="lightgrey",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                legend_title_font_color="black",
            )
            st.plotly_chart(residential_setting, use_container_width=True, theme=None)

            ceased_reasons = make_bar(
                sliced_enriched_np,
                "CeaseReason",
                title="Plans ceasing this year - Reason",
                x_label="Reasons",
                buckets=[
                    "1) Reached maximum age",
                    "2) Need met w/o EHC",
                    "3) Moved to HE",
                    "4) Moved to paid employment/apprenticeships",
                    "5) Transferred",
                    "6) No longer wishes to engage",
                    "7) Moved outside of England",
                    "8) Deceased",
                    "9) Other",
                ],
            )
            st.plotly_chart(ceased_reasons, use_container_width=True, theme=None)

        ehcps_starting_in_year = sliced_enriched_np[
            (sliced_enriched_np["StartDate"] >= sen2.reference_period["start"])
            & (sliced_enriched_np["StartDate"] <= sen2.reference_period["end"])
        ]
        ehcps_starting_months_bar = make_bar(
            ehcps_starting_in_year,
            "StartDate_month",
            title="Plans starting per month",
            x_label="Month",
            buckets=months,
        )
        st.plotly_chart(ehcps_starting_months_bar, use_container_width=True, theme=None)

        ehcps_ceasing_in_year = sliced_enriched_np[
            (sliced_enriched_np["CeaseDate"] >= sen2.reference_period["start"])
            & (sliced_enriched_np["CeaseDate"] <= sen2.reference_period["end"])
        ]
        ehcps_ceasing_months_bar = make_bar(
            ehcps_ceasing_in_year,
            "CeaseDate_month",
            title="Plans ceasing per month",
            x_label="Month",
            buckets=months,
        )
        st.plotly_chart(ehcps_ceasing_months_bar, use_container_width=True, theme=None)

        sen_setting = make_bar(
            sliced_enriched_np[sliced_enriched_np["CeaseDate"].isna()],
            "SENSetting_np",
            x_label="SEN settings",
            title="Plans active on census day - SEN Setting (from named plans)",
        )
        st.plotly_chart(sen_setting, use_container_width=True, theme=None)

        sen_type_chart = make_bar(
            sliced_enriched_np,
            "SENtype",
            title="SEN type (named plan) - all children",
            x_label="SEN Type",
            buckets=[
                "Specific learning difficulty",
                "Moderate learning difficulty",
                "Severe learning difficulty",
                "Profound and multiple learning difficulty",
                "Social, emotional and mental health",
                "Speech, language and communication needs",
                "Hearing impairment",
                "Vision impairment",
                "Multi-sensory impairment",
                "Physical disability",
                "Autistic spectrum disorder",
                "Down Syndrome",
                "Other difficulty",
            ],
        )
        st.plotly_chart(sen_type_chart, use_container_width=True, theme=None)

    with st.expander("Timeliness"):
        st.write(
            "Timeliness is only considered for CYP with: a Named Plan start date and no kinds of mediation or tribunal. "
            "Timeliness is achieved if Request received date to Named Plan start "
            "date is under 140 calendar days."
        )
        timeliness_df = sliced_enriched_np[sliced_enriched_np["StartDate"].notna()]

        assessments_sub_df = sliced_enriched_assessments[
            sliced_enriched_assessments["MediationOrTribunal"] == "No"
        ]

        requests_sub_df = sliced_enriched_requests[
            sliced_enriched_requests["MediationOrTribunal"] == "No"
        ]

        timeliness_df = timeliness_df.merge(
            assessments_sub_df[["child_id", "Week20"]], how="left", on="child_id"
        )

        timeliness_df = timeliness_df.merge(
            requests_sub_df[["child_id", "ReceivedDate"]], how="inner", on="child_id"
        )

        timeliness_df["Timeliness"] = (
            timeliness_df["StartDate"] - timeliness_df["ReceivedDate"]
        ) / pd.Timedelta(days=1)

        timeliness_df["Timeliness - week 20 exceptions not considered"] = timeliness_df[
            "Timeliness"
        ].apply(lambda x: "Not timely" if x > 140 else "Timely")
        timeliness_df["Timeliness - week 20 exceptions considered"] = (
            timeliness_df.apply(
                lambda x: (
                    "Not timely"
                    if ((x["Timeliness"] > 140) & (x["Week20"] == "No"))
                    else ("Exception granted" if x["Week20"] == "Yes" else "Timely")
                ),
                axis=1,
            )
        )

        timeliness_unconsidered = px.pie(
            timeliness_df,
            names="Timeliness - week 20 exceptions not considered",
            title="Timeliness - week 20 including exceptions",
            color_discrete_sequence=px.colors.qualitative.G10,
        )
        timeliness_unconsidered.update_traces(textinfo="value+percent")
        timeliness_unconsidered.update_layout(
            template="seaborn",
            plot_bgcolor="lightgrey",
            paper_bgcolor="lightgrey",
            font_color="black",
            title_font_color="black",
            legend_font_color="black",
            legend_title_font_color="black",
        )

        timeliness_considered = px.pie(
            timeliness_df[
                timeliness_df["Timeliness - week 20 exceptions considered"]
                != "Exception granted"
            ],
            names="Timeliness - week 20 exceptions considered",
            title="Timeliness - week 20 excluding exceptions",
            color_discrete_sequence=px.colors.qualitative.G10,
        )
        timeliness_considered.update_traces(textinfo="value+percent")
        timeliness_considered.update_layout(
            template="seaborn",
            plot_bgcolor="lightgrey",
            paper_bgcolor="lightgrey",
            font_color="black",
            title_font_color="black",
            legend_font_color="black",
            legend_title_font_color="black",
        )

        timeliness_including_exceptions_months_bar = make_bar(
            timeliness_df,
            "StartDate_month",
            title="Timeliness by month (exceptions included)",
            color_column="Timeliness - week 20 exceptions not considered",
            x_label="Month",
            buckets=months,
        )

        timeliness_excluding_exceptions_months_bar = make_bar(
            timeliness_df,
            "StartDate_month",
            title="Timeliness by month (exceptions excluded)",
            color_column="Timeliness - week 20 exceptions considered",
            x_label="Month",
            buckets=months,
        )

        time_col1, time_col2 = st.columns(2)

        with time_col1:
            st.plotly_chart(
                timeliness_unconsidered, use_container_width=True, theme=None
            )

        with time_col2:
            st.plotly_chart(timeliness_considered, use_container_width=True, theme=None)

        st.plotly_chart(
            timeliness_including_exceptions_months_bar,
            use_container_width=True,
            theme=None,
        )

        st.plotly_chart(
            timeliness_excluding_exceptions_months_bar,
            use_container_width=True,
            theme=None,
        )

    with st.expander("Active Plans"):
        ap_col1, ap_col2, ap_col3 = st.columns(3)

        with ap_col1:

            open_closed_ap = px.pie(
                sliced_enriched_ap,
                names="PlanOpen",
                title="Active plans module open and closed",
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            open_closed_ap.update_traces(textinfo="value+percent")
            open_closed_ap.update_layout(
                template="seaborn",
                plot_bgcolor="lightgrey",
                paper_bgcolor="lightgrey",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                legend_title_font_color="black",
            )
            st.plotly_chart(open_closed_ap, use_container_width=True, theme=None)

            ap_review_outcomes = make_bar(
                sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()],
                "ReviewOutcome",
                x_label="Outcomes",
                title="Open active plans - review outcomes",
            )
            ap_review_outcomes.update_layout(yaxis_title="Number of children")
            st.plotly_chart(ap_review_outcomes, use_container_width=True, theme=None)

        with ap_col2:
            ap_residential = make_bar(
                sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()],
                "RES",
                x_label="Residential setting",
                title="Open active plans - residential setting",
            )
            st.plotly_chart(ap_residential, use_container_width=True, theme=None)

            resourced_provision_count = make_bar(
                sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].isna()],
                "ResourcedProvisionIndicator",
                title="In resourced provision on census day",
                x_label="Resourced provision indicator",
            )
            st.plotly_chart(
                resourced_provision_count, use_container_width=True, theme=None
            )

        with ap_col3:
            ap_wpb = make_bar(
                sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()],
                "WPB",
                x_label="Work-based learning activity",
                title="Open active plans - work-based learning ",
            )
            st.plotly_chart(ap_wpb, use_container_width=True, theme=None)

            sen_unit_count = make_bar(
                sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].isna()],
                "SENunitIndicator",
                title="In SEN unit on census day",
                x_label="SEN unit indicator",
            )
            st.plotly_chart(sen_unit_count, use_container_width=True, theme=None)

        ap_2_col1, ap_2_col2 = st.columns(2)

        with ap_2_col1:
            placements_df_ap_open = (
                sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].isna()]
                .groupby(["child_id"])
                .size()
                .to_frame("Number of plans")
                .reset_index()
            )

            multiple_placements_ap_open = px.pie(
                placements_df_ap_open,
                names="Number of plans",
                title="Number of open placements per child",
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            multiple_placements_ap_open.update_traces(textinfo="value+percent")
            multiple_placements_ap_open.update_layout(
                template="seaborn",
                plot_bgcolor="lightgrey",
                paper_bgcolor="lightgrey",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                legend_title_font_color="black",
            )
            st.plotly_chart(
                multiple_placements_ap_open, use_container_width=True, theme=None
            )

        with ap_2_col2:
            # Children with multiple placements
            placements_df_ap = (
                sliced_enriched_ap.groupby(["child_id"])
                .size()
                .to_frame("Number of plans")
                .reset_index()
            )
            multiple_placements_ap = px.pie(
                placements_df_ap,
                names="Number of plans",
                title="Number of placements per child",
                color_discrete_sequence=px.colors.qualitative.G10,
            )
            multiple_placements_ap.update_traces(textinfo="value+percent")
            multiple_placements_ap.update_layout(
                template="seaborn",
                plot_bgcolor="lightgrey",
                paper_bgcolor="lightgrey",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                legend_title_font_color="black",
            )
            st.plotly_chart(
                multiple_placements_ap, use_container_width=True, theme=None
            )

        # Not in columns
        ehcs_transferred = make_bar(
            sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()],
            "LA name",
            x_label="LA name",
            title="Open active plans - EHCs transferred in",
        )
        st.plotly_chart(ehcs_transferred, use_container_width=True, theme=None)

        sen_settings = make_bar(
            sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].isna()],
            "SENSetting_mapped",
            title="Plans active on census day - SEN settings (from active plans)",
            x_label="SEN setting",
        )
        st.plotly_chart(sen_settings, use_container_width=True, theme=None)

    with st.expander("Reviews"):
        col1, col2 = st.columns(2)

        with col1:
            total_reviews = make_indicator(
                sliced_enriched_ap[
                    sliced_enriched_ap["LastReview"].notna()
                    & (sliced_enriched_ap["LastReview"] != "Not applicable")
                ],
                "Total reviews",
            )
            st.plotly_chart(total_reviews, use_container_width=True, theme=None)

            total_reviews_year = make_indicator(
                sliced_enriched_ap[
                    sliced_enriched_ap["LastReview"].notna()
                    & (sliced_enriched_ap["LastReview"] != "Not applicable")
                    & (sliced_enriched_ap["LastReview"] >= sen2.reference_period["start"])
                ],
                "Total reviews in year",
            )
            st.plotly_chart(total_reviews_year, use_container_width=True, theme=None)

        with col2:
            review_outcomes = make_bar(
                sliced_enriched_ap[
                    sliced_enriched_ap["LastReview"].notna()
                    & (sliced_enriched_ap["LastReview"] != "Not applicable")
                ],
                "ReviewOutcome",
                title="Outcome of most recent review",
                x_label="Review Outcome",
                buckets=[
                    "M - maintain the EHC plan",
                    "C - cease the EHC plan",
                    "A - Amend the EHC plan",
                ],
            )
            st.plotly_chart(review_outcomes, use_container_width=True, theme=None)

            review_outcomes_year = make_bar(
                sliced_enriched_ap[
                    sliced_enriched_ap["LastReview"].notna()
                    & (sliced_enriched_ap["LastReview"] != "Not applicable")
                    & (sliced_enriched_ap["LastReview"] >= sen2.reference_period["start"])
                ],
                "ReviewOutcome",
                title="Outcome of most recent review",
                x_label="Review Outcome",
                buckets=[
                    "M - maintain the EHC plan",
                    "C - cease the EHC plan",
                    "A - Amend the EHC plan",
                ],
            )
            st.plotly_chart(review_outcomes_year, use_container_width=True, theme=None)

    with st.expander("CYP in selected drilldown:"):
        st.table(sliced_enriched_ap.head())
        st.table(sliced_enriched_persons)
