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
    MAX(order_region) AS order_region,
    COUNT(*) AS order_item_count,
    SUM(quantity) AS total_quantity,
    SUM(order_item_total)::NUMERIC(12, 2) AS order_total
FROM {{ ref('stg_order_items') }}
GROUP BY order_id
