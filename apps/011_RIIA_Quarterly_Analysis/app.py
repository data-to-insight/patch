import streamlit as st
import pandas as pd
import plotly.express as px



st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/011_RIIA_Quarterly_Analysis/app.py)")

st.title('RIIA Quarterly Analysis')
st.write('For LAs with access to the quarterly RIIA dataset, additional analysis to complement the quarterly Excel data tool')

# Point at "RIIA Quarterly dataset"
uploaded_files = st.file_uploader('Location of RIIA Quarterly Benchmarking Tool:', accept_multiple_files=False)

if uploaded_files:
    # Define the location of the data we want in the Excel file
    loaded_files = {uploaded_files.name: pd.read_excel(uploaded_files,sheet_name='RIIA Measures',usecols="A:P")}  

    for file in loaded_files.items():
        st.write('Displaying "' + file[0] + '"') # Print the key from the dictionary for this file

    # Access the dataframe for the file   
    df = list(loaded_files.values())[0]

    # Display dataframe
    st.dataframe(df)
        
    pass


# Allows user to customise chart title based on their selections, so chart can easily be used in reports
#Chart_name = st.text_input('Type a chart name (e.g. "Regional referrals comparison from RIIA Quarterly Dataset")')
#st.write(f'The chart name is set as "{Chart_name}"')