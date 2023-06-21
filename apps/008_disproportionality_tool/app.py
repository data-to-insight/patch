import streamlit as st
import pandas as pd
from pyodide.http import open_url

@st.cache_data
def file_ingress():
    data_file = 'https://raw.githubusercontent.com/data-to-insight/patch/main/apps/008_disproportionality_tool/spc_pupils_ethnicity_and_language_.csv'
    data = open_url(data_file)
    df = pd.read_csv(data)
    return df

df = file_ingress()

st.table(df)