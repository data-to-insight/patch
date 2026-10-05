import pandas as pd
import numpy as np


# S = "Started to be looked-after"
# L = "Change of legal status only"
# P = "Change of placement and carer(s) only"
# T = "Change of placement (but same carer(s)) only"
# B = "Change of legal status and placement and carer(s) at the same time"
# U = "Change of legal status and change of placement (but same carer(s)) at the same time"

# df['next_time'] = (df.apply(lambda x: next((z for (y, z) in zip(df['price'], df['time'])
#                                     if y > x['price'] if z > x['time']), None), axis=1))


def eop_date_finder(row, enriched_df):
    df = enriched_df[
        (enriched_df["CHILD"] == row["CHILD"])]

    max_dec = df["DEC_dt"].max()
    df["prev_dec"] = df["DEC_dt"].shift(1)
    
    df = df[df["DECOM_dt"] > row["DECOM_dt"]
        ].reset_index()



    this_place_dec = next((dec for (rne, dec) in zip(df["RNE"], df["prev_dec"]) if rne in ["P", "T", "B", "U"]), "FINAL PLACEMENT")

    if (this_place_dec == "FINAL PLACEMENT") | (pd.isnull(this_place_dec)):
        this_place_dec = max_dec

    return this_place_dec
    

enriched_df = pd.DataFrame({
                    "CHILD":[1,1,1,1,1,2],
                    "DECOM_dt": ["1", "2", "3", "4", "5","1"],
                    "DEC_dt": ["1", "2", "3", "4", "5","2"],
                    "RNE":["S", "L", "P", "P", "L","S"]})



enriched_df["End of current placement"] = enriched_df.apply(eop_date_finder, args=(enriched_df,), axis=1)

print(enriched_df)



