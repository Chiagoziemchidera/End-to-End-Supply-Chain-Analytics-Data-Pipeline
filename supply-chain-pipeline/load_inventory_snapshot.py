import csv
import getpass
from datetime import date
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

project_folder = Path(__file__).parent
inventory_file = (
    project_folder / "data" / "synthetic" / "inventory_snapshots.csv"
)

with inventory_file.open("r", encoding="utf-8-sig", newline="") as file:
    inventory_rows = list(csv.DictReader(file))

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
            CREATE TABLE IF NOT EXISTS raw_synthetic_inventory_snapshots (
                snapshot_date DATE NOT NULL,
                product_id INTEGER NOT NULL,
                source_file TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                record JSONB NOT NULL,
                PRIMARY KEY (snapshot_date, product_id)
            );
        """)

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

print(f"Loaded {len(inventory_rows)} inventory snapshots.")