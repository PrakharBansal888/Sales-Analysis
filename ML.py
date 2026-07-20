import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("data/train.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True)
df["days_to_ship"] = (df["Ship Date"] - df["Order Date"]).dt.days

# encode categorical columns so sklearn can use them
le = LabelEncoder()
df["Region_enc"]   = le.fit_transform(df["Region"])
df["Category_enc"] = le.fit_transform(df["Category"])
df["Segment_enc"]  = le.fit_transform(df["Segment"])

# predict Sales from these features
features = ["days_to_ship", "Region_enc", "Category_enc", "Segment_enc"]
df_model = df[features + ["Sales"]].dropna()

X = df_model[features]
y = df_model["Sales"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
preds = model.predict(X_test)

print("=== Model Results ===")
print(f"R²  : {r2_score(y_test, preds):.3f}")
print(f"MAE : {mean_absolute_error(y_test, preds):.2f}")
print("\nWhat this means:")
print("R² close to 1.0 = model predicts well")
print("MAE = average error in Sales prediction (in dollars)")