import streamlit as st
import plotly.express as px
import pandas as pd

st.title('RIIA Quarterly Analysis')
st.write('For LAs with access to the quarterly RIIA dataset, additional analysis to complement the quarterly Excel data tool')

Chart_name = st.text_input('Type a chart name (e.g. "Regional referrals comparison from RIIA Quarterly Dataset")')

st.write(f'The chart name is set as "{Chart_name}"')