import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
#from pyodide.http import open_url


st.title('test')


names = ['assessment_nfa',
        'cin_start',
        'cpp_start',
        'lac_start',
        'last_status_assessment_authorised',
        'last_status_assessment_nfa',
        'last_status_cin_end',
        'last_status_cin_start',
        'last_status_contact',
        'last_status_cpp_end',
        'last_status_cpp_start',
        'last_status_early_help_assessment_end',
        'last_status_icpc',
        'last_status_lac_end',
        'last_status_lac_start',
        'last_status_s47',
        'referral',
        'referral_nfa',
        ]
labels = ['Assessment: No further action', 
        'Child in need plan', 
        'Child protection plan', 
        'Looked after child', 
        'End: Assessment', 
        'End: No further action', 
        'End: Child in need plan ends', 
        'End: Child in need plan', 
        'End: Contact', 
        'End: Child protection plan ends',
        'End: Child protection plan', 
        'End: Early help ends?', 
        'End: Initial child protection conference', 
        'End: Looked after status ends', 
        'End: Looked after child', 
        'End: Section 47 assessment', 
        'Referral',
        'Referral: No further action',
        ]

labs = pd.DataFrame(list(zip(names, labels)),
                            columns=['name', 'lab'])


journey_events = {'contact': {'contacts':'contact_dttm'},
        'early_help_assessment_start': {'early_help_assessments':'eha_startdate'},
        'early_help_assessment_end': {'early_help_assessments':'eha_completeddate'},
        'referral': {'referrals':'refrl_start_dttm'},
        'assessment_start': {'assessments':'assessmentstartdate'},
        'assessment_authorised':{'assessments':'dateofauthorisation'},
        's47': {'section_47': 'startdate'},
        'icpc': {'section_47': 'cpdate'},
        'cin_start': {'children_in_need': 'cinstartdate'},
        'cin_end': {'children_in_need': 'cinclosuredate'},
        'cpp_start': {'child_protection_plans': 'start_dttm2'},
        'cpp_end': {'child_protection_plans': 'end_dttm2'},
        'lac_start': {'children_in_care': 'startdaterecentcareepisode'},
        'lac_end': {'children_in_care': 'dateceasedlac'}}

types_to_var = ["referral", "assessment_start", "cpp_start", "lac_start", "assessment_authorised", "cin_start"]    

#lookups = open_url("https://github.com/data-to-insight/patch/blob/main/apps/006_sankey_processing/annex_a_lookups.pickle")
@st.cache_data
def file_upload_fn(uploaded_files):
    if len(uploaded_files) > 1:
        loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}
        data_dict = {}
        for file in loaded_files.items():
            if ('list 1' in file[0].lower()) | ('contacts' in file[0].lower()):
                data_dict['contacts'] = file[1]
            if ('list 2' in file[0].lower()) | ('help' in file[0].lower()):
                data_dict['early_help_assessments'] = file[1]
            if ('list 3' in file[0].lower()) | ('referral' in file[0].lower()):
                data_dict['referrals'] = file[1]
            if ('list 4' in file[0].lower()) | ('assess' in file[0].lower()) & ~('early' in file[0].lower()):
                data_dict['assessments'] = file[1]
            if ('list 5' in file[0].lower()) | ('47' in file[0].lower()):
                data_dict['section_47'] = file[1]
            if ('list 6' in file[0].lower()) | (('need' in file[0].lower()) & ('child' in file[0].lower())):
                data_dict['children_in_need'] = file[1]
                print(data_dict['children_in_need'])
            if ('list 7' in file[0].lower()) | ('protection' in file[0].lower()) | ('cpp' in file[0].lower()):
                data_dict['child_protection_plans'] = file[1]
            if ('list 8' in file[0].lower()) | ('care' in file[0].lower()) & ~('leaver' in file[0].lower()):
                data_dict['children_in_care'] = file[1]
            if ('list 9' in file[0].lower()) | ('leaver' in file[0].lower()):
                data_dict['care_leavers'] = file[1]

    else:
        loaded_file = pd.read_excel(uploaded_files[0], sheet_name=None)
        data_dict = {}
        keys_list = list(loaded_file.keys())
        for key in keys_list:
            if ('list 1' in key.lower()) | ('contacts' in key.lower()):
                data_dict['contacts'] = loaded_file[key]
            if ('list 2' in key.lower()) | ('help' in key.lower()):
                    data_dict['early_help_assessments'] = loaded_file[key]
            if ('list 3' in key.lower()) | ('referral' in key.lower()):
                    data_dict['referrals'] = loaded_file[key]
            if ('list 4' in key.lower()) | ('assess' in key.lower()) & ~('early' in key.lower()):
                    data_dict['assessments'] = loaded_file[key]
            if ('list 5' in key.lower()) | ('47' in key.lower()):
                    data_dict['section_47'] = loaded_file[key]
            if ('list 6' in key.lower()) | ('need' in key.lower()) | ('cin' in key.lower()):
                    data_dict['children_in_need'] = loaded_file[key]
            if ('list 7' in key.lower()) | ('protection' in key.lower()) | ('cpp' in key.lower()):
                    data_dict['child_protection_plans'] = loaded_file[key]
            if ('list 8' in key.lower()) | ('care' in key.lower()) & ~('leaver' in key.lower()):
                    data_dict['children_in_care'] = loaded_file[key]
            if ('list 9' in key.lower()) | ('leaver' in key.lower()):
                    data_dict['care_leavers'] = loaded_file[key]


    data_dict['contacts'].rename(columns={data_dict['contacts'].columns[0]: 'child unique id', 
                                         data_dict['contacts'].columns[1]: 'gender',
                                         data_dict['contacts'].columns[2]: 'ethnicity',
                                         data_dict['contacts'].columns[5]: 'contact_dttm'},
                                         inplace=True) 
    data_dict['early_help_assessments'].rename(columns={data_dict['early_help_assessments'].columns[0]: 'child unique id', 
                                         data_dict['early_help_assessments'].columns[1]: 'gender',
                                         data_dict['early_help_assessments'].columns[2]: 'ethnicity',
                                         data_dict['early_help_assessments'].columns[3]: 'dob',
                                         data_dict['early_help_assessments'].columns[5]: 'eha_startdate',
                                         data_dict['early_help_assessments'].columns[6]: 'eha_completeddate'},
                                         inplace=True)    
    data_dict['referrals'].rename(columns={data_dict['referrals'].columns[0]: 'child unique id', 
                                         data_dict['referrals'].columns[1]: 'gender',
                                         data_dict['referrals'].columns[2]: 'ethnicity',
                                         data_dict['referrals'].columns[5]: 'refrl_start_dttm',
                                         data_dict['referrals'].columns[6]: 'referral source',
                                         data_dict['referrals'].columns[7]: 'referral nfa?',
                                         data_dict['referrals'].columns[8]: 'number of referrals in last 12 months'},
                                         inplace=True)  
    data_dict['assessments'].rename(columns={data_dict['assessments'].columns[0]: 'child unique id', 
                                         data_dict['assessments'].columns[1]: 'gender',
                                         data_dict['assessments'].columns[2]: 'ethnicity',
                                         data_dict['assessments'].columns[6]: 'assessmentstartdate',
                                         data_dict['assessments'].columns[8]: 'dateofauthorisation'},
                                         inplace=True)  
                                         #got here
    data_dict['section_47'].rename(columns={data_dict['section_47'].columns[0]: 'child unique id', 
                                         data_dict['section_47'].columns[1]: 'gender',
                                         data_dict['section_47'].columns[2]: 'ethnicity',
                                         data_dict['section_47'].columns[6]: 'startdate',
                                         data_dict['section_47'].columns[8]: 'cpdate'},
                                         inplace=True)
    data_dict['children_in_need'].rename(columns={data_dict['children_in_need'].columns[0]: 'child unique id', 
                                         data_dict['children_in_need'].columns[1]: 'gender',
                                         data_dict['children_in_need'].columns[2]: 'ethnicity',
                                         data_dict['children_in_need'].columns[6]: 'cinstartdate',
                                         data_dict['children_in_need'].columns[9]: 'cinclosuredate',
                                         data_dict['children_in_need'].columns[11]: 'case status'},
                                         inplace=True)    
    data_dict['child_protection_plans'].rename(columns={data_dict['child_protection_plans'].columns[0]: 'child unique id', 
                                         data_dict['child_protection_plans'].columns[1]: 'gender',
                                         data_dict['child_protection_plans'].columns[2]: 'ethnicity',
                                         data_dict['child_protection_plans'].columns[6]: 'start_dttm2',
                                         data_dict['child_protection_plans'].columns[12]: 'end_dttm2'},
                                         inplace=True)  
    data_dict['children_in_care'].rename(columns={data_dict['children_in_care'].columns[0]: 'child unique id', 
                                         data_dict['children_in_care'].columns[1]: 'gender',
                                         data_dict['children_in_care'].columns[2]: 'ethnicity',
                                         data_dict['children_in_care'].columns[7]: 'startdaterecentcareepisode',
                                         data_dict['children_in_care'].columns[20]: 'dateceasedlac'},
                                         inplace=True)      
    data_dict['care_leavers'].rename(columns={data_dict['care_leavers'].columns[0]: 'child unique id', 
                                         data_dict['care_leavers'].columns[1]: 'gender',
                                         data_dict['care_leavers'].columns[2]: 'ethnicity'},
                                         inplace=True) 
    return data_dict



@st.cache_data
def build_annexarecord(data, events=journey_events):
    '''
    Creates a flat file with three columns:
    1) child unique id
    2) date
    3) Type
    Based on events in Annex A lists defined in the events argument
    '''

    # Create empty dataframe in which we'll drop our events
    df_list = []

    # Loop over our dictionary to populate the log
    for event in events:
        contents = events[event]
        list_number = list(contents.keys())[0]
        date_column = contents[list_number]
       
        # Load Annex A list
        df = data[list_number] 
        df = df.loc[:,~df.columns.duplicated()]
        # Get date column information
        df.columns = [col.lower().strip() for col in df.columns]

        date_column_lower = date_column.lower()
        if date_column_lower in df.columns:
            df = df[df[date_column_lower].notnull()] # extract dates that aren't null
            df['type'] = event
            df['date'] = df[date_column_lower]
            #df = df[['type', 'date', 'child unique id', 'ethnicity', 'gender']] #<- this would limit 
            df_list.append(df)
        else:
            st.write('>>>>>  Could not find column {} in {}'.format(date_column, list_number))
    
    # Pull all events into a unique datafrane annexarecord
    annexarecord = pd.concat(df_list, sort=False)
    
    # Clean annexarecord
    # Define categories to be able to sort events
    ordered_categories = ["contact",
                      "referral",
                      "early_help_assessment_start",
                      "early_help_assessment_end",
                      "assessment_start",
                      "assessment_authorised",
                      "s47",
                      "icpc",
                      "cin_start",
                      "cin_end",
                      "cpp_start",
                      "cpp_end",
                      "lac_start",
                      "lac_end"]
    annexarecord.type = annexarecord.type.astype('category')
    #st.write(annexarecord.astype('object'))
    annexarecord.type.cat.set_categories([c for c in ordered_categories if c in annexarecord.type.unique()], inplace=True, ordered=True)
    # Ensure dates are in the correct format
    annexarecord.date = pd.to_datetime(annexarecord.date)
    
    # Sort data so that it is by child, then date 
    annexarecord = annexarecord.sort_values(by=['child unique id', 'date'])

    return annexarecord

@st.cache_data
def flag_types(df, t):
    df = df.sort_values(by = ["id", "date", "event_ord"])
    df[("is_" +  t)] = (df["type"] == t)
    df[("id_cum_" +  t)] = df[("is_" +  t)].astype("int").groupby(df["id"]).transform("cumsum")
    df[("id_num_" +  t)] = df[("is_" +  t)].astype("int").groupby(df["id"]).transform("max")
    return df

# CREATE A FUNCTION TO LIMIT DATA 
@st.cache_data
def clean_up_NFAs(dta):
    dta = dta.sort_values(by = ["ref_id", "date", "event_ord"])
    # REFERRAL NFAS 
    # we know referrals are going to be the first obs within each referral id
    if dta.iloc[0]["referral nfa?"] == "Yes": 
        # if the last event is a contact, save thelast row and the referral 
        print("referral NFA")
        if dta.iloc[-1]["type"] == "contact":
            dta_first = dta.iloc[[0]]
            dta_last  = dta.iloc[[-1]]
            dta = dta_first.append(dta_last)
        # if it's not a contact, then just keep the referral
        else:
            dta = dta.iloc[[0]]
        # create a new row for referral nfa 
        nfa_row = dta.iloc[[0]]
        nfa_row["type"] = "referral_nfa"
        # change the date to be one day after the referral (**need to check it is always earlier than the contact**)
        nfa_row["date"] = nfa_row["date"] + datetime.timedelta(days=1) 
        return dta.append(nfa_row)
    
    # replace NAs with blanks strings to solve type errors later
    dta["was the child assessed as requiring la children’s social care support?"] = dta["was the child assessed as requiring la children’s social care support?"].fillna('')
    # save the list of index numbers where the type is assessment start 
    asmt_index = np.where(dta["type"] == "assessment_start")
    
    # confirm there is a row with assessment start, then go in there
    # if no assessment, currently just moving along  
    if len(asmt_index[0]) > 0:
        # extract first index where there is an assessment (should be 1, but making sure)
        fa_i = asmt_index[0][0]
        # if they were assessment nfa...
        if "CS Close Case" in dta.iloc[fa_i]["was the child assessed as requiring la children’s social care support?"]: # -> make this more generic
            print("First assessment was NFA")
            # if the last event is a contact, save that the first row (referral), assessment row (should be 1), and contact 
            if dta.iloc[-1]["type"] == "contact":
                dta = dta.iloc[[0, fa_i, -1]]
            # if it's not a contact, then just keep the referral and assessment
            else:
                dta = dta.iloc[[0, fa_i]]
            
            # create a new row for referral nfa 
            ass_nfa_row = dta.iloc[[fa_i]]
            ass_nfa_row["type"] = "assessment_nfa"
            # change the date to be one day after the assessment (need to check it is always earlier than the contact)
            ass_nfa_row["date"] = ass_nfa_row["date"] + datetime.timedelta(days=1) 
            return dta.append(ass_nfa_row)
   
    return dta
@st.cache_data
def drop_fake_cin(dta):
    # create cumulative flag

    dta = dta.sort_values(by = ["id", "date"])
    #extract indices of eligible outcomes 
    cl = np.where((dta["type"] == "cpp_start") | (dta["type"] == "lac_start")) 
    #cl = np.where(dta["type"] in ["cpp_start", "lac_start"]) why doesn't this work? 
    dta["check"] = 500
    if len(cl[0]) > 0:
            # extract first place
            cli = cl[0][0]
            #extract index of cin plan start
            cini = np.where(dta["type"] == "cin_start")[0][0]

            # store the number of days between the two 
            num_days = (dta.loc[dta.index[cli], "date"] - dta.loc[dta.index[cini], "date"]).days
            dta["check"] =  num_days
            if num_days < days_real_cin :
                # drop first cin start row 
                dta = dta.drop(dta.index[cini])
                # drop cin end 
                ce = np.where(dta["type"] == "cin_end")
                if len(ce[0]) > 0:
                    d = ce[0][0]
                    dta = dta.drop(dta.index[d])
            
    return dta


def flag_last_status(dta): 
        excl = "assessment_start"
    
        dta["last_status"] = 0
        dta = dta.sort_values(by = ["id", "date"])
        #extract indices of eligible outcomes 
        fo_index = np.where(dta["type"] != excl)
        # make sure there is at least some outcome
        if len(fo_index[0]) > 0:
            # extract index of last row 
            last_in = fo_index[0][-1]
            dta.loc[dta.index[last_in], "last_status"] = 1 

        return dta
    
# FIRST STATUS 
def flag_first_status(dta): 
        
        ffs = ["cpp_start", "lac_start", "cin_start", "assessment_nfa", "referral_nfa", "early_help_assessment_start"]
    
        dta["first_status"] = 0
        dta = dta.sort_values(by = ["id", "date"])
        #extract indices of eligible outcomes 
        ffs_ind =  np.isin(dta["type"], ffs)
        p2 = np.where(ffs_ind == True)
        # make sure there is at least some outcome
        if len(p2[0]) > 0:
            #extract index of last tow 
            ind = p2[0][0]
            dta.loc[dta.index[ind], "first_status"] = 1 

        return dta

#NEED TO REPLICATE LAST ROW IF IT IS THE SAME FOR BOTH 
def dup_last_row(dta):

    if (dta.iloc[-1]["last_status"] == 1) & (dta.iloc[-1]["first_status"] == 1): 
        last_row = dta.iloc[[-1]]
        return dta.append(last_row)
    return dta 

def journey_fy(data, filtering_vars = ["gender", "ethnicity"]): 
    val = "last_status_" + data.iloc[-1]["type"]

    data.loc[data.index[-1], "type"] = val
    # limit variables 
    basic_vars = ["ref_id", "type", "date"]
    keep_vars = basic_vars + filtering_vars # need to fix this so it can be empty
    data = data[keep_vars]
    
    # create a new variable that has the next type of event chronologically. I.e., the end point of the journey
    # sort
    data = data.sort_values(by = ["date"])
    data["target"] = data["type"].shift(-1)
    
    # rename type to source 
    data = data.rename(columns = {"type":"source"})
    
    # drop last row within a group because it holds no new information 
    data.drop(index=data.index[-1], 
        axis=0, 
        inplace=True)

    #rename type to source 
    return data

uploaded_files = st.file_uploader('Upload annex a here as set of csvs or single excel file:', accept_multiple_files=True)
if uploaded_files:
    st.write('got here')
    data_dict = file_upload_fn(uploaded_files)
    # if len(uploaded_files) > 1:
    #     loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}
    #     data_dict = {}
    #     for file in loaded_files.items():
    #         if ('list 1' in file[0].lower()) | ('contacts' in file[0].lower()):
    #             data_dict['contacts'] = file[1]
    #         if ('list 2' in file[0].lower()) | ('help' in file[0].lower()):
    #             data_dict['early_help_assessments'] = file[1]
    #         if ('list 3' in file[0].lower()) | ('referral' in file[0].lower()):
    #             data_dict['referrals'] = file[1]
    #         if ('list 4' in file[0].lower()) | ('assess' in file[0].lower()) & ~('early' in file[0].lower()):
    #             data_dict['assessments'] = file[1]
    #         if ('list 5' in file[0].lower()) | ('47' in file[0].lower()):
    #             data_dict['section_47'] = file[1]
    #         if ('list 6' in file[0].lower()) | (('need' in file[0].lower()) & ('child' in file[0].lower())):
    #             data_dict['children_in_need'] = file[1]
    #             print(data_dict['children_in_need'])
    #         if ('list 7' in file[0].lower()) | ('protection' in file[0].lower()) | ('cpp' in file[0].lower()):
    #             data_dict['child_protection_plans'] = file[1]
    #         if ('list 8' in file[0].lower()) | ('care' in file[0].lower()) & ~('leaver' in file[0].lower()):
    #             data_dict['children_in_care'] = file[1]
    #         if ('list 9' in file[0].lower()) | ('leaver' in file[0].lower()):
    #             data_dict['care_leavers'] = file[1]

    # else:
    #     loaded_file = pd.read_excel(uploaded_files[0], sheet_name=None)
    #     data_dict = {}
    #     keys_list = list(loaded_file.keys())
    #     for key in keys_list:
    #         if ('list 1' in key.lower()) | ('contacts' in key.lower()):
    #             data_dict['contacts'] = loaded_file[key]
    #         if ('list 2' in key.lower()) | ('help' in key.lower()):
    #                 data_dict['early_help_assessments'] = loaded_file[key]
    #         if ('list 3' in key.lower()) | ('referral' in key.lower()):
    #                 data_dict['referrals'] = loaded_file[key]
    #         if ('list 4' in key.lower()) | ('assess' in key.lower()) & ~('early' in key.lower()):
    #                 data_dict['assessments'] = loaded_file[key]
    #         if ('list 5' in key.lower()) | ('47' in key.lower()):
    #                 data_dict['section_47'] = loaded_file[key]
    #         if ('list 6' in key.lower()) | ('need' in key.lower()) | ('cin' in key.lower()):
    #                 data_dict['children_in_need'] = loaded_file[key]
    #         if ('list 7' in key.lower()) | ('protection' in key.lower()) | ('cpp' in key.lower()):
    #                 data_dict['child_protection_plans'] = loaded_file[key]
    #         if ('list 8' in key.lower()) | ('care' in key.lower()) & ~('leaver' in key.lower()):
    #                 data_dict['children_in_care'] = loaded_file[key]
    #         if ('list 9' in key.lower()) | ('leaver' in key.lower()):
    #                 data_dict['care_leavers'] = loaded_file[key]


    # data_dict['contacts'].rename(columns={data_dict['contacts'].columns[0]: 'child unique id', 
    #                                      data_dict['contacts'].columns[1]: 'gender',
    #                                      data_dict['contacts'].columns[2]: 'ethnicity',
    #                                      data_dict['contacts'].columns[5]: 'contact_dttm'},
    #                                      inplace=True) 
    # data_dict['early_help_assessments'].rename(columns={data_dict['early_help_assessments'].columns[0]: 'child unique id', 
    #                                      data_dict['early_help_assessments'].columns[1]: 'gender',
    #                                      data_dict['early_help_assessments'].columns[2]: 'ethnicity',
    #                                      data_dict['early_help_assessments'].columns[3]: 'dob',
    #                                      data_dict['early_help_assessments'].columns[5]: 'eha_startdate',
    #                                      data_dict['early_help_assessments'].columns[6]: 'eha_completeddate'},
    #                                      inplace=True)    
    # data_dict['referrals'].rename(columns={data_dict['referrals'].columns[0]: 'child unique id', 
    #                                      data_dict['referrals'].columns[1]: 'gender',
    #                                      data_dict['referrals'].columns[2]: 'ethnicity',
    #                                      data_dict['referrals'].columns[5]: 'refrl_start_dttm',
    #                                      data_dict['referrals'].columns[6]: 'referral source',
    #                                      data_dict['referrals'].columns[7]: 'referral nfa?',
    #                                      data_dict['referrals'].columns[8]: 'number of referrals in last 12 months'},
    #                                      inplace=True)  
    # data_dict['assessments'].rename(columns={data_dict['assessments'].columns[0]: 'child unique id', 
    #                                      data_dict['assessments'].columns[1]: 'gender',
    #                                      data_dict['assessments'].columns[2]: 'ethnicity',
    #                                      data_dict['assessments'].columns[6]: 'assessmentstartdate',
    #                                      data_dict['assessments'].columns[8]: 'dateofauthorisation'},
    #                                      inplace=True)  
    #                                      #got here
    # data_dict['section_47'].rename(columns={data_dict['section_47'].columns[0]: 'child unique id', 
    #                                      data_dict['section_47'].columns[1]: 'gender',
    #                                      data_dict['section_47'].columns[2]: 'ethnicity',
    #                                      data_dict['section_47'].columns[6]: 'startdate',
    #                                      data_dict['section_47'].columns[8]: 'cpdate'},
    #                                      inplace=True)
    # data_dict['children_in_need'].rename(columns={data_dict['children_in_need'].columns[0]: 'child unique id', 
    #                                      data_dict['children_in_need'].columns[1]: 'gender',
    #                                      data_dict['children_in_need'].columns[2]: 'ethnicity',
    #                                      data_dict['children_in_need'].columns[6]: 'cinstartdate',
    #                                      data_dict['children_in_need'].columns[9]: 'cinclosuredate',
    #                                      data_dict['children_in_need'].columns[11]: 'case status'},
    #                                      inplace=True)    
    # data_dict['child_protection_plans'].rename(columns={data_dict['child_protection_plans'].columns[0]: 'child unique id', 
    #                                      data_dict['child_protection_plans'].columns[1]: 'gender',
    #                                      data_dict['child_protection_plans'].columns[2]: 'ethnicity',
    #                                      data_dict['child_protection_plans'].columns[6]: 'start_dttm2',
    #                                      data_dict['child_protection_plans'].columns[12]: 'end_dttm2'},
    #                                      inplace=True)  
    # data_dict['children_in_care'].rename(columns={data_dict['children_in_care'].columns[0]: 'child unique id', 
    #                                      data_dict['children_in_care'].columns[1]: 'gender',
    #                                      data_dict['children_in_care'].columns[2]: 'ethnicity',
    #                                      data_dict['children_in_care'].columns[7]: 'startdaterecentcareepisode',
    #                                      data_dict['children_in_care'].columns[20]: 'dateceasedlac'},
    #                                      inplace=True)      
    # data_dict['care_leavers'].rename(columns={data_dict['care_leavers'].columns[0]: 'child unique id', 
    #                                      data_dict['care_leavers'].columns[1]: 'gender',
    #                                      data_dict['care_leavers'].columns[2]: 'ethnicity'},
    #                                      inplace=True) 


    all_data = build_annexarecord(data_dict)

    # Renaming necessary column headers


    # extract the first type of event an individual has 
    first_event = all_data.sort_values("date").groupby('child unique id').first()
    df =all_data.rename(columns = {"child unique id":"id"})

    # create a variable we can use to sort when the date is all the same 
    event_order = ["contact", "referral", "assessment_start", "assessment_authorised", "cin_start"]
    n = 1 
    # set to 100 for everthing else 
    df["event_ord"] = 100
        
    for t in event_order:
        df.loc[df["type"] == t, "event_ord"] = n
        n = n+1 
    df = df.sort_values(by = ['id', 'date', 'event_ord'])

    tt = df[['id','date', 'type','event_ord']]

    for t in types_to_var: 
        print(t)
        df = flag_types(df, t)

    # limit to those who have a referral
    df = df[df["id_num_referral"] >= 1]

    # drop things before the first referral 
    df = df[df["id_cum_referral"] >= 1]

    #create new ID for each child-referral sequence 
    df["ref_id"] = df["id"].astype("str") +  "_" +  df["id_cum_referral"].astype("str")


    ################################
    # LIMIT THE SAMPLE TO THOSE WITH 45 DAYS BETWEEN REFERRAL AND FINAL DATE IN DATA SET 
    ################################   

    #going to spread by referral ID 
    referral_vars = ["ethnicity", "age", "gender", "number of referrals in last 12 months", "referral source"]
    core_vars = ["ref_id", "date"] + referral_vars
    ref_dta = df[df["type"] == "referral"]
    ref_dta = ref_dta[core_vars]

    ref_dta =ref_dta.rename(columns = {"number of referrals in last 12 months":"num_ref",  
                                    "referral source" : "ref_source", 
                                    "date" : "ref_date"})

    ref_dta['num_ref'] = ref_dta['num_ref'].astype('float')

    #MERGE FILTERING VARIABLES BACK ON 
    df = df.drop(referral_vars, axis=1) 
    df = df.merge(ref_dta, left_on = "ref_id", right_on = "ref_id", validate ="many_to_one")


    last_date = df["date"].max()
    print(last_date)
    df["time_diff"] = last_date - df["ref_date"]
    df["time_diff"] = df["time_diff"].dt.days
    # limit to those who have at least 45 days following referral
    df = df[df["time_diff"] >= 45]

    # Clean up data with clean up nfa function
    df = df.groupby("ref_id").apply(clean_up_NFAs).sort_values(by=['id', 'date']).reset_index(drop=True)
 
    #################################
    #Filters
    #################################

    #gender options
    with st.sidebar:
        gender_option = st.sidebar.multiselect(
        'What gender options category would you like?',
        options=(df['gender'].unique()), default=(df['gender'].unique()))
    df = df[df["gender"].isin(gender_option)] 
    
    #source options
    with st.sidebar:
        source_option = st.sidebar.multiselect(
        'What referral source options category would you like?',
        options=(df['ref_source'].unique()), default=(df['ref_source'].unique()))
    df = df[df["ref_source"].isin(source_option)] 

    # Ethnicity options
    with st.sidebar:
        ethnicity_option = st.sidebar.multiselect(
        'What ethnicity options category would you like?',
        options=(df['ethnicity'].unique()), default=(df['ethnicity'].unique()))
    df = df[df["ethnicity"].isin(ethnicity_option)] 

    # number of referrals in the year
    with st.sidebar:
            num_of_refs = st.sidebar.slider('Number of referrals within 12 months',
                            min_value=0,
                            max_value=int(df['num_ref'].max()),
                            value=[0,int(df['num_ref'].max())])
    df = df[(df['num_ref'].astype(int) >= num_of_refs[0]) & (df['num_ref'].astype(int) <= num_of_refs[1])]

    with st.sidebar:
            ages = st.sidebar.slider('Age range of children',
                            min_value=0,
                            max_value=int(df['age'].max()),
                            value=[0,int(df['age'].max())])
    df = df[(df['age'].astype(int) >= ages[0]) & (df['age'].astype(int) <= ages[1])]




    ################################################
    # SET UP LOGIC FOR SKIPPING CIN PLAN
    ################################################
    # below is the number of days of lag time after cin start date and CPP/LAC before we consider it a different plan step 
    days_real_cin = 70 
    # variable for is cin or is lac 
    df['is_cpp_lac'] = ((df["is_cpp_start"] == 1) | (df['is_lac_start'] == 1)).astype("int")
    df['is_cin_cpp_lac'] = ((df["is_cpp_start"] == 1) | (df['is_lac_start'] == 1) | (df['is_cin_start'] == 1)).astype("int")
    df = df.groupby('ref_id').apply(drop_fake_cin).reset_index(drop=True)


    df = df.groupby('ref_id').apply(flag_last_status).reset_index(drop=True)
    df = df.groupby('ref_id').apply(flag_first_status).reset_index(drop=True)

    # LIMIT OBSERVATIONS
    check = df[["id", "ref_id", "date", "type", "event_ord", "last_status", "first_status", "case status", "check", "ethnicity", "gender"]].sort_values(by = ['id', 'date'])
    df_lim = check[(df["type"] == "referral") | (df["last_status"] == 1) | (df["first_status"] == 1)]
    df_lim = df_lim.groupby('ref_id').apply(dup_last_row).reset_index(drop=True)

    #####################################
    # STEP 2 - RESHAPING - this code is actually okay except do we want to duplicate the row if first status = final status
    #######################################
    
    journey = df_lim.groupby('ref_id').apply(journey_fy).reset_index(drop=True)
    journey = journey[["target", "source", "ref_id"]]

    # collapse data frame 
    df = journey.groupby(['target', 'source']).count().reset_index()

    #####################################
    # Sankey
    #####################################
    df = df.merge(labs, left_on = "target", right_on = "name")
    df = df.rename(columns = {'lab':'target_lab'})
    df = df.merge(labs, left_on = "source", right_on = "name")
    df = df.rename(columns = {'lab':'source_lab'})
    df = df.drop(columns = ["name_x", "target", "source", "name_y"])
    df = df.rename(columns = {'target_lab':'target','source_lab':'source'})
    source_string = df["source"].values.tolist()
    target_string = df["target"].values.tolist()

    # create index values for source and target 
    combo = source_string + target_string
    all_options = np.unique(combo)
    options_to_merge = pd.DataFrame(all_options, columns = ["options"])
    options_to_merge.reset_index(inplace=True)
    options_to_merge = options_to_merge.rename(columns = {'index':'sankey_index'})
    labels = options_to_merge["options"].values.tolist()


    # first merge the index values for source
    df_ind = df.merge(options_to_merge, left_on = "source", right_on = "options")
    # rename and drop so we can re-merge
    df_ind = df_ind.rename(columns = {"sankey_index":"source_index"})
    df_ind = df_ind.drop(columns = "options")
    # merge the index values for target 
    df_ind = df_ind.merge(options_to_merge, left_on = "target", right_on = "options")
    df_ind = df_ind.rename(columns = {"sankey_index":"target_index"})

    #turn columns into arrays so we can create a dictionary for the Sankey input
    source = df_ind["source_index"].values.tolist()
    target = df_ind["target_index"].values.tolist()
    value  = df_ind["ref_id"].values.tolist()

    link = dict(source = source, target = target, value = value)
    node = dict(label = labels, pad = 15, thickness = 5)

    
    data = go.Sankey(link = link, node = node)
    fig = go.Figure(data)
    st.plotly_chart(fig)


    st.write(df.astype(object))
    st.write('got here')
