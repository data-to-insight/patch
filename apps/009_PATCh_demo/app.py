import streamlit as st
import pandas as pd
import plotly.express as px
from pyodide.http import open_url



data = open_url("https://raw.githubusercontent.com/WillLP-code/stlite-tests/main/benchmarking%20test/data/a1.csv")
df = pd.read_csv(data)
        
category = df['category'].unique()        

with st.sidebar:
     st.title('Chart Options')
     chart_title = st.sidebar.text_input(label='What do you want to call the chart?',
                                         value='Please name the chart')


with st.sidebar:
        years = st.sidebar.slider('Year select',
                        min_value=2013,
                        max_value=2022,
                        value=[2013,2022])

df = df[(df['time_period'].astype(int) >= years[0]) & (df['time_period'].astype(int) <= years[1])]



with st.sidebar:
    cat_option = st.sidebar.selectbox(
    'What data category would you like?',
    (category))
    st.write('You selected:', cat_option)
df = df[df['category'] == cat_option]

with st.sidebar:
    category_type = df['category_type'].unique()
    cat_type_option = st.sidebar.selectbox(
    'What sub-category would you like?',
    (category_type))
    st.write('You selected:', cat_type_option)
df = df[df['category_type'] == cat_type_option]
st.dataframe(df)



fig = px.line(df, x="time_period", y="number", title=f'{chart_title}')
st.plotly_chart(fig)
