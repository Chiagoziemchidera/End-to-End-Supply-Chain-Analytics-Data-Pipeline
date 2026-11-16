import csv
import getpass
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

project_folder = Path(__file__).parent
data_folder = project_folder / "data" / "synthetic"

supplier_file = data_folder / "suppliers.csv"
purchase_order_file = data_folder / "purchase_orders.csv"

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
            CREATE TABLE IF NOT EXISTS raw_synthetic_suppliers (
                supplier_id TEXT PRIMARY KEY,
                source_file TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                record JSONB NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_synthetic_purchase_orders (
                purchase_order_id TEXT PRIMARY KEY,
                source_file TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                record JSONB NOT NULL
            );
        """)

        with supplier_file.open("r", encoding="utf-8-sig", newline="") as file:
            suppliers = list(csv.DictReader(file))

        cursor.executemany(
            """
            INSERT INTO raw_synthetic_suppliers
                (supplier_id, source_file, record)
            VALUES (%s, %s, %s)
            ON CONFLICT (supplier_id) DO UPDATE SET
                source_file = EXCLUDED.source_file,
                loaded_at = NOW(),
                record = EXCLUDED.record
            """,
            [
                (
                    row["supplier_id"],
                    "suppliers.csv",
                    Jsonb(row),
                )
                for row in suppliers
            ],
        )

        with purchase_order_file.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            purchase_orders = list(csv.DictReader(file))

        cursor.executemany(
            """
            INSERT INTO raw_synthetic_purchase_orders
                (purchase_order_id, source_file, record)
            VALUES (%s, %s, %s)
            ON CONFLICT (purchase_order_id) DO UPDATE SET
                source_file = EXCLUDED.source_file,
                loaded_at = NOW(),
                record = EXCLUDED.record
            """,
            [
                (
                    row["purchase_order_id"],
                    "purchase_orders.csv",
                    Jsonb(row),
                )
                for row in purchase_orders
            ],
        )

print(f"Loaded {len(suppliers)} synthetic suppliers.")
print(f"Loaded {len(purchase_orders)} synthetic purchase orders.")