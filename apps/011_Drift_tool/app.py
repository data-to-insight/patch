import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/001_template/app.py)")

class Drift_Data():
    def __init__(self, referrals, child_protection_plans, cla):
        self.ref = self._data_clean(referrals, 'ref')
        self.cp = self._data_clean(child_protection_plans, 'cp')
        self.cla = self._data_clean(cla, 'cla')
        
        self.ref_cp = self._id_merge(self.ref, self.cp)
        self.ref_cla = self._id_merge(self.ref, self.cla)
        self.cp_cla = self._id_merge(self.cp, self.cla)

        self.ref_cp_wby = self._cases_per_year(self.ref_cp)
        self.ref_cla_wby = self._cases_per_year(self.ref_cla)
        self.cp_cla_wby = self._cases_per_year(self.cp_cla)

        self.ref_cp_clean = self._tidy_to_display(self.ref_cp)
        self.ref_cla_clean = self._tidy_to_display(self.ref_cla)
        self.cp_cla_clean = self._tidy_to_display(self.cp_cla)

        self.time_range = [int(max([self.ref.iloc[:,1].dt.year.max(), 
                               self.cp.iloc[:,1].dt.year.max(), 
                               self.cla.iloc[:,1].dt.year.max()])),
                              int(min([self.ref.iloc[:,1].dt.year.min(), 
                               self.cp.iloc[:,1].dt.year.min(), 
                               self.cla.iloc[:,1].dt.year.min()]))]

    def _data_clean(self, df, name):
        df.rename(columns={df.columns[0]:'person_id',
                           df.columns[1]:f'{name}_date'}, inplace=True)
        df.iloc[:,1] = pd.to_datetime(df.iloc[:,1], dayfirst=True)

        return df

    def _tidy_to_display(self, df):
        df.iloc[:,1] = df.iloc[:,1].dt.date
        df.iloc[:,2] = df.iloc[:,2].dt.date

        df.rename(columns={'person_id':'Person ID',
                            'ref_date':'Date of referral',
                            'cp_date':'Date of CP plan',
                            'cla_date':'CLA Date',},
                            inplace=True)

        return df

    def _id_merge(self, df_1, df_2):
        df = pd.merge(df_1, df_2, how='inner', on='person_id')    
        df['delta'] = df.iloc[:,-1] - df.iloc[:,-2]
        df['delta'] = df['delta']/pd.Timedelta(days=1)

        df.sort_values(['person_id', 'delta'], inplace=True)
        df = df[~df['delta'].between(-14, 0)]
        df.drop(df[df['delta'] < 0].index, inplace=True)
        df.drop_duplicates(subset=df.columns[[0, 2]], keep='first', inplace=True)
        df.drop_duplicates(subset=df.columns[[0, 1]], keep='first', inplace=True)

        return df
    
    def _cases_per_year(self, df):
        df['year'] = df.iloc[:,2].dt.year.astype(int)
        wait_by_year = df.groupby(df['year'])['delta'].mean()
        cases_by_year = df.value_counts('year').rename_axis('year').reset_index(name='cases_starting_that_year')
        wait_cases_by_year = pd.merge(wait_by_year, cases_by_year, on='year')
        wait_cases_by_year.columns = ['year', 'average_wait', 'cases_starting_that_year']

        return wait_cases_by_year

    def plot_wait_by_start_year_bar(self, years, df):
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
        df['last_five_years'] = 'No'
        df['last_five_years'].iloc[-5:] = 'Yes'
        fig = px.bar(df,
                    x='year', 
                    y='average_wait',
                    color='last_five_years',
                    )

        return fig

    def plot_wait_by_start_year_box(self, years, df):
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
        year_max = df['year'].max() - 5
        year_check = lambda x: 'Yes' if x > year_max else 'No'
        df['last_five_years'] = df['year'].apply(year_check)

        fig = px.box(df, 
                     x='year', 
                     y='delta',
                     color='last_five_years')

        return fig

    def plot_wait_time_hist(self, years, df):
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
        fig = px.histogram(df, y='delta')

        return fig


with st.sidebar:
    uploaded_file = st.sidebar.file_uploader('Upload historical referrals, CP plan, and CLA data', accept_multiple_files=True)

if uploaded_file:
    for file in uploaded_file:
        if ('ref' in file.name.lower()):
            ref = pd.read_csv(file)
        if 'cp' in file.name.lower():
            cp = pd.read_csv(file)
        if 'cla' in file.name.lower() :
            cla = pd.read_csv(file)
    
    data = Drift_Data(referrals=ref, child_protection_plans=cp, cla=cla)
    

    tab1, tab2, tab3 = st.tabs(['Referral to CP Plan', 
                                'Referral to CLA', 
                                'CP Plan to CLA'])
    
    with st.sidebar:
        years = st.sidebar.slider('Year select',
                        min_value=data.time_range[0],
                        max_value=data.time_range[1],
                        value=[data.time_range[0],data.time_range[1]])

    with tab1:
        fig = data.plot_wait_by_start_year_bar(years, data.ref_cp_wby)
        st.plotly_chart(fig)

        fig = data.plot_wait_by_start_year_box(years, data.ref_cp)
        st.plotly_chart(fig)
        
        fig = data.plot_wait_time_hist(years, data.ref_cp)
        st.plotly_chart(fig)

        st.dataframe(data.ref_cp_clean)

    with tab2:
        fig = data.plot_wait_by_start_year_bar(years, data.ref_cla_wby)
        st.plotly_chart(fig)

        fig = data.plot_wait_by_start_year_box(years, data.ref_cla)
        st.plotly_chart(fig)
        
        fig = data.plot_wait_time_hist(years, data.ref_cla)
        st.plotly_chart(fig)

        st.dataframe(data.ref_cla_clean)
   
    with tab3:
        fig = data.plot_wait_by_start_year_bar(years, data.cp_cla_wby)
        st.plotly_chart(fig)

        fig = data.plot_wait_by_start_year_box(years, data.cp_cla)
        st.plotly_chart(fig)
        
        fig = data.plot_wait_time_hist(years, data.cp_cla)
        st.plotly_chart(fig)

        st.dataframe(data.cp_cla_clean)