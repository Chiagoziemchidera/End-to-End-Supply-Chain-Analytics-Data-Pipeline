import csv
import os
from datetime import date
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


data_folder = Path("/opt/airflow/config/dbt")
dataset_file = data_folder / "DataCoSupplyChainDataset.csv"
synthetic_folder = data_folder / "synthetic"

connection_settings = {
    "host": os.environ["DBT_HOST"],
    "port": int(os.environ["DBT_PORT"]),
    "dbname": os.environ["DBT_DBNAME"],
    "user": os.environ["DBT_USER"],
    "password": os.environ["DBT_ENV_SECRET_PASSWORD"],
}

excluded_columns = {"Customer Email", "Customer Password"}
batch_size = 1_000
loaded_rows = 0

with psycopg.connect(**connection_settings) as connection:
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_synthetic_inventory_snapshots (
                snapshot_date DATE NOT NULL,
                product_id INTEGER NOT NULL,
                source_file TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                record JSONB NOT NULL,
                PRIMARY KEY (snapshot_date, product_id)
            );
        """)

        # Replace this CSV's rows so a rerun does not duplicate them.
        # This and the inserts below happen in one database transaction.
        cursor.execute(
            """
            DELETE FROM raw_supply_chain_orders
            WHERE source_file = %s
            """,
            ("DataCoSupplyChainDataset.csv",),
        )

        with dataset_file.open("r", encoding="cp1252", newline="") as file:
            reader = csv.DictReader(file)
            batch = []

            for row in reader:
                safe_row = {
                    column: value
                    for column, value in row.items()
                    if column not in excluded_columns
                }
                batch.append(
                    ("DataCoSupplyChainDataset.csv", Jsonb(safe_row))
                )

                if len(batch) >= batch_size:
                    cursor.executemany(
                        """
                        INSERT INTO raw_supply_chain_orders
                            (source_file, record)
                        VALUES (%s, %s)
                        """,
                        batch,
                    )
                    loaded_rows += len(batch)
                    batch.clear()

            if batch:
                cursor.executemany(
                    """
                    INSERT INTO raw_supply_chain_orders
                        (source_file, record)
                    VALUES (%s, %s)
                    """,
                    batch,
                )
                loaded_rows += len(batch)

        with (synthetic_folder / "suppliers.csv").open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
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

        with (synthetic_folder / "purchase_orders.csv").open(
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

        with (synthetic_folder / "inventory_snapshots.csv").open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            inventory_rows = list(csv.DictReader(file))

        cursor.executemany(
            """
            INSERT INTO raw_synthetic_inventory_snapshots
                (snapshot_date, product_id, source_file, record)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (snapshot_date, product_id) DO UPDATE SET
                source_file = EXCLUDED.source_file,
                loaded_at = NOW(),
                record = EXCLUDED.record
            """,
            [
                (
                    date.fromisoformat(row["snapshot_date"]),
                    int(row["product_id"]),
                    "inventory_snapshots.csv",
                    Jsonb(row),
                )
                for row in inventory_rows
            ],
        )

print(f"Refreshed {loaded_rows:,} DataCo rows.")
print(f"Upserted {len(suppliers)} suppliers.")
print(f"Upserted {len(purchase_orders)} purchase orders.")
print(f"Upserted {len(inventory_rows)} inventory snapshots.")