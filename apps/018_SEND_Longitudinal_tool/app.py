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
            st.write(la_dfs.keys())
