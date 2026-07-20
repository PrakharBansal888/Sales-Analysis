import pandas as pd

df = pd.read_csv("data/train.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True)
df["days_to_ship"] = (df["Ship Date"] - df["Order Date"]).dt.days

# add useful columns for Power BI
df["year"]          = df["Order Date"].dt.year
df["month"]         = df["Order Date"].dt.month
df["month_name"]    = df["Order Date"].dt.strftime("%b")
df["quarter"]       = df["Order Date"].dt.quarter

df.to_csv("superstore_clean.csv", index=False)
print("Exported successfully. Shape:", df.shape)
print(df.head())