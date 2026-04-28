import pandas as pd
import numpy as np

from io import BytesIO

import streamlit as st
from pyodide.http import open_url

# Set variables
# #TODO In the pipeline version this must be updated to take actual reference dates.
# Ideally the data ought to be in every row already.
reference_date_q1 = pd.to_datetime("19/09/2024", format="%d/%m/%Y")
reference_date_q2 = pd.to_datetime("19/09/2024", format="%d/%m/%Y")
reference_date_q3 = pd.to_datetime("19/09/2024", format="%d/%m/%Y")
reference_date_q4 = pd.to_datetime("19/09/2024", format="%d/%m/%Y")


mye2_persons_url = "https://raw.githubusercontent.com/data-to-insight/patch/refs/heads/main/apps/014_Eastern_Region_Pre_processing/MYE2%20-%20Persons.csv"
mye2_females_url = "https://raw.githubusercontent.com/data-to-insight/patch/refs/heads/main/apps/014_Eastern_Region_Pre_processing/MYE2%20-%20Females.csv"
mye2_males_url = "https://raw.githubusercontent.com/data-to-insight/patch/refs/heads/main/apps/014_Eastern_Region_Pre_processing/MYE2%20-%20Males.csv"


# Utility functions for pre-processing
# #TODO This needs to be updated to work for every reference date
def quarter_reference_date(df):
    if "Q1" in df["Time Period"]:
        return reference_date_q1
    if "Q2" in df["Time Period"]:
        return reference_date_q2
    if "Q3" in df["Time Period"]:
        return reference_date_q3
    if "Q4" in df["Time Period"]:
        return reference_date_q4


def reference_date(df):
    st.write(df)
    date_string = f"01/{int(df['Month'])}/{int(df['Year'])}"
    ref_date = pd.to_datetime(date_string, format="%d/%m/%Y").date()
    return ref_date


def age_bins(df):
    # Sums ages from ONS data into age groups used by the ChAT
    df["0-17 years"] = df.iloc[:, :22].sum(axis="columns")
    df["Under 1"] = df.iloc[:, :1].sum(axis="columns")
    df["1-4 years"] = df.iloc[:, 1:5].sum(axis="columns")
    df["5-9 years"] = df.iloc[:, 5:10].sum(axis="columns")
    df["5-16 years"] = df.iloc[:, 5:17].sum(axis="columns")
    df["10-15 years"] = df.iloc[:, 10:16].sum(axis="columns")
    df["16 & over"] = df.iloc[:, 16:].sum(axis="columns")
    df["17-18 years"] = df.iloc[:, 17:19].sum(axis="columns")
    df["19-21 years"] = df.iloc[:, 19:22].sum(axis="columns")
    df["18-25 years"] = df.iloc[:, 18:].sum(axis="columns")
    df["0-25 years"] = df.iloc[:, :].sum(axis="columns")

    return df


def ethnic_main_group(row):
    # Used to  add ethnic main groups to every row
    if row[-4:] in ["WBRI", "WIRI", "WIRT", "WROM", "WOTH"]:
        return "White"
    if row[-4:] in ["MWBC", "MWBA", "MWAS", "MOTH"]:
        return "Mixed"
    if row[-4:] in ["AIND", "APKN", "ABAN", "AOTH"]:
        return "Asian"
    if row[-4:] in ["BCRB", "BAFR", "BOTH"]:
        return "Black"
    if row[-4:] == "CHNE":
        return "Chinese"
    if row[-4:] == "OOTH":
        return "Other"
    if row[-4:] == "REFU":
        return "Refused"
    if row[-4:] == "NOBT":
        return "Not Obtained"


def over_12_months(df):
    if pd.to_datetime(
        df["Date Started to be Looked After"], dayfirst=True, errors="coerce"
    ) <= pd.to_datetime(
        df["Reference Date"], dayfirst=True, errors="coerce"
    ) - pd.DateOffset(
        months=12
    ):
        return "Yes"
    else:
        return "No"


# Calculation functions
def la_groupby(df, col, frame_col_name, val_col_name):
    """
    Used to groupby columns to count number of instances
    Col unspecific where we need every row counted per la/period (for instance total contacts)
    """
    if col:
        grouped = df.groupby(["name_period", col]).size()
    else:
        grouped = df.groupby(["name_period"]).size()

    grouped = grouped.to_frame(frame_col_name).reset_index()
    grouped = grouped.rename(columns={col: val_col_name})

    return grouped


def region_groupby(df, col, frame_col_name, val_col_name):
    """
    Used to groupby columns to count number of instances
    Col unspecific where we need every row counted per la/period (for instance total contacts)
    """
    if col:
        region = df.groupby(["Time Period", col]).size()
    else:
        region = df.groupby(["Time Period"]).size()

    region = region.to_frame(frame_col_name).reset_index()
    region = region.rename(columns={col: val_col_name})

    region["name_period"] = "Region/" + region["Time Period"]
    region.drop("Time Period", axis=1, inplace=True)

    return region


def group_dfs(df, col, frame_col_name, val_col_name):
    grouped_number = la_groupby(df, col, frame_col_name, val_col_name)
    region_number = region_groupby(df, col, frame_col_name, val_col_name)

    grouped = pd.concat([grouped_number, region_number])
    grouped[frame_col_name].fillna(0, inplace=True)

    return grouped


def rate_calc(df, frame_col_name, population):
    la = df["name_period"].split("/")[0]
    key = f"{la} - {population}"

    pop = pop_dict[f"{la} - {population}"]
    value = df[frame_col_name]

    rate = (value / pop) * 10000

    return rate


def add_rates_col(df, frame_col_name, population):
    df["Rate"] = df.apply(rate_calc, args=(frame_col_name, population), axis=1)

    df.set_index("name_period", inplace=True)

    df_count = df[frame_col_name].to_dict()
    df_rate = df["Rate"].to_dict()

    return df_count, df_rate


def percent_calculations(df, val_col_name, col):
    df_other = (
        df[~df[val_col_name].str.contains("Yes") | ~df[val_col_name].str.contains("No")]
        .drop(val_col_name, axis=1)
        .copy()
    )
    df_other = df_other.groupby(["name_period"]).sum().reset_index()
    df_other.rename(columns={"count": "count_other"}, inplace=True)

    df_yes = df[df[val_col_name].str.contains("Yes")].drop(val_col_name, axis=1).copy()
    df_no = df[df[val_col_name].str.contains("No")].drop(val_col_name, axis=1).copy()
    df_grouped = df_yes.merge(
        df_no, how="outer", on="name_period", suffixes=["_yes", "_no"]
    )
    df_grouped = df_grouped.merge(df_other, how="outer", on="name_period")

    df_grouped["Measure count_yes"] = df_grouped["Measure count_yes"].fillna(0)

    df_grouped[f"Percent {val_col_name}"] = (
        df_grouped[f"Measure count_yes"] / (df_grouped["Measure count"]) * 100
    )

    df_grouped[f"Percent Measure name"].fillna(0, inplace=True)
    df_grouped.set_index("name_period", inplace=True)
    df_grouped = df_grouped[f"Percent Measure name"].to_dict()

    return df_grouped

    df[val_col_name + "- Percent"] = (df[val_col_name] / df["Total CYP"]) * 100

    df.drop("Total CYP", axis=1, inplace=True)
    df.rename(columns={val_col_name: val_col_name + " - Count"}, inplace=True)

    return multiples


def cyp_count(
    df,
    frame_col_name="Measure count",
    val_col_name="Measure name",
    population="0-17 Total",
    col=None,
):
    """
    frame_col_name and val_col_name need only be given when outputs are tabular
    """

    grouped = group_dfs(df, col, frame_col_name, val_col_name)
    grouped_count, grouped_rate = add_rates_col(grouped, frame_col_name, population)

    return grouped_count, grouped_rate


def percent_of_col_with_value(
    df, frame_col_name="Measure count", val_col_name="Measure name", col=None
):  # population='0-17 Total'):
    """
    Percentage for yes out of all possible values. If needed for
    just yes/no excluding other, filter before use.
    """

    df = df.copy()
    df[col] = df[col].fillna("NA")

    grouped = group_dfs(df, col, frame_col_name, val_col_name)

    percent_grouped = percent_calculations(grouped, val_col_name, col)

    return percent_grouped


def appears_on_both(df1, df2):
    """
    Finds unique values in two dataframes and inner merges to find children who are in
    both. Then merges back to the dataframe of interest adding a column highlighting
    whether children appear on both. Returns a dict of percentages.
    """
    df1_unique = df1.drop_duplicates(subset=["Child Unique ID", "name_period"]).copy()
    df2_unique = df2.drop_duplicates(subset=["Child Unique ID", "name_period"]).copy()

    merged_df = df1_unique.merge(
        df2_unique, how="inner", on=["Child Unique ID", "name_period"]
    )

    merged_df["on_both"] = "Yes"

    df = (
        df1_unique[["Child Unique ID", "name_period", "Time Period"]]
        .merge(
            merged_df[["Child Unique ID", "name_period", "on_both"]],
            how="left",
            on=["Child Unique ID", "name_period"],
        )
        .copy()
    )

    df["on_both"].fillna("No", inplace=True)

    output = percent_of_col_with_value(df, col="on_both")

    return output


def cohort_percent(df, new_col):
    df["Total CYP"] = df.groupby(["name_period"])[new_col].transform("sum")

    df[new_col + " - Percent"] = (df[new_col] / df["Total CYP"]) * 100

    df.drop("Total CYP", axis=1, inplace=True)
    df.rename(columns={new_col: new_col + " - Count"}, inplace=True)

    return df


def multiple_same_event(df, new_col_name, multiples_col=False):
    """
    Used to find count and percentage of the number of times a CYP has multiples of
    the same event. If there is no column specifying times for each child, it uses the
    number of appearances of each child per name_period by not specifying a column.

    Returns a df which should be outer merged to others.
    """
    if multiples_col == False:
        multiples = (
            df.groupby(["name_period", "Child Unique ID"])
            .size()
            .to_frame("Number of events")
            .reset_index()
        )
        multiples["Time Period"] = multiples["name_period"].str.split("/").str[1]
        multiples = group_dfs(
            multiples,
            frame_col_name=new_col_name,
            val_col_name="Measure Category",
            col="Number of events",
        )
    else:
        multiples = group_dfs(
            df,
            frame_col_name=new_col_name,
            val_col_name="Measure Category",
            col=multiples_col,
        )

    multiples = cohort_percent(multiples, new_col_name)

    return multiples


def category_metrics(df, source_col, category):
    """
    Used to find percentages of categoricals from totals. Unlike other outputs, this
    is created to be concatenated, otherwise it would need to be seprate tables for Power BI.
    """
    grouped = group_dfs(
        df, source_col, frame_col_name="Measure count", val_col_name="Value"
    )
    grouped["Category"] = category

    grouped["Total CYP"] = grouped.groupby(["name_period"])["Measure count"].transform(
        "sum"
    )
    grouped["Percent"] = (grouped["Measure count"] / grouped["Total CYP"]) * 100

    grouped.drop("Total CYP", axis=1, inplace=True)
    grouped.rename(columns={"Measure count": "Count"}, inplace=True)
    grouped = grouped[["name_period", "Category", "Value", "Count", "Percent"]]

    return grouped


def age_gender_metric(df, new_col):
    """
    Counts of age by gender, a column per gender.
    Percents are given as a percentage of given gender's cohort, not total cohort.
    """
    df_male = df[df["Gender"] == "a) Male"]
    df_female = df[df["Gender"] == "b) Female"]

    age_gender_male = df_male.groupby(["name_period", "Age of Child (Years)"]).size()
    age_gender_male = age_gender_male.to_frame(f"{new_col} male").reset_index()

    age_gender_female = df_female.groupby(
        ["name_period", "Age of Child (Years)"]
    ).size()
    age_gender_female = age_gender_female.to_frame(f"{new_col} female").reset_index()

    age_gender_all = df.groupby(["name_period", "Age of Child (Years)"]).size()
    age_gender_all = age_gender_all.to_frame(f"{new_col} all").reset_index()

    age_gender = age_gender_male.merge(
        age_gender_female, how="outer", on=["name_period", "Age of Child (Years)"]
    )
    age_gender = age_gender.merge(
        age_gender_all, how="outer", on=["name_period", "Age of Child (Years)"]
    )
    age_gender["Time Period"] = age_gender["name_period"].str.split("/").str[1]

    region_male = df_male.groupby(["Time Period", "Age of Child (Years)"]).size()
    region_male = region_male.to_frame(f"{new_col} male").reset_index()

    region_female = df_female.groupby(["Time Period", "Age of Child (Years)"]).size()
    region_female = region_female.to_frame(f"{new_col} female").reset_index()

    region_all = df.groupby(["Time Period", "Age of Child (Years)"]).size()
    region_all = region_all.to_frame(f"{new_col} all").reset_index()

    region = region_male.merge(
        region_female[["Time Period", "Age of Child (Years)", f"{new_col} female"]],
        how="outer",
        on=["Time Period", "Age of Child (Years)"],
    )
    region = region.merge(
        region_all[["Time Period", "Age of Child (Years)", f"{new_col} all"]],
        how="outer",
        on=["Time Period", "Age of Child (Years)"],
    )

    region.rename(columns={"Time Period": "name_period"}, inplace=True)
    region["name_period"] = "Region/" + region["name_period"]

    output = pd.concat([age_gender, region])
    output.drop("Time Period", axis=1, inplace=True)

    output = cohort_percent(output, f"{new_col} male")
    output = cohort_percent(output, f"{new_col} female")
    output = cohort_percent(output, f"{new_col} all")

    return output


def ethnic_background_metric(df, new_col):

    ethnicities = group_dfs(
        df, "Ethnicity Group", frame_col_name=new_col, val_col_name="Ethnicity"
    )
    ethnicities = cohort_percent(ethnicities, new_col)

    return ethnicities


def time_diff_calc(df, start_col, end_col, working_days=False):
    df = df.copy()
    df["start_col_dt"] = pd.to_datetime(df[start_col], dayfirst=True, errors="coerce")
    df["end_col_dt"] = pd.to_datetime(df[end_col], dayfirst=True, errors="coerce")

    df["end_col_dt"] = df.apply(
        lambda x: (
            x["end_col_dt"] if pd.notnull(x["end_col_dt"]) else x["Reference Date"]
        ),
        axis=1,
    )

    if working_days == True:
        df["time_diff"] = np.busday_count(
            df["start_col_dt"].values.astype("datetime64[D]"),
            df["end_col_dt"].values.astype("datetime64[D]"),
        )
    else:
        df["time_diff"] = (
            pd.to_datetime(df["end_col_dt"]) - pd.to_datetime(df["start_col_dt"])
        ).dt.days
        # df["time_diff"] = df["time_diff"] / pd.Timedelta(days=1)
        # df["time_diff"] = (df["end_col_dt"] - df["start_col_dt"]) / pd.Timedelta(days=1)
        # df["time_diff"] = df["time_diff"].round(decimals=0)

    return df


def icpc_bins(x):
    if x < 1:
        return "a) Same day"
    elif x <= 5:
        return "b) 1-5 days"
    elif x <= 10:
        return "c) 6-10 days"
    elif x <= 13:
        return "d) 11-13 days"
    elif x <= 15:
        return "e) 14-15 days"
    elif x <= 17:
        return "f) 16-17 days"
    elif x <= 20:
        return "g) 18-20 days"
    elif x > 20:
        return "h) 20+ days"


def day_bins(x):
    if x < 1:
        return "a) Same day"
    elif x <= 10:
        return "b) 1 - 10 days"
    elif x <= 20:
        return "c) 11-20 days"
    elif x <= 30:
        return "d) 21-30 days"
    elif x <= 40:
        return "e) 31-40 days"
    elif x <= 45:
        return "f) 41-45 days"
    elif x <= 50:
        return "g) 46-50 days"
    elif x <= 60:
        return "h) 51-60 days"
    elif x >= 61:
        return "i) 61 days+"
    else:
        return "x) Date Error"


def month_year_bins(x):
    x = int(x)
    delta = np.timedelta64(x, "D")

    if delta < np.timedelta64(91, "D"):
        return "a) 0-3 months"
    elif delta < np.timedelta64(182, "D"):
        return "b) 3-6 months"
    elif delta < np.timedelta64(365, "D"):
        return "c) 6 months - 1 year"
    elif delta < np.timedelta64(730, "D"):
        return "d) 1-2 years"
    else:
        return "e) 2+ years"


def review_bins(delta):
    if delta <= 91:
        return "a) 0-3 months"
    elif delta <= 182:
        return "b) 3-6 months"
    elif delta <= 273:
        return "c) 6-9 months"
    elif delta <= 365:
        return "d) 12+ Months"
    elif delta >= 365:
        return "d) 12+ Months"


def last_seen_bins(x):

    if x <= 42:
        return "a) 0-6 weeks"
    elif x <= 84:
        return "b) 6-12 weeks"
    elif x <= 126:
        return "c) 12-18 weeks"
    elif x > 126:
        return "d) 18+ weeks"


def timelines_metric(df, start_col, end_col, count_name, working_days=False):
    df = time_diff_calc(df, start_col, end_col, working_days).copy()

    diff_grouped = group_dfs(df, "time_diff", count_name, "Days Taken")
    diff_grouped = cohort_percent(diff_grouped, count_name)

    return diff_grouped, df


# def timelines_with_bins(df, start_col, end_col, count_name, bin_function):
# #     df['timeline_bin'] = df['time_diff'].apply(day_bins)
#     df['timeline_bin'] = df['time_diff'].apply(bin_function)

#     bins_grouped = category_metrics(df, 'timeline_bin', count_name)
#     #bins_grouped = group_dfs(df, 'timeline_bin', count_name, 'Time Taken')

#     return bins_grouped


def timelines_with_bins(df, count_name, bin_function):
    #     df['timeline_bin'] = df['time_diff'].apply(day_bins)
    df["timeline_bin"] = df["time_diff"].apply(bin_function)

    bins_grouped = category_metrics(df, "timeline_bin", count_name)
    # bins_grouped = group_dfs(df, 'timeline_bin', count_name, 'Time Taken')

    return bins_grouped


def event_in_time(df, col, days):
    """
    Takes dataframes with a 'Days Taken' column (from timelines_metric) to determine if
    an event has occurred in a specfic timeframe. Returns percentage that are in time.
    """
    df["in_time"] = df[col].apply(lambda x: "Yes" if x <= days else "No")

    percent_in_time = percent_of_col_with_value(df, col="in_time")

    return percent_in_time


def event_in_period(df, event_col, days, months):
    df = df.copy()
    df[event_col] = pd.to_datetime(df[event_col], dayfirst=True, errors="coerce")
    df = df[
        df[event_col] >= df["Reference Date"] - pd.DateOffset(days=days, months=months)
    ]

    event_count, event_rate = cyp_count(df)

    return event_count, event_rate


def event_timeliness(df, event_col, days, months):
    df = df.copy()
    df[event_col] = pd.to_datetime(df[event_col], dayfirst=True, errors="coerce")
    df["Reference Date"] = pd.to_datetime(
        df["Reference Date"], dayfirst=True, errors="coerce"
    )

    df["Timeliness"] = df.apply(
        lambda x: (
            "Yes"
            if (
                x[event_col]
                > x["Reference Date"] - pd.DateOffset(days=days, months=months)
            )
            else "No"
        ),
        axis=1,
    )

    timeliness_dict = percent_of_col_with_value(df, col="Timeliness")

    return timeliness_dict


def short_term_stability(df, col):
    """
    A CYP is short term stable if they have had less than threee placements in the last 12 months.
    """

    def stability_short(row):
        if row >= 3:
            return "No"
        if row < 3:
            return "Yes"

    df["Stable"] = df[col].apply(stability_short)

    output = percent_of_col_with_value(df, col="Stable")

    return output


def long_term_stability(df):
    """
    A placement is long term stable if they've been looked after for more than 2.5 years
    and their most recent placement is at least 2 years long.
    """
    df["Date Started to be Looked After"] = pd.to_datetime(
        df["Date Started to be Looked After"], dayfirst=True, errors="coerce"
    )
    df["Reference Date"] = pd.to_datetime(
        df["Reference Date"], dayfirst=True, errors="coerce"
    )
    df["Start Date of Most Recent Placement"] = pd.to_datetime(
        df["Start Date of Most Recent Placement"], dayfirst=True, errors="coerce"
    )

    def stability_long(df):
        if (
            df["Start Date of Most Recent Placement"]
            < df["Start Date of Most Recent Placement"]
            - pd.DateOffset(years=2, months=6)
        ) | pd.isnull(df["Date Started to be Looked After"]):
            return "N/A"
        else:
            if df["Start Date of Most Recent Placement"] <= df[
                "Reference Date"
            ] - pd.DateOffset(years=2):
                return "Yes"
            if df["Start Date of Most Recent Placement"] > df[
                "Reference Date"
            ] - pd.DateOffset(years=2):
                return "No"
            else:
                return "Something is wrong here"

    df["Stable"] = df.apply(stability_long, axis=1)

    output = percent_of_col_with_value(df, col="Stable")

    return output


def groupby_age(df, col, frame_col_name, val_col_name):
    # Pass a df with only values you need counted by age

    df = df.groupby(["name_period", col]).size()
    df = df.to_frame(frame_col_name).reset_index()

    df["Total CYP"] = df.groupby(["name_period"])[frame_col_name].transform("sum")

    df[frame_col_name + " - Percent"] = (df[frame_col_name] / df["Total CYP"]) * 100

    df.drop("Total CYP", axis=1, inplace=True)
    df.rename(columns={frame_col_name: frame_col_name + " - Count"}, inplace=True)

    return df


def eet(col):
    if (
        (col == "d1) Not in education, training or employment - illness/disability")
        | (col == "d2) Not in education, training or employment - other reasons")
        | (col == "d3) Not in education, training or employment - pregnancy/parenting")
        | (col == "NEET")
        | (pd.isnull(col))
    ):
        return "No"
    else:
        return "Yes"


def sum_events(df, col):

    sum_la_year = df[["name_period", col]].groupby(["name_period"]).sum().reset_index()
    region_averages = (
        df[["Time Period", col]].groupby(["Time Period"]).sum().reset_index()
    )
    region_averages[col] = region_averages[col] / num_las

    region_averages["name_period"] = "Region average/" + region_averages["Time Period"]
    region_averages.drop("Time Period", axis=1, inplace=True)
    sum_la_year = pd.concat([sum_la_year, region_averages])

    sum_la_year.set_index("name_period", inplace=True)
    sum_la_year = sum_la_year.to_dict()

    return sum_la_year


def to_excel(dfs):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    for name, frame in dfs.items():
        frame.to_excel(writer, sheet_name=name, index=False)
    workbook = writer.book
    writer.save()
    processed_data = output.getvalue()
    return processed_data


# App Begins
st.title("Eastern Region Dashboard Pre-processing tool")

uploaded_files = st.file_uploader(
    "Upload Annex A  CSV files here", accept_multiple_files=True
)
mye2_persons = open_url(mye2_persons_url)
mye2_females = open_url(mye2_females_url)
mye2_males = open_url(mye2_males_url)
# mid_year_estimates = st.file_uploader(
#     "Upload mid year population esitmates Excel file here", accept_multiple_files=False
# )
st.write(
    "ONS mid year population esitmates can be found here: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates"
)
st.write("As of the time of writing, the most recent population estimate was in 2023.")
st.write("They are not embedded in the site as they change very regularly.")

# if (uploaded_files != None) & (mid_year_estimates != None):
if uploaded_files:

    st.write("Files uploaded sucessfully.")

    # Read Annex A and ONS data in as dfs
    test_file = uploaded_files[0]
    if test_file.name[-4:] == ".csv":
        upload_dfs = {
            uploaded_file.name[:-4]: pd.read_csv(uploaded_file)
            for uploaded_file in uploaded_files
        }
    elif uploaded_files[0].name[-5:] == ".xlsx":
        upload_dfs = pd.read_excel(uploaded_files[0])
    else:
        st.write("Unexpected file type. Upload type expected .csv or .xsls")

    # Check which files are uploaded & standardize dict
    dfs = {}
    for k, v in upload_dfs.items():
        if ("list_1" in k.lower()) | ("list 1" in k.lower()) & ("10" not in k) & (
            "11" not in k
        ) & ("12" not in k):
            dfs["list_1"] = v
        if ("list_2" in k.lower()) | ("list 2" in k.lower()):
            dfs["list_2"] = v
        if ("list_3" in k.lower()) | ("list 3" in k.lower()):
            dfs["list_3"] = v
        if ("list_4" in k.lower()) | ("list 4" in k.lower()):
            dfs["list_4"] = v
        if ("list_5" in k.lower()) | ("list 5" in k.lower()):
            dfs["list_5"] = v
        if ("list_6" in k.lower()) | ("list 6" in k.lower()):
            dfs["list_6"] = v
        if ("list_7" in k.lower()) | ("list 7" in k.lower()):
            dfs["list_7"] = v
        if ("list_8" in k.lower()) | ("list 8" in k.lower()):
            dfs["list_8"] = v
        if ("list_9" in k.lower()) | ("list 9" in k.lower()):
            dfs["list_9"] = v

    lists_uploaded = list(dfs.keys())
    st.write(f"Lists uploaded {lists_uploaded}")

    for k, df in dfs.items():
        dfs[k]["Time Period"] = df["Month"].astype(str) + "_" + df["Year"].astype(str)
        dfs[k] = (
            df[
                (~df["Child Unique ID"].astype("str").str.contains("None"))
                & (~df["Child Unique ID"].astype("str").str.contains("filters"))
            ]
        ).copy()

    ons = {
        "MYE2 - Persons": pd.read_csv(mye2_persons, skiprows=7),
        "MYE2 - Females": pd.read_csv(mye2_females, skiprows=7),
        "MYE2 - Males": pd.read_csv(mye2_males, skiprows=7),
    }

    # Pre-process ONS data
    ons["Metadata"] = ons["MYE2 - Persons"].iloc[:, 0:4].copy()
    ons["Persons"] = ons["MYE2 - Persons"].iloc[:, 4:30].astype("int").copy()
    ons["Females"] = ons["MYE2 - Females"].iloc[:, 4:30].copy()
    ons["Males"] = ons["MYE2 - Males"].iloc[:, 4:30].copy()

    for df in [ons["Persons"], ons["Females"], ons["Males"]]:
        df = age_bins(df)

    ons["Persons"] = ons["Persons"].add_suffix(" - Total")
    ons["Females"] = ons["Females"].add_suffix(" - Female")
    ons["Males"] = ons["Males"].add_suffix(" - Male")

    ons["All"] = (
        ons["Metadata"]
        .merge(ons["Persons"], how="left", left_index=True, right_index=True)
        .merge(ons["Females"], how="left", left_index=True, right_index=True)
        .merge(ons["Males"], left_index=True, right_index=True)
    )

    ons["Region"] = ons["All"][
        (ons["All"]["Name"].isin(dfs["list_1"]["LA"].unique()))
    ].copy()

    ons_pops = ons["Region"]

    ons_pops.loc["Total"] = ons_pops.sum(numeric_only=True)
    ons_pops["Name"].fillna("Region", inplace=True)

    # Used to create a dict for easy access to most common pop numbers for rate calculations
    pop_dict = {}
    for la in ons_pops["Name"].unique():
        pop_total = ons_pops[ons_pops["Name"] == la]["0-17 years - Total"].sum()
        pop_male = ons_pops[ons_pops["Name"] == la]["0-17 years - Male"].sum()
        pop_female = ons_pops[ons_pops["Name"] == la]["0-17 years - Female"].sum()

        pop_dict[f"{la} - 0-17 Total"] = pop_total
        pop_dict[f"{la} - 0-17 Male"] = pop_male
        pop_dict[f"{la} - 0-17 Female"] = pop_female

    # Pre-process Annex A Data
    # Set reference dates in test data
    # TODO should not be needed with real pipeline outputs
    # Cleans any empty rows being read into the df
    for k, v in dfs.items():
        dfs[k] = v[v["Child Unique ID"].notna()].copy()

    for df in dfs.values():
        # df["Reference Date"] = df.apply(quarter_reference_date, axis=1)
        df["Reference Date"] = df.apply(reference_date, axis=1)
        df["Ethnicity Group"] = df["Ethnicity"]
        df["name_period"] = df["LA"] + "/" + df["Time Period"]

    la_names = list(df["name_period"].unique())
    num_las = len(df["LA"].unique())
    periods = list(df["Time Period"].unique())
    measures = {}

    # Contacts
    # Unique Contacts
    if "list_1" in lists_uploaded:
        (
            measures["Contacts - Contacts - Count"],
            measures["Contacts - Contacts - Rate"],
        ) = cyp_count(dfs["list_1"])
        if "list_3" in lists_uploaded:
            # Percentage of contacts also appearing on referrals
            measures["Contacts - Appears on Referrals - Percent"] = appears_on_both(
                dfs["list_1"], dfs["list_3"]
            )
        # Contacts by age and gender - percents given as percentage of given gender
        contact_age_gender = age_gender_metric(
            dfs["list_1"], "Contacts - Age breakdown"
        )
        # Sources of contacts
        contact_sources = category_metrics(
            dfs["list_1"], "Contact Source", "Contacts - Contact Source"
        )
        # Multiple contacts in period
        multiple_contacts = multiple_same_event(
            dfs["list_1"], "Contacts - Number of contacts"
        )
        # Contacts - ethnicity breakdown
        contact_ethnicity = ethnic_background_metric(
            dfs["list_1"], "Contacts - Ethnicities"
        )

        st.write("Completed calculations for Contacts")

    # Early help assessments
    # Unique Eh
    if "list_2" in lists_uploaded:
        (
            measures["Early Help Assessments - Early Help Assessments - Count"],
            measures["Early Help Assessments - Early Help Assessments - Rate"],
        ) = cyp_count(dfs["list_2"])
        # Percentage of Early Help also appearing on the Referrals list
        if "list_3" in lists_uploaded:
            measures[
                "Early Help Assessments - Early Help Assessments appearing on Referrals - Percent"
            ] = appears_on_both(dfs["list_2"], dfs["list_3"])
        # EH by age and gender
        eh_age_gender = age_gender_metric(
            dfs["list_2"], "Early Help Assessments - Age breakdown"
        )
        # Multiple assessments in period
        multiple_assessments = multiple_same_event(
            dfs["list_2"], "Early Help Assessments - Number of Assessments"
        )
        # Ethnic backgrounds
        eh_ethnicity = ethnic_background_metric(
            dfs["list_2"], "Early Help Assessments - Ethnicities"
        )
        st.write("Completed calculations for Early Help Assessments")

    # Referrals
    # Unique referrals
    if "list_3" in lists_uploaded:
        (
            measures["Referrals - Referrals - Count"],
            measures["Referrals - Referrals - Rate"],
        ) = cyp_count(dfs["list_3"])
        # Referral Sources
        referral_sources = category_metrics(
            dfs["list_3"], "Referral Source", "Referrals - Referral Source"
        )
        # Referrals by age and gender count
        referral_age_gender = age_gender_metric(
            dfs["list_3"], "Referrals - Age breakdown"
        )
        # Ethnic backgrounds
        referral_ethnicity = ethnic_background_metric(
            dfs["list_3"], "Referrals - Ethnicities"
        )
        # re-referrals by count and as percentage
        multiple_referral = multiple_same_event(
            dfs["list_3"], "Referrals - Number of Referrals in Last 12 Months"
        )
        # Referrals with NFA
        measures["Referrals - Referral NFA - Percent"] = percent_of_col_with_value(
            dfs["list_3"], col="Referral NFA?"
        )
        st.write("Completed calculations for Referrals")

    # Assessments
    # Unique assessments
    if "list_4" in lists_uploaded:
        (
            measures["Assessments - Assessments - Count"],
            measures["Assessments - Assessments - Rate"],
        ) = cyp_count(dfs["list_4"])
        # Open and closed assessments
        open_assessments = dfs["list_4"][
            dfs["list_4"]["Continuous Assessment Date of Authorisation"].isna()
        ]
        closed_assessments = dfs["list_4"][
            dfs["list_4"]["Continuous Assessment Date of Authorisation"].notna()
        ]
        (
            measures["Assessments - Open - Count"],
            measures["Assessments - Open - Rate"],
        ) = cyp_count(open_assessments)
        (
            measures["Assessments - Closed - Count"],
            measures["Assessments - Closed - Rate"],
        ) = cyp_count(closed_assessments)
        # Assessments by age and gender
        assessments_age_gender = age_gender_metric(
            dfs["list_4"], "Assessments - Age breakdown"
        )
        # Assessments for child with disability
        measures["Assessments - Disability - Percent"] = percent_of_col_with_value(
            dfs["list_4"], col="Does the Child have a Disability"
        )
        # Assessment ethnic breakdown
        assessments_ethnicity = ethnic_background_metric(
            dfs["list_4"], "Assessments - Ethnicities"
        )
        # Child assessed as needing CSC support?
        measures["Assessments - Needs CSC support? - Percent"] = (
            percent_of_col_with_value(
                dfs["list_4"],
                col="Was the child assessed as requiring LA children's social care support?",
            )
        )
        # Duration for all completed and open assessments
        assessment_durations, assessments_with_days = timelines_metric(
            dfs["list_4"],
            "Continuous Assessment Start Date",
            "Continuous Assessment Date of Authorisation",
            "Assessments - Assessments Durations",
            working_days=True,
        )
        # Assessments completed in 45 working days
        measures["Assessments - Assessments in 45 working days - Percent"] = (
            event_in_time(assessments_with_days, "time_diff", 45)
        )
        # assessment durations by bin
        assessment_durations_bins = timelines_with_bins(
            assessments_with_days, "Assessments - Assessments Durations", day_bins
        )
        st.write("Completed calculations for Assessments")

    # Section 47s
    if "list_5" in lists_uploaded:
        # S47 count and rp10k
        (
            measures["Section 47 - Section 47 - Count"],
            measures["Section 47 - Section 47 - Rate"],
        ) = cyp_count(dfs["list_5"])
        # S47 age and gender
        s47_age_gender = age_gender_metric(dfs["list_5"], "Section 47 - Age Breakdown")
        # S47s with disabilites - percent
        measures["Section 47 - Disability - Percent"] = percent_of_col_with_value(
            dfs["list_5"], col="Does the Child have a Disability"
        )
        # multiple s47s
        multiple_s47 = multiple_same_event(
            dfs["list_5"],
            "Section 47 - Number of Section 47 (within 12 months)",
            "Number of Section 47 Enquiries in the last 12 months",
        )
        # S47 ethnicity
        s47_ethnicity = ethnic_background_metric(
            dfs["list_5"], "Section 47 - Ethnicities"
        )
        st.write("Completed calculations for Section 47s")

    # ICPCs
    if "list_5" in lists_uploaded:
        icpc = dfs["list_5"][
            dfs["list_5"]["Date of Initial Child Protection Conference"].notna()
        ]
        measures["ICPC - ICPC - Count"], measures["ICPC - ICPC - Rate"] = cyp_count(
            icpc
        )
        # S47 not requiring an ICPC
        measures["Section 47 - Section 47 Not requiring ICPC - Percent"] = (
            percent_of_col_with_value(
                dfs["list_5"],
                col="Was an Initial Child Protection Conference deemed unnecessary?",
            )
        )
        # multiple icpc
        multiple_icpc = multiple_same_event(
            icpc,
            "ICPC - Number of ICPCs (within 12 months)",
            "Number of ICPCs in the last 12 months",
        )
        # ICPC leading to CPP
        measures["ICPC - Resulting in CPP - Percent"] = percent_of_col_with_value(
            icpc,
            col="Did the Initial Child Protection Conference Result in a Child Protection Plan",
        )
        icpc_durations, icpcs_with_days = timelines_metric(
            dfs["list_5"][
                dfs["list_5"]["Date of Initial Child Protection Conference"].notna()
            ],
            "Strategy discussion initiating Section 47 Enquiry Start Date",
            "Date of Initial Child Protection Conference",
            "ICPC - ICPC Durations",
            working_days=True,
        )
        # ICPS completed in 15 working days
        measures["ICPC - Completed in 15 working days - Percent"] = event_in_time(
            icpcs_with_days, "time_diff", 15
        )
        # ICPCs durations by bin
        icpc_durations_bins = timelines_with_bins(
            icpcs_with_days, "ICPC - ICPC Durations", icpc_bins
        )
        st.write("Completed calculations for ICPCs")

    # # CINs
    # # CIN plans
    if "list_6" in lists_uploaded:
        (
            measures["CIN plans - CIN plans - Count"],
            measures["CIN plans - CIN plans - Percent"],
        ) = cyp_count(dfs["list_6"])
        # CIN started in 6 months
        (
            measures["CIN plans - Started within 6 months - Count"],
            measures["CIN plans - Started 6 months - Rate"],
        ) = event_in_period(dfs["list_6"], "CIN Start Date", 0, 6)
        # CIN ceased in 6 months
        (
            measures["CIN plans - Ceased within 6 months - Count"],
            measures["CIN plans - Ceased 6 months - Percent"],
        ) = event_in_period(
            dfs["list_6"][dfs["list_6"]["CIN Closure Date"].notna()],
            "CIN Closure Date",
            0,
            6,
        )
        # CIN ceased durations
        cin_closed_durations, cin_closed_with_days = timelines_metric(
            dfs["list_6"][dfs["list_6"]["CIN Closure Date"].notna()],
            "CIN Start Date",
            "CIN Closure Date",
            "CIN plans - CIN plans (closed plans)",
        )
        cin_closed_bins = timelines_with_bins(
            cin_closed_with_days, "CIN plans - CIN (closed plans)", month_year_bins
        )
        # CIN ceased reasons
        cin_ceased_reasons = category_metrics(
            dfs["list_6"][dfs["list_6"]["Reason for Closure"].notna()],
            "Reason for Closure",
            "CIN plans - Reason for closure",
        )
        st.write("Completed calculations for CIN Plans.")

    # # Open CIN
    if "list_6" in lists_uploaded:
        open_cin = dfs["list_6"][dfs["list_6"]["CIN Closure Date"].isna()]
        (
            measures["CIN plans - CIN plans (open plans) - Count"],
            measures["CIN plans - CIN plans (open plans) - Rate"],
        ) = cyp_count(open_cin)
        # age gender split
        open_cin_age_gender = age_gender_metric(
            open_cin, "CIN plans - Age breakdown (open plans)"
        )
        # CYP with a disability
        measures["CIN plans - Disability (open plans) - Percent"] = (
            percent_of_col_with_value(open_cin, col="Does the Child have a Disability")
        )
        # Ethnicity breakdown
        open_cin_ethnicity = ethnic_background_metric(
            open_cin, "CIN plans - Ethnicities (open plans)"
        )
        # Length of open CINs
        open_cin_durations, open_cin_with_days = timelines_metric(
            open_cin,
            "CIN Start Date",
            "CIN Closure Date",
            "CIN plans - CIN plans (open plans)",
            working_days=False,
        )
        open_cin_bins = timelines_with_bins(
            open_cin_with_days, "CIN plans - CIN plans (open plans)", month_year_bins
        )
        # Time since child was last seen by SW
        open_cin_sw_date_durations, open_cin_sw_date_with_days = timelines_metric(
            open_cin[open_cin["Date Child Was Last Seen"].notna()],
            "Date Child Was Last Seen",
            "CIN Closure Date",
            "CIN plans - Time since SW (open plans)",
            working_days=False,
        )
        # Comparing primary need of open CIN
        open_cin_need = category_metrics(
            open_cin, "Primary Need Code", "CIN - Primary need code (open plans)"
        )
        st.write("Completed calculations for Open CINs.")

    # # CPPs
    if "list_7" in lists_uploaded:
        cpp_started_6mths = dfs["list_7"][
            (
                pd.to_datetime(
                    dfs["list_7"]["Child Protection Plan Start Date"],
                    dayfirst=True,
                    errors="coerce",
                )
                >= pd.to_datetime(
                    dfs["list_7"]["Reference Date"], dayfirst=True, errors="coerce"
                )
                - pd.DateOffset(months=6)
            )
        ].copy()
        cpp_ended_6mths = dfs["list_7"][
            (
                pd.to_datetime(
                    dfs["list_7"]["Child Protection Plan End Date"],
                    dayfirst=True,
                    errors="coerce",
                )
                >= pd.to_datetime(
                    dfs["list_7"]["Reference Date"], dayfirst=True, errors="coerce"
                )
                - pd.DateOffset(months=6)
            )
        ].copy()
        # # CPP stearted and ceased
        (
            measures["CPP - CPP Started within 6 months - Count"],
            measures["CPP - CPP started within 6 months - Rate"],
        ) = event_in_period(dfs["list_7"], "Child Protection Plan Start Date", 0, 6)
        (
            measures["CPP - CPP Ended within 6 months - Count"],
            measures["CPP - CPP ended within 6 months - Rate"],
        ) = event_in_period(dfs["list_7"], "Child Protection Plan End Date", 0, 6)
        # # CPP re-registrations
        multiple_cpp = multiple_same_event(
            dfs["list_7"],
            "CPP - Multiple CPP",
            "Number of Previous Child Protection Plans",
        )
        multiple_cpp_started_6mths = multiple_same_event(
            cpp_started_6mths,
            "CPP - Multiple CPP (started 6 months)",
            "Number of Previous Child Protection Plans",
        )
        # Initial category of abuse
        cpp_initial_category_of_abuse = category_metrics(
            cpp_started_6mths,
            "Initial Category of Abuse",
            "CPP - Initial category of abuse",
        )
        cpp_ended_durations, cpp_ended_with_days = timelines_metric(
            cpp_ended_6mths,
            "Child Protection Plan Start Date",
            "Child Protection Plan End Date",
            "CPP - CPP length (closed plans)",
            working_days=False,
        )
        cpp_ended_bins = timelines_with_bins(
            cpp_ended_with_days, "CPP - CPP length (closed plans)", month_year_bins
        )
        # End date is later that start date plus two years
        cpp_2_years_6_mths = cpp_ended_6mths[
            (
                pd.to_datetime(
                    cpp_ended_6mths["Child Protection Plan End Date"],
                    dayfirst=True,
                    errors="coerce",
                )
                >= pd.to_datetime(
                    cpp_ended_6mths["Child Protection Plan Start Date"],
                    dayfirst=True,
                    errors="coerce",
                )
                + pd.DateOffset(years=2)
            )
        ].copy()
        cpp_2_years_6_mths["Longer than 2 years"] = "Yes"
        cpp_ended_6mths = cpp_ended_6mths.merge(
            cpp_2_years_6_mths["Longer than 2 years"],
            how="left",
            left_index=True,
            right_index=True,
        )
        cpp_ended_6mths["Longer than 2 years"].fillna("No")
        measures["CPP - CPP longer than 2 years closed within 6 months - Percent"] = (
            percent_of_col_with_value(cpp_ended_6mths, col="Longer than 2 years")
        )
        st.write("Completed calculations for CPPs - general")

    # # CPPs currently open
    if "list_7" in lists_uploaded:
        cpps_currently_open = dfs["list_7"][
            dfs["list_7"]["Child Protection Plan End Date"].isna()
        ]
        (
            measures["CPP - CPP (open plans) - Count"],
            measures[" CPP - CPP (currently open) - Rate"],
        ) = cyp_count(cpps_currently_open)
        cpp_currently_open_age_gender = age_gender_metric(
            cpps_currently_open, "CPP - Age breakdown (open plans)"
        )
        open_cpp_ethnicity = ethnic_background_metric(
            cpps_currently_open, "CPP - Ethnicities (open plans)"
        )
        measures["CPP - disability (open plans) - Percent"] = percent_of_col_with_value(
            cpps_currently_open, col="Does the Child have a Disability"
        )
        open_ccp_latest_abuse = category_metrics(
            cpps_currently_open,
            "Latest Category of Abuse",
            "CPP - Latest category of Abuse (open plans)",
        )
        cpp_open_durations, cpp_open_with_days = timelines_metric(
            cpps_currently_open,
            "Child Protection Plan Start Date",
            "Reference Date",
            "CPP - length (open plans)",
            working_days=False,
        )
        cpp_open_bins = timelines_with_bins(
            cpp_open_with_days, "CPP - CPP length (open plans)", month_year_bins
        )
        cpp_open_time_last_seen, cpp_open_time_last_seen_days = timelines_metric(
            cpps_currently_open[
                cpps_currently_open["Date of the Last Statutory Visit"].notna()
            ],
            "Date of the Last Statutory Visit",
            "Reference Date",
            "CPP - Last visit (open plans)",
        )
        measures["CPPs - Open CPP seen alone - Percent"] = percent_of_col_with_value(
            cpps_currently_open, col="Was the Child Seen Alone?"
        )
        cpp_open_time_last_review, cpp_open_time_last_review_days = timelines_metric(
            cpps_currently_open[
                cpps_currently_open["Date of latest review conference"].notna()
            ],
            "Date of latest review conference",
            "Reference Date",
            "CPP - Last review (open plans)",
        )
        cpp_open_last_seen_bins = timelines_with_bins(
            cpp_open_time_last_seen_days,
            "CPP - Last visit (open plans)",
            last_seen_bins,
        )
        cpp_open_last_review_bins = timelines_with_bins(
            cpp_open_time_last_review_days,
            "CPP - Last review (open plans)",
            review_bins,
        )
        st.write("Calculations completed for CPPs Currently Open.")

    # # CLA started ceased 6 months
    if "list_8" in lists_uploaded:
        cla_started_6mths = dfs["list_8"][
            (
                pd.to_datetime(
                    dfs["list_8"]["Date Started to be Looked After"],
                    dayfirst=True,
                    errors="coerce",
                )
                >= pd.to_datetime(
                    dfs["list_8"]["Reference Date"], dayfirst=True, errors="coerce"
                )
                - pd.DateOffset(months=6)
            )
        ].copy()
        cla_ended_6mths = dfs["list_8"][
            (
                pd.to_datetime(
                    dfs["list_8"]["Date Ceased to be Looked After"],
                    dayfirst=True,
                    errors="coerce",
                )
                >= pd.to_datetime(
                    dfs["list_8"]["Reference Date"], dayfirst=True, errors="coerce"
                )
                - pd.DateOffset(months=6)
            )
        ].copy()
        (
            measures["CLA - CLA Started within 6 months - Count"],
            measures["CLA - CLA Started within 6 months - Rate"],
        ) = cyp_count(cla_started_6mths)
        (
            measures["CLA - CLA Ended within 6 months - Count"],
            measures["CLA - CLA Ended within 6 months - Rate"],
        ) = cyp_count(cla_ended_6mths)
        cla_started_gender = age_gender_metric(
            cla_started_6mths, "CLA  - Age breakdown (Started within 6 months)"
        )
        cla_ended_gender = age_gender_metric(
            cla_ended_6mths, " CLA  - Age breakdown (Ended within 6 months)"
        )
        measures["CLA - UASC (Started within 6 months) - Percent"] = (
            percent_of_col_with_value(
                cla_started_6mths,
                col="Unaccompanied Asylum Seeking Child (UASC) within the Last 12 Months (Y/N)",
            )
        )
        measures["CLA - Previous CLA (Started within 6 months) - Percent"] = (
            percent_of_col_with_value(
                cla_started_6mths,
                col="Is this a second or subsequent period of being a Looked After Child within the last 12 months (Y/N)",
            )
        )
        cla_started_6mths_need = category_metrics(
            cla_started_6mths,
            "Child's Category of Need",
            "CLA - Category of need (Started within 6 months)",
        )
        cla_ceased_6mths_reason = category_metrics(
            cla_ended_6mths,
            "Reason Ceased to be Looked After",
            "CLA - Reason (Started within 6 months)",
        )
        st.write("Calculations completed for CLA Started and Ceased within 6 months.")

    # # CLA with open episode
    if "list_8" in lists_uploaded:
        open_cla = dfs["list_8"][
            dfs["list_8"]["Date Ceased to be Looked After"].isna()
        ].copy()
        (
            measures["CLA - CLA (open plans) - Count"],
            measures["CLA - CLA (open plans) - Rate"],
        ) = cyp_count(open_cla)
        cla_open_gender = age_gender_metric(
            open_cla, "CLA - Age breakdown (open plans)"
        )
        measures["CLA - UASC (open plans) - Percent"] = percent_of_col_with_value(
            open_cla,
            col="Unaccompanied Asylum Seeking Child (UASC) within the Last 12 Months (Y/N)",
        )
        open_cla_ethnicity = ethnic_background_metric(
            open_cla, "CLA -  Ethnicities (Open CLA)"
        )
        measures["CLA - Disability (open plans) - Percent"] = percent_of_col_with_value(
            open_cla, col="Does the Child have a Disability"
        )
        cla_open_legal_status = category_metrics(
            open_cla, "Child's Legal Status", "CLA - Legal status (open plans)"
        )
        cla_open_plan = category_metrics(
            open_cla,
            "What is the permanence plan for this child?",
            " CLA - Permenance plan (open plans)",
        )
        cla_time_last_review, cla_time_last_review_days = timelines_metric(
            open_cla,
            "Date of Latest Statutory Review",
            "Reference Date",
            "CLA - Time since last review (open plans)",
        )
        cla_last_review_bins = timelines_with_bins(
            cla_time_last_review_days,
            "CLA - Time since last review (open plans)",
            review_bins,
        )
        cla_time_last_seen, cla_time_last_seen_days = timelines_metric(
            open_cla,
            "Date of Last Social Work Visit",
            "Reference Date",
            "CLA - Time since last visit (open plans)",
        )
        cla_last_seen_bins = timelines_with_bins(
            cla_time_last_seen_days,
            "CLA - Time since last seen (open plans)",
            last_seen_bins,
        )
        st.write("Completed calculations for CLA with open episode.")

    # # CLA Placements
    if "list_8" in lists_uploaded:
        cla_type = category_metrics(
            dfs["list_8"], "Placement Type", "CLA - Placement type"
        )
        cla_provider = category_metrics(
            dfs["list_8"], "Placement Provider", "CLA - Placement provider"
        )
        multiple_cla = multiple_same_event(
            dfs["list_8"],
            "CLA - Number of Placements (12months)",
            "Number of Placements in the Last 12 months",
        )
        measures["CLA - Short term stability - Percent"] = short_term_stability(
            dfs["list_8"], col="Number of Placements in the Last 12 months"
        )
        measures["CLA - Long term stability - Percent"] = long_term_stability(
            dfs["list_8"]
        )
        cla_over_30_months = dfs["list_8"][
            pd.to_datetime(
                dfs["list_8"]["Date Started to be Looked After"],
                dayfirst=True,
                errors="coerce",
            )
            <= pd.to_datetime(
                dfs["list_8"]["Reference Date"] - pd.DateOffset(years=2, months=6)
            )
        ]
        cla_over_30_months_duration, cla_over_30_months_duration_days = (
            timelines_metric(
                cla_over_30_months,
                "Start Date of Most Recent Placement",
                "Reference Date",
                "CLA - CLA Duration (CLA over 30 months)",
            )
        )
        cla_over_30_months_bins = timelines_with_bins(
            cla_over_30_months_duration_days,
            "CLA - CLA Duration (CLA over 30 months)",
            month_year_bins,
        )
        st.write("Completed calculations for CLA Placements.")

    # # CLA health and missing/absent
    if "list_8" in lists_uploaded:
        open_cla["Open over 12 months"] = open_cla.apply(over_12_months, axis=1)
        cla_open_over_12_months = open_cla[open_cla["Open over 12 months"] == "Yes"]
        (
            measures["CLA - CLA open over 12 months - Count"],
            measures["CLA - CLA open over 12 months - Rate"],
        ) = cyp_count(cla_open_over_12_months)
        measures["CLA - CLA open over 12 months - Percent"] = percent_of_col_with_value(
            open_cla, col="Open over 12 months"
        )
        st.write("Completed calculations for CLA missing/absent.")

    # # open cla with health assessment in six months if under 5 and 12 months if 5 plus
    if "list_8" in lists_uploaded:
        over_5_12_months = (
            pd.to_datetime(
                cla_open_over_12_months["Date of Last Health Assessment"],
                dayfirst=True,
                errors="coerce",
            )
            >= pd.to_datetime(
                cla_open_over_12_months["Reference Date"],
                dayfirst=True,
                errors="coerce",
            )
            - pd.DateOffset(months=6)
        ) & (cla_open_over_12_months["Age of Child (Years)"] >= 5)
        under_5_6_months = (
            pd.to_datetime(
                cla_open_over_12_months["Date of Last Health Assessment"],
                dayfirst=True,
                errors="coerce",
            )
            >= pd.to_datetime(
                cla_open_over_12_months["Reference Date"],
                dayfirst=True,
                errors="coerce",
            )
            - pd.DateOffset(months=6)
        ) & (cla_open_over_12_months["Age of Child (Years)"] < 5)
        health_assessment_up_to_date = cla_open_over_12_months[
            over_5_12_months | under_5_6_months
        ].copy()
        health_assessment_up_to_date["Health assessment up to date"] = "Yes"
        cla_open_over_12_months = cla_open_over_12_months.merge(
            health_assessment_up_to_date["Health assessment up to date"],
            how="inner",
            left_index=True,
            right_index=True,
        )
        cla_open_over_12_months["Health assessment up to date"] = (
            cla_open_over_12_months["Health assessment up to date"].fillna("No")
        )
        measures["CLA - Health assessment up to date (open 12 months) - Percent"] = (
            percent_of_col_with_value(
                cla_open_over_12_months, col="Health assessment up to date"
            )
        )
        measures["CLA - Dental timeliness (open 12 months) - Percent"] = (
            event_timeliness(
                cla_open_over_12_months, "Date of Last Dental Check", days=0, months=12
            )
        )
        multiple_cla_missing = multiple_same_event(
            dfs["list_8"],
            "CLA - Number of missing incidents",
            "Number of Episodes the Child has been 'Missing' from their Placement in the last 12 months",
        )
        dfs["list_8"]["At least one missing"] = dfs["list_8"][
            "Number of Episodes the Child has been 'Missing' from their Placement in the last 12 months"
        ].apply(
            lambda x: (
                "No" if (x == "0") | (x == 0) | (pd.isnull(x)) | (x == " ") else "Yes"
            )
        )
        measures["CLA - At least one missing - Percent"] = percent_of_col_with_value(
            dfs["list_8"], col="At least one missing"
        )
        cla_missing = dfs["list_8"][dfs["list_8"]["At least one missing"] == "Yes"]
        measures["CLA - Missing offered return interview - Percent"] = (
            percent_of_col_with_value(
                cla_missing,
                col="Was the child offered a Return Interview after their last missing episode (Y/N)?",
            )
        )
        cla_absent = dfs["list_8"][
            dfs["list_8"][
                "Number of Episodes the Child has been 'Absent' from their Placement in the last 12 months"
            ].notna()
        ]
        dfs["list_8"]["Has absent episode?"] = dfs["list_8"][
            "Number of Episodes the Child has been 'Absent' from their Placement in the last 12 months"
        ].apply(lambda x: "No" if (x < 1) | pd.notnull(x) else "Yes")
        measures["CLA - With absent incident - Percent"] = percent_of_col_with_value(
            dfs["list_8"], col="Has absent episode?"
        )
        st.write(
            "Calculations completed for open cla with health assessment in six months if under 5 and 12 months if 5 plus."
        )

    # # Care leavers
    if "list_9" in lists_uploaded:
        (
            measures["Care leavers - Care leavers - Count"],
            measures["Care leavers - Care leavers - Rate"],
        ) = cyp_count(dfs["list_9"])
        care_leavers_gender = age_gender_metric(
            dfs["list_9"], "Care leavers - Age breakdown"
        )
        measures["Care leavers - Disability - Percent"] = percent_of_col_with_value(
            dfs["list_9"], col="Does the Child have a Disability"
        )
        care_leavers_ethnicity = ethnic_background_metric(
            dfs["list_9"], "Care leavers - Ethnicities"
        )
        care_leavers_eligibility = category_metrics(
            dfs["list_9"], "Eligibility Category", "Care leavers - Eligibility category"
        )
        leavers_17_18 = dfs["list_9"][
            (dfs["list_9"]["Age of Child (Years)"] == 18)
            | (dfs["list_9"]["Age of Child (Years)"] == 17)
        ]
        measures["Care leavers - In touch 17 to 18 - Percent"] = (
            percent_of_col_with_value(leavers_17_18, col="LA in Touch")
        )
        leavers_19_21 = dfs["list_9"][
            (dfs["list_9"]["Age of Child (Years)"] >= 19)
            | (dfs["list_9"]["Age of Child (Years)"] <= 21)
        ]
        measures["Care leavers - In touch 19 to 21 - Percent"] = (
            percent_of_col_with_value(leavers_19_21, col="LA in Touch")
        )
        metrics_by_age = groupby_age(
            dfs["list_9"], "Age of Child (Years)", "Care leavers - By age", "Age"
        )
        leavers_in_touch = dfs["list_9"][dfs["list_9"]["LA in Touch"] == "a) Yes"]
        la_in_touch = groupby_age(
            leavers_in_touch, "Age of Child (Years)", "Care leavers - In touch", "Age"
        )
        metrics_by_age = metrics_by_age.merge(
            la_in_touch, how="outer", on=["name_period", "Age of Child (Years)"]
        )
        metrics_by_age["Care leavers - In touch - Percent"] = (
            metrics_by_age["Care leavers - In touch - Count"]
            / metrics_by_age["Care leavers - By age - Count"]
            * 100
        )

        # # Care leavers accomodation and suitability type
        measures["Care leavers - Accomodation suitability - Percent"] = (
            percent_of_col_with_value(dfs["list_9"], col="Suitability of Accommodation")
        )
        care_leavers_suitable = dfs["list_9"][
            dfs["list_9"]["Suitability of Accommodation"] == "a) Yes"
        ]
        suitable_accomodation = groupby_age(
            care_leavers_suitable,
            "Age of Child (Years)",
            "Care leavers - Accomodation suitability by age",
            "Age",
        )
        metrics_by_age = metrics_by_age.merge(
            suitable_accomodation,
            how="outer",
            on=["name_period", "Age of Child (Years)"],
        )
        care_leavers_accomodation_17_18 = category_metrics(
            leavers_17_18,
            "Type of Accommodation",
            "Care leavers - type of accomodation",
        )
        care_leavers_accomodation_19_21 = category_metrics(
            leavers_19_21,
            "Type of Accommodation",
            "Care leavers - type of accomodation",
        )

        # # Care leavers EET
        care_leavers_eet = dfs["list_9"][
            ~(
                dfs["list_9"]["Activity Status"]
                == "d1) Not in education, training or employment - illness/disability"
            )
            & ~(
                dfs["list_9"]["Activity Status"]
                == "d2) Not in education, training or employment - other reasons"
            )
            & ~(
                dfs["list_9"]["Activity Status"]
                == "d3) Not in education, training or employment - pregnancy/parenting"
            )
            & ~(dfs["list_9"]["Activity Status"] == "NEET")
            & (dfs["list_9"]["Activity Status"].notna())
        ]
        care_leavers_eet_age = groupby_age(
            care_leavers_eet, "Age of Child (Years)", "Care leavers - In EET", "Age"
        )
        metrics_by_age = metrics_by_age.merge(
            care_leavers_eet_age,
            how="outer",
            on=["name_period", "Age of Child (Years)"],
        )
        care_leavers_activity_17_18 = category_metrics(
            leavers_17_18,
            "Activity Status",
            "Care leavers - Activity status (17 to 18)",
        )
        care_leavers_activity_19_21 = category_metrics(
            leavers_19_21,
            "Activity Status",
            "Care leavers - Activity status (19 to 21)",
        )
        st.write("Completed calculations for Care Leavers.")

    # # Calculations end, organisation for outputs begins
    categoricals_to_concat = []
    multiples_to_merge = []
    age_gender_to_merge = []
    ethnicities_to_merge = []
    if "list_1" in lists_uploaded:
        categoricals_to_concat.extend([contact_sources])
        multiples_to_merge.extend([multiple_contacts])
        age_gender_to_merge.extend([contact_age_gender])
        ethnicities_to_merge.extend([contact_ethnicity])
    if "list_2" in lists_uploaded:
        multiples_to_merge.extend([multiple_assessments])
        age_gender_to_merge.extend([eh_age_gender])
        ethnicities_to_merge.extend([eh_ethnicity])
    if "list_3" in lists_uploaded:
        categoricals_to_concat.extend([referral_sources])
        multiples_to_merge.extend([multiple_referral])
        age_gender_to_merge.extend([referral_age_gender])
        ethnicities_to_merge.extend([referral_ethnicity])
    if "list_4" in lists_uploaded:
        categoricals_to_concat.extend([assessment_durations_bins])
        age_gender_to_merge.extend([assessments_age_gender])
        ethnicities_to_merge.extend([assessments_ethnicity])
    if "list_5" in lists_uploaded:
        categoricals_to_concat.extend([icpc_durations_bins])
        multiples_to_merge.extend([multiple_s47, multiple_icpc])
        age_gender_to_merge.extend([s47_age_gender])
        ethnicities_to_merge.extend([s47_ethnicity])
    if "list_6" in lists_uploaded:
        categoricals_to_concat.extend(
            [cin_ceased_reasons, cin_closed_bins, open_cin_bins]
        )
        age_gender_to_merge.extend([open_cin_age_gender])
        ethnicities_to_merge.extend([open_cin_ethnicity])
    if "list_7" in lists_uploaded:
        categoricals_to_concat.extend(
            [
                cpp_initial_category_of_abuse,
                cpp_ended_bins,
                cpp_open_bins,
                cpp_open_last_seen_bins,
                cpp_open_last_review_bins,
            ]
        )
        multiples_to_merge.extend([multiple_cpp, multiple_cpp_started_6mths])
        age_gender_to_merge.extend([cpp_currently_open_age_gender])
        ethnicities_to_merge.extend([open_cpp_ethnicity])
    if "list_8" in lists_uploaded:
        categoricals_to_concat.extend(
            [
                cla_open_legal_status,
                cla_open_plan,
                cla_type,
                cla_provider,
                cla_last_review_bins,
                cla_last_seen_bins,
                cla_over_30_months_bins,
            ]
        )
        multiples_to_merge.extend([multiple_cla, multiple_cla_missing])
        age_gender_to_merge.extend(
            [cla_started_gender, cla_ended_gender, cla_open_gender]
        )
        ethnicities_to_merge.extend([open_cla_ethnicity])
    if "list_9" in lists_uploaded:
        categoricals_to_concat.extend(
            [
                care_leavers_eligibility,
                care_leavers_accomodation_19_21,
                care_leavers_accomodation_17_18,
                care_leavers_activity_17_18,
                care_leavers_activity_19_21,
            ]
        )
        age_gender_to_merge.extend([care_leavers_gender])
        ethnicities_to_merge.extend([care_leavers_ethnicity])

    # categoricals_to_concat = [
    #     contact_sources, #
    #     referral_sources, #
    #     cin_ceased_reasons, #
    #     cin_closed_bins, #
    #     open_cin_bins, #
    #     cla_open_legal_status, #
    #     cla_open_plan, #
    #     cla_type, #
    #     cla_provider, #
    #     cla_last_review_bins, #
    #     cla_last_seen_bins, #
    #     cla_over_30_months_bins, #
    #     care_leavers_eligibility, #
    #     care_leavers_accomodation_19_21, #
    #     care_leavers_accomodation_17_18, #
    #     care_leavers_activity_17_18, #
    #     care_leavers_activity_19_21, #
    #     assessment_durations_bins, #
    #     icpc_durations_bins, #
    #     open_ccp_latest_abuse, #
    #     cpp_initial_category_of_abuse, #
    #     cpp_ended_bins, #
    #     cpp_open_bins, #
    #     cpp_open_last_seen_bins, #
    #     cpp_open_last_review_bins, #
    # ]

    # multiples_to_merge = [
    #     multiple_contacts, #
    #     multiple_assessments, #
    #     multiple_referral, #
    #     multiple_s47, #
    #     multiple_icpc, #
    #     multiple_cpp,
    #     multiple_cpp_started_6mths,
    #     multiple_cla,
    #     multiple_cla_missing,
    # ]

    # age_gender_to_merge = [
    #     contact_age_gender,
    #     eh_age_gender,
    #     referral_age_gender,
    #     assessments_age_gender,
    #     s47_age_gender,
    #     open_cin_age_gender,
    #     cpp_currently_open_age_gender,
    #     cla_started_gender,
    #     cla_ended_gender,
    #     cla_open_gender,
    #     care_leavers_gender,
    # ]

    # ethnicities_to_merge = [
    #     contact_ethnicity,
    #     eh_ethnicity,
    #     referral_ethnicity,
    #     assessments_ethnicity,
    #     open_cin_ethnicity,
    #     open_cpp_ethnicity,
    #     open_cla_ethnicity,
    #     care_leavers_ethnicity,
    # ]

    # # Processing into categorical, multiple events, etc tables for slicing in Power BI
    categorical_table = pd.concat(categoricals_to_concat)
    multiple_events_table = pd.DataFrame(columns=["name_period", "Measure Category"])
    for table in multiples_to_merge:
        multiple_events_table = multiple_events_table.merge(
            table, how="outer", on=["name_period", "Measure Category"]
        )
    age_gender_table = pd.DataFrame(columns=["name_period", "Age of Child (Years)"])
    for table in age_gender_to_merge:
        age_gender_table = age_gender_table.merge(
            table, how="outer", on=["name_period", "Age of Child (Years)"]
        )
    age_gender_table = age_gender_table[age_gender_table["Age of Child (Years)"] <= 25]
    ethnicity_table = pd.DataFrame(columns=["name_period", "Ethnicity"])
    for table in ethnicities_to_merge:
        ethnicity_table = ethnicity_table.merge(
            table, how="outer", on=["name_period", "Ethnicity"]
        )

    # # Convert measures dict to df and order
    measures_table = pd.DataFrame({"name_period": la_names})
    for measure, dictionary in measures.items():
        df = pd.DataFrame(
            {"name_period": dictionary.keys(), measure: dictionary.values()}
        )
        measures_table = measures_table.merge(df, how="outer", on="name_period")

    tables = {
        "Count rate percentage measures": measures_table,
        "Age Gender breakdowns": age_gender_table,
        "Categorical measures": categorical_table,
        "Ethnicity breakdowns": ethnicity_table,
        "Multiple event measures": multiple_events_table,
    }

    for key, table in tables.items():
        table[["LA", "Time Period"]] = table["name_period"].str.split("/", expand=True)
        table.drop("name_period", axis=1, inplace=True)

        cols = ["LA", "Time Period"]
        cols.extend(table.columns)

        table = table[cols]
        table = table.iloc[:, :-2]

        tables[key] = table

    for key, table in tables.items():
        if key == "Count rate percentage measures":
            cols_to_melt = list(table.columns)
            cols_to_melt = cols_to_melt[:2]

            table = table.melt(
                id_vars=cols_to_melt, var_name="Measure", value_name="Value"
            )

        elif key in [
            "Age Gender breakdowns",
            "Ethnicity breakdowns",
            "Multiple event measures",
            "Durations measures (days)",
            "Durations table (short term)",
            "Durations table (mid term)",
        ]:
            cols_to_melt = list(table.columns)
            cols_to_melt = cols_to_melt[:3]

            table = table.melt(
                id_vars=cols_to_melt, var_name="Measure", value_name="Value"
            )

        if key == "Age Gender breakdowns":
            table["Value"].fillna(0, inplace=True)

        if key in [
            "Durations measures (days)",
            "Durations table (short term)",
            "Durations table (mid term)",
        ]:
            cols_to_melt = list(table.columns)
            del cols_to_melt[2]

            table = table.melt(
                id_vars=cols_to_melt, var_name="Duration Type", value_name="Duration"
            )
            table = table[
                ["LA", "Time Period", "Measure", "Duration Type", "Duration", "Value"]
            ]
            table.drop("Duration Type", axis=1, inplace=True)
            table.rename(columns={"Duration": "Duration (Days)"}, inplace=True)

        if key != "Categorical measures":
            table[["Category", "Measure", "Measure Type"]] = table["Measure"].str.split(
                "-", expand=True
            )

        if key == "Categorical measures":
            cols_to_melt = list(table.columns)
            cols_to_melt = cols_to_melt[:3]
            cols_to_melt.append("Measure Category")
            table = table.rename(columns={"Value": "Measure Category"})
            table = table.melt(
                id_vars=cols_to_melt, var_name="Measure Type", value_name="Value"
            )

            table[["Category", "Measure"]] = table["Category"].str.split(
                "-", expand=True
            )

        if key == "Ethnicity breakdowns":
            table = table.rename(columns={"Ethnicity": "Measure Category"})

        tables[key] = table

    for k, df in tables.items():
        print(k)
        df_obj = df.select_dtypes("object")
        df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
        df["Measure Type"] = df["Measure Type"].apply(lambda x: x.capitalize())

        tables[k] = df

    final_tables = {}
    final_tables["Categorical Measures"] = pd.concat(
        [
            tables["Categorical measures"],
            tables["Ethnicity breakdowns"],
            tables["Multiple event measures"],
        ]
    )

    final_tables["Numerical measures"] = tables["Count rate percentage measures"]

    final_tables["Age Gender breakdowns"] = tables["Age Gender breakdowns"]

    output = to_excel(final_tables)

    if output != None:
        st.download_button(
            "Download output excel here",
            output,
            file_name="Annex A pre-processing output.xlsx",
        )
    else:
        st.download_button(
            "Please wait for processing to finish.",
            output,
            file_name="Annex A pre-processing output.xlsx",
            disabled=True,
        )
