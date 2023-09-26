import streamlit as st
import pandas as pd

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/001_template/app.py)")

class Drift_Data():
    def __init__(self, referrals, child_protection_plans, cla):
        self.ref = self.data_clean(referrals, 'ref')
        self.cp = self.data_clean(child_protection_plans, 'cp')
        self.cla = self.data_clean(cla, 'cla')
        self.ref_cp = self.id_merge(self.ref, self.cp)
        self.ref_cla = self.id_merge(self.ref, self.cla)
        self.cp_cla = self.id_merge(self.cp, self.cla)

    def data_clean(self, df, name):
        df.rename(columns={df.columns[0]:'person_id',
                           df.columns[1]:f'{name}_date'}, inplace=True)
        df.iloc[:,1] = pd.to_datetime(df.iloc[:,1], dayfirst=True).dt.date

        return df


    def id_merge(self, df_1, df_2):
        df = pd.merge(df_1, df_2, how='inner', on='person_id')    
        df['delta'] = df.iloc[:,-1] - df.iloc[:,-2]
        df['delta'] = df['delta']/pd.Timedelta(days=1)

        df = df[~df['delta'].between(-14, 0)]

        return df

uploaded_file = st.file_uploader('Upload historical referrals, CP plan, and CLA data', accept_multiple_files=True)

if uploaded_file:
    for file in uploaded_file:
        if ('ref' in file.name.lower()):
            ref = pd.read_csv(file)
        if 'cp' in file.name.lower():
            cp = pd.read_csv(file)
        if 'cla' in file.name.lower() :
            cla = pd.read_csv(file)
    
    data = Drift_Data(referrals=ref, child_protection_plans=cp, cla=cla)
    
