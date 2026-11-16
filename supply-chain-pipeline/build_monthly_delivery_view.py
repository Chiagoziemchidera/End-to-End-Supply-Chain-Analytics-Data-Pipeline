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
            CREATE OR REPLACE VIEW mart_monthly_delivery_performance AS
            SELECT
                DATE_TRUNC('month', order_datetime)::DATE AS order_month,
                COUNT(*) AS orders,
                COUNT(*) FILTER (
                    WHERE late_delivery_risk = 1
                ) AS orders_flagged_risk,
                COUNT(*) FILTER (
                    WHERE actual_shipping_days > scheduled_shipping_days
                ) AS orders_actually_late,
                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE actual_shipping_days > scheduled_shipping_days
                    ) / COUNT(*),
                    2
                ) AS actual_late_rate_pct,
                ROUND(AVG(actual_shipping_days::NUMERIC), 2)
                    AS avg_actual_shipping_days,
                ROUND(AVG(scheduled_shipping_days::NUMERIC), 2)
                    AS avg_scheduled_shipping_days
            FROM fact_orders
            GROUP BY DATE_TRUNC('month', order_datetime)::DATE;
        """)

        cursor.execute("""
            SELECT *
            FROM mart_monthly_delivery_performance
            ORDER BY order_month;
        """)
        results = cursor.fetchall()

print(
    "Month | Orders | Risk flagged | Actually late | "
    "Actual late rate % | Avg actual days | Avg scheduled days"
)
for row in results:
    print(row)