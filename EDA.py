import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns

df = pd.read_csv("data/train.csv", encoding="latin1")

# clean dates
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True)
df["days_to_ship"] = (df["Ship Date"] - df["Order Date"]).dt.days

# check data quality
print("=== Null Values ===")
print(df.isnull().sum())
print("\n=== Data Types ===")
print(df.dtypes)
print("\n=== Basic Stats ===")
print(df.describe())