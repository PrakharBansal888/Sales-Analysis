import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/train.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True)
df["days_to_ship"] = (df["Ship Date"] - df["Order Date"]).dt.days

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Monthly revenue trend
monthly = df.groupby(df["Order Date"].dt.to_period("M"))["Sales"].sum()
monthly.plot(ax=axes[0,0], title="Monthly Revenue Trend", color="steelblue")
axes[0,0].set_xlabel("Month")
axes[0,0].set_ylabel("Sales")

# 2. Sales by category
df.groupby("Category")["Sales"].sum().plot(
    kind="bar", ax=axes[0,1], title="Sales by Category", color="coral")
axes[0,1].set_xlabel("Category")
axes[0,1].set_ylabel("Sales")

# 3. Sales by region
df.groupby("Region")["Sales"].sum().plot(
    kind="bar", ax=axes[1,0], title="Sales by Region", color="mediumseagreen")
axes[1,0].set_xlabel("Region")
axes[1,0].set_ylabel("Sales")

# 4. Days to ship distribution
axes[1,1].hist(df["days_to_ship"].dropna(), bins=20, color="mediumpurple")
axes[1,1].set_title("Days to Ship Distribution")
axes[1,1].set_xlabel("Days")
axes[1,1].set_ylabel("Count")

plt.tight_layout()
plt.savefig("eda_charts.png", dpi=150)
plt.show()
print("Charts saved as eda_charts.png")