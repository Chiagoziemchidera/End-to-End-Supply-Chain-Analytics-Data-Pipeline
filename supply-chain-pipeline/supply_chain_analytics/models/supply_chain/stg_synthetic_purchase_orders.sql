SELECT
    record->>'purchase_order_id' AS purchase_order_id,
    record->>'supplier_id' AS supplier_id,
    (record->>'product_id')::INTEGER AS product_id,
    (record->>'order_date')::DATE AS order_date,
    (record->>'promised_delivery_date')::DATE AS promised_delivery_date,
    (record->>'actual_delivery_date')::DATE AS actual_delivery_date,
    (record->>'quantity_ordered')::INTEGER AS quantity_ordered,
    (record->>'quantity_received')::INTEGER AS quantity_received,
    (record->>'is_late')::BOOLEAN AS is_late,
    record->>'data_origin' AS data_origin
FROM {{ source('supply_chain_raw', 'raw_synthetic_purchase_orders') }}
