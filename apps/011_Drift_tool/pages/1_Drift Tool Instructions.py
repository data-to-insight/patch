import streamlit as st

st.set_page_config(
    page_title="Instructions",
    page_icon="📄",
)

st.title("Data and usage instrucitons")
st.markdown(
    " To use this analysis first upload the relevant data using the widget in the sidebar. This analysis needs three CSVs of data, each with \
            Child/Person IDs and dates of Children's services provision. One CSV for Referrals, one for Child \
            Protection plans, and one for CLA dates. These need to be in the form that appears below: two columns, the first with IDs, the second with dates. \
            Column names do not matter. We recommend using around 20 years worth of data, or as much as is avaliable in order to get an accurate representaiton \
            of drift."
)

st.markdown(
    "[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/drift_upload_image.png?raw=true)]"
)

st.markdown(
    "The names of each CSV DO matter, however. The Referrals filename must include the word referrals, the Child Protection plans filename must include \
            either CP or Child Protection, and the CLA filename must include either CLA, LAC, or Looked After. Further, filenames for different files cannot \
            include the identifying text for other filenames, or this will confuse the file upload."
)

st.markdown(
    "Once the upload is completed, plots will appear in the main pane, with explanantions for each. Three sliders will also be generated in the sidebar. \
            The first sliders change two things: the first changes how many years worth of uploaded data is used to make drift calculations, the second \
            changes how many years worth of data is displayed in the plots. As is explained on the main page of the app, this view slider defaults to \
            showing the last five years worth of data, as earlier years are more likely to skew lower. The third slider only controls the histogram of \
            wait times and can be used to control which years data is displayed, This alsoi defaults to the last five years. All sliders are double ended \
            and, as such, can be used to select data from any period, although users will have to do some sense checking to determine if their slider choices \
            make sense, as weird things can happen if the time ranges chosen are dramatically different between sliders!"
)

st.title("Model explanation")
st.write(
    "The drift visualisations demonstrate how long it takes children to go between different stages of Children's Services provision. For instance, \
         how long children wait between a referral and a CIN or CP plan, how long children wait between CP plans and a CLA status, \
         and also larger periods such as how long children wait between initial referral and a CLA status. These statistics are presented in two ways, the first is histograms \
        demonstrating spread of wait times between different stages of Children's Services provision. This first visualisation is a useful way of \
        demonstrating what proportions of children are waiting what lengths of times for different levels of provision. The second, and most important visualisation, \
        presents bar and box plots demonstrating the wait times between different provisions starting in different years. This second set of visualisations \
        allows users to see how long children waited tro recieve different types of provision in any year, over a range of years. This can be used to help determine \
        if wait times are improving or not, and see trends in wait times over time"
)
st.markdown(
    "1) The data for the model builds over time, for the earliest years in the data set, there is not much data, as such, the further back you look in the \
            visualisationsthe less appropriate those years are as indications of drift. As such, in the plots which display wait time by end year, only the most \
            recent five years are displayed by default, but the earlier years are still included to demonstrate where the data for the model is drawn from and \
            can be seen by changing sliders or interacting with the plot susing the toolbar on mouse-over. \
            \n \n 2) The model calculates the time between referral and CP plan and referral and CLA  plan by assuming that the last referral before any CP plan \
            or CLA status is the one that lead to that plan or status, this means that for a small number of children who have a referral then CP plan and then CLA \
            status without another referral, the one referral will count as the most recent referral for both the CP plan and the CLA status. This is not necessarily \
            wrong for all cases, as the assumption can be made in some cases that if a child had a referral and was moved from CP plan to CLA status, they ought to \
            have had a CLA status initially, instead of a CP plan. As the number of times this happens is small, relative to the rest of the data, and it happens \
            every year, it it relatively balanced out across the model. \
            \n \n 3) A small number of data points are dropped in an effort to remove data points that the model would calculate incorrectly leading to large \
            false outliers - some children have a referral very shortly after a CP plan or CLA status is started which is due to some quirks in the way that childrens \
            services case management systems work, if those children then move from CLA status to CP plan  years later, the calculations would count that as having \
            waited years from that referral to the CP plan. To avoid this, children who have a referral within two weeks of a CP plan or CLA status are dropped from \
            the model to avoid these large outliers."
)
st.title("Behind the scenes")
st.markdown(
    "The model works by matching IDs across the different data tables and using that to find dates for levels of Childrens Services provision where \
         the lower level preceeded the higher level (so rows where a Referral was after a CLA, for instance, are removed). The data is also sorted and organised \
         so that only rows where the most recent escalation of CS provision is counted as the one that lead to a step up (so if a child has two referrals before \
         a CP plan, the most recent referral is considered to be the one that gave rise to the CP plan). This means that we are left only with rows where one \
         event has lead to an escalation, and the preceeding event closest in time to the later event is considered to be the causal event. This means that if a child has \
         two referrals and two CP plans, we will only be left with rows where the earlier referral is linked to the earlier CP plan, and the later referral is linked \
         to the later CP plan."
)
