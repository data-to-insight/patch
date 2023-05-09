import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


def read_data(input_file):
    # READ IN EARLY HELP AND COLLAPSE TO CHILD LEVEL
    df_EH = pd.read_excel(input_file, sheet_name="Early Help")

    # rename Eh columns
    df_EH = df_EH.rename(
        columns={
            "Child Unique ID": "id",
            "Assessment start date": "EH_start",
            "Assessment completion date": "EH_end",
        }
    )

    df_EH = df_EH[["id", "EH_start", "EH_end"]]

    # only keep first date per child
    df_EH_lim = (
        df_EH.sort_values(by=["id", "EH_start"]).groupby("id").first().reset_index()
    )

    # READ IN CIN
    df_CIN = pd.read_excel(input_file, sheet_name="Children in Need")

    # rename CIN columns
    df_CIN = df_CIN.rename(
        columns={
            "Child Unique ID": "id",
            "CIN Start Date": "CIN_start",
            "CIN Closure Date": "CIN_end",
            "Primary Need Code": "need_type",
            "Ethnicity": "ethnicity",
            "Gender": "gender",
        }
    )
    # limit CIN
    df_CIN = df_CIN[["id", "CIN_start", "CIN_end", "need_type", "gender", "ethnicity"]]

    # only keep first CIN episode
    df_CIN_lim = (
        df_CIN.sort_values(by=["id", "CIN_start"]).groupby("id").first().reset_index()
    )

    # merge files together - only keeping those in the CiN file
    data = pd.merge(df_CIN_lim, df_EH_lim, how="left", on=["id"]).reset_index()

    # create variable for Early Help before CiN
    data["EH_before_CIN"] = 0
    data.loc[data.EH_start < data.CIN_start, "EH_before_CIN"] = 1

    return data


st.header("usecase for quality data EH")

uploaded_file = st.file_uploader("Choose a dummy annex A file")
if uploaded_file is not None:
    data = read_data(uploaded_file)
    option_to_col = {
        "Primary need": "need_type",
        "Gender": "gender",
        "Ethnicity": "ethnicity",
    }
    option = st.selectbox("Child characteristics", option_to_col.keys())

    st.write("You selected:", option)
    col_name = option_to_col[option]
    dt = data.groupby([data["EH_before_CIN"], col_name], as_index=False).size()
    dt["group_size"] = dt.groupby(dt["EH_before_CIN"])["size"].transform(np.sum)
    dt["perc"] = round((dt["size"] / dt["group_size"]) * 100, 1)
    dt["EH_before_CIN"] = dt["EH_before_CIN"].astype(str)
    # st.bar_chart(dt, x=col_name, y="perc")
    fig = px.bar(
        dt,
        x=col_name,
        color="EH_before_CIN",
        y="perc",
        barmode="group",
        title="Child characteristics by whether or not<br>they received Early Help before children's services",
    )

    fig.update_layout(yaxis_title="Percentage of children", xaxis_title=option)
    st.plotly_chart(fig)
    st.write(dt)
