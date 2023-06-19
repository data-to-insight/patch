import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import numpy as np
import datetime

uploaded_file = st.file_uploader('Upload file here', accept_multiple_files=True)
if uploaded_file:
    for file in uploaded_file:
        if 'head' in file.name:
            header = pd.read_csv(file)
        if 'episodes' in file.name:
            epis = pd.read_csv(file)
        if 'distance' in file.name:
            distance = pd.read_csv(file)
    
    header.rename(columns={header.columns[0]: 'id',
                           header.columns[1]: 'gender',
                           header.columns[3]: 'ethnicity'},
                            inplace=True)
    epis.rename(columns={epis.columns[0]: 'id',}, inplace=True)
    distance.rename(columns={distance.columns[0]: 'id',}, inplace=True)

    epis.columns = map(str.lower, epis.columns)
    header.columns = map(str.lower, header.columns)
    distance.columns = map(str.lower, distance.columns)

    epis = epis.merge(distance, on='id', how='left')

    epis["cnt"] = 1
    # tag the number of episodes
    epis = epis.sort_values(by = ["id","decom"])
    epis[("epi_num")] = epis["cnt"].groupby(epis["id"]).transform("cumsum")

    epis["first_placement"] = epis["epi_num"] == 1
    epis = epis.merge(header, on = "id", validate = "many_to_one")   

    xvar = st.selectbox('select xvar', options=('gender', 'ethnicity', 'first_placement'))  

    dt= epis.sort_values(by = xvar)
    dt['ind'] = dt.reset_index().index

    fig = px.scatter(dt, 
                 x = "pl_distance", 
                 color = xvar, 
                 y = "ind", 
                 title = "Placement distance from home post code by episode and characteristics")
    fig.update_layout(yaxis_title = "Placement episode", 
                      xaxis_title = "Placement distance from home post code (km)")
    st.plotly_chart(fig)