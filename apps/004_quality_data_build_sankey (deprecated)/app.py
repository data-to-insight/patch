import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np


uploaded_files = st.file_uploader("Load both files ('sankey_input.xlsx' and 'sankey_labels.xlsx') here:", accept_multiple_files=True)
if uploaded_files:
    loaded_files = {uploaded_file.name: pd.read_excel(uploaded_file) for uploaded_file in uploaded_files}
    df = loaded_files['sankey_input.xlsx']
    labs = loaded_files['sankey_labels.xlsx']
    
    df = df.merge(labs, left_on = "target", right_on = "name")
    df = df.rename(columns = {'lab':'target_lab'})
    df = df.merge(labs, left_on = "source", right_on = "name")
    df = df.rename(columns = {'lab':'source_lab'})
    df = df.drop(columns = ["name_x", "target", "source", "name_y"])
    df = df.rename(columns = {'target_lab':'target','source_lab':'source'})
    source_string = df["source"].values.tolist()
    target_string = df["target"].values.tolist()


    # create index values for source and target 
    combo = source_string + target_string
    all_options = np.unique(combo)
    options_to_merge = pd.DataFrame(all_options, columns = ["options"])
    options_to_merge.reset_index(inplace=True)
    options_to_merge = options_to_merge.rename(columns = {'index':'sankey_index'})
    labels = options_to_merge["options"].values.tolist()


    # first merge the index values for source
    df_ind = df.merge(options_to_merge, left_on = "source", right_on = "options")
    # rename and drop so we can re-merge
    df_ind = df_ind.rename(columns = {"sankey_index":"source_index"})
    df_ind = df_ind.drop(columns = "options")
    # merge the index values for target 
    df_ind = df_ind.merge(options_to_merge, left_on = "target", right_on = "options")
    df_ind = df_ind.rename(columns = {"sankey_index":"target_index"})

    #turn columns into arrays so we can create a dictionary for the Sankey input
    source = df_ind["source_index"].values.tolist()
    target = df_ind["target_index"].values.tolist()
    value  = df_ind["ref_id"].values.tolist()

    link = dict(source = source, target = target, value = value)
    node = dict(label = labels, pad = 15, thickness = 5)

    
    data = go.Sankey(link = link, node = node)
    fig = go.Figure(data)
    st.plotly_chart(fig)
