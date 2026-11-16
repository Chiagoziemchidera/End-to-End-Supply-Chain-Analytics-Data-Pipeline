import getpass

import psycopg

password = getpass.getpass("Project PostgreSQL password: ")

create_table_sql = """
CREATE TABLE IF NOT EXISTS fact_orders AS
SELECT
    order_id,
    MIN(order_datetime) AS order_datetime,
    MAX(shipping_datetime) AS shipping_datetime,
    MAX(actual_shipping_days) AS actual_shipping_days,
    MAX(scheduled_shipping_days) AS scheduled_shipping_days,
    MAX(late_delivery_risk) AS late_delivery_risk,
    MAX(delivery_status) AS delivery_status,
    MAX(order_status) AS order_status,
    MAX(shipping_mode) AS shipping_mode,
    MAX(market) AS market,
    MAX(order_region) AS order_region
FROM fact_order_items
GROUP BY order_id;
"""

summary_sql = """
SELECT
    shipping_mode,
    COUNT(*) AS orders,
    COUNT(*) FILTER (WHERE late_delivery_risk = 1) AS orders_flagged_risk,
    COUNT(*) FILTER (
        WHERE actual_shipping_days > scheduled_shipping_days
    ) AS orders_actually_late,
    ROUND(AVG(actual_shipping_days::NUMERIC), 2) AS avg_actual_days,
    ROUND(AVG(scheduled_shipping_days::NUMERIC), 2) AS avg_scheduled_days
FROM fact_orders
GROUP BY shipping_mode
ORDER BY shipping_mode;
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="supply_chain_dev",
    user="supply_admin",
    password=password,
) as connection:
    with connection.cursor() as cursor:
        cursor.execute(create_table_sql)
        cursor.execute(summary_sql)
        results = cursor.fetchall()

print("Order-level delivery summary")
print(
    "Shipping mode | Orders | Risk flagged | Actually late | "
    "Avg actual days | Avg scheduled days"
)
for row in results:
    print(row)