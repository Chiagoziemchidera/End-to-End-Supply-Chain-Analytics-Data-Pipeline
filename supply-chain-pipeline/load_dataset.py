import csv
import getpass
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

dataset_path = Path(
    r"C:\Users\Admin\.cache\kagglehub\datasets\shashwatwork"
    r"\dataco-smart-supply-chain-for-big-data-analysis\versions\1"
    r"\DataCoSupplyChainDataset.csv"
)

excluded_columns = {"Customer Email", "Customer Password"}
batch_size = 1_000
loaded_rows = 0

password = getpass.getpass("Project PostgreSQL password: ")

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="supply_chain_dev",
    user="supply_admin",
    password=password,
) as connection:
    with connection.cursor() as cursor:
        with dataset_path.open("r", encoding="cp1252", newline="") as file:
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
                    print(f"Loaded {loaded_rows:,} rows")
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

print(f"Finished. Loaded {loaded_rows:,} rows.")