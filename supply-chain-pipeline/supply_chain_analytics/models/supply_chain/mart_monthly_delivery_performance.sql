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
FROM {{ ref('int_orders') }}
GROUP BY DATE_TRUNC('month', order_datetime)::DATE
