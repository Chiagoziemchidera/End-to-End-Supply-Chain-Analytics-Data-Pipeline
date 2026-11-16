SELECT
    record->>'supplier_id' AS supplier_id,
    record->>'supplier_name' AS supplier_name,
    record->>'supplier_region' AS supplier_region,
    (record->>'standard_lead_time_days')::INTEGER
        AS standard_lead_time_days,
    'synthetic_demo' AS data_origin
FROM {{ source('supply_chain_raw', 'raw_synthetic_suppliers') }}
