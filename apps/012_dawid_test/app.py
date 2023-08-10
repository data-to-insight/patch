import streamlit as st
import pandas as pd

uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        data_dict = {file.name : pd.read_csv(file)}

    category = data_dict['spc_class_size_.csv']['classtype'].unique()

    with st.sidebar:
        option = st.sidebar.selectbox('Select option',
                                      (category))

    df = data_dict['spc_class_size_.csv']
    
    st.table(df[df['classtype']==option].head())

    