import streamlit as st
from PIL import Image

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/README.md) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/009_PATCh_demo/app.py)")

st.title("PATCh: Create your own app")


st.markdown(
    """
### PATCh

For those interested in how PATCh apps work: every time you load a PATCh app, the webpage will use something called Pyodide to run
Python in the browser. The product of the Python code is then displayed as HTML using a package called streamlit lite.
This only outside connection the apps make is the initial setup to run Python in the browser. It uses **stlite**, which is is a port of
_Streamlit_ to Wasm, powered by Pyodide,
that runs completely on web browsers. Once an app is running it's self contained,
you could even test this by running apps with the internet turned off once they've loaded. Pyodide uses your browser's memory 
and other resources to run the Python code making up the apps on your computer. This is unlike many other apps which would run the Python 
on a server somewhere and send information back and forth, which is why you can't use confidential data with them. The way streamlit 
lite works is that every time you do something in the app, it re-runs the Python code from the beginning (not including the install). 
This allows it to be easier to write for analysts, but does mean some apps take a while to update between widget interractions.




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



