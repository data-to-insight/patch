import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title ("Kirsty's App")
text = st.text_input("Input text to display in app")
if text:
    st.write(text)

data = st.file_uploader('Upload Excel File')
if data:
    df = pd.read_excel(data, skiprows=4)
# sheet_name=None if more than one sheet
    st.dataframe(df.head(10))

    columns = ['Gender', 'Ethnicity', 'Contact Source']   

    column = st.selectbox('Choose data to plot',columns)
  
    fig, ax = plt.subplots()
    ax = sns.histplot(data=df, x=column,)
    plt.xticks(rotation=90)
    st.pyplot(fig)
