import csv
import getpass
import math
import random
from datetime import date
from pathlib import Path

import psycopg

project_folder = Path(__file__).parent
data_folder = project_folder / "data" / "synthetic"
supplier_file = data_folder / "suppliers.csv"
output_file = data_folder / "inventory_snapshots.csv"

snapshot_date = date(2018, 1, 31)
demand_window_days = 90
random_generator = random.Random(2026)

with supplier_file.open("r", encoding="utf-8-sig", newline="") as file:
    suppliers = list(csv.DictReader(file))

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
            SELECT
                p.product_id,
                COALESCE(SUM(i.quantity), 0) AS quantity_sold
            FROM analytics_dev.stg_products AS p
            LEFT JOIN analytics_dev.stg_order_items AS i
                ON p.product_id = i.product_id
                AND i.order_datetime::DATE > DATE '2017-11-02'
                AND i.order_datetime::DATE <= DATE '2018-01-31'
            GROUP BY p.product_id
            ORDER BY p.product_id
        """)
        product_demand = cursor.fetchall()

columns = [
    "snapshot_date",
    "product_id",
    "preferred_supplier_id",
    "on_hand_quantity",
    "avg_daily_demand_90d",
    "reorder_point",
    "supplier_lead_time_days",
    "demand_window_days",
    "data_origin",
]

coverage_multipliers = [0.3, 0.6, 0.9, 1.1, 1.5, 2.2]

with output_file.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()

    for index, (product_id, quantity_sold) in enumerate(product_demand):
        supplier = suppliers[index % len(suppliers)]
        lead_time_days = int(supplier["standard_lead_time_days"])
        average_daily_demand = quantity_sold / demand_window_days

        reorder_point = math.ceil(
            average_daily_demand * lead_time_days * 1.5
        )

        if average_daily_demand > 0:
            multiplier = random_generator.choice(coverage_multipliers)
            on_hand_quantity = round(
                average_daily_demand * lead_time_days * multiplier
            )
        else:
            on_hand_quantity = random_generator.randint(0, 40)

        writer.writerow({
            "snapshot_date": snapshot_date.isoformat(),
            "product_id": product_id,
            "preferred_supplier_id": supplier["supplier_id"],
            "on_hand_quantity": on_hand_quantity,
            "avg_daily_demand_90d": round(average_daily_demand, 4),
            "reorder_point": reorder_point,
            "supplier_lead_time_days": lead_time_days,
            "demand_window_days": demand_window_days,
            "data_origin": "synthetic_inventory_demo",
        })

print(f"Created inventory snapshots for {len(product_demand)} products:")
print(output_file)