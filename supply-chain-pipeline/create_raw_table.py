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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_supply_chain_orders (
                row_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                source_file TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                record JSONB NOT NULL
            );
        """)

print("Raw landing table is ready.")