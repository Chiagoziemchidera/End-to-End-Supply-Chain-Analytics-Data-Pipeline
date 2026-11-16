import getpass

import psycopg

password = getpass.getpass("Project PostgreSQL password: ")

query = """
SELECT
    shipping_mode,
    COUNT(*) AS order_items,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(*) FILTER (WHERE late_delivery_risk = 1) AS items_flagged_risk,
    COUNT(*) FILTER (
        WHERE actual_shipping_days > scheduled_shipping_days
    ) AS items_actually_late,
    ROUND(AVG(actual_shipping_days), 2) AS avg_actual_days,
    ROUND(AVG(scheduled_shipping_days), 2) AS avg_scheduled_days
FROM fact_order_items
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
        cursor.execute(query)
        results = cursor.fetchall()

print(
    "Shipping mode | Items | Orders | Risk flags | Actually late | "
    "Avg actual days | Avg scheduled days"
)
for row in results:
    print(row)