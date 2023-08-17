import streamlit as st
import pandas as pd
import thefuzz
from thefuzz import process, fuzz

name_town = pd.DataFrame([
    {'restaurant':'McDonalds','town':'Lewes'},
    {'restaurant':'The Lamb','town':'Gora'},
    {'restaurant':'Capadocia','town':'Leszno'},
    {'restaurant':'Chicken Shack','town':'London'},
    {'restaurant':'Pierogarnia','town':'Chiang Mai'},
    {'restaurant':'Thai Square','town':'Bangkok'},
     {'restaurant':'The Boomerang','town':'Melbourne'}
])

name_cuisine = pd.DataFrame([
  {'restaurant':'Mc Donalds','cuisine':'fusion'},
    {'restaurant':'The Lambs','cuisine':'mixed'},
    {'restaurant':'Capaddocia','cuisine':'kebab'},
    {'restaurant':'Chicken Shed','cuisine':'fish'},
    {'restaurant':'Pierogi','cuisine':'Thai'},
    {'restaurant':'Thai Town','cuisine':'Chinese'},
    {'restaurant':'Frankfurter','cuisine':'German'}

])

m1 = []
m2 = []

# # st.table(name_town)
# # st.table(name_cuisine)

# # restaurant_df = name_town.merge(name_cuisine,how='left',on='restaurant')
# # st.table(restaurant_df)

# # two ways of converting values from column to list
# names_1 = list(name_town['restaurant'])
# names_2 = name_cuisine['restaurant'].to_list()

# st.write(names_1)
# st.write(names_2)

# # define an empty list
# m1 = []

# for i in names_1:
#     m1.append(process.extract(i,names_2,limit=2))
# name_town['matches'] = m1


# st.table(name_town)

# p = []
# m2 = []
# threshold = 59

# for j in name_town['matches']:
#     for k in j:
#         if k[1] >= threshold:
#             p.append(k[0])
#     m2.append(','.join(str(i) for i in p))
#     p=[]

# name_town['matches'] = m2

# new_restaurants = name_town.merge(name_cuisine,
#                                   how='left',
#                                   left_on = 'matches',
#                                   right_on = 'restaurant',
#                                   )

# # axis specifies that I'm dropping columns
# new_restaurants.drop(['restaurant_y','matches'],axis=1,inplace=True)
# new_restaurants.rename(columns={'restaurant_x':'restaurant'},inplace=True)


# st.table(new_restaurants)

m1 = []
m2 = []
p = []

names_1 = list(name_town['restaurant'])
names_2 = name_cuisine['restaurant'].to_list()

for i in names_1:
    m1.append(process.extractOne(i,names_2,scorer=fuzz.ratio))
name_town['matches'] = m1

for j in name_town['matches']:
    if j[1]>60:
        p.append(j[0])

    m2.append(",".join(p))
    p=[]

name_town['matches'] = m2

st.table(name_town)

new_restaurants = name_town.merge(name_cuisine,
                                  how = 'left',
                                  left_on = 'matches',
                                  right_on = 'restaurant'

)

st.table(new_restaurants)