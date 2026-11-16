SELECT
    po.supplier_id,
    s.supplier_name,
    s.supplier_region,
    COUNT(*) AS purchase_orders,
    COUNT(*) FILTER (
        WHERE po.actual_delivery_date <= po.promised_delivery_date
    ) AS on_time_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE po.actual_delivery_date <= po.promised_delivery_date
        ) / COUNT(*),
        2
    ) AS on_time_delivery_rate_pct,
    COUNT(*) FILTER (
        WHERE po.quantity_received < po.quantity_ordered
    ) AS partially_filled_orders,
    SUM(po.quantity_ordered) AS total_quantity_ordered,
    SUM(po.quantity_received) AS total_quantity_received,
    ROUND(
        100.0 * SUM(po.quantity_received)::NUMERIC
        / NULLIF(SUM(po.quantity_ordered), 0),
        2
    ) AS quantity_fill_rate_pct,
    ROUND(
        AVG((po.actual_delivery_date - po.order_date)::NUMERIC),
        2
    ) AS avg_actual_lead_time_days,
    'synthetic_demo' AS data_origin
FROM {{ ref('stg_synthetic_purchase_orders') }} AS po
JOIN {{ ref('stg_synthetic_suppliers') }} AS s
    ON po.supplier_id = s.supplier_id
GROUP BY
    po.supplier_id,
    s.supplier_name,
    s.supplier_region
