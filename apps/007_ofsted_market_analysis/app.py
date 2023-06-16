import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib


# Takes "Ofsted Social care providers list for LAs"
uploaded_files = st.file_uploader('Upload Ofsted social care providers list', accept_multiple_files=False)

if uploaded_files:
    if uploaded_files.name[-4:] == '.csv':
        loaded_files = {uploaded_files.name: pd.read_csv(uploaded_files)}
    else:
        loaded_files = {uploaded_files.name: pd.read_excel(uploaded_files)}
    
    for file in loaded_files.items():
        st.write(file[0]) # Print the key from the dictionary for this file
        #st.dataframe(file[1]) # Print the dataframe from the dictionary for this file

    # Access the dataframe for the file
    df = list(loaded_files.values())[0]

    # Take only the first 48 columns and rows where URN is not null
    df = df.iloc[:, : 47]
    df = df.dropna(subset=['URN'])

    # Filter out Sectors "Local Authority" and "Health Authority"
    df = df[~df['Sector'].isin(['Local Authority', 'Health Authority'])]

    # Where owner fields are blank, replace with setting fields
    df['Owner ID'][df['Owner ID'].isna()] = df['URN']
    df['Owner name'][df['Owner name'].isna()] = df['Setting name']

    # Add column for number of settings per owner
    df['Number of settings with this owner'] = df.groupby('Owner ID')['Owner ID'].transform('count')
    #st.dataframe(df)

    # Widgit to select either a single or two regions
    with st.sidebar:
        comparison_mode = st.sidebar.radio('Would you like to view a single region or compare two regions?',
             ('One region', 'Multiple regions')
             )


    # Widgits to filter the dataframe
    regions = df['Region'].unique()

    if comparison_mode == 'Multiple regions':
        with st.sidebar:
            region_multiple = st.sidebar.multiselect(
                'Select regions',
                (regions),
                default = ([regions[0], regions[1]])
            )
        df = df[df['Region'].isin(region_multiple)]
    else:
        with st.sidebar:
            region_option = st.sidebar.selectbox(
            'Select region',
            (regions),
            key = 1
        )
        df = df[df['Region'] == region_option]

    with st.sidebar:
        upper_threshold = st.sidebar.number_input(
            'Enter upper threshold for portfolio of settings per owner',
            min_value = 1,
            max_value = 100,
            value = 5
        )
    # Filter dataframe according to selections
    df = df[df['Number of settings with this owner'] <= upper_threshold]

    # Select only certain columns in dataframe
    df = df[['URN',
             'Setting name',
             'Owner name',
             'Local authority',
             'Region',
             'Number of registered places',
             'Number of settings with this owner']]

    
    # Display dataframe
    st.dataframe(df)

    # Group by number of settings per owener
    counts = df.groupby(['Number of settings with this owner', 'Region']).count().reset_index()
    #st.dataframe(counts)

    # Create a plot
    fig = px.bar(counts,
                 x = 'Number of settings with this owner',
                 y = 'URN',
                 color = 'Region',
                 #color_discrete_sequence = ['Red', 'Light Blue'],
                 barmode = 'group'
    )
    st.plotly_chart(fig)


    pass