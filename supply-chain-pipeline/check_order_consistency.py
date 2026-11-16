import getpass

import psycopg

password = getpass.getpass("Project PostgreSQL password: ")

query = """
SELECT
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE actual_days_versions > 1
           OR scheduled_days_versions > 1
           OR shipping_mode_versions > 1
           OR delivery_status_versions > 1
           OR risk_flag_versions > 1
    ) AS orders_with_inconsistent_shipping_details
FROM (
    SELECT
        order_id,
        COUNT(DISTINCT actual_shipping_days) AS actual_days_versions,
        COUNT(DISTINCT scheduled_shipping_days) AS scheduled_days_versions,
        COUNT(DISTINCT shipping_mode) AS shipping_mode_versions,
        COUNT(DISTINCT delivery_status) AS delivery_status_versions,
        COUNT(DISTINCT late_delivery_risk) AS risk_flag_versions
    FROM fact_order_items
    GROUP BY order_id
) AS order_checks;
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
        print(cursor.fetchone())