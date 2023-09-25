import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib
from pyodide.http import open_url

# Buttons for each page linking to code
st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/007_ofsted_market_analysis/app.py)")

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

    # Convert Month-Year to datetime format
    df['Month-Year'] = df['month'] + '/' + df['year'].astype(str)
    df["ofsted_date_order"] = pd.to_datetime(df['Month-Year'])
    df['Ofsted date'] = df['ofsted_date_order'].apply(lambda x: x.strftime('%B-%Y'))

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

    # Widgit to select geography level
    with st.sidebar:
        geography_level = st.sidebar.radio('Select geography level',
             ('England', 'Region', 'Local authority')
             )
    
    # Widgits to select geographic area
    england = 'England'
    regions = pd.DataFrame(df['Region'].unique())
    regions = regions.sort_values([0])
    local_authorities = pd.DataFrame(df['Local authority'].unique())
    local_authorities = local_authorities.sort_values([0])
    #st.dataframe(local_authorities)

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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Setting & Beds',
                                            'Overall Effectiveness', 
                                            'CYP Safety', 
                                            'Leadership & Management',
                                            'Conditions Supported'])

    with tab1:
        # Group and plot number of settings per year by sector
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Sector']).count().reset_index()
        #count_settings['Ofsted date'].dtypes
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Sector',
                   var_title = f"Number of settings in {geographic_area} by sector<br>{', '.join(provider_type_select)}",
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"))

        # Group and plot average number of places per year by sector
        average_places = df.groupby(['ofsted_date_order', 'Ofsted date', 'Sector']).mean('Number of registered places').reset_index()
        average_places = average_places.rename(columns = {'Number of registered places':'Average registered places per provision'})
        #average_places = average_places.sort_values(['ofsted_date_order'])
        #st.dataframe(average_places)
        plot_chart(data_frame=average_places,
                   var_x = 'Ofsted date',
                   var_y = 'Average registered places per provision',
                   var_color = 'Sector',
                   var_title = f"Average number of registered places for provisions in {geographic_area} by sector<br>{', '.join(provider_type_select)}",
                   var_barmode = 'group')

    with tab2:
        # Group and plot number of settings per year by Overall Effectiveness grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Overall effectiveness']).count().reset_index()
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Overall effectiveness',
                   var_title = f'Number of settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}',
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
                   var_title = f'Number of private sector settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}',
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
                   var_title = f'Number of local authority sector settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}',
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
        # Group and plot number of settings per year by CYP Safety grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'CYP safety']).count().reset_index()
        count_settings = count_settings.sort_values(['CYP safety'])
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'CYP safety',
                   var_title = f'Number of settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}',
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
                   var_title = f'Number of private sector settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}',
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
                   var_title = f'Number of local authority sector settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}',
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
        # Group and plot number of settings per year by Leadership & Management grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Leadership and management']).count().reset_index()
        count_settings = count_settings.sort_values(['Leadership and management'])
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Leadership and management',
                   var_title = f'Number of settings in {geographic_area}<br>by Leadership & Management grade<br>{provider_type_select}',
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
                   var_title = f'Number of private sector settings in {geographic_area}<br>by Leadership & Management grade<br>{provider_type_select}',
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
                   var_title = f'Number of local authority sector settings in {geographic_area}<br>by Leadership & Management grade<br>{provider_type_select}',
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
                   var_title = f'Number of settings in {geographic_area}<br>providing care for categories of need<br>{provider_type_select}',
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"))

    pass