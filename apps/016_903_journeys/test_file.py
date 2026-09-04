import pandas as pd

df = pd.DataFrame({"Lens": ["1", "222", "33333", "44", "55"]})

print(df[df["Lens"].str.len() < 3])
