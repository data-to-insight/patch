# SEND provision:
# •	Number of children recorded as N, K or E, broken down by academic year/ year group.
# •	Using UPN to match children across years, we could look at how many remain at the same level, move from N to K, K to E, N to E or move in the other direction.
# •	It would be useful to show both numbers and percentages.
# •	We could also look at children who are new to the data or no longer appear in the following year, so we can separate these from children whose provision has actually changed.
# SEN needs:
# •	We could look at whether certain needs are more commonly associated with changes in provision at particular year groups. I think the SEN needs extract links to Pupil on Roll through 'pupilonrolltableid'.
# •	We would need to ensure we are look at the 'sentyperank' to use the primary need (1) not the secondary need (2).



import pandas as pd
import numpy as np
import datetime as dt

import zipfile

import streamlit as st

import xml.etree.ElementTree as ET
import time

from enum import Enum
from dateutil.relativedelta import relativedelta

from pyodide.http import open_url

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def determine_school_year_entry(entry):
    if entry.month >= 9:
        entry_year = entry.year
    elif entry.month < 9:
        entry_year = entry.year - 1

    entry_date = pd.to_datetime(f"01/09/{entry_year}", format="%d/%m/%Y")

    return entry_date

def determine_school_year(row):
    start_date_school_year_start_of_entry = determine_school_year_entry(row["entrydate_dt"])
    age_at_school_year_start_of_entry = (start_date_school_year_start_of_entry - row["dob_dt"])/pd.Timedelta(days=365.25)

    school_year = int(age_at_school_year_start_of_entry - 4)

    return school_year 


def enrich_pupils_df(df):

    # df = df[[
    #         "upn",
    #         "formerupn",
    #         "surname",
    #         "forename",
    #         "middlenames",
    #         "formersurname",
    #         "dob",
    #         "entrydate",
    #         "leavingdate",
    #         "parttime",
    #         "termlysessionspossible",
    #         "moveonrollflag",
    #         "uniquelearnernumber",
    #         "sex",
    #         "ethnicity",
    #         "language",
    #         "boarder",
    #         "Academy or LA_x",
    #         "Original Table_x",
    #         "roll_id",
    #         "preferredsurname",
    #         "schoollunchtaken",
    #         "senunitindicator",
    #         "resourcedprovisionindicator",
    #         "missingaddress",
    #         "hoursatsetting",
    #         "fundedhours",
    #         "extendedhours",
    #         "expandedhours",
    #         "eligibilitycode",
    #         "dafindicator",
    #         "duplicatenotfunded",
    #         "moveoffrollflag",
    #         "topupfunding",
    #         "unitcontacttime",
    #         "yssa",
    #         "enrolstatus",
    #         "classtype",
    #         "ncyearactual",
    #         "senprovision",
    #         "servicechild",
    #         "youngcarer",
    #         "plaa",
    #         "eyppr",
    #         "eyppbf",
    #         "senneedstableid",
    #         "senneedsorderseqcolumn",
    #         "sentyperank",
    #         "sentype",
    #     ]].copy()
                
    df["dob"] = df['dob'].str.split(" ").str[0]
    df['dob_dt'] = pd.to_datetime(df["dob"], format="%Y-%b-%d")

    df["entrydate"] = df['entrydate'].str.split(" ").str[0]
    df['entrydate_dt'] = pd.to_datetime(df["entrydate"], format="%Y-%b-%d")

    df['age on entry date'] = (df["entrydate_dt"] - df["dob_dt"])/pd.Timedelta(days=365.25)
    df['age on entry date'] = df['age on entry date'].astype("int")

    df['school year on entry date'] = df.apply(determine_school_year, axis=1)

    return df


st.title("Longitudinal tracking tool")

st.markdown(
    "[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/015_SEN2_app/sen2_app.py)"
)

input_files = st.file_uploader(
    "Upload BOTH LA maintained and academy school zip files containing CSV files here",
    accept_multiple_files=True,
)

if input_files:
    if len(input_files) != 2:
        st.write("Pleased upload maintained and academy schools zip files here")
    else:
        la_dfs = False
        ac_dfs = False
        for file in input_files:
            zip_file = zipfile.ZipFile(file)
            if "AC" in file.name:
                ac_dfs = {
                    text_file.filename: pd.read_csv(zip_file.open(text_file.filename))
                    for text_file in zip_file.infolist()
                    if text_file.filename.endswith(".csv")
                }
            if "LA" in file.name:
                la_dfs = {
                    text_file.filename: pd.read_csv(zip_file.open(text_file.filename))
                    for text_file in zip_file.infolist()
                    if text_file.filename.endswith(".csv")
                }
            elif ("LA" not in file.name) & ("AC" not in file.name):
                st.write(
                    "File detected without LA or AC in file name, please check file names and re-upload"
                )

        if (ac_dfs == False) & (la_dfs == False):
            st.write(
                "LA and AC zip files not both detected in upload, please check uploads and try again"
            )
            if ac_dfs == False:
                st.write("AC file not detected in upload")
            if la_dfs == False:
                st.write("LA file not detected in upload")
        else:
            del input_files

            dfs = {}
            for item in ['approvisiondetailoffroll', 'approvisiondetailonroll', 'pupilnolongeronroll', 'pupilonroll', 'senneeds']:
                dfs[item] = pd.DataFrame() 

            for df_dict in [ac_dfs, la_dfs]:
                for k, df in df_dict.items():
                    table_name = k.split("_")[-1][:-4]

                    df = df.rename(columns={'pupilonrolltableid': 'roll_id', 'pupilnolongeronrolltableid': 'newName2'})

                    df["Academy or LA"] = "Academy"
                    df["Original Table"] = table_name
                    dfs[table_name] = pd.concat([dfs[table_name], df])

            dfs['approvisiondetail'] = pd.concat([dfs['approvisiondetailoffroll'], dfs['approvisiondetailonroll']])
            dfs['pupils'] = pd.concat([dfs['pupilnolongeronroll'], dfs['pupilonroll']])

            enriched_pupils_df = dfs['pupils'].merge(dfs['approvisiondetail'], how='left', on='roll_id')
            enriched_pupils_df = enriched_pupils_df.merge(dfs['senneeds'], how='left', on='roll_id')

            enriched_pupils_df = enrich_pupils_df(enriched_pupils_df)

            by_year_provision = df_counts = (
                    enriched_pupils_df.groupby(['school year on entry date', 'senprovisionentry'])
                    .size()
                    .to_frame("Number of children")
                    .reset_index()
                )

            def make_bar(df, x_column, colour_column, title, x_label):

                df_counts = (
                        df.groupby([x_column, colour_column])
                        .size()
                        .to_frame("Number of children")
                        .reset_index()
                    )

                df_counts['Percentage of children'] = (df_counts["Number of children"] / df_counts["Number of children"].sum())*100
                df_sum = df_counts.groupby(x_column).sum()
                df_sum['Percentage of children'] = ((df_sum["Number of children"] / df_sum["Number of children"].sum())*100).round(1)

                bar_number = px.bar(df_counts, 
                             x=x_column, 
                             y="Number of children",
                             color=colour_column,
                             title=f'{title} - Count',
                             labels={x_column:x_label}
                             )

                bar_number.add_trace(
                            go.Scatter(
                                mode="text",
                                x=df_sum.index,
                                y=df_sum["Number of children"].tolist(),
                                text=[str(x) for x in df_sum["Number of children"].tolist()],
                                textposition="bottom center",
                                showlegend=False,
                            )
                        )

                bar_percent = px.bar(df_counts, 
                             x=x_column, 
                             y="Percentage of children",
                             color=colour_column,
                             title=f'{title} - Percent',
                             labels={x_column:x_label}
                             )

                bar_percent.add_trace(
                            go.Scatter(
                                mode="text",
                                x=df_sum.index,
                                y=df_sum["Percentage of children"].tolist(),
                                text=[str(x) for x in df_sum["Percentage of children"].tolist()],
                                textposition="bottom center",
                                showlegend=False,
                            )
                        )

                return bar_number, bar_percent
            
            by_year_provision_number, by_year_provision_percentage = make_bar(enriched_pupils_df, 
                                         x_column='school year on entry date', 
                                         colour_column='senprovisionentry', 
                                         title="SEN provision by school year", 
                                         x_label="School Year")
                       
            st.plotly_chart(by_year_provision_number, use_container_width=True, theme=None)
            st.plotly_chart(by_year_provision_percentage, use_container_width=True, theme=None)

            

            