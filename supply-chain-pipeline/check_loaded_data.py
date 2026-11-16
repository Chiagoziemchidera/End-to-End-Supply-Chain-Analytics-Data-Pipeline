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
        cursor.execute("SELECT COUNT(*) FROM raw_supply_chain_orders")
        row_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                record->>'Order Id',
                record->>'Order Status',
                record->>'Delivery Status'
            FROM raw_supply_chain_orders
            ORDER BY row_id
            LIMIT 3
        """)
        sample_rows = cursor.fetchall()

print(f"Rows in database: {row_count:,}")
print("Sample order fields:")
for row in sample_rows:
    print(row)