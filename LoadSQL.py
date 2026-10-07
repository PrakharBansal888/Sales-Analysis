"""
LoadSQL.py — Load Superstore CSV into a normalised SQLite schema.

Creates four tables:
  customers  (customer_id, customer_name, segment, country, city, state, postal_code, region)
  products   (product_id, category, sub_category, product_name)
  orders     (order_id, order_date, ship_date, ship_mode, customer_id, days_to_ship)
  order_items(row_id PK, order_id FK, product_id FK, sales)

Dates are converted from dd/mm/yyyy → ISO YYYY-MM-DD so SQLite date
functions (strftime, DATE, etc.) work correctly.
"""

import pandas as pd
import sqlite3
from datetime import datetime


def parse_dmy(date_str):
    """Convert dd/mm/yyyy string to ISO YYYY-MM-DD string."""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def main():
    # ── 1. Read raw CSV ──────────────────────────────────────────────
    df = pd.read_csv("data/train.csv", encoding="latin1")
    print(f"Loaded {len(df)} rows from train.csv")
    print(f"Columns: {df.columns.tolist()}\n")

    # ── 2. Convert dates to ISO format ───────────────────────────────
    df["Order Date"] = df["Order Date"].apply(parse_dmy)
    df["Ship Date"]  = df["Ship Date"].apply(parse_dmy)

    # Derive days_to_ship as integer
    df["days_to_ship"] = (
        pd.to_datetime(df["Ship Date"]) - pd.to_datetime(df["Order Date"])
    ).dt.days

    # ── 3. Build normalised DataFrames ───────────────────────────────
    # Customers — one row per customer
    customers = (
        df[["Customer ID", "Customer Name", "Segment",
            "Country", "City", "State", "Postal Code", "Region"]]
        .drop_duplicates(subset=["Customer ID"])
        .rename(columns={
            "Customer ID":   "customer_id",
            "Customer Name": "customer_name",
            "Segment":       "segment",
            "Country":       "country",
            "City":          "city",
            "State":         "state",
            "Postal Code":   "postal_code",
            "Region":        "region",
        })
    )

    # Products — one row per product
    products = (
        df[["Product ID", "Category", "Sub-Category", "Product Name"]]
        .drop_duplicates(subset=["Product ID"])
        .rename(columns={
            "Product ID":   "product_id",
            "Category":     "category",
            "Sub-Category": "sub_category",
            "Product Name": "product_name",
        })
    )

    # Orders — one row per order (an order can have many items)
    orders = (
        df[["Order ID", "Order Date", "Ship Date",
            "Ship Mode", "Customer ID", "days_to_ship"]]
        .drop_duplicates(subset=["Order ID"])
        .rename(columns={
            "Order ID":    "order_id",
            "Order Date":  "order_date",
            "Ship Date":   "ship_date",
            "Ship Mode":   "ship_mode",
            "Customer ID": "customer_id",
        })
    )

    # Order Items — every row in the CSV is an item-level record
    order_items = (
        df[["Row ID", "Order ID", "Product ID", "Sales"]]
        .rename(columns={
            "Row ID":     "row_id",
            "Order ID":   "order_id",
            "Product ID": "product_id",
            "Sales":      "sales",
        })
    )

    # ── 4. Write to SQLite ───────────────────────────────────────────
    conn = sqlite3.connect("sales.db")

    customers.to_sql("customers",   conn, if_exists="replace", index=False)
    products.to_sql("products",     conn, if_exists="replace", index=False)
    orders.to_sql("orders",         conn, if_exists="replace", index=False)
    order_items.to_sql("order_items", conn, if_exists="replace", index=False)

    # ── 5. Verify ────────────────────────────────────────────────────
    for tbl in ["customers", "products", "orders", "order_items"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl:14s}  ->  {count:>6,} rows")

    conn.close()
    print("\nDone. Database: sales.db")


if __name__ == "__main__":
    main()