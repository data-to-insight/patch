import streamlit as st
import numpy as np
import pandas as pd
from random import randrange
import scipy.stats as stats
from scipy.stats import chisquare
from pyodide.http import open_url
import matplotlib.pyplot as plt
import seaborn as sns

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/008_disproportionality_tool/app.py)")

st.title('Disproportionality Tool')
st.write('A Python deployment of the excel disproportionality tool allowing the comparison of ethnic breakdowns between LAs (as reported by the DFE), and numbers input by the user.\
        There are tabs for graphs and data for Relative Rate Index, Rate per 10,000, and percentages for both sub and main groups. These can be navigated using arrow keys. Statistically significant \
        differences between chosen LA and input figures are displayed using different coloured bars in the plots. LA, time period, and comparison numbers can be entered in the sidebar to the left.')

# Ingress data for benchmarking
@st.cache_data
def file_ingress():
    data_file = 'https://raw.githubusercontent.com/data-to-insight/patch/main/apps/008_disproportionality_tool/spc_pupils_ethnicity_and_language_.csv'
    data = open_url(data_file)
    df = pd.read_csv(data)
    return df

def denominator(LA, Date):
    '''creates a new dataframe of using only data specified in the setup contaning a census for only one LA and time period'''
    LAN = data[(data['la_name'] == LA) & (data['time_period'] == Date)]#slices census according to setup variables


    #  Initialises and populates lists of all major ethnic groups with their ethnic sub-groups to allow for totalling ethnic groups.
    W_ind = ['White - White British', 'White - Any other White background', 'White - Gypsy/Roma', 'White - Irish', 'White - Traveller of Irish heritage']
    A_ind = ['Asian - Any other Asian background', 'Asian - Bangladeshi', 'Asian - Chinese', 'Asian - _indian', 'Asian - Pakistani']
    B_ind = ['Black - Any other Black background', 'Black - Black African', 'Black - Black Caribbean']
    M_ind = ['Mixed - Any other Mixed background', 'Mixed - White and Asian', 'Mixed - White and Black African', 'Mixed - White and Black Caribbean']
    O_ind = ['Any other ethnic group', 'Not obtained', 'Refused']
    U_ind = ['Unclassified']
    #  Initialises and populates list of lists of ethnic subgroups for calculations.
    Subgroups = [W_ind, A_ind, B_ind, M_ind, O_ind, U_ind]
    
    #  Initialises a dictionary with keys as ethnic sub-groups and values as the total of that number in the population
    #  nested for loop runs through subgroups by main group.
    LAdf = {} #  It's always best practice to populate a dictionary then convert it to a dataframe.
    for SG in Subgroups:
        for i in SG:
            #  Accesses the rows of the LAN df where the ethnicity is the one currently specified by i in the subgroup and the grouping is total.
            tots = LAN[(LAN['ethnicity'] == i) & (LAN['phase_type_grouping'] == 'Total')]
            #  Initialises variable v (for value) and populates it with the sum of the values given in the headcount collumn of the row selected and called tots above.
            v=tots['headcount'].sum()
            #  Updates the dictionary LAdf with the key i (ethnic subgroup searched for in the loop) and the value from the census.
            LAdf[i]=v

    #  These following blocks of code calculate ethnic major-group totals using the sub-group totals from above and add them tot he LAdf dictionary.       
    LAWhite = LAN[(LAN['ethnicity'].isin(W_ind)) & (LAN['phase_type_grouping'] == 'Total')]#  Takes rows of LAN where the ethnicity column is in the W_ind list, and phase type grouping is Total.
    Wtot = LAWhite['headcount'].sum() #  Sums the headcount column of the above rows.
    LAdf['White Total'] = Wtot #  Returns the above value to the LAdf dictionary with the key White Total.

    LAAsian = LAN[(LAN['ethnicity'].isin(A_ind)) & (LAN['phase_type_grouping'] == 'Total')]
    Atot = LAAsian['headcount'].sum()
    LAdf['Asian Total'] = Atot
    
    LABlack = LAN[(LAN['ethnicity'].isin(B_ind)) & (LAN['phase_type_grouping'] == 'Total')]
    Btot = LABlack['headcount'].sum()
    LAdf['Black Total'] = Btot

    LAMixed = LAN[(LAN['ethnicity'].isin(M_ind)) & (LAN['phase_type_grouping'] == 'Total')]
    Mtot = LAMixed['headcount'].sum()
    LAdf['Mixed Total'] = Mtot

    LAOther = LAN[(LAN['ethnicity'].isin(O_ind)) & (LAN['phase_type_grouping'] == 'Total')]
    Otot = LAOther['headcount'].sum()
    LAdf['Other Total'] = Otot

    LAUnclassified = LAN[(LAN['ethnicity'].isin(U_ind)) & (LAN['phase_type_grouping'] == 'Total')]
    Utot = LAUnclassified['headcount'].sum()
    LAdf['Unclassified Total']=Utot
    
    #  Takes the LAdf dictionary created above and uses pandas to turn it into a dataframe.
    LAdf = pd.DataFrame(LAdf.items())
    #  Renames the columns of the new dataframe.
    LAdf.columns = ['ethnicity','denominator']
    #  Returns the dataframe from the function.
    return LAdf


def calcs_for_plots():
    #  Calculating percentages.
    percentages = []
    for i in range(len(comparison_df)):
        if comparison_df['denominator'].iloc[i] != 0: #checks to see no division by 0 will happen
            v = round(((comparison_df['numerator'].iloc[i]/comparison_df['denominator'].iloc[i])*100), 1)
        else: 
            v = 0
        percentages.append(v)
    comparison_df['Percentages'] = percentages


    #  Rate per 10,000.
    RP10k = []
    for i in range(len(comparison_df)):
        if comparison_df['denominator'].iloc[i] != 0:
            v = round(((comparison_df['numerator'].iloc[i]/comparison_df['denominator'].iloc[i])*10000), 1)
        else: 
            v = 0
        RP10k.append(v)
    comparison_df['Rate per 10,000'] = RP10k

    #  RRI
    RRI = []
    for i in range(len(comparison_df)):
        v = round(comparison_df['Rate per 10,000'].iloc[i]/comparison_df['Rate per 10,000'].iloc[0], 2)
        RRI.append(v)
    comparison_df['RRI'] = RRI


    #  No observed.
    no_observed = []
    for i in range(len(comparison_df)):
        v = total_known_ethnicity_numerator -  comparison_df['numerator'].iloc[i]
        no_observed.append(v)
    comparison_df['no_observed'] = no_observed

    #  Yes observed.
    yes_observed = []
    for i in range(len(comparison_df)):
        v = comparison_df['numerator'].iloc[i]
        yes_observed.append(v)
    comparison_df['Yes observed'] = yes_observed


    #  Yes expected.
    Yesexpected = []
    for i in range(len(comparison_df)):
        v = round((comparison_df['denominator'].iloc[i]/total_known_ethnicity_denominator) * total_known_ethnicity_numerator)
        Yesexpected.append(v)
    comparison_df['Yes expected'] = Yesexpected

    #  No expected.
    yes_expected = []
    for i in range(len(comparison_df)):
        v = round(total_known_ethnicity_numerator - comparison_df['Yes expected'].iloc[i])
        yes_expected.append(v)
    comparison_df['No expected'] = yes_expected 



    oe = ['observed', 'expected']
    observed = {}
    expected = {}
    ChiSquared = []
    for i in range(len(comparison_df)):
        if (comparison_df['numerator'].iloc[i] == 0) or (comparison_df['numerator'].iloc[i] == 0):
            ChiSquared.append(0)
        else:
            observed = {'Yes':comparison_df['Yes observed'].iloc[i], 'No':comparison_df['no_observed'].iloc[i]}
            expected = {'Yes':comparison_df['Yes expected'].iloc[i], 'No':comparison_df['No expected'].iloc[i]}
            TempDF =  pd.DataFrame([observed, expected])
            TempDF['oe'] = oe
            TempDF = TempDF.set_index('oe')
            d, p, dof, ex = stats.chi2_contingency(TempDF)
            v = round(p ,4)
            ChiSquared.append(v)
    comparison_df['Chi Squared'] = ChiSquared

    #  Higher Lower.
    HigherLower = []
    for i in range(len(comparison_df)):
        if comparison_df['numerator'].iloc[i] > comparison_df['Yes expected'].iloc[i]:
            v = 'Higher'
        elif comparison_df['numerator'].iloc[i] < comparison_df['Yes expected'].iloc[i]:
            v = 'Lower'
        else:
            v = 'Same or input error'
        HigherLower.append(v)
    comparison_df['Higher Lower'] = HigherLower

    #  Significance Test.
    SigTest = []
    for i in range(len(comparison_df)):
        if comparison_df['Chi Squared'].iloc[i] < 0.05:
            v = 'Sig'
        else:
            v = 'Not Sig'
        SigTest.append(v)
    comparison_df['Stat Sig'] = SigTest

    #  Adds lookup codes to the COmparisonDf dataframe.
    comparison_df['Chart Titles'] = ['WBRI', 'WOTH', 'WROM', 'WIRI', 'WIRT', 'AOTH', 'ABAN', 'ACHN', 'AIND', 'APKN', 'BOTH', 'BAFR','BCRB', 'MOTH', 'MWAS', 'MWBA', 'MWBC', 'OOTH', 'NOBT', 'REFU', 'Unkn', 'White', 'Asian', 'Black', 'Mixed', 'Other', 'Unkn']    

    #  Returns the RRI value of given rows where the RRI is greater than 1, and the value is considered to be statistically significant by the CHI2 test
    #  returns 0 in other cases.
    sig_higher_RRI = []
    for i in range(len(comparison_df)):
        if (comparison_df['RRI'].iloc[i] > 1) & (comparison_df['Stat Sig'].iloc[i] == 'Sig'):
            v = comparison_df['RRI'].iloc[i]
        else:
            v = 0
        sig_higher_RRI.append(v)
    comparison_df['Sig Higher RRI'] = sig_higher_RRI

    #  Returns RRI where RRI < 1 and Chi2 deems it a statistically significant difference from expected
    #  else returns 0.
    sig_lower_RRI = []
    for i in range(len(comparison_df)):
        if (comparison_df['RRI'].iloc[i] < 1) & (comparison_df['Stat Sig'].iloc[i] == 'Sig'):
            v = comparison_df['RRI'].iloc[i]
        else:
            v = 0
        sig_lower_RRI.append(v)
    comparison_df['Sig Lower RRI'] = sig_lower_RRI

    #  Adds values from sig higher and sig lower columns to a new column in comparison_df to make checking for Sig Diff easier.
    comparison_df['no_sig_diff_RRI_calc'] = (comparison_df['Sig Higher RRI'] + comparison_df['Sig Lower RRI']).to_list()

    #  Where the SigDiffCalc is 0, returns RRI, else returns 0.
    #  Works by checking that both higher and lower are zero, and only retyurning non-zero values where they are not.
    no_sig_diff_RRI = []
    for i in range(len(comparison_df)):
        if comparison_df['no_sig_diff_RRI_calc'].iloc[i] == 0:
            v = comparison_df['RRI'].iloc[i]
        else:
            v = 0
        no_sig_diff_RRI.append(v)
    comparison_df['No Sig Diff (RRI)'] = no_sig_diff_RRI

    #  Sig Diff Calcs Rate.
    sig_higher_RP10k = []
    for i in range(len(comparison_df)):
        if (comparison_df['Higher Lower'].iloc[i] == 'Higher') & (comparison_df['Stat Sig'].iloc[i] == 'Sig'):
            v = comparison_df['Rate per 10,000'].iloc[i]
        else:
            v = 0
        sig_higher_RP10k.append(v)
    comparison_df['Sig Higher RP10k'] = sig_higher_RP10k


    sig_lower_RP10k = []
    for i in range(len(comparison_df)):
        if (comparison_df['Higher Lower'].iloc[i] == 'Lower') & (comparison_df['Stat Sig'].iloc[i] == 'Sig'):
            v = comparison_df['Rate per 10,000'].iloc[i]
        else:
            v = 0
        sig_lower_RP10k.append(v)
    comparison_df['Sig Lower RP10k'] = sig_lower_RP10k

    comparison_df['no_sig_diff_RP10k_calc'] =( comparison_df['Sig Higher RP10k'] +comparison_df['Sig Lower RP10k']).to_list()
        
    no_sig_diff_RP10k = []
    for i in range(len(comparison_df)):
        if comparison_df['no_sig_diff_RP10k_calc'].iloc[i] == 0:
            v = comparison_df['Rate per 10,000'].iloc[i]
        else:
            v = 0
        no_sig_diff_RP10k.append(v)
    comparison_df['No Sig Diff RP10k'] = no_sig_diff_RP10k

    #  Sig Diff Calcs Percentage.
    sig_higher_PCT = []
    for i in range(len(comparison_df)):
        if (comparison_df['Higher Lower'].iloc[i] == 'Higher') & (comparison_df['Stat Sig'].iloc[i] == 'Sig'):
            v = comparison_df['Percentages'].iloc[i]
        else:
            v = 0
        sig_higher_PCT.append(v)
    comparison_df['Sig Higher PCT'] = sig_higher_PCT


    sig_lower_PCT = []
    for i in range(len(comparison_df)):
        if (comparison_df['Higher Lower'].iloc[i] == 'Lower') & (comparison_df['Stat Sig'].iloc[i] == 'Sig'):
            v = comparison_df['Percentages'].iloc[i]
        else:
            v = 0
        sig_lower_PCT.append(v)
    comparison_df['Sig Lower PCT'] = sig_lower_PCT

    comparison_df['no_sig_diff_PCT_calc'] =( comparison_df['Sig Higher PCT'] +comparison_df['Sig Lower PCT']).to_list()
        
    no_sig_diff_PCT = []
    for i in range(len(comparison_df)):
        if comparison_df['no_sig_diff_PCT_calc'].iloc[i] == 0:
            v = comparison_df['Percentages'].iloc[i]
        else:
            v = 0
        no_sig_diff_PCT.append(v)
    comparison_df['No Sig Diff PCT'] = no_sig_diff_PCT
    return comparison_df

data = file_ingress()


with st.sidebar:
    time_period = st.sidebar.selectbox('Select school year for school census population data', options=data['time_period'].unique())
    la_name = st.sidebar.selectbox('Select LA for school census population data', options=data['la_name'].unique())

with st.sidebar:
    comp_name = st.sidebar.text_input('Name of local subgroup for comparison (e.g. "CLA")', 
                                      value='sample data')
    st.sidebar.write('Input numbers of ethnic subgroups for comparison to LA numbers.')
    wb = st.sidebar.number_input('White British', value=60000)
    waob = st.sidebar.number_input('White any other background', value=3000)
    wgr = st.sidebar.number_input('White Gypsy Roma', value=300)
    wiri = st.sidebar.number_input('White Irish', value=250)
    wti = st.sidebar.number_input('White Traveller of Irish Heritage', value=100)
    aobg = st.sidebar.number_input('Asian any other Asian Background', value=600)
    abg = st.sidebar.number_input('Asian Bangladeshi', value=900)
    ach = st.sidebar.number_input('Asian Chinese', value=250)
    aind = st.sidebar.number_input('Asian Indian', value=350)
    apk = st.sidebar.number_input('Asian Pakistani', value=50)
    baob = st.sidebar.number_input('Black any other background', value=150)
    bafr = st.sidebar.number_input('Black African', value=500)
    bcbr = st.sidebar.number_input('Black Carribean', value=100)
    maob = st.sidebar.number_input('Mixed any other background', value=1500)
    mwa = st.sidebar.number_input('Mixed White Asian', value=750)
    mwba = st.sidebar.number_input('Mixed White and Black African', value=900)
    mwbc = st.sidebar.number_input('Mixed White and Black Carribean', value=750)
    aoeg = st.sidebar.number_input('Any other ethnic group', value=550)
    nobt = st.sidebar.number_input('Not obtained', value=0)
    ref = st.sidebar.number_input('Refused', value=0)
    unc = st.sidebar.number_input('Unclassified', value=1150)
    # white = st.sidebar.number_input('White', value=63650)
    # black = st.sidebar.number_input('Black', value=750)
    # asian = st.sidebar.number_input('Asian', value=2150)
    # mixed = st.sidebar.number_input('Mixed', value=3900)
    # other = st.sidebar.number_input('Other', value=550)
    # unctot = st.sidebar.number_input('Unclassified total', value=1150)

main_plot_title = f'Proportions of ethnic groups between {la_name} and {comp_name} in census period {time_period}'

ethnic_input = {
    'White_White_British' : wb,
    'White_Any_other_White_background' : waob,
    'White_Gypsy_Roma' : wgr,
    'White_Irish' : wiri,
    'White_Traveller_of_Irish_heritage' : wti,
    'Asian_Any_other_Asian_background' : aobg,
    'Asian_Bangladeshi' : abg,
    'Asian_Chinese' : ach,
    'Asian__indian' : aind,
    'Asian_Pakistani' : apk,
    'Black_Any_other_Black_background' : baob,
    'Black_Black_African' : bafr,
    'Black_Black_Caribbean' : bcbr,
    'Mixed_Any_other_Mixed_background' : maob,
    'Mixed_White_and_Asian' : mwa,
    'Mixed_White_and_Black_African' : mwba,
    'Mixed_White_and_Black_Caribbean' : mwbc,
    'Any_other_ethnic_group' : aoeg,
    'Not_obtained' : nobt,
    'Refused' : ref,
    'Unclassified' : unc,
    'White' : wb + waob + wgr + wiri + wti,
    'Asian' : aobg + abg + ach + aind + apk,
    'Black' : baob + bafr + bcbr,
    'Mixed' : maob + mwa + mwba + mwbc,
    'Other' : aoeg ,
    'Unclassified_total' : unc + nobt + ref,
}
# Excel test values for comparison to tool
# ethnic_input = {
#     'White_White_British' : 60000,
#     'White_Any_other_White_background' : 3000,
#     'White_Gypsy_Roma' : 300,
#     'White_Irish' :250,
#     'White_Traveller_of_Irish_heritage' : 80,
#     'Asian_Any_other_Asian_background' : 558,
#     'Asian_Bangladeshi' : 871,
#     'Asian_Chinese' : 244,
#     'Asian__indian' : 350,
#     'Asian_Pakistani' : 70,
#     'Black_Any_other_Black_background' : 120,
#     'Black_Black_African' : 500,
#     'Black_Black_Caribbean' : 90,
#     'Mixed_Any_other_Mixed_background' : 1500,
#     'Mixed_White_and_Asian' : 730,
#     'Mixed_White_and_Black_African' : 839,
#     'Mixed_White_and_Black_Caribbean' : 751,
#     'Any_other_ethnic_group' : 558,
#     'Not_obtained' : 0,
#     'Refused' : 0,
#     'Unclassified' : 1120,
#     'White' : 63630,
#     'Asian' : 2093,
#     'Black' : 710,
#     'Mixed' : 3820,
#     'Other' : 558,
#     'Unclassified_total' : 1120,
# }

InputList = [*ethnic_input.values()]

comparison_df = denominator(la_name, time_period)
comparison_df['numerator'] = InputList

#  Sums all non-White-British students from input data, slicing dataframe using correspoinding indexes and column.
total_minority_SG_numerator = comparison_df['numerator'].iloc[1:18].sum()

#  Sums all non-White-British students from census data, slicing dataframe using correspoinding indexes and column.
total_minority_SG_denominator = comparison_df['denominator'].iloc[1:18].sum()

#  Sums all known ethnicity students from input data, slicing dataframe using correspoinding indexes and column.
total_known_ethnicity_numerator = comparison_df['numerator'].iloc[21:26].sum()

#  Sums all known ethnicity students from census data, slicing dataframe using correspoinding indexes and column.
total_known_ethnicity_denominator = comparison_df['denominator'].iloc[21:26].sum()

comparison_df = calcs_for_plots()






tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['RRI subgroup',
                                            'RRI main groups', 
                                            'Rate per 10k subgroups', 
                                            'Rate per 10k main-groups',
                                            'Percentages subgroups',
                                            'Percentages main-groups'])
with tab1:
    #  Creates a pandas plot of the relevant colums of comparison_df to reproduce the relevant disproportionality tool chart.
    #  The table includes all the ethnic minority sub-groups and uses variables from the setup to name columns correctly.
    RRI_tab = comparison_df[['ethnicity', 'numerator', 'denominator', 'Rate per 10,000', 'RRI']].iloc[:21]
    RRI_tab.set_index('ethnicity')
    RRI_tab.rename(columns = {'numerator':'Input numbers', 'denominator':str(time_period) + ' Population'}, inplace=True)

    #  Sets the size of the table as otherwise pandas plot function returns an unreadably small table.
    plt.rcParams['figure.figsize'] = [20, 5]

    #  Plots the dataframe as a figure for sharing.
    ax = plt.subplot(111, frame_on=False) #  No visible frame.
    ax.xaxis.set_visible(False)  #  Hide the x axis.
    ax.yaxis.set_visible(False)  #  Hide the y axis.

    hue_diff_ = [] #  Empty list for the different colours.
    for i in range(len(comparison_df.iloc[:21])): #  Slices comparison_df to only select sub-groups.
        if comparison_df['Chart Titles'].iloc[i] == 'WBRI': #  Returns black if white british.
            hue = 'black'
        elif comparison_df['No Sig Diff (RRI)'].iloc[i] > 0:  #  elif means other colours will only be returned if the WBRI check was not True.
            hue = "grey"
        elif comparison_df['Sig Higher RRI'].iloc[i] == 0:
            hue = "blue"
        elif comparison_df['Sig Lower RRI'].iloc[i] == 0:
            hue = "red"

        hue_diff_.append(hue) #  Updates list with colours.

    #  Sets the palette for the seaborn graoh to follow, this is updated for later plots.
    sns.set_palette(sns.color_palette(hue_diff_)) 

    fig, ax = plt.subplots()
    #plt.rcParams['figure.figsize'] = [10, 5] #  Updates the figure size for the plot as the previous figure size was set for the table.
    ax = sns.barplot(data=comparison_df.iloc[:21], x='Chart Titles', y='RRI') #  Barplot with x and y values set.
    plt.xticks(rotation=90) #  Rotates x ticks for readability.
    ax.set_ylabel('RRI of each ethnic group') #  Sets titles for x, y, and plot.
    ax.set_xlabel('Red = Sig higher, Blue = Sig lower, Grey = No sig diff') #  Uses x titles to set key to keep the plot tight.
    ax.set_title(f'RRI of minority ethnic sub-groups in {comp_name} compared to White British in {la_name} in census period {time_period}')

    st.header('RRI subgroup charts')
    st.pyplot(ax.figure, use_container_width=True)
    st.table(RRI_tab)

with tab2:
    RRI_tab = comparison_df[['ethnicity', 'numerator', 'denominator', 'Rate per 10,000', 'RRI']].iloc[21:27]
    RRI_tab.set_index('ethnicity')
    RRI_tab.rename(columns = {'numerator':'Input numbers', 'denominator':str(time_period) + ' Population'}, inplace=True)

    plt.rcParams['figure.figsize'] = [20, 5]

    #  Plots the dataframe as a figure for sharing.
    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False) 

    plt.rcParams['figure.figsize'] = [5, 5]
    hue_diff_RRI = []
    for i in range(len(comparison_df.iloc[21:27])):
        if comparison_df['Chart Titles'].iloc[21 + i] == 'White':
            hue = "black"
        elif comparison_df['No Sig Diff (RRI)'].iloc[21 + i] > 0:
            hue = "grey"
        elif comparison_df['Sig Lower RRI'].iloc[21 + i] != 0:
            hue = "blue"
        elif comparison_df['Sig Higher RRI'].iloc[21 + i] != 0:
            hue = "red"
        hue_diff_RRI.append(hue)


    sns.set_palette(sns.color_palette(hue_diff_RRI))
    fig, ax = plt.subplots()

    ax = sns.barplot(data=comparison_df.iloc[21:27], x='Chart Titles', y='RRI')
    plt.xticks(rotation=90)
    ax.set_ylabel('RRI of each ethnic group')
    ax.set_xlabel('Red = Sig higher, Blue = Sig lower, Grey = No sig diff')
    ax.set_title(f'RRI of minority ethnic main groups in {comp_name} compared to White British in {la_name} in census period {time_period}')

    st.header('RRI main-group charts')
    st.pyplot(ax.figure, use_container_width=True)
    st.table(RRI_tab)

with tab3:
    RP10k_tab = comparison_df[['ethnicity', 'numerator', 'denominator', 'Rate per 10,000', 'Higher Lower']].iloc[:21]
    RP10k_tab.set_index('ethnicity')
    RP10k_tab.rename(columns = {'numerator':'Input numbers', 'denominator':str(time_period)+ ' Population'}, inplace=True)

    plt.rcParams['figure.figsize'] = [20, 5]

    #  plots the dataframe as a figure for sharing
    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False)  

    hue_diff_ = []
    for i in range(len(comparison_df.iloc[:21])):
        if comparison_df['No Sig Diff RP10k'].iloc[i] > 0:
            hue = "grey"
        elif comparison_df['Sig Higher RP10k'].iloc[i] == 0:
            hue = "blue"
        elif comparison_df['Sig Lower RP10k'].iloc[i] == 0:
            hue = "red"

        hue_diff_.append(hue)

    sns.set_palette(sns.color_palette(hue_diff_))

    plt.rcParams['figure.figsize'] = [10, 5]

    fig, ax = plt.subplots()
    ax = sns.barplot(data=comparison_df.iloc[:21], x='Chart Titles', y='Rate per 10,000')
    plt.xticks(rotation=90)
    ax.set_ylabel('Rater per 10,000')
    ax.set_xlabel('Red = Sig higher, Blue = Sig lower, Grey = No sig diff')
    ax.set_title(f'Rate per 10,000 population of ethnic sub-groups in {comp_name} compared to {la_name} in census period {time_period}')

    st.header('Rate per 10k subgroup charts')
    st.pyplot(ax.figure, use_container_width=True)
    st.table(RP10k_tab)

with tab4:
    RP10k_tab = comparison_df[['ethnicity', 'numerator', 'denominator', 'Rate per 10,000', 'Higher Lower']].iloc[21:27]
    RP10k_tab.set_index('ethnicity')
    RP10k_tab.rename(columns = {'numerator':'Input numbers', 'denominator':str(time_period) + ' Population'}, inplace=True)

    plt.rcParams['figure.figsize'] = [20, 5]


    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False)  

    plt.rcParams['figure.figsize'] = [5, 5]
    hue_diff_rp10k = []
    for i in range(len(comparison_df.iloc[21:27])):
        if comparison_df['Sig Lower RP10k'].iloc[21 + i] != 0:
            hue = "blue"       
        elif comparison_df['Sig Higher RP10k'].iloc[21 + i] != 0:
            hue = "red"
        else:
            hue = "grey"
        hue_diff_rp10k.append(hue)

    sns.set_palette(sns.color_palette(hue_diff_rp10k))
    fig, ax = plt.subplots()
    ax = sns.barplot(data=comparison_df.iloc[21:27], x='Chart Titles', y='Rate per 10,000')
    plt.xticks(rotation=90)
    ax.set_ylabel('Rate per 10,000')
    ax.set_xlabel('Red = Sig higher, Blue = Sig lower, Grey = No sig diff')
    ax.set_title(f'Rate per 10,000 of main ethnic groups in {comp_name} compared to {la_name} in census period {time_period}')

    st.header('Rate per 10k main-group charts')
    st.pyplot(ax.figure, use_container_width=True)
    st.table(RP10k_tab)

with tab5:
    PCTTab = comparison_df[['ethnicity', 'numerator', 'denominator', 'Percentages', 'Higher Lower']].iloc[:21]
    PCTTab.set_index('ethnicity')
    PCTTab.rename(columns = {'numerator':'Input numbers', 'denominator':str(time_period) + ' Population'}, inplace=True)

    plt.rcParams['figure.figsize'] = [20, 5]

    ax = plt.subplot(111, frame_on = False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False)  

    hue_diff_PCT = []
    for i in range(len(comparison_df.iloc[:21])):
        if comparison_df['Sig Higher PCT'].iloc[i] != 0:
            hue = "red"
        if comparison_df['No Sig Diff PCT'].iloc[i] != 0:
            hue = "grey"
        elif comparison_df['Sig Lower PCT'].iloc[i] != 0:
            hue = "blue"

        hue_diff_PCT.append(hue)

    sns.set_palette(sns.color_palette(hue_diff_PCT))

    plt.rcParams['figure.figsize'] = [10, 5]
    fig, ax = plt.subplots()
    ax = sns.barplot(data=comparison_df.iloc[:21], x='Chart Titles', y='Percentages')
    plt.xticks(rotation=90)
    ax.set_ylabel('Percentage of expected sub-ethnic group')
    ax.set_xlabel('Red = Sig higher, Blue = Sig lower, Grey = No sig diff')
    ax.set_title(f'Percentage of ethnic subgroups in {comp_name} compared to {la_name} in census period {time_period}')

    st.header('Percentages subgroup charts')
    st.pyplot(ax.figure, use_container_width=True)
    st.table(PCTTab)

with tab6:
    PCTTab = comparison_df[['ethnicity', 'numerator', 'denominator', 'Percentages', 'Higher Lower']].iloc[21:27]
    PCTTab.set_index('ethnicity')
    PCTTab.rename(columns = {'numerator':'Input numbers', 'denominator':str(time_period) + ' Population'}, inplace=True)

    plt.rcParams['figure.figsize'] = [20, 5]


    ax = plt.subplot(111, frame_on = False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False) 

    plt.rcParams['figure.figsize'] = [5, 5]
    hue_diff_PCT = []
    for i in range(len(comparison_df.iloc[21:27])):
        if comparison_df['Sig Lower PCT'].iloc[21 + i] != 0:
            hue = "blue"
        if comparison_df['No Sig Diff PCT'].iloc[21 + i] > 0:
            hue = "grey"
        elif comparison_df['Sig Higher PCT'].iloc[21 + i] != 0:
            hue = "red"
        hue_diff_PCT.append(hue)

    sns.set_palette(sns.color_palette(hue_diff_PCT))

    fig, ax = plt.subplots()
    ax = sns.barplot(data=comparison_df.iloc[21:27], x='Chart Titles', y='Percentages')
    plt.xticks(rotation=90)
    ax.set_ylabel('Percent')
    ax.set_xlabel('Red = Sig higher, Blue = Sig lower, Grey = No sig diff')
    ax.set_title(f'Percentage of main ethnic groups in {comp_name} compared to {la_name} in census period {time_period}')

    st.header('Percentages main-group charts')
    st.pyplot(ax.figure, use_container_width=True)
    st.table(PCTTab)





