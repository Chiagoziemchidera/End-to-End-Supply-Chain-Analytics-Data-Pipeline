import getpass

import psycopg

password = getpass.getpass("Project PostgreSQL password: ")

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="supply_chain_dev",
    user="supply_admin",
    password=password,
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                COUNT(*) AS order_items,
                COUNT(DISTINCT order_id) AS orders,
                COUNT(*) FILTER (WHERE late_delivery_risk = 1) AS items_flagged_late_risk,
                ROUND(AVG(actual_shipping_days), 2) AS avg_actual_shipping_days,
                ROUND(AVG(scheduled_shipping_days), 2) AS avg_scheduled_shipping_days
            FROM fact_order_items;
        """)
        summary = cursor.fetchone()

print("Order items | Orders | Items flagged late risk | Avg actual days | Avg scheduled days")
print(summary)