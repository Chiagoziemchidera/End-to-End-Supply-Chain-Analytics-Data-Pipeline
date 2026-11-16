import getpass

import psycopg

password = getpass.getpass("Project PostgreSQL password: ")

sql = """
CREATE TABLE IF NOT EXISTS fact_order_items AS
SELECT
    (record->>'Order Item Id')::BIGINT AS order_item_id,
    (record->>'Order Id')::BIGINT AS order_id,
    (record->>'Product Card Id')::INTEGER AS product_id,
    TO_TIMESTAMP(
        record->>'order date (DateOrders)',
        'MM/DD/YYYY HH24:MI'
    ) AS order_datetime,
    TO_TIMESTAMP(
        record->>'shipping date (DateOrders)',
        'MM/DD/YYYY HH24:MI'
    ) AS shipping_datetime,
    (record->>'Days for shipping (real)')::INTEGER AS actual_shipping_days,
    (record->>'Days for shipment (scheduled)')::INTEGER AS scheduled_shipping_days,
    (record->>'Late_delivery_risk')::INTEGER AS late_delivery_risk,
    record->>'Delivery Status' AS delivery_status,
    record->>'Order Status' AS order_status,
    record->>'Shipping Mode' AS shipping_mode,
    record->>'Market' AS market,
    record->>'Order Region' AS order_region,
    (record->>'Order Item Quantity')::INTEGER AS quantity,
    (record->>'Sales')::NUMERIC(12, 2) AS sales_amount,
    (record->>'Order Item Total')::NUMERIC(12, 2) AS order_item_total
FROM raw_supply_chain_orders;
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="supply_chain_dev",
    user="supply_admin",
    password=password,
) as connection:
    with connection.cursor() as cursor:
        cursor.execute(sql)

print("Analytical order-item table created.")