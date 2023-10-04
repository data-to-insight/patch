import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/001_template/app.py)")

st.markdown("This dashboard takes historical data about children's Referral, Child Protection plan and CLA status dates and uses it to visualise drift. \
         Drift, in this case means how long it takes to provide children the level of care they need. The key assumption in these visualisations is that \
         in general, if a child moves from one level of Children's Service provision to another, it is likely that they needed that higher level of provision. \
         For instance, if a child recieves a Referral and becomes a CLA, it is likely that the level of provision they needed was a CLA status. \
         By visualising how long it takes to move up stages of provision, we can see how long it takes to meet children's needs. \
         \n \
         \n This set of visualisations needs three CSVs to work, each with two columns, one of Child IDs, and  one of provision start date. \
        The upload takes one CSV of this data for Referrals, one for CP plan, and one for CLA status.")

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

    def plot_wait_by_start_year_bar(self, years, df, title, end_point):
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
        df['last_five_years'] = 'No'
        df['last_five_years'].iloc[-5:] = 'Yes'
        fig = px.bar(df,
                    x='year', 
                    y='average_wait',
                    title=f'Average wait time from {title}',
                    color='last_five_years',
                    labels={'last_five_years':'Data from 5 most<br>recent years of data?'}
                    )
        fig.update_xaxes(range=[years_showing[0]+0.5, years_showing[1]+0.5])
        fig.update_layout(
                        xaxis_title=f'Year of {end_point}', yaxis_title=f'Days from {title}'
                    )
        #fig.update_xaxes(range=[,])

        return fig

    def plot_wait_by_start_year_box(self, years, df, title, end_point):
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
        year_max = df['year'].max() - 5
        year_check = lambda x: 'Yes' if x > year_max else 'No'
        df['last_five_years'] = df['year'].apply(year_check)

        fig = px.box(df, 
                     x='year', 
                     y='delta',
                     color='last_five_years',
                    labels={'last_five_years':'Data from 5 most<br>recent years of data?'})
        fig.update_xaxes(range=[years_showing[0]+0.5, years_showing[1]+1])
        fig.update_yaxes(range=[0, years_showing[1]+1])
        fig.update_layout(
                        xaxis_title=f'Year of {end_point}', yaxis_title=f'Days from {title}'
                    )
        return fig

    def plot_wait_time_hist(self, years, df):
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
        fig = px.histogram(df, 
                           x='delta',
                           title=f'Spread of time from {title} for years {years[0]} ato {years[1]}')
        fig.update_layout(
                xaxis_title=f'Time from {title}', yaxis_title=f'Number of children waiting this long between {years[0]} and {years[1]}'
            )

        return fig


with st.sidebar:
    uploaded_file = st.sidebar.file_uploader('Upload historical referrals, CP plan, and CLA data', accept_multiple_files=True)

if uploaded_file:
    for file in uploaded_file:
        if ('ref' in file.name.lower()):
            ref = pd.read_csv(file)
        if ('cp' in file.name.lower()) | ('child protection' in file.name.lower()):
            cp = pd.read_csv(file)
        if ('cla' in file.name.lower()) | ('lac' in file.name.lower()) | ('looked after' in file.name.lower()):
            cla = pd.read_csv(file)
    
    data = Drift_Data(referrals=ref, child_protection_plans=cp, cla=cla)
    

    tab1, tab2, tab3 = st.tabs(['Referral to CP Plan', 
                                'Referral to CLA', 
                                'CP Plan to CLA'])
    
    with st.sidebar:
        years = st.sidebar.slider('Years to calculate box and bar plots',
                        min_value=data.time_range[0],
                        max_value=data.time_range[1],
                        value=[data.time_range[0],data.time_range[1]])
        years_showing = st.sidebar.slider('Years to display box and bar plots',
                        min_value=data.time_range[0],
                        max_value=data.time_range[1],
                        value=[data.time_range[0],data.time_range[0]-5])
        years_hist = st.sidebar.slider('Years for wait time histogram',
                        min_value=data.time_range[0],
                        max_value=data.time_range[1],
                        value=[data.time_range[0],data.time_range[0]-5])

    with tab1:
        title = 'Referral to Child Protection plan'
        start_point = 'Referral'
        end_point = 'Child Protection Plan'
        st.write(f"The bar and box plots below, as default, show only the five most recent year's outcomes. They can be zoomed out \
                 by using the tool bar that appears when you hover over the plots to show more or fewer years worth of outcomes. \
                 The maths behind the plots uses historical data to calculate the time from {title}. This means that calculations for earlier years can \
                show artifically low  wait time outcomes as there is no {start_point} data for children with referrals from before \
                the data starts, meaning long wait times are not included, lowering the average. It is for this reason that the plots \
                default to showing only recent data.")
        fig = data.plot_wait_by_start_year_bar(years, data.ref_cp_wby, title, end_point)
        st.plotly_chart(fig)
        st.write(f"This plot shows the average time children wait from {title}, using data from between {years[0]} to {years[1]}, \
                 with the year being the year each child's {end_point}s started. On the assumption that when a child has a {start_point} that \
                    leads to a {end_point}, that child needed a {end_point}, it represents, yearly, how long on average it takes to \
                meet children's needs. ")

        fig = data.plot_wait_by_start_year_box(years, data.ref_cp, title, end_point)
        st.plotly_chart(fig)
        st.write(f"This plot shows the distribution of wait times from {title}, using data from between {years[0]} and {years[1]}, \
                 with the year being the year each child's {end_point}s started. It is a good representation of the time it takes to meet children's needs as \
                it allows us to see outliers, and the general spread of wait times.")

        fig = data.plot_wait_time_hist(years_hist, data.ref_cp)
        st.plotly_chart(fig)
        st.write(f"The histogram above shows how wait times were distributed from {title} between {years_hist[0]} and {years_hist[1]}. \
                 It is a useful representation of how many children wait for different lengths of time for care they need, and what the \
                 spread of wait times is.")

        st.dataframe(data.ref_cp_clean)

    with tab2:
        title = 'Referral to Child Looked After'
        start_point = 'Referral'
        end_point = 'Child Looked After'
        st.write(f"The bar and box plots below, as default, show only the five most recent year's outcomes. They can be zoomed out \
                 by using the tool bar that appears when you hover over the plots to show more or fewer years worth of outcomes. \
                 The maths behind the plots uses historical data to calculate the time from {title} status. This means that calculations for earlier years can \
                show artifically low  wait time outcomes as there is no {start_point} data for children with referrals from before \
                the data starts, meaning long wait times are not included, lowering the average. It is for this reason that the plots \
                default to showing only recent data.")
        fig = data.plot_wait_by_start_year_bar(years, data.ref_cla_wby, title, end_point)
        st.plotly_chart(fig)
        st.write(f"This plot shows the average time children wait from {title}, using data from between {years[0]} to {years[1]}, \
                 with the year being the year each child's {end_point} status began. On the assumption that when a child has a {start_point} that \
                leads to a {end_point} status, that child needed a {end_point} status, it represents, yearly, how long on average it takes to \
                meet children's needs. ")

        fig = data.plot_wait_by_start_year_box(years, data.ref_cla, title, end_point)
        st.plotly_chart(fig)
        st.write(f"This plot shows the distribution of wait times from {title} status, using data from between {years[0]} and {years[1]}, \
                 with the year being the year each child's {end_point} status began. It is a good representation of the time it takes to meet children's needs as \
                it allows us to see outliers, and the general spread of wait times.")

        fig = data.plot_wait_time_hist(years_hist, data.ref_cla)
        st.plotly_chart(fig)
        st.write(f"The histogram above shows how wait times were distributed from {title} status between {years_hist[0]} and {years_hist[1]}. \
                 It is a useful representation of how many children wait for different lengths of time for care they need, and what the \
                 spread of wait times is.")

        st.dataframe(data.ref_cla_clean)
   
    with tab3:
        title = 'Child Protection plan to Child Looked After'
        start_point = 'Child Protection Plan'
        end_point = 'Child Looked After'
        st.write(f"The bar and box plots below, as default, show only the five most recent year's outcomes. They can be zoomed out \
                 by using the tool bar that appears when you hover over the plots to show more or fewer years worth of outcomes. \
                 The maths behind the plots uses historical data to calculate the time from {title} status. This means that calculations for earlier years can \
                show artifically low  wait time outcomes as there is no {start_point} data for children with Child Protection plans beginning before \
                the data starts, meaning long wait times are not included, lowering the average. It is for this reason that the plots \
                default to showing only recent data.")
        fig = data.plot_wait_by_start_year_bar(years, data.cp_cla_wby, title, end_point)
        st.plotly_chart(fig)
        st.write(f"This plot shows the average time children wait from {title} status, using data from between {years[0]} to {years[1]}, \
                 with the year being the year each child's {end_point} status began. On the assumption that when a child has a {start_point} that \
                leads to a {end_point} status, that child needed a {end_point} status, it represents, yearly, how long on average it takes to \
                meet children's needs. ")

        fig = data.plot_wait_by_start_year_box(years, data.cp_cla, title, end_point)
        st.plotly_chart(fig)
        st.write(f"This plot shows the distribution of wait times from {title} status, using data from between {years[0]} and {years[1]}, \
                 with the year being the year each child's {end_point} status began. It is a good representation of the time it takes to meet children's needs as \
                it allows us to see outliers, and the general spread of wait times.")
        
        fig = data.plot_wait_time_hist(years_hist, data.cp_cla)
        st.plotly_chart(fig)
        st.write(f"The histogram above shows how wait times were distributed from {title} status between {years_hist[0]} and {years_hist[1]}. \
                 It is a useful representation of how many children wait for different lengths of time for care they need, and what the \
                 spread of wait times is.")

        st.dataframe(data.cp_cla_clean)