# Questions:
# What extra measures do we want
# Are there any measures we'd rather view in a different way
# Are there colour scheme adjustments to make
# How do we want to look at active plans
# WHat slicers would we like
# WHat buckets would we like on different timeframe calculations


import pandas as pd
import numpy as np
import datetime as dt

import streamlit as st

import xml.etree.ElementTree as ET
import time

from enum import Enum
from dateutil.relativedelta import relativedelta

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

###################
# Config
###################

st.set_page_config(layout="wide")


class EthnicSubcategories(Enum):
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


###################
# Util functions
###################
def calculate_age_buckets(age):
    # Used to make age buckets matching published data
    if age < 1:
        return "a) Under 1 year"
    elif age < 5:
        return "b) 1 to 4 years"
    elif age < 10:
        return "c) 5 to 9 years"
    elif age < 16:
        return "d) 10 to 16 years"
    elif age >= 16:
        return "e) 16 years and over"
    else:
        return "f) Age error"


def make_bar(df, buckets, column, title):
    values_df = pd.DataFrame({column: buckets})
    df_counts = df.groupby(column).size().to_frame("Count").reset_index()
    df_counts = df_counts.merge(values_df, how="outer", on="AgeBuckets")
    df_counts["Count"] = df_counts["Count"].fillna(0)
    df_counts.sort_values(column, inplace=True)

    bar = px.bar(df_counts, x=column, y="Count", title=title)

    return bar


def make_indicator(df, title):
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
    for element in xml_elements:
        try:
            table_dict[element] = xml_block.find(element).text
        except:
            table_dict[element] = pd.NA
    return table_dict


class XMLtoDF:
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
            # The progress info doesn't work on streamlit
            # if self.child_id % 1000 == 0:
            #     st.write(f'Read data for {self.child_id} children of {self.total_children} children.')

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
    datafiles = XMLtoDF(_root)

    return datafiles


###########################
# Datacontainer
###########################
class Datacontainer:
    """
    A container for SEN2 data. Indexes data by table type. Provides methods for
    merging data to create a single, consistent dataset.
    """

    def __init__(self, data_dict: dict):
        self.data = data_dict

        self.reference_period = self._get_reference_period(self.data.header)

        self.persons = self.data.persons

    def _get_reference_period(self, df):
        year = int(df["Year"].iloc[0])

        start = pd.to_datetime(f"{str(year-1)}-01-01", format=f"%Y-%m-%d")
        end = pd.to_datetime(f"{str(year-1)}-12-31", format=f"%Y-%m-%d")

        reference_period = {"start": start, "end": end}

        return reference_period

    @property
    def enriched_persons(self):
        enriched_df = self.data.persons.copy()
        enriched_df["EthnicityGroup"] = enriched_df["Ethnicity"].apply(
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

        return enriched_df

    @property
    def enriched_requests(self):
        enriched_df = self.data.requests[
            self.data.requests["ReceivedDate"].notna()
        ].copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[["AgeBuckets", "EthnicityGroup", "Sex", "child_id"]],
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
                "Yes"
                if (x["RequestMediation"] == "1") | (x["RequestTribunal"] == "1")
                else "No"
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
        
        enriched_df['RYA'] = enriched_df['RYA'].astype("str").map({"0":"No", "1":"Yes"})

        enriched_df["Exported"] = [
            "No" if pd.isnull(col) else "Yes" for col in enriched_df["Exported"]
        ]

        return enriched_df

    @property
    def enriched_assessments(self):
        enriched_df = self.data.assessments.copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[["AgeBuckets", "EthnicityGroup", "Sex", "child_id"]],
            how="left",
            on="child_id",
        )

        enriched_df["AssessmentOutcomeDate"] = pd.to_datetime(
            enriched_df["AssessmentOutcomeDate"], format="%Y-%m-%d", errors="coerce"
        )

        enriched_df["MediationOrTribunal"] = enriched_df.apply(
            lambda x: (
                "Yes"
                if (x["AssessmentOutcome"] != "H")
                & (
                    (x["AssessmentMediation"] == "1")
                    | (x["AssessmentTribunal"] == "1")
                    | (x["OtherMediation"] == "1")
                    | (x["OtherTribunal"] == "1")
                )
                else "No"
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
            self.enriched_persons[["AgeBuckets", "EthnicityGroup", "Sex", "child_id"]],
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

        enriched_df["CeaseDate"] = pd.to_datetime(
            enriched_df["CeaseDate"], format="%Y-%m-%d", errors="coerce"
        )

        enriched_df["CeaseDate_year"] = enriched_df["CeaseDate"].dt.year

        enriched_df["NamedPlanLength (days)"] = (
            self.reference_period["end"] - enriched_df["StartDate"]
        ) / pd.Timedelta(days=1)

        enriched_df["PlanRes"] = enriched_df["PlanRes"].map(
            {"A": "38 to 51 weeks", "B": "52 weeks"}
        )

        enriched_df["PlacementRank"] = enriched_df["PlacementRank"].astype("str")

        return enriched_df

    @property
    def enriched_active_plans(self):
        enriched_df = self.data.active_plans.copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[["AgeBuckets", "EthnicityGroup", "Sex", "child_id"]],
            how="left",
            on="child_id",
        )

        enriched_df["PlanOpen"] = enriched_df["LeavingDate"].apply(lambda x: "Closed" if pd.isnull(x) else "Open")

        enriched_df["RES"].fillna("Not applicable", inplace=True)
        enriched_df["WPB"].fillna("Not applicable", inplace=True)
        enriched_df["ReviewOutcome"].fillna("Not applicable", inplace=True)
        
        
        enriched_df["LastReview"].fillna("Not applicable", inplace=True)
        

        enriched_df["TransferLA"] = enriched_df["TransferLA"].apply(lambda x: f"LA Code: {x}" if pd.notnull(x) else "Not transferred")
        enriched_df["TransferLA"].fillna("Not transferred", inplace=True)

        return enriched_df


###########################
# Main App
###########################

input_file = st.file_uploader("Upload SEN2 XML here")

if input_file:
    # Get time to test ingress speed and caching
    start_time = time.time()
    st.write("Starting data read, for large datasets this could take 5 minutes.")

    tree = ET.parse(input_file)
    root = tree.getroot()
    data_files = convert_data(root)

    after_ingress_time = time.time()
    total_ingress_time = after_ingress_time - start_time
    st.write(f"Total ingress time: {int(total_ingress_time/60)} minutes.")

    sen2 = Datacontainer(data_files)

    with st.sidebar:
        st.write("Slice here")
        # SEN Type
        # SEN Setting
        # Open SEN plan lengths
        # Exported
        # Week 20
        # TODO SLICERS
        # display charts by age/male-female
        # output measures and ingress to excel?

        sex_selected = st.sidebar.multiselect(
            "Select Sex",
            (sen2.enriched_persons["Sex"].unique()),
            default=(sen2.enriched_persons["Sex"].unique()),
        )
        age_selected = st.sidebar.multiselect(
            "Select age buckets",
            (
                [
                    "a) Under 1 year",
                    "b) 1 to 4 years",
                    "c) 5 to 9 years",
                    "d) 10 to 16 years",
                    "e) 16 years and over",
                    "f) Age error",
                ]
            ),
            default=(
                [
                    "a) Under 1 year",
                    "b) 1 to 4 years",
                    "c) 5 to 9 years",
                    "d) 10 to 16 years",
                    "e) 16 years and over",
                    "f) Age error",
                ]
            ),
        )

        ethnicity_selected = st.sidebar.multiselect(
            "Select ethnicities",
            (sen2.enriched_persons["EthnicityGroup"].unique()),
            default=(sen2.enriched_persons["EthnicityGroup"].unique()),
        )

    sliced_enriched_persons = sen2.enriched_persons[
        sen2.enriched_persons["Sex"].isin(sex_selected)
        & sen2.enriched_persons["AgeBuckets"].isin(age_selected)
        & (sen2.enriched_persons["EthnicityGroup"].isin(ethnicity_selected))
    ]

    sliced_enriched_requests = sen2.enriched_requests[
        sen2.enriched_requests["Sex"].isin(sex_selected)
        & sen2.enriched_requests["AgeBuckets"].isin(age_selected)
        & (sen2.enriched_requests["RequestOutcome"] != "H")
        & (sen2.enriched_requests["EthnicityGroup"].isin(ethnicity_selected))
    ]

    sliced_enriched_assessments = sen2.enriched_assessments[
        (sen2.enriched_assessments["Sex"].isin(sex_selected))
        & (sen2.enriched_assessments["AgeBuckets"].isin(age_selected))
        & (sen2.enriched_assessments["AssessmentOutcome"] != "H")
        & (sen2.enriched_assessments["EthnicityGroup"].isin(ethnicity_selected))
    ]

    sliced_enriched_np = sen2.enriched_named_plan[
        (sen2.enriched_named_plan["Sex"].isin(sex_selected))
        & (sen2.enriched_named_plan["AgeBuckets"].isin(age_selected)
        & (sen2.enriched_named_plan["EthnicityGroup"].isin(ethnicity_selected))
        )
    ]

    sliced_enriched_ap = sen2.enriched_active_plans[
        (sen2.enriched_active_plans["Sex"].isin(sex_selected))
        & (sen2.enriched_active_plans["AgeBuckets"].isin(age_selected))
        & (sen2.enriched_active_plans["EthnicityGroup"].isin(ethnicity_selected))
    ]

    with st.expander("Headline Figures"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            gender_all = make_indicator(sliced_enriched_persons, "Total children")
            st.plotly_chart(gender_all, use_container_width=True)

        with col2:
            ethnicity_chart = px.histogram(sliced_enriched_persons, "EthnicityGroup", color="Sex", title="Ethnicity - all children")
            st.plotly_chart(ethnicity_chart, use_container_width=True)

        with col3:
            age_chart = make_bar(
                sliced_enriched_persons,
                [
                    "a) Under 1 year",
                    "b) 1 to 4 years",
                    "c) 5 to 9 years",
                    "d) 10 to 16 years",
                    "e) 16 years and over",
                    "f) Age error",
                ],
                "AgeBuckets",
                title="Age group - all children"
            )
            st.plotly_chart(age_chart, use_container_width=True)

        with col4:
            sen_type_chart = px.histogram(sen2.enriched_active_plans, "SENtype", color="Sex", title="Sen Type - all children")
            st.plotly_chart(sen_type_chart, use_container_width=True)

    with st.expander("Requests"):
        req_col1, req_col2, req_col3, req_col4 = st.columns(4)

        with req_col1:
            total_requests = make_indicator(sliced_enriched_requests, "Total Requests")
            st.plotly_chart(total_requests, use_container_width=True)

            request_lengths = px.histogram(sliced_enriched_requests, "RequestLength", color="Sex", title="Request timeframe")
            st.plotly_chart(request_lengths, use_container_width=True)

        with req_col2:
            request_sources = px.histogram(
                sliced_enriched_requests, "RequestSource", color="Sex", title="Request sources"
            )

            st.plotly_chart(request_sources, use_container_width=True)

            requests_rya = px.pie(sliced_enriched_requests, names="RYA", title="Registered youth accomodation")
            st.plotly_chart(requests_rya, use_container_width=True)

        with req_col3:
            request_outcomes = px.histogram(
                sliced_enriched_requests, "RequestOutcome", color="Sex", title="Request outcomes"
            )

            st.plotly_chart(request_outcomes, use_container_width=True)

            requests_by_age = make_bar(
                sliced_enriched_requests,
                [
                    "a) Under 1 year",
                    "b) 1 to 4 years",
                    "c) 5 to 9 years",
                    "d) 10 to 16 years",
                    "e) 16 years and over",
                    "f) Age error",
                ],
                "AgeBuckets",
                title="Requests by age"
            )
            st.plotly_chart(requests_by_age, use_container_width=True)

            

        with req_col4:
            request_tribunal = px.histogram(
                sliced_enriched_requests, "MediationOrTribunal", color="Sex", title="Requests - mediation or tribunal"
            )
            st.plotly_chart(request_tribunal, use_container_width=True)

            requests_exported = px.pie(sliced_enriched_requests, names="Exported", title="Requests exported")
            st.plotly_chart(requests_exported, use_container_width=True)

    with st.expander("Assessments"):
        ass_col1, ass_col2, ass_col3, ass_col4 = st.columns(4)

        with ass_col1:
            total_assessments = make_indicator(
                sliced_enriched_assessments, "Total assessments"
            )
            st.plotly_chart(total_assessments, use_container_width=True)


        with ass_col2:
            assessment_outcomes = px.histogram(
                sliced_enriched_assessments, "AssessmentOutcome", color="Sex", title="Assessment outcomes"
            )
            st.plotly_chart(assessment_outcomes, use_container_width=True)

        with ass_col3:
            assessment_tribunal = px.histogram(
                sliced_enriched_assessments, "MediationOrTribunal", color="Sex", title="Assessments - mediation or tribunal"
            )
            st.plotly_chart(assessment_tribunal, use_container_width=True)

        with ass_col4:
            assessments_by_age = make_bar(sliced_enriched_assessments,
                [
                    "a) Under 1 year",
                    "b) 1 to 4 years",
                    "c) 5 to 9 years",
                    "d) 10 to 16 years",
                    "e) 16 years and over",
                    "f) Age error",
                ],
                "AgeBuckets",
                title="Assessments by age")
            st.plotly_chart(assessments_by_age, use_container_width=True)

    with st.expander("Named Plans"):
        np_col1, np_col2, np_col3, np_col4 = st.columns(4)

        with np_col1:
            plans_starting = make_indicator(
                sliced_enriched_np[
                    (sliced_enriched_np["StartDate"] > sen2.reference_period["start"])
                ],
                "Plans starting (year)",
            )
            st.plotly_chart(plans_starting, use_container_width=True)

            open_plan_lengths = px.histogram(
                sliced_enriched_np[sliced_enriched_np["CeaseDate"].isna()],
                "NamedPlanLength (days)",
                color="Sex",
                title="Plans active on census day - Length",
            )
            st.plotly_chart(open_plan_lengths, use_container_width=True)

        with np_col2:
            plans_starting = make_indicator(
                sliced_enriched_np[
                    (sliced_enriched_np["CeaseDate"] > sen2.reference_period["start"])
                ],
                "Plans ending (year)",
            )
            st.plotly_chart(plans_starting, use_container_width=True)

            # Children with multiple placements
            placements_df = sliced_enriched_np.groupby(['child_id']).size().to_frame('Number of placements').reset_index()
            multiple_placements = px.pie(placements_df, names="Number of placements", title="Number of placements per child")
            st.plotly_chart(multiple_placements, use_container_width=True)

        with np_col3:
            ceased_reasons = px.histogram(
                sliced_enriched_np,
                "CeaseReason",
                color="Sex",
                title="Plans ceasing this year - Reason",
            )
            st.plotly_chart(ceased_reasons, use_container_width=True)

            sen_setting = px.histogram(
                sliced_enriched_np[sliced_enriched_np["CeaseDate"].isna()],
                "SENSetting",
                color="Sex",
                title="Plans active on census day - SEN Setting",
            )
            st.plotly_chart(sen_setting, use_container_width=True)

        with np_col4:
            active_census_day = make_indicator(
                sliced_enriched_np[sliced_enriched_np["CeaseDate"].isna()],
                "Plans active on census day",
            )
            st.plotly_chart(active_census_day, use_container_width=True)

            residential_setting = px.pie(
                sliced_enriched_np[
                    sliced_enriched_np["CeaseDate"].isna()
                    & sliced_enriched_np["PlanRes"].notna()
                ],
                names="PlanRes",
                title="Residential Setting",
            )
            st.plotly_chart(residential_setting, use_container_width=True)


        # TODO named plans:

        #   work based learning activities (plan wbp)
        #   personal budget taken up PB, peronal budget organised arrangements OA, direct payments DP
        #   plan detail  establishments

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

        timeliness_unconsidered = px.histogram(
            timeliness_df, "Timeliness - week 20 exceptions not considered", color="Sex", title="Timeliness - week 20 exceptions not considered"
        )

        timeliness_considered = px.histogram(
            timeliness_df, "Timeliness - week 20 exceptions considered", color="Sex", title="Timeliness - week 20 exceptions considered"
        )
        time_col1, time_col2 = st.columns(2)

        with time_col1:
            st.plotly_chart(timeliness_unconsidered, use_container_width=True)

        with time_col2:
            st.plotly_chart(timeliness_considered, use_container_width=True)

    with st.expander("Active Plans"):
        ap_col1, ap_col2, ap_col3, ap_col4 = st.columns(4)

        with ap_col1:

            open_closed_ap = px.pie(sliced_enriched_ap, names="PlanOpen", title="Active plans open/closed")
            st.plotly_chart(open_closed_ap, use_container_width=True)

            ehcs_transferred = px.histogram(sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()], "TransferLA", color="Sex", title="Open active plans - EHCs transferred ")
            st.plotly_chart(ehcs_transferred, use_container_width=True)
        
        with ap_col2:
            ap_residential = px.histogram(sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()], "RES", color="Sex", title="Open active plans - residential setting")
            st.plotly_chart(ap_residential, use_container_width=True)

            # Children with multiple placements
            placements_df_ap = sliced_enriched_ap.groupby(['child_id']).size().to_frame('Number of plans').reset_index()
            multiple_placements_ap = px.pie(placements_df_ap, names="Number of plans", title="Number of plans per child")
            st.plotly_chart(multiple_placements_ap, use_container_width=True)

        with ap_col3:
            ap_wpb = px.histogram(sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()], "WPB", color="Sex", title="Open active plans - work based learning ")
            st.plotly_chart(ap_wpb, use_container_width=True)

            placements_df_ap_open = sliced_enriched_ap[sliced_enriched_ap['LeavingDate'].isna()].groupby(['child_id']).size().to_frame('Number of plans').reset_index()
            multiple_placements_ap_open = px.pie(placements_df_ap_open, names="Number of plans", title="Number of open plans per child")
            st.plotly_chart(multiple_placements_ap_open, use_container_width=True)

        with ap_col4:
            ap_review_outcomes = px.histogram(sliced_enriched_ap[sliced_enriched_ap["LeavingDate"].notna()], "ReviewOutcome", color="Sex", title="Open active plans - review outcomes")
            st.plotly_chart(ap_review_outcomes, use_container_width=True)

            # st.table(sliced_enriched_ap.head(20))
        # TODO active plans
        #   date of last review meeting (time since?)
        #   annual review decisions
        #   phase transfer reviews
        #   placement details



    with st.expander("CYP in selected drilldown:"):
        st.table(sliced_enriched_persons)
