import streamlit as st
import pandas as pd
from thefuzz import process,fuzz

nba_teams = pd.DataFrame([
{'Team':'Boston','Star':'Tatum'},
{'Team':'Dallas','Star':'Luka'},
{'Team':'Denver','Star':'Jokic'},
{'Team':'Chicago','Star':'LaVine'},
{'Team':'Golden State','Star':'Curry'},
{'Team':'Phoenix','Star':'Durant'},

]
)

nba_needs = pd.DataFrame([
{'Team':'Bosston','Need':'continuity'},
{'Team':'Dalas Mavs','Need':'depth'},
{'Team':'Den','Need':'health'},
{'Team':'Chi','Need':'youth'},
{'Team':'GS','Need':'stability'},
{'Team':'Phonix','Need':'more players'},

]
)

teams_1 = list(nba_teams['Team'])
teams_2 = list(nba_needs['Team'])


m1=[]
m2=[]
p=[]

for i in teams_1:
    m1.append(process.extractOne(i,teams_2,scorer=fuzz.ratio))

for j in m1:
    if j[1]>=50:
        p.append(j[0])
    m2.append(",".join(p))
    p=[]

nba_teams['matches'] = m2
st.table(nba_teams)

nba_total = nba_teams.merge(nba_needs,
                            how='left',
                            left_on = 'matches',
                            right_on = 'Team'
                            
)

st.table(nba_total)