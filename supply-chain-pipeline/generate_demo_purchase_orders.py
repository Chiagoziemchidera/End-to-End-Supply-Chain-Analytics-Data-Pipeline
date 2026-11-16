import csv
import getpass
import random
from datetime import date, timedelta
from pathlib import Path

import psycopg

project_folder = Path(__file__).parent
data_folder = project_folder / "data" / "synthetic"
supplier_file = data_folder / "suppliers.csv"
output_file = data_folder / "purchase_orders.csv"

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
            SELECT product_id
            FROM analytics_dev.stg_products
            ORDER BY product_id
        """)
        product_ids = [row[0] for row in cursor.fetchall()]

with supplier_file.open("r", encoding="utf-8-sig", newline="") as file:
    suppliers = list(csv.DictReader(file))

# These probabilities are invented for the simulation.
on_time_chances = {
    "SYN-SUP-001": 0.95,
    "SYN-SUP-002": 0.85,
    "SYN-SUP-003": 0.92,
    "SYN-SUP-004": 0.78,
    "SYN-SUP-005": 0.88,
    "SYN-SUP-006": 0.72,
    "SYN-SUP-007": 0.90,
    "SYN-SUP-008": 0.68,
}

random_generator = random.Random(42)
start_date = date(2015, 1, 1)
end_date = date(2018, 1, 31)
date_range_days = (end_date - start_date).days

columns = [
    "purchase_order_id",
    "supplier_id",
    "product_id",
    "order_date",
    "promised_delivery_date",
    "actual_delivery_date",
    "quantity_ordered",
    "quantity_received",
    "is_late",
    "data_origin",
]

with output_file.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()

    for number in range(1, 1001):
        supplier = random_generator.choice(suppliers)
        supplier_id = supplier["supplier_id"]
        lead_days = int(supplier["standard_lead_time_days"])

        order_date = start_date + timedelta(
            days=random_generator.randint(0, date_range_days)
        )
        promised_date = order_date + timedelta(days=lead_days)

        arrived_on_time = (
            random_generator.random() < on_time_chances[supplier_id]
        )

        if arrived_on_time:
            actual_days = random_generator.randint(max(1, lead_days - 2), lead_days)
        else:
            actual_days = lead_days + random_generator.randint(1, 7)

        actual_date = order_date + timedelta(days=actual_days)
        quantity_ordered = random_generator.randint(10, 200)

        if random_generator.random() < 0.05:
            quantity_received = random_generator.randint(
                max(1, int(quantity_ordered * 0.7)),
                quantity_ordered - 1,
            )
        else:
            quantity_received = quantity_ordered

        writer.writerow({
            "purchase_order_id": f"SYN-PO-{number:05d}",
            "supplier_id": supplier_id,
            "product_id": random_generator.choice(product_ids),
            "order_date": order_date.isoformat(),
            "promised_delivery_date": promised_date.isoformat(),
            "actual_delivery_date": actual_date.isoformat(),
            "quantity_ordered": quantity_ordered,
            "quantity_received": quantity_received,
            "is_late": str(actual_date > promised_date).lower(),
            "data_origin": "synthetic_demo",
        })

print(f"Created 1,000 synthetic purchase orders: {output_file}")