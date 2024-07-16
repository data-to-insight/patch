import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import re

"""
Things we may want to find:
Multiples of things before step-ups

"""

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

journey_events_stripped = {
    "contact": {"List 1": 5},
    "early_help_assessment_start": {"List 2": 5},
    "early_help_assessment_end": {"List 2": 6},
    "referral": {"List 3": 5},
    "assessment_start": {"List 4": 6},
    "assessment_authorised": {"List 4": 8},
    "s47": {"List 5": 6},
    "icpc": {"List 5": 8},
    "cin_start": {"List 6": 6},
    "cin_end": {"List 6": 9},
    "cpp_start": {"List 7": 6},
    "cpp_end": {"List 7": 12},
    "lac_start": {"List 8": 7},
    "lac_end": {"List 8": 20},
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


def csv_annex_a_record(input_file, events=journey_events_stripped):
    df_list = []

    # Loop over our dictionary to populate the log
    for event in events:

        contents = events[event]
        list_number = list(contents.keys())[0]

        date_column = contents[list_number]
        # Load Annex A list
        df = input_file[list_number]
        # st.write(df)

        df = df[df.iloc[:, date_column].notnull()]
        df["Type"] = event
        df["Date"] = df.iloc[:, date_column]
        # st.write(df[['Type', 'Date']])
        df_list.append(df)

        # # Get date column information
        # df.columns = [col.lower().strip() for col in df.columns]
        # date_column_lower = date_column.lower()
        # if date_column_lower in df.columns:
        #     df = df[df[date_column_lower].notnull()]
        #     df["Type"] = event
        #     df["Date"] = df[date_column_lower]
        #     df_list.append(df)

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
    events_split["Type"] = events_split["Type"].str.strip()
    events_split["Date"] = events_split["Date"].str.replace("[", "")

    events_split["Date"] = pd.to_datetime(
        events_split["Date"], format="%Y-%m-%d"
    ).dt.date
    events_split.sort_values("Date", ascending=True)

    events_split["Event order"] = events_split.groupby("Type").cumcount()

    return events_split


def no_esc_function(df, concern_event, following_events):

    ordered_categories = [
        "referral",
        "contact",
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

    concern_children = set(
        df[(df["Type"].str.contains(concern_event)) & (df["count"] >= 2)][
            "child unique id"
        ].to_list()
    )
    not_referral = [
        event for event in ordered_categories if event not in (following_events)
    ]
    with_other_steps = set(
        df[df["Type"].isin(not_referral)]["child unique id"].to_list()
    )
    no_escalation = concern_children - with_other_steps

    return no_escalation


def concern_data_generator(df):
    events_split = df[["child unique id", "Child journey"]].copy()
    events_split["Child journey"] = events_split["Child journey"].str.split("->")
    events_split = events_split.explode("Child journey")
    events_split[["Date", "Type"]] = events_split["Child journey"].str.split(
        "/", n=1, expand=True
    )

    events_split.drop("Child journey", axis=1, inplace=True)
    events_split["Type"] = events_split["Type"].str.replace("]", "")
    events_split["Type"] = events_split["Type"].str.strip()
    events_split["Date"] = events_split["Date"].str.replace("[", "")

    count_events = (
        events_split.groupby(["child unique id", "Type"])["child unique id"]
        .count()
        .reset_index(name="count")
    )
    # count_events = count_events[count_events['count'] > 1]

    count_events["type number"] = (
        count_events["child unique id"].astype("str")
        + " "
        + count_events["count"].astype("str")
    )
    # st.write(count_events)

    count_events["count"] = count_events["count"].astype("int")

    # refs without contact, contact without ass/s47/icpc/, ass without cin/lac
    ref_concern_list = count_events[
        (count_events["Type"].str.contains("referral")) & (count_events["count"] >= 3)
    ]["type number"].to_list()
    contact_concern_list = count_events[
        (count_events["Type"].str.contains("contact")) & (count_events["count"] >= 2)
    ]["type number"].to_list()
    ass_concern_list = count_events[
        (count_events["Type"].str.contains("assessment_start"))
        & (count_events["count"] >= 2)
    ]["type number"].to_list()

    ref_no_escalation = no_esc_function(count_events, "referral", ("referral"))
    contact_no_escalation = no_esc_function(
        count_events, "contact", ("referral", "contact")
    )
    eh_no_escalation = no_esc_function(
        count_events,
        "early_help_assessment_start",
        (
            "referral",
            "contact",
            "early_help_assessment_start",
            "early_help_assessment_end",
        ),
    )
    ass_no_escalation = no_esc_function(
        count_events,
        "assessment_start",
        (
            "referral",
            "contact",
            "early_help_assessment_start",
            "early_help_assessment_end",
            "assessment_start",
            "assessment_authorised",
        ),
    )
    s47_no_escalation = no_esc_function(
        count_events,
        "s47",
        (
            "referral",
            "contact",
            "early_help_assessment_start",
            "early_help_assessment_end",
            "assessment_start",
            "assessment_authorised",
            "s47",
        ),
    )
    icpc_no_escalation = no_esc_function(
        count_events,
        "icpc",
        (
            "referral",
            "contact",
            "early_help_assessment_start",
            "early_help_assessment_end",
            "assessment_start",
            "assessment_authorised",
            "icpc",
        ),
    )
    cin_no_escalation = no_esc_function(
        count_events,
        "cin_start",
        (
            "referral",
            "contact",
            "early_help_assessment_start",
            "early_help_assessment_end",
            "assessment_start",
            "assessment_authorised",
            "icpc",
            "cin_start",
            "cin_end",
        ),
    )
    cpp_no_escalation = no_esc_function(
        count_events,
        "cpp_start",
        (
            "referral",
            "contact",
            "early_help_assessment_start",
            "early_help_assessment_end",
            "assessment_start",
            "assessment_authorised",
            "icpc",
            "cin_start",
            "cin_end",
            "cpp_start",
            "cpp_end",
        ),
    )

    # st.write(f'concern kids {ref_concern_list}')

    # ordered_categories = [
    #     "referral",
    #     "contact",
    #     "early_help_assessment_start",
    #     "early_help_assessment_end",
    #     "assessment_start",
    #     "assessment_authorised",
    #     "s47",
    #     "icpc",
    #     "cin_start",
    #     "cin_end",
    #     "cpp_start",
    #     "cpp_end",
    #     "lac_start",
    #     "lac_end",
    # ]

    # 2 + refs with no escalation
    # ref_concern_children = set(count_events[(count_events['Type'].str.contains('referral')) & (count_events['count'] >= 2)]['child unique id'].to_list())
    # not_referral = [event for event in ordered_categories if event not in ('referral')]
    # with_other_steps = set(count_events[count_events['Type'].isin(not_referral)]['child unique id'].to_list())
    # ref_no_escalation = ref_concern_children - with_other_steps

    # # 2+ contacts no escalation
    # contact_concern_children = set(count_events[(count_events['Type'].str.contains('contact')) & (count_events['count'] >= 2)]['child unique id'].to_list())
    # nothing_after_contact = [event for event in ordered_categories if event not in ('referral', 'contact')]
    # with_other_steps = set(count_events[count_events['Type'].isin(nothing_after_contact)]['child unique id'].to_list())
    # contact_no_escalation = contact_concern_children - with_other_steps

    # #2+ eh no esc
    # eh_concern_children = set(count_events[(count_events['Type'].str.contains('early_help_assessment_start')) & (count_events['count'] >= 2)]['child unique id'].to_list())
    # nothing_after_eh = [event for event in ordered_categories if event not in ('referral', 'contact')]
    # with_other_steps = set(count_events[count_events['Type'].isin(nothing_after_eh)]['child unique id'].to_list())
    # contact_no_escalation = eh_concern_children - with_other_steps

    concern_dict = {
        "Referrals": ref_concern_list,
        "Contacts": contact_concern_list,
        "Assessments": ass_concern_list,
        "Multiple referrals no escalation": ref_no_escalation,
        "Multiple contact no escalation": contact_no_escalation,
        "Multiple early help no escalation": eh_no_escalation,
        "Multiple s47 no escalation": s47_no_escalation,
        "Multiple ICPC no escalation": icpc_no_escalation,
        "Multiple CIN no escalation": cin_no_escalation,
        "Multiple CPP no escalation": cpp_no_escalation,
    }

    return count_events, concern_dict


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
    elif ("assessment_start" in type) & ("early_help" not in type):
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


def type_check(type):
    if "contact" in type:
        return "Contacts"
    elif "referral" in type:
        return "Referrals"
    elif "s47" in type:
        return "Section 47s"
    elif "icpc" in type:
        return "ICPCs"
    elif ("assessment" in type) & ("early_help" not in type):
        return "Assessments"
    elif "early_help_assessment" in type:
        return "Early Help Assessments"
    elif "cin" in type:
        return "CIN"
    elif "cpp" in type:
        return "CPP"
    elif "lac" in type:
        return "LAC"
    else:
        return pd.NA


def make_gantt_chart(df, chosen_child):
    df = df[~(df["Type"].str.contains("end") | df["Type"].str.contains("authorised"))]
    df["Type"] = df["Type"].apply(type_check)
    # st.write(df)
    fig = px.timeline(
        df,
        x_start="Date",
        x_end="Finish Dates",
        y="Type",
        color="Type",
        title=f"Journey for child: {chosen_child}",
    )
    fig.update_yaxes(autorange="reversed")

    return fig, df


def gantt_type_2(chosen_child, df):
    df["Finish Dates"] = df["Date"] + pd.DateOffset(days=1)

    df["Joined Types"] = df["Type"].apply(type_check)
    # st.write(df)

    fig = px.timeline(
        df,
        x_start="Date",
        x_end="Finish Dates",
        y="Joined Types",
        color="Type",
        title=f"Journey for child: {chosen_child}",
    )
    fig.update_yaxes(autorange="reversed")
    # st.write(df)

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


file = st.file_uploader("Upload annex A here", accept_multiple_files=True)

if file:
    st.write("File upload sucessful!")
    # st.write(len(file))

    excel, gantt, concern = st.tabs(
        [
            "Annex A journeys table and download",
            "Journeys timeline",
            "Potentially concerning children",
        ]
    )

    if len(file) == 1:
        file = file[0]
        annexa = build_annexarecord(file)
    elif len(file) > 1:
        loaded_files = {
            uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in file
        }

        renamed_files = {}
        for k, v in loaded_files.items():
            if "List 1" in k:
                renamed_files["List 1"] = v
            if "List 2" in k:
                renamed_files["List 2"] = v
            if "List 3" in k:
                renamed_files["List 3"] = v
            if "List 4" in k:
                renamed_files["List 4"] = v
            if "List 5" in k:
                renamed_files["List 5"] = v
            if "List 6" in k:
                renamed_files["List 6"] = v
            if "List 7" in k:
                renamed_files["List 7"] = v
            if "List 8" in k:
                renamed_files["List 8"] = v
            if "List 9" in k:
                renamed_files["List 9"] = v

        annexa = csv_annex_a_record(renamed_files)
    journeys = create_journeys(annexa)

    with excel:
        st.dataframe(journeys)

        output = to_excel(journeys)

        # st.write(annexa)

        st.download_button(
            "Download output excel here", output, file_name="df_test.xlsx"
        )

    with st.sidebar:
        chosen_child = st.sidebar.selectbox(
            "Select child for journey visualisation", journeys["child unique id"]
        )
        end_of_collection = st.sidebar.date_input(
            "Select end date for ongoing plans/assessments.",
        )

    with gantt:
        # gannt chart type 1
        events_split = gantt_data_generator(chosen_child, journeys)
        events_split["Finish Dates"] = events_split.apply(
            lambda row: finish_dates(row["Type"], row["Date"], row["Event order"]),
            axis=1,
        )

        gantt, gantt_data = make_gantt_chart(events_split, chosen_child)
        st.dataframe(gantt_data[["Type", "Date", "Finish Dates"]])
        st.plotly_chart(gantt)

        # gantt chart type 2
        gantt_2 = gantt_type_2(chosen_child, events_split)
        st.plotly_chart(gantt_2)

    with concern:
        concern_split, concern_dict = concern_data_generator(journeys)
        st.write(concern_split)
        st.write(concern_dict)
