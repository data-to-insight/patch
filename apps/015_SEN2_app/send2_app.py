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


def make_bar(df, buckets, column):
    values_df = pd.DataFrame({column: buckets})
    df_counts = df.groupby(column).size().to_frame("Count").reset_index()
    df_counts = df_counts.merge(values_df, how="outer", on="AgeBuckets")
    df_counts["Count"] = df_counts["Count"].fillna(0)
    df_counts.sort_values(column, inplace=True)

    bar = px.bar(df_counts, x=column, y="Count")

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

        self.reference_date = self._get_reference_date(self.data.header)

        self.persons = self.data.persons

    def _get_reference_date(self, df):
        reference_date = df["ReferenceDate"].iloc[0]

        reference_date = pd.to_datetime(reference_date, format="%Y-%m-%d")

        return reference_date

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
            lambda x: relativedelta(dt1=self.reference_date, dt2=x).normalized().years
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
        # [relativedelta(outcome, received).days if ~pd.isnull(received) else pd.NaT for outcome, received  in zip(enriched_df['RequestOutcomeDate'], enriched_df['ReceivedDate'])]
        # enrich requests sources (pg 20)

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
        enriched_df = self.data.names_plan.copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[["AgeBuckets", "EthnicityGroup", "Sex", "child_id"]],
            how="left",
            on="child_id",
        )

        return enriched_df

    @property
    def enriched_active_plans(self):
        enriched_df = self.data.active_plans.copy()

        enriched_df = enriched_df.merge(
            self.enriched_persons[["AgeBuckets", "EthnicityGroup", "Sex", "child_id"]],
            how="left",
            on="child_id",
        )

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
            (sen2.enriched_requests["Sex"].unique()),
            default=(sen2.enriched_requests["Sex"].unique()),
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

    sliced_enriched_persons = sen2.enriched_persons[
        sen2.enriched_persons["Sex"].isin(sex_selected)
        & sen2.enriched_persons["AgeBuckets"].isin(age_selected)
    ]

    sliced_enriched_requests = sen2.enriched_requests[
        sen2.enriched_requests["Sex"].isin(sex_selected)
        & sen2.enriched_requests["AgeBuckets"].isin(age_selected)
    ]

    sliced_enriched_assessments = sen2.enriched_assessments[
        (sen2.enriched_assessments["Sex"].isin(sex_selected))
        & (sen2.enriched_assessments["AgeBuckets"].isin(age_selected))
        & (sen2.enriched_assessments["AssessmentOutcome"] != "H")
    ]

    with st.expander("Headline Figures"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            gender_pie = px.pie(sliced_enriched_persons, names="Sex")
            st.plotly_chart(gender_pie, use_container_width=True)

        with col2:
            ethnicity_chart = px.histogram(sliced_enriched_persons, "EthnicityGroup")
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
            )
            st.plotly_chart(age_chart, use_container_width=True)

        with col4:
            sen_type_chart = px.histogram(sen2.enriched_active_plans, "SENtype")
            st.plotly_chart(sen_type_chart, use_container_width=True)

    with st.expander("Requests"):
        req_col1, req_col2, req_col3, req_col4 = st.columns(4)

        with req_col1:
            total_requests = make_indicator(sliced_enriched_requests, "Total Requests")
            st.plotly_chart(total_requests, use_container_width=True)

            request_lengths = px.histogram(sliced_enriched_requests, "RequestLength")
            st.plotly_chart(request_lengths, use_container_width=True)

        with req_col2:
            request_sources = px.histogram(
                sliced_enriched_requests, "RequestSource", color="Sex"
            )

            st.plotly_chart(request_sources, use_container_width=True)

            requests_rya = px.pie(sliced_enriched_requests, names="RYA")
            st.plotly_chart(requests_rya, use_container_width=True)

        with req_col3:
            request_outcomes = px.histogram(
                sliced_enriched_requests, "RequestOutcome", color="Sex"
            )

            st.plotly_chart(request_outcomes, use_container_width=True)

            requests_by_age = px.histogram(sliced_enriched_requests, "AgeBuckets")
            st.plotly_chart(requests_by_age, use_container_width=True)

        with req_col4:
            request_tribunal = px.histogram(
                sliced_enriched_requests, "MediationOrTribunal", color="Sex"
            )
            st.plotly_chart(request_tribunal, use_container_width=True)

            requests_exported = px.pie(sliced_enriched_requests, names="Exported")
            st.plotly_chart(requests_exported, use_container_width=True)

    with st.expander("Assessments"):
        ass_col1, ass_col2, ass_col3, ass_col4 = st.columns(4)

        with ass_col1:
            total_assessments = make_indicator(
                sliced_enriched_assessments, "Total Assessments"
            )
            st.plotly_chart(total_assessments, use_container_width=True)

            st.write(
                "TODO assessment timeliness - how many in 20 weeks, how many over 20 weeks without extension"
            )

        with ass_col2:
            assessment_outcomes = px.histogram(
                sliced_enriched_assessments, "AssessmentOutcome", color="Sex"
            )
            st.plotly_chart(assessment_outcomes, use_container_width=True)

        with ass_col3:
            assessment_tribunal = px.histogram(
                sliced_enriched_assessments, "MediationOrTribunal", color="Sex"
            )
            st.plotly_chart(assessment_tribunal, use_container_width=True)

        with ass_col4:
            week20s = px.histogram(sliced_enriched_assessments, "Week20", color="Sex")
            st.plotly_chart(week20s, use_container_width=True)

    with st.expander("Named Plans"):
        np_col1, np_col2, np_col3, np_col4 = st.columns(4)
        # TODO named plans:
        #   plans starting in year
        #   plans ending in year
        #   plans ceased in year reasons
        #   active plans on census day
        #   active plans open length
        #   sen settings
        #   plan res (residential setting)
        #   work based learning activities (plan wbp)
        #   personal budget taken up PB, peronal budget organised arrangements OA, direct payments DP
        #   plan detail  establishments
        #   sen settings

        pass

    with st.expander("Active Plans"):
        ap_col1, ap_col2, ap_col3, ap_col4 = st.columns(4)
        # TODO active plans
        #   ehcs transferred in TransferLA
        #   residential settings
        #   work based learning activities
        #   date of lasr review meeting (time since?)
        #   annual review decisions
        #   phase transfer reviews
        #   placement details
        pass

    with st.expander("CYP in selected drilldown:"):
        st.table(sliced_enriched_persons)
