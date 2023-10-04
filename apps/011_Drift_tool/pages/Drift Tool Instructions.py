import streamlit as st

st.set_page_config(
    page_title="Instructions",
    page_icon="📄",
)

st.title("Data and usage instrucitons") 
st.markdown(" To use this analysis first upload the relevant data using the widget in the sidebar. This analysis needs three CSVs of data, each with \
            Child/Person IDs and dates of Children's services provision. One CSV for Referrals, one for Child \
            Protection plans, and one for CLA dates. These need to be in the form that appears below: two columns, the first with IDs, the second with dates. \
            Column names do not matter. We recommend using around 20 years worth of data, or as much as is avaliable in order to get an accurate representaiton \
            of drift.")

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/drift_upload_image.png?raw=true)]")

st.markdown("The names of each CSV DO matter, however. The Referrals filename must include the word referrals, the Child Protection plans filename must include \
            either CP or Child Protection, and the CLA filename must include either CLA, LAC, or Looked After. Further, filenames for different files cannot \
            include the identifying text for other filenames, or this will confuse the file upload.")

st.markdown("Once the upload is completed, plots will appear in the main pane, with explanantions for each. Three sliders will also be generated in the sidebar. \
            The first sliders change two things: the first changes how many years worth of uploaded data is used to make drift calculations, the second \
            changes how many years worth of data is displayed in the plots. As is explained on the main page of the app, this view slider defaults to \
            showing the last five years worth of data, as earlier years are more likely to skew lower. The third slider only controls the histogram of \
            wait times and can be used to control which years data is displayed, This alsoi defaults to the last five years. All sliders are double ended \
            and, as such, can be used to select data from any period, although users will have to do some sense checking to determine if their slider choices \
            make sense, as weird things can happen if the time ranges chosen are dramatically different between sliders!")

st.title("Model explanation")
st.write("")


