import streamlit as st
import plotly.express as px
import pandas as pd 

st.title('This is a demo')
st.write('A demo of the PATCh workflow')

user_name = st.text_input('Add your name')

st.write(f'Your name is {user_name}')
