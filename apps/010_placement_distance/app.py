import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import datetime

st.markdown(
    "[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/009_PATCh_demo/app.py)"
)

st.write(
    "This tool can be used to plot the distance between the post code of a looked after \
         child placement and their home post code. In the plot, each point represents a placement. \
         The height of the point on the plot on the y-axis does not have meaning. To create the plot, please upload \
         the header file and placement distance file from your SSDA 903 return. Use the dropdown menu \
         to choose the child chacteristic you would like to group the data by. \
         The average distance by child characteristic is also displayed below the plot. \
         Use header, and distance and placement extended CSV files. Their filenames must include: \
         head and distance respectively to be read and the column order for each must match that needed \
         to paste into the ChAT."
)

uploaded_file = st.file_uploader(
    "Upload header.csv, and distance_and_Placement_Extended.csv",
    accept_multiple_files=True,
)
if uploaded_file:
    for file in uploaded_file:
        if "head" in file.name:
            header = pd.read_csv(file)
        if "distance" in file.name:
            distance = pd.read_csv(file)

    header.rename(
        columns={
            header.columns[0]: "id",
            header.columns[1]: "gender",
            header.columns[3]: "ethnicity",
        },
        inplace=True,
    )
    distance.rename(
        columns={
            distance.columns[0]: "id",
        },
        inplace=True,
    )

    distance.columns = map(str.lower, distance.columns)

    # tag the number of episodes
    distance["cnt"] = 1
    distance = distance.sort_values(by=["id"])
    distance[("epi_num")] = distance["cnt"].groupby(distance["id"]).transform("sum")

    # create an indicator for first placement
    distance["one_placement"] = distance["epi_num"] == 1
    distance = distance.merge(header, on="id", validate="many_to_one")

    # create grouping for ethnicities based on ChAT
    eth_groups = {
        "white": ["WBRI", "WIRI", "WIRT", "WORH", "WROM"],
        "mixed": ["MWBC", "MWBA", "MWAS", "MOTH"],
        "asian": ["AIND", "APKN", "ABAN", "AOTH"],
        "black": ["BCRB", "BAFR", "BOTH"],
        "other": ["CHNE", "OOTH"],
        "dk": ["REFU", "NOBT"],
    }
    distance["ethnicity_group"] = ""
    for g in eth_groups.keys():
        distance["ethnicity_group"] = np.where(
            distance["ethnicity"].isin(eth_groups[g]), g, distance["ethnicity_group"]
        )

    vars = {
        "one_placement": "Child only has one placement in file?",
        "gender": "Gender",
        "ethnicity": "Ethnicity",
        "ethnicity_group": "Ethnicity group",
    }

    def format_func(option):
        return vars[option]

    # Set labels for grouping variables
    labels = ["one_placement", "gender", "ethnicity", "ethnicity_group"]
    dicts = [
        {True: "Yes", False: "No"},
        {1: "Male", 2: "Female"},
        {
            "ABAN": "Bangladeshi",
            "AIND": "Indian",
            "AOTH": "Any other Asian",
            "APKN": "Pakistani",
            "BAFR": "African",
            "BCRB": "Caribbean",
            "Both": "Any other Black",
            "CHNE": "Chinese",
            "MOTH": "Any other mixed background",
            "MWAS": "White and Asian",
            "MWBA": "White and Black African",
            "MWBC": "White and Black Caribbean",
            "NOBT": "Information not available",
            "OOTH": "Other",
            "REFU": "Refused",
            "WBRI": "White British",
            "WIRI": "White Irish",
            "WIRT": "Traveller of Irish heritage",
            "WOTH": "Any other White",
            "WROM": "Gypsy/Roma",
        },
        {
            "white": "White",
            "mixed": "Mixed",
            "asian": "Asian",
            "black": "Black",
            "other": "Other ethnic group",
            "dk": "Not available",
        },
    ]

    result = {key: val for key, val in zip(labels, dicts)}
    xvar = st.selectbox(
        "Select child characteristic to group by below:",
        options=list(vars.keys()),
        format_func=format_func,
    )

    dt = distance.sort_values(by=xvar)
    dt["ind"] = dt.reset_index().index
    dt[xvar] = dt[xvar].astype(object)

    fig = px.scatter(
        dt,
        x="pl_distance",
        color=dt[xvar].map(result[xvar]),
        y="ind",
        title="Placement distance from home post code by child characteristic:<br>"
        + vars[xvar],
    )
    fig.update_layout(
        yaxis_title="Placement episode",
        xaxis_title="Placement distance from home post code (km)",
        legend_title_text=vars[xvar],
    )
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig)

    dt_coll = dt

    for v in result[xvar].keys():
        dt_coll[xvar] = np.where(dt[xvar] == v, result[xvar][v], dt_coll[xvar])

    dt_coll = dt.groupby(xvar)["pl_distance"].mean()
    st.write("Average distance by child characteristic: " + vars[xvar])
    st.table(dt_coll)
