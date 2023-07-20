import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.title("Will's app")

text = st.text_input("Input text to display in app")

if text:
    st.write(text)

data = st.file_uploader('Upload Excel file')

if data:
    df = pd.read_excel(data, sheet_name='Contacts')

    st.dataframe(df.head(10))

    columns = ['Gender', 'Ethnicity', 'Contact Source']

    column = st.selectbox('Choose data to plot', columns)

    fig, ax = plt.subplots()
    ax = sns.histplot(data=df, x=column,)
    plt.xticks(rotation=90)
    st.pyplot(fig)