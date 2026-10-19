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


def enrich_pupils_df(df):
    df["dob"] = df['dob'].str.split(" ").str[0]
    df['dob_dt'] = pd.to_datetime(df["dob"], format="%Y-%b-%d")

    df["entrydate"] = df['entrydate'].str.split(" ").str[0]
    df['entrydate_dt'] = pd.to_datetime(df["entrydate"], format="%Y-%b-%d")

    df['age on entry date'] = (df["entrydate_dt"] - df["dob_dt"])/pd.Timedelta(days=365.25)

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
            else:
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
            enriched_pupils_df = dfs['pupils'].merge(dfs['senneeds'], how='left', on='roll_id')

            enriched_pupils_df = enriched_pupils_df[[
              "upn",
              "formerupn",
              "surname",
              "forename",
              "middlenames",
              "formersurname",
              "dob",
              "entrydate",
              "leavingdate",
              "parttime",
              "termlysessionspossible",
              "moveonrollflag",
              "uniquelearnernumber",
              "sex",
              "ethnicity",
              "language",
              "boarder",
              "Academy or LA_x",
              "Original Table_x",
              "roll_id",
              "preferredsurname",
              "schoollunchtaken",
              "senunitindicator",
              "resourcedprovisionindicator",
              "missingaddress",
              "hoursatsetting",
              "fundedhours",
              "extendedhours",
              "expandedhours",
              "eligibilitycode",
              "dafindicator",
              "duplicatenotfunded",
              "moveoffrollflag",
              "topupfunding",
              "unitcontacttime",
              "yssa",
              "enrolstatus",
              "classtype",
              "ncyearactual",
              "senprovision",
              "servicechild",
              "youngcarer",
              "plaa",
              "eyppr",
              "eyppbf",
              "senneedstableid",
              "senneedsorderseqcolumn",
              "sentyperank",
              "sentype",
            ]].copy()

            enriched_pupils_df = enrich_pupils_df(enriched_pupils_df)

            

            