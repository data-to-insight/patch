import streamlit as st 
import pandas as pd 
import plotly.express as px 

st.title('Demo app')
st.write('This is a demo showing how to make an app')

uploaded_file = st.file_uploader('Upload file here')
if uploaded_file:
    class_size = pd.read_csv(uploaded_file)
    
    with st.sidebar:
        class_type = st.sidebar.selectbox('Choose class type',
                                          options=class_size['classtype'].unique())
        st.sidebar.write(f'You have chosen {class_type}')

    class_size = class_size[class_size['classtype'] == class_type]
    class_size = class_size[class_size['size'] == 'Total']
    class_size = class_size[class_size['region_name'].isna()]
    
    class_size['time_period'] = class_size['time_period'].astype('str').str[:4].astype('float')

    st.table(class_size)

    fig = px.line(class_size, x='time_period', y='average_class_size')
    st.plotly_chart(fig)

