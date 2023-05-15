import streamlit as st
from PIL import Image

st.title("PATCh: Create your own app")


st.markdown(
    """
### PATCh

This editor uses **stlite** is a port of _Streamlit_ to Wasm, powered by Pyodide,
that runs completely on web browsers.

To contribute to PATCh apps, see it's documentation [here](https://github.com/SocialFinanceDigitalLabs/patch/blob/main/README.md).
The official stlite repository is [🔗 here](https://github.com/whitphx/stlite).

If you are new to Streamlit, read the Getting Started tutorial [🔗 here](https://docs.streamlit.io/library/get-started) first
(don't worry, it only takes a few minutes 👍),
but **you can skip the "Installation" section** because you are here 😎.
"""
)


st.header("Streamlit Component Samples")
st.markdown(
    """
    All these features are working on your browser!
"""
)

name = st.text_input("Your name?")
st.write("Hello,", name or "world", "!")

value = st.slider("Value?")
st.write("The slider value is", value)

import numpy as np
import pandas as pd

st.subheader("Chart sample")
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

tab1, tab2, tab3 = st.tabs(["Line chart", "Area chart", "Bar chart"])
with tab1:
    st.line_chart(chart_data)
with tab2:
    st.area_chart(chart_data)
with tab3:
    st.bar_chart(chart_data)

st.subheader("DataFrame sample")
df = pd.DataFrame(np.random.randn(50, 20), columns=("col %d" % i for i in range(20)))

st.dataframe(df)

st.subheader("Camera input")
st.info(
    "Don't worry! The photo data is processed on your browser and never uploaded to any remote servers."
)
enable_camera_input = st.checkbox("Use the camera input")
if enable_camera_input:
    picture = st.camera_input("Take a picture")

    if picture:
        st.image(picture)



