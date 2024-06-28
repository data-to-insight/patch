import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px

# Useful dictionaries

# Events we want to include in the child journeys
journey_events = {
    "contact": {"List_1": "Date of Contact"},
    "early_help_assessment_start": {"List_2": "Assessment start date"},
    "early_help_assessment_end": {"List_2": "Assessment completion date"},
    "referral": {"List_3": "Date of referral"},
    "assessment_start": {"List_4": "Continuous Assessment Start Date"},
    "assessment_authorised": {"List_4": "Continuous Assessment Date of Authorisation"},
    "s47": {"List_5": "Strategy discussion initiating Section 47 Enquiry Start Date"},
    "icpc": {"List_5": "Date of Initial Child Protection Conference"},
    "cin_start": {"List_6": "CIN Start Date"},
    "cin_end": {"List_6": "CIN Closure Date"},
    "cpp_start": {"List_7": "Child Protection Plan Start Date"},
    "cpp_end": {"List_7": "Child Protection Plan End Date"},
    "lac_start": {"List_8": "Date Started to be Looked After"},
    "lac_end": {"List_8": "Date Ceased to be Looked After"},
}

journey_events_named = {
    "contact": {"Contacts": "Date of Contact"},
    "early_help_assessment_start": {"Early Help": "Assessment start date"},
    "early_help_assessment_end": {"Early Help": "Assessment completion date"},
    "referral": {"Referrals": "Date of referral"},
    "assessment_start": {"Assessments": "Continuous Assessment Start Date"},
    "assessment_authorised": {
        "Assessments": "Continuous Assessment Date of Authorisation"
    },
    "s47": {
        "Sec47 and ICPC": "Strategy discussion initiating Section 47 Enquiry Start Date"
    },
    "icpc": {"Sec47 and ICPC": "Date of Initial Child Protection Conference"},
    "cin_start": {"Children in Need": "CIN Start Date"},
    "cin_end": {"Children in Need": "CIN Closure Date"},
    "cpp_start": {"Child Protection": "Child Protection Plan Start Date"},
    "cpp_end": {"Child Protection": "Child Protection Plan End Date"},
    "lac_start": {"Children in Care": "Date Started to be Looked After"},
    "lac_end": {"Children in Care": "Date Ceased to be Looked After"},
}

journey_events_by_index = {
    "contact": {0: "Date of Contact"},
    "early_help_assessment_start": {1: "Assessment start date"},
    "early_help_assessment_end": {1: "Assessment completion date"},
    "referral": {2: "Date of referral"},
    "assessment_start": {3: "Continuous Assessment Start Date"},
    "assessment_authorised": {3: "Continuous Assessment Date of Authorisation"},
    "s47": {4: "Strategy discussion initiating Section 47 Enquiry Start Date"},
    "icpc": {4: "Date of Initial Child Protection Conference"},
    "cin_start": {5: "CIN Start Date"},
    "cin_end": {5: "CIN Closure Date"},
    "cpp_start": {6: "Child Protection Plan Start Date"},
    "cpp_end": {6: "Child Protection Plan End Date"},
    "lac_start": {7: "Date Started to be Looked After"},
    "lac_end": {7: "Date Ceased to be Looked After"},
}

# Abbreviations for events (for the "journeys reduced")
events_map = {
    "contact": "C",
    "referral": "R",
    "early_help_assessment_start": "EH",
    "early_help_assessment_end": "EH|",
    "assessment_start": "AS",
    "assessment_authorised": "AA",
    "s47": "S47",
    "icpc": "ICPC",
    "cin_start": "CIN",
    "cin_end": "CIN|",
    "cpp_start": "CPP",
    "cpp_end": "CPP|",
    "lac_start": "LAC",
    "lac_end": "LAC|",
}


# Functions


def build_annexarecord(
    input_file, events=journey_events, events_named=journey_events_named
):
    """
    Creates a flat file with three columns:
    1) child unique id
    2) Date
    3) Type
    Based on events in Annex A lists defined in the events argument
    """

    # Create empty dataframe in which we'll drop our events
    df_list = []

    try:
        # Loop over our dictionary to populate the log
        for event in events:

            contents = events[event]
            list_number = list(contents.keys())[0]
            date_column = contents[list_number]
            # Load Annex A list
            df = pd.read_excel(input_file, sheet_name=list_number)

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
                    ">>>>>  Could not find column {} in {}".format(
                        date_column, list_number
                    )
                )
    except:
        try:
            for event in events_named:

                contents = events_named[event]
                list_number = list(contents.keys())[0]
                date_column = contents[list_number]
                # Load Annex A list
                df = pd.read_excel(input_file, sheet_name=list_number)

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
                        ">>>>>  Could not find column {} in {}".format(
                            date_column, list_number
                        )
                    )
        except:
            for event in journey_events_by_index:

                contents = journey_events_by_index[event]
                list_number = list(contents.keys())[0]
                date_column = contents[list_number]
                # Load Annex A list
                df = pd.read_excel(input_file, sheet_name=list_number)

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
                        ">>>>>  Could not find column {} in {}".format(
                            date_column, list_number
                        )
                    )

    # Pull all events into a unique datafrane annexarecord
    annexarecord = pd.concat(df_list, sort=False)

    # Clean annexarecord
    # Define categories to be able to sort events
    ordered_categories = [
        "contact",
        "referral",
        "early_help_assessment_start",
        "early_help_assessment_end",
        "assessment_start",
        "assessment_authorised",
        "s47",
        "icpc",
        "cin_start",
        "cin_end",
        "cpp_start",
        "cpp_end",
        "lac_start",
        "lac_end",
    ]
    annexarecord.Type = annexarecord.Type.astype("category")
    annexarecord.Type.cat.set_categories(
        [c for c in ordered_categories if c in annexarecord.Type.unique()],
        inplace=True,
        ordered=True,
    )
    # Ensure dates are in the correct format
    annexarecord.Date = pd.to_datetime(annexarecord.Date)

    return annexarecord


def joined_string(series):
    """
    Turns all elements from a series into a string, joining elements with "->"
    """
    list_elements = series.tolist()
    return " -> ".join(list_elements)


def create_journeys(df):
    df = df[~df["Date"].isnull()]
    df = df[~df["Type"].isnull()]
    df = df.sort_values(["Date", "Type"])

    # Add new column showing each event in format [00-00-0000/event]
    df["TimeEvent"] = "[" + df.Date.astype(str) + "/" + df.Type.astype(str) + "]"

    # Add new column showing each event in reduced form e.g. "C" for contact
    df["reduced"] = df.Type.map(events_map)

    # Create both long and reduced journeys
    grouped = df.groupby("child unique id")
    journey_long = grouped["TimeEvent"].apply(joined_string)
    journey_reduced = grouped["reduced"].apply(joined_string)

    # Create new dataframe with both long and reduced journeys
    journeys_df = pd.DataFrame(
        {"Child journey": journey_long, "Child journey reduced": journey_reduced},
        index=journey_long.index,
    )

    return journeys_df.reset_index()


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Journeys")
    workbook = writer.book
    worksheet = writer.sheets["Journeys"]
    format1 = workbook.add_format({"num_format": "0.00"})
    worksheet.set_column("A:A", None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def gantt_data_generator(child_data, df):
    data_string = df[df["child unique id"] == child_data]["Child journey"].iloc[0]
    events_split = pd.DataFrame(data_string.split("->"), columns=["original_split"])

    events_split[["Date", "Type"]] = events_split["original_split"].str.split(
        "/", n=1, expand=True
    )
    events_split["Type"] = events_split["Type"].str.replace("]", "")
    events_split["Date"] = events_split["Date"].str.replace("[", "")

    events_split["Date"] = pd.to_datetime(
        events_split["Date"], format="%Y-%m-%d"
    ).dt.date
    events_split.sort_values("Date", ascending=True)

    events_split["Event order"] = events_split.groupby("Type").cumcount()

    return events_split


def empty_date_check(date_to_check):
    if len(date_to_check) == 1:
        return date_to_check.iloc[0]
    else:
        # return pd.to_datetime("today")
        return end_of_collection


def finish_dates(type, date, event):
    if "contact" in type:
        return date + pd.DateOffset(days=1)
    elif "referral" in type:
        return date + pd.DateOffset(days=1)
    elif "s47" in type:
        return date + pd.DateOffset(days=1)
    elif "icpc" in type:
        return date + pd.DateOffset(days=1)
    elif "assessment_start" in type:
        return_date = events_split[
            (events_split["Type"].str.contains("assessment_authorised"))
            & (events_split["Event order"] == event)
        ]["Date"]
        return_date = empty_date_check(return_date)
        return return_date
    elif "early_help_assessment_start" in type:
        return_date = events_split[
            (events_split["Type"].str.contains("early_help_assessment_end"))
            & (events_split["Event order"] == event)
        ]["Date"]
        return_date = empty_date_check(return_date)
        return return_date
    elif "cin_start" in type:
        return_date = events_split[
            (events_split["Type"].str.contains("cin_end"))
            & (events_split["Event order"] == event)
        ]["Date"]
        return_date = empty_date_check(return_date)
        return return_date
    elif "cpp_start" in type:
        return_date = events_split[
            (events_split["Type"].str.contains("cpp_end"))
            & (events_split["Event order"] == event)
        ]["Date"]
        return_date = empty_date_check(return_date)
        return return_date
    elif "lac_start" in type:
        return_date = events_split[
            (events_split["Type"].str.contains("lac_end"))
            & (events_split["Event order"] == event)
        ]["Date"]
        return_date = empty_date_check(return_date)
        return return_date
    else:
        return pd.NA


def make_gantt_chart(df, chosen_child):
    df = df[~(df["Type"].str.contains("end") | df["Type"].str.contains("authorised"))]
    st.write(df)
    fig = px.timeline(
        df,
        x_start="Date",
        x_end="Finish Dates",
        y="Type",
        color="Type",
        title=f"Journey for child: {chosen_child}",
    )
    fig.update_yaxes(autorange="reversed")

    return fig


# Main app
st.markdown(
    "[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/001_template/app.py)"
)

st.title("Child Event Journeys")

with st.expander("Explanation and accreditation"):
    st.markdown(
        """
    This code was originally developed by [Celine Gross](https://github.com/Cece78) and [Kaj Siebert](https://github.com/kws) 
    at Social Finance as part of a grant funded programme to support Local Authorities to collaborate on data analysis (since 
    this, Data to Insight have given the code a new home on the PATCh tool). The 
    programme was called the ‘Front Door Data Collaboration’. It was supported financially by the Christie Foundation and Nesta 
    (through the ‘What Works Centre for Children’s Social Care’). The LAs whose staff guided its development were Bracknell 
    Forest, West Berkshire, Southampton, and Surrey. It also benefitted from advice from the National Performance and Information 
    Managers Group and from the Ofsted Social Care Inspection Insight team.

    ## What does this code do?

    **What is the child's journey through social care?**

    Getting a longitudinal view of the child's journey through social care is not easy with [Annex A](https://www.gov.uk/government/publications/inspecting-local-authority-childrens-services-from-2018). Annex A is a spreadsheet containing different tabs for different "types" of events: List 1 for Contacts, List 2 for Early Help assessments, etc. It contains useful data but it does not allow to get the whole picture of what happened to each child (unless you want to run from one tab to the next, frantically hitting Ctrl+F to find events related to a particular child...).

    **That is a problem because understanding the child's experience is key to providing better support**. Analysing events in isolation (e.g. looking only at Contacts, or Referrals) is valuable, but not enough for a comprehensive view.

    **This code creates a simple "journey" line showing the experience of the child from the Annex A data**. For each child, you'll be able to read a one-liner in the following format:
    ```
    [2025-03-01/contact] -> [2025-05-02/contact] -> [2025-05-05/referral] -> [2025-05-10/assessment_start]
    ```
    In this example, the child had a first contact on 1 March 2025, followed by a second contact on 2 May 2025. This second contact triggers a referral on 5 May 2025 and an assessment start on 10 May 2025.

    We also included a "reduced" journey line to enable you to do quick searches on journey patterns. In its "reduced" form, the above example would be:
    ```
    C -> C -> R -> AS
    ```
    The reduced column allows for easy searches: if I wanted to see all the children who had at least 3 contacts one after the other, I could do a quick Ctrl+F on "C -> C -> C".

    ## How to run this code

    This code has been adapted from the original Python which required the user to have Python installed on their local machine. In this version one simply needs to drop their
    Annex A xlsx into the upload box. There are, however, some slight requirements. Firstly, you need to have your entire Annex A
    in one Excel file. Next, you must either name the sheets in the style of "List_1", through to "List_8" or capitalised and named, such as "Contacts" and "Children in Care".
    Full tables of necessary sheet and column name spellings/syntax/grammar can be seen in the dropdown below.
    """
    )

with st.expander("Sheet names and column headers"):
    st.write(
        """
    Only lists 1-8 are needed, and they must be labelled according to one of the two following schema. 
    We've tried to add some leeway into the code in case it doesn't match exactly, but if things are going wrong, 
    these are good things to check!"""
    )
    st.table(
        pd.DataFrame(
            {
                "Allowed sheet names (numbered)": [
                    "List_1",
                    "List_2",
                    "List_3",
                    "List_4",
                    "List_5",
                    "List_6",
                    "List_7",
                    "List_8",
                ],
                "Allowed sheet names (named)": [
                    "Contacts",
                    "Early Help",
                    "Referrals",
                    "Assessments",
                    "Sec47 and ICPC",
                    "Children in Need",
                    "Child Protection",
                    "Children in Care",
                ],
            }
        )
    )
    st.write(
        "Only some columns from each table are needed, and they must be formatted as below."
    )
    st.table(
        pd.DataFrame(
            {
                "Contacts": ["Date of Contact", ""],
                "Early Help": ["Assessment start date", "Assessment completion date"],
                "Referrals": ["Date of referral", ""],
                "Assessments": [
                    "Continuous Assessment Start Date",
                    "Continuous Assessment Date of Authorisation",
                ],
                "Sec47 and ICPC": [
                    "Strategy discussion initiating Section 47 Enquiry Start Date",
                    "Date of Initial Child Protection Conference",
                ],
                "Children in Need": ["CIN Start Date", "CIN Closure Date"],
                "Child Protection": [
                    "Child Protection Plan Start Date",
                    "Child Protection Plan End Date",
                ],
                "Children in Care": [
                    "Date Started to be Looked After",
                    "Date Ceased to be Looked After",
                ],
            }
        )
    )


file = st.file_uploader("Upload annex A here")

if file:
    st.write("File upload sucessful!")

    annexa = build_annexarecord(file)
    journeys = create_journeys(annexa)

    st.dataframe(journeys)

    output = to_excel(journeys)

    # st.write(annexa)

    st.download_button("Download output excel here", output, file_name="df_test.xlsx")

    with st.sidebar:
        chosen_child = st.sidebar.selectbox(
            "Select child for journey visualisation", journeys["child unique id"]
        )
        end_of_collection = st.sidebar.date_input(
            "Select end date for ongoing plans/assessments.",
        )

    # gannt chart
    events_split = gantt_data_generator(chosen_child, journeys)
    events_split["Finish Dates"] = events_split.apply(
        lambda row: finish_dates(row["Type"], row["Date"], row["Event order"]), axis=1
    )

    gantt = make_gantt_chart(events_split, chosen_child)
    st.plotly_chart(gantt)
