import streamlit as st
import math
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib
from pyodide.http import open_url

# Buttons for each page linking to code
st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/007_ofsted_market_analysis/app.py)")

def owner_movements(df, col_1, col_2):
    existing_df = df[((df[col_1] == 'Existing') |(df[col_1] == 'New')) & (df[col_2] == 1)]
    existing_df[col_2] = 'Existing'
    left_df =  df[(df[col_1] == 'Existing') & (df[col_2] == 0)]
    left_df[col_2] = 'Left'
    new_df = df[(df[col_1] == 'None') & (df[col_2] == 1)]
    new_df[col_2] = 'New'
    temp_df = pd.concat([existing_df, left_df, new_df]).sort_index()
    index_list = temp_df['index'].tolist()
    none_df = df[~df['index'].isin(index_list)]
    none_df[col_2] = 'None'
    df = pd.concat([temp_df, none_df]).sort_index()
    return df[col_2]

def needs_coder(row, field):
    if row[field] == 'Y':
        return 'Yes'
    elif (int(row[field])) > 0:
        return 'Yes'
    else:
        return 'No'

def plot_chart(data_frame, var_x, var_y, var_color, var_title, var_barmode, var_labels=None, var_cdm=None, var_cat_orders=None):
    fig = px.bar(data_frame,
        x = var_x,
        y = var_y,
        color = var_color,
        title = var_title,
        barmode=var_barmode,
        labels=var_labels,
        color_discrete_map=var_cdm,
        category_orders=var_cat_orders)
    st.plotly_chart(fig)

def line_chart(data_frame, var_x, var_y, var_color, var_title):
    fig = px.line(data_frame,
        x = var_x,
        y = var_y,
        color = var_color,
        title = var_title)
    st.plotly_chart(fig)

data1 = open_url('https://raw.githubusercontent.com/data-to-insight/patch/main/apps/007_ofsted_market_analysis/Local%20authorities%20and%20regions.csv')
regions = pd.read_csv(data1)

# Title and description
st.title('Ofsted Market Analysis')
st.markdown('* This tool analyses a list of social care settings providers as provided by Ofsted.')
st.markdown('* Use the sidebar selectors to filter by geography and provider type.')
st.markdown('* Click on the tabs below the table to view different breakdowns for the selected filters.')

# Takes "Ofsted Social care providers list for LAs"
uploaded_files = st.file_uploader('Upload Ofsted social care providers list:', accept_multiple_files=True)


if uploaded_files:

    loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}

    files_dict = {}

    rename_dict = {'Local Authority':'Local authority',
                    'Provider Type':'Provider type',
                    'Provision type':'Provider type',
                    'Provider Subtype':'Provider subtype',
                    'Setting Name':'Setting name',
                    'Provider Status':'Registration status',
                    'Registration Status':'Registration status',
                    'Owner Name':'Owner name',
                    'Organisation name':'Owner name',
                    'Latest overall Effectiveness grade from last full inspection':'Overall effectiveness',
                    'Overall Effectiveness':'Overall effectiveness',
                    'CYP Safety':'CYP safety',
                    'Leadership and Management':'Leadership and management',
                    'Max Users':'Number of registered places',
                    'Emotional and Behavioural Difficulties':'Emotional and behavioural difficulties',
                    'Mental Disorders':'Mental disorders',
                    'Sensory Impairment':'Sensory impairment',
                    'Present impairment':'Present alcohol problems',
                    'Present Alcohol Problems':'Present alcohol problems',
                    'Present Drug Problems':'Present drug problems',
                    'Learning Difficulty':'Learning difficulty',
                    'Physical Disabilities':'Physical disabilities'}

    for name,file in loaded_files.items():
        file.dropna(axis=1, how="all", inplace=True) # Drop any fields with only nan
        file.dropna(axis=0, how="all", inplace=True) # Drop any rows with only nan
        year = name[-8:-4] # Find year of dataset from file name
        file["year"] = year # Place year into new field
        #st.write(year)

        # Find month of dataset from file name
        if "april" in name.lower():
            month = "april"
            # st.write(month)
        if "may" in name.lower():
            month = "may"
        if "june" in name.lower():
            month = "june"
        if "july" in name.lower():
            month = "july"
        if "august" in name.lower():
            month = "august"
        if "september" in name.lower():
            month = "september"
        if "october" in name.lower():
            month = "october"
        if "november" in name.lower():
            month = "november"
        if "december" in name.lower():
            month = "december"
        if "january" in name.lower():
            month = "january"
        if "february" in name.lower():
            month = "february"
        if "march" in name.lower():
            month = "march"
        file["month"] = month  # Populate new field with month name

        # Find CH, Non-CH or all from file name
        if " non" in name.lower():
            homestype = "non-ch"
        elif " ch" in name.lower():
            homestype = "ch"
        else:
            homestype = "all"
        file["homestype"] = homestype # Place homes type into new field

        name = f"{month}{year}{homestype}"

        # Rename columns to standard names
        file.rename(columns = rename_dict, inplace = True)

        # Put name of datasets and datasets themselves into a dictionary
        files_dict[name] = file

    # Append all datasets together to check which columns line up
    df = pd.concat(list(files_dict.values()), axis=0).reset_index()

    # Cleaning data
    cols = ['Setting name', 'Owner name']
    df[cols] = df[cols].apply(lambda x: x.str.strip())#.str.title())

    # Match local authority to region
    df = df.merge(regions,how='left',on='Local authority')

    # Select only necessary columns
    df = df[['year',
             'month',
             'homestype',
             'Local authority',
             'Region_y',
             'URN',
             'Provider type',
             'Provider subtype',
             'Sector',
             'Setting name',
             'Registration status',
             'Owner ID',
             'Owner name',
             'Overall effectiveness',
             'CYP safety',
             'Leadership and management',
             'Number of registered places',
             'Emotional and behavioural difficulties',
             'Mental disorders',
             'Sensory impairment',
             'Present alcohol problems',
             'Present drug problems',
             'Learning difficulty',
             'Physical disabilities']]

    df = df.rename(columns = {'Region_y':'Region'})

    # Select only settings with Registration Status = Active
    df = df[df['Registration status'] == 'Active']

    # Convert Month-Year to datetime format
    df['Month-Year'] = df['month'] + '/' + df['year'].astype(str)
    df["ofsted_date_order"] = pd.to_datetime(df['Month-Year'])
    df['Ofsted date'] = df['ofsted_date_order'].apply(lambda x: x.strftime('%B-%Y'))

    # Order dataframe by month then by setting name
    df.sort_values(['ofsted_date_order', 'Setting name'], inplace=True)

    # Replace values
    df['Overall effectiveness'] = df['Overall effectiveness'].replace('Requires Improvement', 'Requires improvement to be good')
    df['CYP safety'] = df['CYP safety'].replace('Requires Improvement', 'Requires improvement to be good')
    df['Leadership and management'] = df['Leadership and management'].replace('Requires Improvement', 'Requires improvement to be good')

    # Create additional dataframe to code "needs provisions" fields into a Yes-No format
    needs_list = ['Emotional and behavioural difficulties',
             'Mental disorders',
             'Sensory impairment',
             'Present alcohol problems',
             'Present drug problems',
             'Learning difficulty',
             'Physical disabilities']

    for field in needs_list:
        df[field].fillna(0, inplace=True)
        df[field] = df.apply(lambda row: needs_coder(row, field), axis=1)
    #st.dataframe(df)

    # Create lists of regions and local authorites
    england = 'England'
    regions = pd.DataFrame(df['Region'].unique())
    regions = regions.sort_values([0])
    regions = regions.dropna(axis=0)
    #st.dataframe(regions)
    local_authorities = pd.DataFrame(df['Local authority'].unique())
    local_authorities = local_authorities.sort_values([0])
    local_authorities = local_authorities[local_authorities[0] != '(select)']
    #st.dataframe(local_authorities)

    # Create list of months
    months_list = df['Ofsted date'].unique()
    #st.dataframe(months_list)

    # Add column for number of settings per owner
    df['Total number of settings with this owner'] = df.groupby('Owner name')['Setting name'].transform('count')

    # Create list of owners to widget
    owner_list = pd.DataFrame(df['Owner name'].unique())
    owner_list = owner_list.sort_values([0])

    # Widgit to toggle between geography and owner-level analysis
    with st.sidebar:
        toggle = st.sidebar.radio('Analyse by geographic area or owner name',
            ('Geographic area', 'Owner name')
            )

    if toggle == 'Geographic area':
        # Widgit to select geography level
        with st.sidebar:
            geography_level = st.sidebar.radio('Select geography level',
                ('England', 'Region', 'Local authority')
                )
        
        # Widgits to select geographic area
        if geography_level == 'Local authority':
            with st.sidebar:
                la_option = st.sidebar.selectbox(
                    'Select local authority',
                    (local_authorities),
                    key = 1
                )
            df = df[df['Local authority'] == la_option]
            geographic_area = la_option
        elif geography_level == 'Region':
            with st.sidebar:
                region_option = st.sidebar.selectbox(
                    'Select region',
                    (regions),
                    key = 1
                )
            df = df[df['Region'] == region_option]
            geographic_area = region_option
        else:
            df = df
            geographic_area = 'England'

        # Widgit to select provider type(s)
        provider_types = pd.DataFrame(df['Provider type'].unique())
        provider_types = provider_types.sort_values([0])
        #st.dataframe(provider_types)
        with st.sidebar:
            provider_type_select = st.sidebar.multiselect( # something wrong here
                'Select provider type',
                (provider_types),
                default = (["Children's Home"])
            )
        df = df[df['Provider type'].isin(provider_type_select)]

    elif toggle == 'Owner name':
        # Widgit to select provider
        with st.sidebar:
            owner_selected = st.sidebar.selectbox(
                'Select owner name',
                (owner_list)
            )
        df = df[df['Owner name'] == owner_selected]
        #geographic_area = ""

    else:
        df = df

    # Create dataframe of owners ordered by owner name, then Ofsted date (earliest first), and remove duplicates, keeping first
    owners1 = df[['Owner name','Ofsted date']].copy()
    owners1.sort_values(['Owner name','Ofsted date'], inplace=True)
    owners1.drop_duplicates('Owner name', keep='first', inplace=True)
    owners1.rename(columns = {'Ofsted date':'First appearance in data'}, inplace=True)

    # Create dataframe of owners ordered by owner name, then Ofsted date (latest first), and remove duplicates, keeping first
    owners2 = df[['Owner name','Ofsted date']].copy()
    owners2.sort_values(['Owner name','Ofsted date'], ascending=False, inplace=True)
    owners2.drop_duplicates('Owner name', keep='first', inplace=True)
    owners2.rename(columns = {'Ofsted date':'Last appearance in data'}, inplace=True)

    # Create dataframe of owners showing in which months they appear
    owner_appearances = df[['Owner name', 'Ofsted date']]
    owner_appearances = owner_appearances.drop_duplicates()
    owner_appearances.sort_values(['Owner name','Ofsted date'], inplace=True)
    owner_appearances['Count'] = 1
    owner_appearances = owner_appearances.pivot(index='Owner name', columns='Ofsted date', values='Count')
    owner_appearances = owner_appearances.rename_axis('Owner name').reset_index()
    owner_appearances.fillna(0, inplace=True)
    owner_appearances.reset_index(inplace=True)
    #st.dataframe(owner_appearances)

    # Use function "owner_movements" to identify where owners exist, where they are new to the market and where they leave the market
    owner_appearances.iloc[:,2] = owner_appearances.iloc[:,2].apply(lambda row: 'Existing' if row == 1 else 'None')
    for i in range(len(months_list)):
        if i > 0:
            owner_appearances[months_list[i]] = owner_movements(owner_appearances, months_list[i-1], months_list[i])

    owner_appearances = owner_appearances.drop(['index'], axis=1)
    #st.dataframe(owner_appearances)

    # Create dataframe of owners and their number of settings
    owner_size = df[['Owner name', 'Total number of settings with this owner']]
    owner_size = owner_size.drop_duplicates()
    #st.dataframe(owner_size)

    # Merge owners dataframes
    owners = pd.merge(owners1, owners2, how='inner', on='Owner name')
    owners = pd.merge(owners, owner_appearances, how='inner', on='Owner name')
    owners = pd.merge(owners, owner_size, how='left', on='Owner name')

    # Display dataframe, reset index and don't display index column
    df_display = df[['Ofsted date',
             'Local authority',
             'Region',
             'URN',
             'Provider type',
             'Provider subtype',
             'Sector',
             'Setting name',
             'Registration status',
             'Owner ID',
             'Owner name',
             'Total number of settings with this owner',
             'Overall effectiveness',
             'CYP safety',
             'Leadership and management',
             'Number of registered places',
             'Emotional and behavioural difficulties',
             'Mental disorders',
             'Sensory impairment',
             'Present alcohol problems',
             'Present drug problems',
             'Learning difficulty',
             'Physical disabilities']].reset_index()
    st.dataframe(df_display.iloc[:,1:])

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Setting & Beds',
                                            'Overall Effectiveness', 
                                            'CYP Safety', 
                                            'Leadership & Management',
                                            'Conditions Supported',
                                            'Owners'])

    with tab1:
        if toggle == 'Geographic area':
            title_1 = f"Number of settings in {geographic_area} by sector<br>{', '.join(provider_type_select)}"
            title_2 = f"Total number of registered places for provisions in {geographic_area} by sector<br>{', '.join(provider_type_select)}"
            title_3 = f"Number of settings with grouped number of registered places in {geographic_area} by sector<br>{', '.join(provider_type_select)}"
        else:
            title_1 = f"Number of settings owned by {owner_selected}"
            title_2 = f"Total number of registered places for provisions owned by {owner_selected}"
            title_3 = f"Number of settings with grouped number of registered places owned by {owner_selected}"

        # Group and plot number of settings by sector
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Sector']).count().reset_index()
        #count_settings['Ofsted date'].dtypes
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Sector',
                   var_title = title_1,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"))

        # Group and plot total number of places by sector
        total_places = df.groupby(['ofsted_date_order', 'Ofsted date', 'Sector']).sum('Number of registered places').reset_index()
        total_places = total_places.rename(columns = {'Number of registered places':'Total registered places'})
        #total_places = total_places.sort_values(['ofsted_date_order'])
        #st.dataframe(total_places)
        plot_chart(data_frame=total_places,
                   var_x = 'Ofsted date',
                   var_y = 'Total registered places',
                   var_color = 'Sector',
                   var_title = title_2,
                   var_barmode = 'group')

        # User selects boundaries for groups of registered places
        st.markdown('The chart below shows the number of settings grouped by the of registered places in the setting. You can alter the size of each group by toggling the numbers in these three boxes:')

        floor2 = tab1.selectbox(
            'Boundary between groups 1 and 2 (number of registered places per setting)',
            range(2, 12),
            index=0
        )

        floor3 = tab1.selectbox(
            'Boundary between groups 2 and 3 (number of registered places per setting)',
            range(2, 12),
            index=3
        )

        floor4 = tab1.selectbox(
            'Boundary between groups 3 and 4 (number of registered places per setting)',
            range(2, 12),
            index=8
        )
        
        ceiling1 = floor2 - 1
        ceiling2 = floor3 - 1
        ceiling3 = floor4 - 1

        # Add grouped column for number of registered places
        df['Registered places group'] = df['Number of registered places'].transform(lambda x: '1 to ' + str(ceiling1) if x < floor2
                                                                                    else str(floor2) + ' to ' + str(ceiling2) if floor2 <= x < floor3
                                                                                    else str(floor3) + ' to ' + str(ceiling3) if floor3 <= x < floor4
                                                                                    else str(floor4) + '+')

        # Group and plot number of settings with grouped number of registered places
        grouped_places = df.groupby(['ofsted_date_order', 'Ofsted date', 'Registered places group']).count().reset_index()
        line_chart(data_frame=grouped_places,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Registered places group',
                   var_title = title_3)

    with tab2:
        if toggle == 'Geographic area':
            title_3 = f"Number of settings in {geographic_area} by overall effectiveness grade<br>{', '.join(provider_type_select)}"
            title_4 = f'Number of private sector settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}'
            title_5 = f'Number of local authority sector settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}'
        else:
            title_3 = f"Number of settings owned by {owner_selected} by overall effectiveness grade"
            title_4 = f'Number of private sector settings owned by {owner_selected}<br>by overall effectiveness grade'
            title_5 = f'Number of local authority sector settings owned by {owner_selected}<br>by overall effectiveness grade'

        # Group and plot number of settings by Overall Effectiveness grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Overall effectiveness']).count().reset_index()
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Overall effectiveness',
                   var_title = title_3,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Overall effectiveness':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})

        # Plot for private sector only
        count_settings_private = df[df['Sector'] == 'Private'].groupby(['ofsted_date_order', 'Ofsted date', 'Overall effectiveness']).count().reset_index()
        #count_settings_private = count_settings_private.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_private)
        plot_chart(data_frame=count_settings_private,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Overall effectiveness',
                   var_title = title_4,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Overall effectiveness':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for local authority sector only
        count_settings_la = df[df['Sector'] == 'Local Authority'].groupby(['ofsted_date_order', 'Ofsted date', 'Overall effectiveness']).count().reset_index()
        #count_settings_la = count_settings_la.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_la)
        plot_chart(data_frame=count_settings_la,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Overall effectiveness',
                   var_title = title_5,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Overall effectiveness':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})

        

    with tab3:
        if toggle == 'Geographic area':
            title_6 = f"Number of settings in {geographic_area} by CYP safety grade<br>{', '.join(provider_type_select)}"
            title_7 = f'Number of private sector settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}'
            title_8 = f'Number of local authority sector settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}'
        else:
            title_6 = f"Number of settings owned by {owner_selected} by CYP safety"
            title_7 = f'Number of private sector settings owned by {owner_selected}<br>by CYP safety grade'
            title_8 = f'Number of local authority sector settings owned by {owner_selected}<br>by CYP safety grade'

        # Group and plot number of settings by CYP Safety grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'CYP safety']).count().reset_index()
        count_settings = count_settings.sort_values(['CYP safety'])
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'CYP safety',
                   var_title = title_6,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'CYP safety':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for private sector only
        count_settings_private = df[df['Sector'] == 'Private'].groupby(['ofsted_date_order', 'Ofsted date', 'CYP safety']).count().reset_index()
        #count_settings_private = count_settings_private.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_private)
        plot_chart(data_frame=count_settings_private,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'CYP safety',
                   var_title = title_7,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'CYP safety':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for local authority sector only
        count_settings_la = df[df['Sector'] == 'Local Authority'].groupby(['ofsted_date_order', 'Ofsted date', 'CYP safety']).count().reset_index()
        #count_settings_la = count_settings_la.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_la)
        plot_chart(data_frame=count_settings_la,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'CYP safety',
                   var_title = title_8,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'CYP safety':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


    with tab4:
        if toggle == 'Geographic area':
            title_9 = f"Number of settings in {geographic_area} by Leadership & Management grade<br>{', '.join(provider_type_select)}"
            title_10 = f'Number of private sector settings in {geographic_area}<br>by Leadership & Management grade<br>{provider_type_select}'
            title_11 = f'Number of local authority sector settings in {geographic_area}<br>by Leadership & Management<br>{provider_type_select}'
        else:
            title_9 = f"Number of settings owned by {owner_selected} by CYP safety"
            title_10 = f'Number of private sector settings owned by {owner_selected}<br>by Leadership & Management'
            title_11 = f'Number of local authority sector settings owned by {owner_selected}<br>by Leadership & Management'

        # Group and plot number of settings by Leadership & Management grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Leadership and management']).count().reset_index()
        count_settings = count_settings.sort_values(['Leadership and management'])
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Leadership and management',
                   var_title = title_9,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Leadership and management':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for private sector only
        count_settings_private = df[df['Sector'] == 'Private'].groupby(['ofsted_date_order', 'Ofsted date', 'Leadership and management']).count().reset_index()
        #count_settings_private = count_settings_private.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_private)
        plot_chart(data_frame=count_settings_private,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Leadership and management',
                   var_title = title_10,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Leadership and management':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for local authority sector only
        count_settings_la = df[df['Sector'] == 'Local Authority'].groupby(['ofsted_date_order', 'Ofsted date', 'Leadership and management']).count().reset_index()
        #count_settings_la = count_settings_la.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_la)
        plot_chart(data_frame=count_settings_la,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Leadership and management',
                   var_title = title_11,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Leadership and management':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


    with tab5:
        if toggle == 'Geographic area':
            title_12 = f"Number of settings in {geographic_area}<br>providing care for categories of need<br>{', '.join(provider_type_select)}"

        else:
            title_12 = f"Number of settings owned by {owner_selected}<br>providing care for categories of need"

        # Group and plot number of settings per year that support each category of need
        count_needs = pd.DataFrame()

        for need in needs_list:
            df_yes = df.groupby(['ofsted_date_order', 'Ofsted date', need]).count().reset_index()
            df_yes = df_yes[df_yes[need] == 'Yes']
            df_yes.rename(columns = {need:'Category_of_need'}, inplace = True)
            df_yes['Category_of_need'] = df_yes['Category_of_need'].replace('Yes', need)
            df_yes = df_yes[['Ofsted date',
                            'ofsted_date_order',
                            'Category_of_need',
                            'URN']]
            count_needs = count_needs.append(df_yes)
            #st.dataframe(df_yes)
        
        #st.dataframe(count_needs)
        plot_chart(data_frame=count_needs,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Category_of_need',
                   var_title = title_12,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"))

    with tab6:
        if toggle == 'Geographic area':
            title_13 = f"Number of owners with settings in {geographic_area}<br>{', '.join(provider_type_select)}"

        else:
            title_13 = f"SHowing owner: {owner_selected}"
        # settings_range = tab6.slider(
        #     'Enter range of values for settings per owner',
        #     min_value = 1,
        #     max_value = 1000,
        #     value = (1,50)
        # )

        # # Filter dataframe according to selection
        # #st.write('Range:', settings_range)
        # lower_bound = int(settings_range[0])
        # upper_bound = int(settings_range[1])
        # #st.write('Lower bound:', lower_bound)
        # #st.write('Upper bound:', upper_bound)
        # owners = owners[owners['Total number of settings with this owner'].between(lower_bound, upper_bound)]

        st.dataframe(owners)

        # Find counts of owners in each month by market leaving/joining status
        count_owners_data = {'Month': [],
                             'Existing': [],
                             'None': [],
                             'New': [],
                             'Left': []}
        count_owners = pd.DataFrame(count_owners_data)
        #st.dataframe(count_owners)

        for i in range(len(months_list)):
            month = months_list[i]
            existing = len(owners[owners[month] == 'Existing'])
            none = len(owners[owners[month]== 'None'])
            new = len(owners[owners[month] == 'New'])
            left = len(owners[owners[month] == 'Left'])
            new_record = pd.DataFrame([{'Month':month, 'Existing':existing, 'None':none, 'New':new, 'Left':left}])
            #st.dataframe(new_record)
            count_owners = pd.concat([count_owners, new_record], ignore_index=True)
        
        count_owners = count_owners.drop(['None'], axis=1)
        #st.dataframe(count_owners)

        # Reformat counts into 'long' format and group for chart display
        
        count_owners_long = pd.melt(count_owners, id_vars=['Month'], value_vars=['Existing', 'New', 'Left'])
        owner_group_dict = {'Existing': 'group1', 
                    'New': 'group1', 
                    'Left': 'group2'
                    }
        count_owners_long['Group'] = count_owners_long['variable'].map(owner_group_dict)
        count_owners_long = count_owners_long.rename(columns = {'variable':'Market status', 'value':'Number of owners'})
        #st.dataframe(count_owners_long)
        
        fig = px.bar(count_owners_long,
                    x='Group',
                    y='Number of owners',
                    facet_col='Month',
                    color='Market status',
                    color_discrete_map={
                        'Existing' : '#1f77b4',
                        'New' : '#2ca02c',
                        'Left' : '#d62728'},
                    title=title_13
                    )
        fig.update_xaxes(visible=False)
        
        st.plotly_chart(fig)


    pass