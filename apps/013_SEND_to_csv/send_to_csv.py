import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

dfs = {}

def get_values(xml_elements, table_dict: dict, xml_block):
    # st.write(table_dict)
    # st.write(xml_block)
    for element in xml_elements:
        try:
            table_dict[element] = xml_block.find(element).text
        except:
            table_dict[element] = pd.NA
    return table_dict

class XMLtoCSV:
    header = pd.DataFrame(columns=["Collection", "Year", "Reference Date"])

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
        self.Header = self.create_header(header)
        self.name = None

        children = root.find("Persons")

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
        person_dict["name"] = self.name
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

            requests_dict["name"] = self.name
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

        if named_plan_locs:
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
        if active_plan_locs:
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


def convert_data(root: ET.Element):
    datafiles = XMLtoCSV(root)

    return datafiles

def convert_for_sen2_tool(m1, m2, m3, m4, m5):
    output_dict = {"Persons": m1, "Requests": m2, "Assessments": m3, "Named Plan": m4, "Active Plans": m5}

    return output_dict

def to_excel(dfs):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    for name, frame in dfs.items():
        frame.to_excel(writer, sheet_name = name, index=False)
    workbook = writer.book
    writer.save()
    processed_data = output.getvalue()
    return processed_data
    
def move_column_inplace(df, col, pos):
    col = df.pop(col)
    df.insert(pos, col.name, col)

def move_to_front_inplace(df, col1, col2):
    move_column_inplace(df, col2, 0)
    move_column_inplace(df, col1, 0)
    return df

#################
# Streamlit Page
#################

st.title('SEN2 to CSV')

file = st.file_uploader("Upload SEN2 XML here", accept_multiple_files=False)

if file:
    st.write("File upload sucessful!")

    fulltree = ET.parse(file)
    root = fulltree.getroot()

    st.write('Beginning conversion')
    with st.spinner("Wait for it..."):
        data_files = convert_data(root)

    modules = convert_for_sen2_tool(
        data_files.persons,
        data_files.requests,
        data_files.assessments,
        data_files.named_plan,
        data_files.active_plans,
    )

    st.write('Conversion done, processing to excel')

    for key, module in modules.items():
        if 'child_id' in module.columns:
            modules[key] = move_to_front_inplace(module, 'name', "child_id")
        st.write(module)

    output = to_excel(modules)

    st.download_button(
        "Download output excel here", output, file_name="df_test.xlsx"
    )