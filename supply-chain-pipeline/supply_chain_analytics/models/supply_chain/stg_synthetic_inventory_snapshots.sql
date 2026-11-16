SELECT
    (record->>'snapshot_date')::DATE AS snapshot_date,
    (record->>'product_id')::INTEGER AS product_id,
    record->>'preferred_supplier_id' AS preferred_supplier_id,
    (record->>'on_hand_quantity')::INTEGER AS on_hand_quantity,
    (record->>'avg_daily_demand_90d')::NUMERIC(12, 4)
        AS avg_daily_demand_90d,
    (record->>'reorder_point')::INTEGER AS reorder_point,
    (record->>'supplier_lead_time_days')::INTEGER
        AS supplier_lead_time_days,
    (record->>'demand_window_days')::INTEGER AS demand_window_days,
    record->>'data_origin' AS data_origin
FROM {{ source('supply_chain_raw', 'raw_synthetic_inventory_snapshots') }}