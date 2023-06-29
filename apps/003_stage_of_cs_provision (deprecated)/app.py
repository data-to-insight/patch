import streamlit as st


import pandas as pd
import matplotlib.pyplot as plt

uploaded_files = st.file_uploader("Load all of your files here:", accept_multiple_files=True)
if uploaded_files:
    loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}
    contacts = loaded_files['Ofsted List 1 - Initial Contacts - with date parameters.csv']
    early_help = loaded_files['Ofsted List 2 - Early Help Assessments - with date parameters.csv']
    referrals = loaded_files['Ofsted List 3 - Referrals - with date parameters.csv']
    assessments = loaded_files['Ofsted List 4 - Assessments - with date parameters.csv']
    section_47 = loaded_files['Ofsted List 5 - Section 47 Enquiries - with date parameters.csv']
    child_in_need = loaded_files['Ofsted List 6 - Children In Need - with date parameters.csv']
    child_protection = loaded_files['Ofsted List 7 - Child Protection Plans - with date parameters.csv']

    class ContactToStage():
        def __init__(self, input_form, contacts=contacts):
            self.contacts = contacts
            self.input_form = input_form
            self.merged = self.stage_merge()
            self.contact_to_stage = len(self.merged['PersonID'].unique())
            
        def stage_merge(self):
            return pd.merge(self.contacts, self.input_form, how='inner', on='PersonID')

    unique_children = len(contacts['PersonID'].unique())

    contact_to_ref = ContactToStage(referrals).contact_to_stage
    contact_to_early_help = ContactToStage(early_help).contact_to_stage
    contact_to_assessments = ContactToStage(assessments).contact_to_stage
    contact_to_s47 = ContactToStage(section_47).contact_to_stage
    contact_to_cin = ContactToStage(child_in_need).contact_to_stage
    contact_to_cp = ContactToStage(child_protection).contact_to_stage

    df = pd.DataFrame({'Category':['Total Children', 
                                'Contacts with referrals', 
                                'Contacts with early help',
                                'Contacts assessed',
                                'Contacts with s47 cases',
                                'Contacts with CIN cases',
                                'Contacts with CP cases'],
                    'Value':[unique_children,
                                contact_to_ref,
                                contact_to_early_help,
                                contact_to_assessments,
                                contact_to_s47,
                                contact_to_cin,
                                contact_to_cp
                                ]}
                    )

    fig = plt.figure()

    plt.bar(df['Category'], height = df['Value'])

    plt.xticks(rotation=90)
    plt.title('Children with contacts who had cases opened with different stages of provision '
            'in an Annex A reporting Period (including children who did not recieve that level of provision)',
            loc='center',
            wrap=True)
    plt.xlabel('Stage of CS provision')
    plt.ylabel('Number of children')
    st.pyplot(fig)
