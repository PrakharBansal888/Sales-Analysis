"""
SQLQueries.py — 12 analytical SQL queries demonstrating joins, CTEs, and
window functions against the normalised sales.db schema.

Tables used:
  customers(customer_id, customer_name, segment, country, city, state,
            postal_code, region)
  products(product_id, category, sub_category, product_name)
  orders(order_id, order_date, ship_date, ship_mode, customer_id, days_to_ship)
  order_items(row_id, order_id, product_id, sales)
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect("sales.db")


def run(title, sql):
    """Execute a query and print the result with a header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)
    result = pd.read_sql(sql, conn)
    print(result.to_string(index=False))
    return result


# ─────────────────────────────────────────────────────────────
# 1. Total revenue by year (JOIN order_items -> orders)
# ─────────────────────────────────────────────────────────────
run("Q1: Total Revenue by Year", """
    SELECT strftime('%Y', o.order_date) AS year,
           ROUND(SUM(oi.sales), 2)      AS total_revenue
      FROM order_items oi
      JOIN orders o ON oi.order_id = o.order_id
     GROUP BY year
     ORDER BY year
""")

# ─────────────────────────────────────────────────────────────
# 2. Top 10 products by revenue (JOIN products)
# ─────────────────────────────────────────────────────────────
run("Q2: Top 10 Products by Revenue", """
    SELECT p.product_name,
           p.category,
           ROUND(SUM(oi.sales), 2) AS revenue
      FROM order_items oi
      JOIN products p ON oi.product_id = p.product_id
     GROUP BY p.product_name, p.category
     ORDER BY revenue DESC
     LIMIT 10
""")

# ─────────────────────────────────────────────────────────────
# 3. Sales by region with order count (3-table JOIN)
# ─────────────────────────────────────────────────────────────
run("Q3: Sales by Region", """
    SELECT c.region,
           ROUND(SUM(oi.sales), 2)         AS revenue,
           COUNT(DISTINCT o.order_id)       AS total_orders
      FROM order_items oi
      JOIN orders    o ON oi.order_id    = o.order_id
      JOIN customers c ON o.customer_id  = c.customer_id
     GROUP BY c.region
     ORDER BY revenue DESC
""")

# ─────────────────────────────────────────────────────────────
# 4. Sales by category and sub-category
# ─────────────────────────────────────────────────────────────
run("Q4: Sales by Category & Sub-Category", """
    SELECT p.category,
           p.sub_category,
           ROUND(SUM(oi.sales), 2) AS revenue
      FROM order_items oi
      JOIN products p ON oi.product_id = p.product_id
     GROUP BY p.category, p.sub_category
     ORDER BY revenue DESC
""")

# ─────────────────────────────────────────────────────────────
# 5. Monthly revenue trend
# ─────────────────────────────────────────────────────────────
run("Q5: Monthly Revenue Trend", """
    SELECT strftime('%Y-%m', o.order_date) AS month,
           ROUND(SUM(oi.sales), 2)         AS revenue
      FROM order_items oi
      JOIN orders o ON oi.order_id = o.order_id
     GROUP BY month
     ORDER BY month
""")

# ─────────────────────────────────────────────────────────────
# 6. MoM Growth (CTE + LAG window function)
# ─────────────────────────────────────────────────────────────
run("Q6: Month-over-Month Revenue Growth", """
    WITH monthly AS (
        SELECT strftime('%Y-%m', o.order_date) AS ym,
               SUM(oi.sales) AS rev
          FROM order_items oi
          JOIN orders o ON oi.order_id = o.order_id
         GROUP BY ym
    )
    SELECT ym,
           ROUND(rev, 2) AS revenue,
           ROUND(100.0 * (rev - LAG(rev) OVER (ORDER BY ym))
                        / LAG(rev) OVER (ORDER BY ym), 1) AS mom_pct
      FROM monthly
""")

# ─────────────────────────────────────────────────────────────
# 7. Top 3 products per category (CTE + ROW_NUMBER)
# ─────────────────────────────────────────────────────────────
run("Q7: Top 3 Products per Category (ROW_NUMBER)", """
    WITH ranked AS (
        SELECT p.category,
               p.product_name,
               ROUND(SUM(oi.sales), 2) AS revenue,
               ROW_NUMBER() OVER (
                   PARTITION BY p.category
                   ORDER BY SUM(oi.sales) DESC
               ) AS rn
          FROM order_items oi
          JOIN products p ON oi.product_id = p.product_id
         GROUP BY p.category, p.product_name
    )
    SELECT category, product_name, revenue, rn
      FROM ranked
     WHERE rn <= 3
""")

# ─────────────────────────────────────────────────────────────
# 8. Pareto — customers driving 80 % of revenue (cumulative SUM)
# ─────────────────────────────────────────────────────────────
run("Q8: Pareto Analysis (Cumulative Revenue Share)", """
    WITH cust AS (
        SELECT o.customer_id,
               SUM(oi.sales) AS rev
          FROM order_items oi
          JOIN orders o ON oi.order_id = o.order_id
         GROUP BY o.customer_id
    )
    SELECT customer_id,
           ROUND(rev, 2) AS revenue,
           ROUND(100.0 * SUM(rev) OVER (ORDER BY rev DESC)
                        / SUM(rev) OVER (), 1) AS cum_pct
      FROM cust
""")

# ─────────────────────────────────────────────────────────────
# 9. YTD Running Total per Year (SUM window, PARTITION BY year)
# ─────────────────────────────────────────────────────────────
run("Q9: YTD Running Total per Year", """
    WITH monthly AS (
        SELECT strftime('%Y', o.order_date) AS yr,
               CAST(strftime('%m', o.order_date) AS INTEGER) AS mo,
               SUM(oi.sales) AS rev
          FROM order_items oi
          JOIN orders o ON oi.order_id = o.order_id
         GROUP BY yr, mo
    )
    SELECT yr, mo,
           ROUND(rev, 2)   AS month_revenue,
           ROUND(SUM(rev) OVER (
               PARTITION BY yr ORDER BY mo
           ), 2)            AS ytd_revenue
      FROM monthly
     ORDER BY yr, mo
""")

# ─────────────────────────────────────────────────────────────
# 10. YoY Growth by Category (LAG with 12-month offset)
# ─────────────────────────────────────────────────────────────
run("Q10: YoY Growth by Category", """
    WITH yearly AS (
        SELECT p.category,
               strftime('%Y', o.order_date) AS yr,
               SUM(oi.sales) AS rev
          FROM order_items oi
          JOIN orders   o ON oi.order_id   = o.order_id
          JOIN products p ON oi.product_id = p.product_id
         GROUP BY p.category, yr
    )
    SELECT category, yr,
           ROUND(rev, 2)   AS revenue,
           ROUND(100.0 * (rev - LAG(rev) OVER (PARTITION BY category ORDER BY yr))
                        / LAG(rev) OVER (PARTITION BY category ORDER BY yr), 1) AS yoy_pct
      FROM yearly
     ORDER BY category, yr
""")

# ─────────────────────────────────────────────────────────────
# 11. RFM Segmentation (NTILE for Recency / Frequency / Monetary)
# ─────────────────────────────────────────────────────────────
run("Q11: RFM Segmentation (NTILE)", """
    WITH rfm_raw AS (
        SELECT o.customer_id,
               CAST(julianday('2018-12-31') - julianday(MAX(o.order_date)) AS INTEGER)
                   AS recency_days,
               COUNT(DISTINCT o.order_id) AS frequency,
               ROUND(SUM(oi.sales), 2)   AS monetary
          FROM order_items oi
          JOIN orders o ON oi.order_id = o.order_id
         GROUP BY o.customer_id
    ),
    rfm_scored AS (
        SELECT customer_id, recency_days, frequency, monetary,
               NTILE(4) OVER (ORDER BY recency_days ASC)  AS r_score,
               NTILE(4) OVER (ORDER BY frequency    DESC) AS f_score,
               NTILE(4) OVER (ORDER BY monetary     DESC) AS m_score
          FROM rfm_raw
    )
    SELECT customer_id, recency_days, frequency, monetary,
           r_score, f_score, m_score,
           r_score + f_score + m_score AS rfm_total,
           CASE
               WHEN r_score + f_score + m_score >= 10 THEN 'Champion'
               WHEN r_score + f_score + m_score >= 7  THEN 'Loyal'
               WHEN r_score + f_score + m_score >= 4  THEN 'At Risk'
               ELSE 'Lost'
           END AS segment
      FROM rfm_scored
     ORDER BY rfm_total DESC
""")

# ─────────────────────────────────────────────────────────────
# 12. Cohort Retention (first-order month → months active)
# ─────────────────────────────────────────────────────────────
run("Q12: Cohort Retention", """
    WITH first_order AS (
        SELECT customer_id,
               MIN(order_date) AS first_date,
               strftime('%Y-%m', MIN(order_date)) AS cohort
          FROM orders
         GROUP BY customer_id
    ),
    activity AS (
        SELECT o.customer_id,
               fo.cohort,
               (  (CAST(strftime('%Y', o.order_date) AS INTEGER)
                  - CAST(strftime('%Y', fo.first_date) AS INTEGER)) * 12
                + CAST(strftime('%m', o.order_date) AS INTEGER)
                - CAST(strftime('%m', fo.first_date) AS INTEGER)
               ) AS month_offset
          FROM orders o
          JOIN first_order fo ON o.customer_id = fo.customer_id
    )
    SELECT cohort,
           month_offset,
           COUNT(DISTINCT customer_id) AS active_customers
      FROM activity
     GROUP BY cohort, month_offset
     ORDER BY cohort, month_offset
""")


conn.close()
print("\n\nAll 12 queries executed successfully.")