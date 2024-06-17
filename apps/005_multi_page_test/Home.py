import streamlit as st

st.session_state.update(st.session_state)

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)


def render_page():
    st.write("# Welcome to the Home Page, {}!".format(st.session_state.name))
    st.write(st.session_state)
    st.markdown(
        """
        This is a test multi-page app
        """
    )


if "name" not in st.session_state:
    with st.form(key="name_form"):
        name = st.text_input("What's your name?", key="name")
        submit_button = st.form_submit_button(label="Submit", on_click=render_page)
name = st.session_state.name
