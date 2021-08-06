import pandas as pd
import datetime

df = pd.read_csv("executions_fx_btc.tsv", sep="\t")
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%dT%H:%M:%S.%fZ")
df = df.set_index("date")


df = df["price"].resample("S").mean()
df = df.resample("S").interpolate()

dfs = []
for i in range(1, 11):
    _df = df.rolling(i).mean()
    _df.name = str(i)
    dfs.append(_df)

df = pd.concat(dfs, axis=1)
print(df)

# for i, row in enumerate(df.iterrows()):
#     print(i, row[1])