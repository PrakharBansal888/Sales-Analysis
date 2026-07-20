import pandas as pd
import sqlite3

df = pd.read_csv("train.csv", encoding="latin1")
conn = sqlite3.connect("sales.db")
df.to_sql("orders", conn, if_exists="replace", index=False)
print("Done. Rows:", len(df))

print(df.columns.tolist())