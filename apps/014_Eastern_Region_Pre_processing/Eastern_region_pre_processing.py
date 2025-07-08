import pandas as pd
from glob import glob
import os 
import numpy as np

import streamlit as streamlit

st.title('Eastern Region Dashboard Pre-processing tool')

files = st.file_uploader("Upload Annex A files here", accept_multiple_files=True)