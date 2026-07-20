import sqlite3
import pandas as pd

conn = sqlite3.connect("sales.db")

# 1. Total revenue by year
q1 = pd.read_sql("""
    SELECT strftime('%Y', "Order Date") AS year,
           ROUND(SUM(Sales), 2) AS total_revenue
    FROM orders
    GROUP BY year
    ORDER BY year
""", conn)
print("=== Revenue by Year ===")
print(q1)

# 2. Top 10 products by revenue
q2 = pd.read_sql("""
    SELECT "Product Name",
           ROUND(SUM(Sales), 2) AS revenue
    FROM orders
    GROUP BY "Product Name"
    ORDER BY revenue DESC
    LIMIT 10
""", conn)
print("\n=== Top 10 Products ===")
print(q2)

# 3. Sales by region
q3 = pd.read_sql("""
    SELECT Region,
           ROUND(SUM(Sales), 2) AS revenue,
           COUNT(DISTINCT "Order ID") AS total_orders
    FROM orders
    GROUP BY Region
    ORDER BY revenue DESC
""", conn)
print("\n=== Sales by Region ===")
print(q3)

# 4. Sales by category and sub-category
q4 = pd.read_sql("""
    SELECT Category, "Sub-Category",
           ROUND(SUM(Sales), 2) AS revenue
    FROM orders
    GROUP BY Category, "Sub-Category"
    ORDER BY revenue DESC
""", conn)
print("\n=== Sales by Category ===")
print(q4)

# 5. Monthly revenue trend
q5 = pd.read_sql("""
    SELECT strftime('%Y-%m', "Order Date") AS month,
           ROUND(SUM(Sales), 2) AS revenue
    FROM orders
    GROUP BY month
    ORDER BY month
""", conn)
print("\n=== Monthly Trend ===")
print(q5)

conn.close()