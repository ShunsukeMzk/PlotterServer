import pandas as pd

df = pd.read_csv("executions_fx_btc.tsv", sep="\t")

df["base_price"] = df.iloc[0]["price"]
df["price"] = df["price"] - df["base_price"]
# print(df)
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%dT%H:%M:%S.%fZ")
df = df.set_index("date")


df = df["price"].resample("S").mean()
df = df.resample("S").interpolate()

dfs = []
for i in range(1, 101):
    _df = df.rolling(i).mean()
    _df.name = str(i)
    dfs.append(_df)

df = pd.concat(dfs, axis=1)
df = df.reset_index()
df = df.drop("date", axis=1)
# print(df)

for index, row in df.iterrows():
    for i, value in enumerate(row.values):
        if not pd.isna(value):
            x = index / 10
            y = value / 1_000
            z = i / 10
            print(x, y, z, sep="\t")

    if index == 300:
        break