SELECT
    inv.snapshot_date,
    inv.product_id,
    p.product_name,
    p.category_name,
    inv.preferred_supplier_id AS supplier_id,
    s.supplier_name,
    inv.on_hand_quantity,
    inv.avg_daily_demand_90d,
    inv.reorder_point,
    inv.supplier_lead_time_days,
    CASE
        WHEN inv.avg_daily_demand_90d > 0
        THEN ROUND(
            inv.on_hand_quantity::NUMERIC
                / inv.avg_daily_demand_90d,
            2
        )
        ELSE NULL
    END AS days_of_cover,
    CASE
        WHEN inv.avg_daily_demand_90d <= 0
            THEN 'No recent demand'
        WHEN inv.on_hand_quantity::NUMERIC
                / NULLIF(inv.avg_daily_demand_90d, 0)
                < inv.supplier_lead_time_days
            THEN 'At risk'
        ELSE 'Covered'
    END AS stockout_risk_status,
    CASE
        WHEN inv.avg_daily_demand_90d > 0
         AND inv.on_hand_quantity <= inv.reorder_point
            THEN TRUE
        ELSE FALSE
    END AS reorder_needed,
    inv.data_origin
FROM {{ ref('stg_synthetic_inventory_snapshots') }} AS inv
JOIN {{ ref('stg_products') }} AS p
    ON inv.product_id = p.product_id
JOIN {{ ref('stg_synthetic_suppliers') }} AS s
    ON inv.preferred_supplier_id = s.supplier_id