import streamlit as st

st.set_page_config(
    page_title="Page2",
    page_icon="📄",
)

st.write("Hello, I still remember you, {}.".format(st.session_state.name))
