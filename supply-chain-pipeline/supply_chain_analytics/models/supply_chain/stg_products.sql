SELECT
    (record->>'Product Card Id')::INTEGER AS product_id,
    MAX(record->>'Product Name') AS product_name,
    MAX(record->>'Category Name') AS category_name,
    MAX(record->>'Department Name') AS department_name,
    MAX((record->>'Product Price')::NUMERIC(12, 2)) AS product_price
FROM {{ source('supply_chain_raw', 'raw_supply_chain_orders') }}
GROUP BY (record->>'Product Card Id')::INTEGER
