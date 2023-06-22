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
    
    epis['ind'] = epis.reset_index().index
    distance['ind'] = distance.reset_index().index

    epis = epis.merge(distance, on=['id', 'ind'], validate='one_to_one')

    # tag the number of episodes
    epis["cnt"] = 1
    epis = epis.sort_values(by = ["id","decom"])
    epis[("epi_num")] = epis["cnt"].groupby(epis["id"]).transform("cumsum")
    
    # create an indicator for first placement 
    epis["first_placement"] = epis["epi_num"] == 1
    epis = epis.merge(header, on = "id", validate = "many_to_one")   

    # create grouping for ethnicities based on ChAT 
    eth_groups = {"white": ["WBRI", "WIRI", "WIRT", "WORH", "WROM"], 
                  "mixed": ["MWBC", "MWBA", "MWAS", "MOTH"] , 
                  "asian": ["AIND", "APKN", "ABAN", "AOTH"], 
                  "black": ["BCRB", "BAFR", "BOTH"] , 
                  "other": ["CHNE", "OOTH"], 
                  "dk": ["REFU", "NOBT"]}
    epis["ethnicity_group"] = ""
    for g in eth_groups.keys(): 
        epis["ethnicity_group"] = np.where(epis["ethnicity"].isin(eth_groups[g]), g, epis["ethnicity_group"])
    
   # create grouping for placement type based on ChAT

    pt_groups = {"foster": ["U1", "U2", "U3", "U4", "U5", "U6"], 
                  "adoption": ["A3", "A4", "A5", "A6"], 
                  "parents": ["P1"] , 
                  "il": ["P2"], 
                  "res_employment": ["P3"] , 
                  "res_accom": ["H5"],
                  "sec_ch": ["K1"],
                  "ch": ["K2"],
                  "res_ch": ["R1"],
                  "nhs": ["R2"], 
                  "young_offender": ["R3"], 
                  "fc_mother": ["R5"], 
                  "other": ["Z1"], 
                   "temp": ["T0", "T1", "T2", "T3", "T4"], 
                   "res_sch": ["S1"]}
     
    epis["pt_group"] = ""
    for g in pt_groups.keys(): 
        epis["pt_group"] = np.where(epis["place"].isin(pt_groups[g]), g, epis["pt_group"])
 

    vars = {'first_placement':"First placement?",
            'gender':"Gender", 
            "ethnicity": "Ethnicity",
            "ethnicity_group": "Ethnicity group", 
            "pt_group": "Placement  type"}
    
    def format_func(option):
     return vars[option]
    # Set labels for grouping variables 
    labels = ["first_placement", "gender", "ethnicity", "ethnicity_group", "pt_group"] 
    dicts  = [{True: "Yes", False : "No"},
              {1: "Male", 2: "Female"}, 
              {"ABAN": "Bangladeshi", "AIND" : "Indian", "AOTH": "Any other Asian",
              "APKN": "Pakistani","BAFR": "African","BCRB": "Caribbean","Both": "Any other Black",
              "CHNE": "Chinese","MOTH": "Any other mixed background",
              "MWAS": "White and Asian","MWBA": "White and Black African","MWBC": "White and Black Caribbean",
              "NOBT": "Information not available","OOTH": "Other","REFU": "Refused","WBRI": "White British", "WIRI":
              "White Irish", "WIRT":"Traveller of Irish heritage", "WOTH":"Any other White", "WROM":"Gypsy/Roma"},
              {"white": "White", "mixed" : "Mixed", "asian": "Asian",
              "black": "Black","other": "Other ethnic group","dk": "Not available"}, 
               {"foster":"Foster placement", "adoption": "Placed for adoption",  "parents": "Placed with parents", 
               "il": "Independent living","res_employment": "Residential employment", 
               "red_accom": "Residential accommodation", "sec_ch": "Secure Children’s Homes", 
               "ch":"Children’s Homes", "res_ch": "Residential Care Home", 
               "nhs":"NHS/Health Trust", "fc_mother": "Family Centre or Mother and Baby Unit", 
               "young_offedner":"Young Offender Institution", "other": "Other type", 
               "temp":"Temporary placement", "res_sch": "Residential school"}] 
    
    result = {key: val for key, val in zip(labels, dicts)}
    xvar = st.selectbox('Select' , options=list(vars.keys()), format_func=format_func)

    dt= epis.sort_values(by = xvar)
    dt['ind'] = dt.reset_index().index
    dt[xvar] = dt[xvar].astype(object)
    
    fig = px.scatter(dt, 
                 x = "pl_distance", 
                 color = dt[xvar].map(result[xvar]),
                 y = "ind", 
                 title = "Placement distance from home post code by episode and characteristics")
    fig.update_layout(yaxis_title = "Placement episode", 
                      xaxis_title = "Placement distance from home post code (km)", 
                      legend_title_text = vars[xvar])
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig)
    


    dt_coll = dt

    for v in result[xvar].keys():
        dt_coll[xvar] = np.where(dt[xvar] == v, result[xvar][v], dt_coll[xvar])
     
    dt_coll = dt.groupby(xvar)["pl_distance"].mean()
    st.write("Average distance by characteristic: " + vars[xvar])
    st.table(dt_coll)
