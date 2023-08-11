import streamlit as st
import pandas as pd

name=st.text_input('please input name')
if name:
 st.title(f'my name is {name}')

data=st.file_uploader('upload file')
if data:
 df=pd.read_excel(data, sheet_name="current tracker",skiprows=2)
 st.table(df.head(10))
 