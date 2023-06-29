import streamlit as st
import pandas as pd
import plotly.express as px
from pyodide.http import open_url






st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/009_PATCh_demo/app.py)")

st.title('PATCh demo')
st.write('This app is a demo for the PATCh tool showing off some features users can lean to code, and some of the types of functionality available. \
          It uses data used for benchmarking avaliable from the DFE here: https://explore-education-statistics.service.gov.uk/find-statistics/characteristics-of-children-in-need \
         It is easy to build apps that sefely use data uploaded from your computer, but for simplicity of the demo, this app avoids that.')

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

st.subheader(f'{cat_option} : {cat_type_option}')

st.dataframe(df)

fig = px.line(df, x="time_period", y="number", title=f'{chart_title}')
st.plotly_chart(fig)
