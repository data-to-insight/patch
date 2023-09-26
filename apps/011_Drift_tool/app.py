import streamlit as st

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/001_template/app.py)")

uploaded_file = st.file_uploader('Upload historical referrals, CP plan, and CLA data', accept_multiple_files=True)

if uploaded_file:
    for file in uploaded_file:
        if 'ref' in file.name:
            ref = pd.read_csv(file)
        if 'cp' in file.name | 'protection' in file.name:
            cp = pd.read_csv(file)
        if 'cla' in file.name | 'CLA' in file.name:
            cla = pd.read_csv(file)
    
