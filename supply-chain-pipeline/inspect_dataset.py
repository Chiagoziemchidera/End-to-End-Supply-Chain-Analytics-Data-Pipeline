import csv
from datetime import datetime
from pathlib import Path

dataset_path = Path(
    r"C:\Users\Admin\.cache\kagglehub\datasets\shashwatwork"
    r"\dataco-smart-supply-chain-for-big-data-analysis\versions\1"
    r"\DataCoSupplyChainDataset.csv"
)

order_dates = []
shipping_dates = []

with dataset_path.open("r", encoding="cp1252", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        order_dates.append(
            datetime.strptime(row["order date (DateOrders)"], "%m/%d/%Y %H:%M")
        )
        shipping_dates.append(
            datetime.strptime(row["shipping date (DateOrders)"], "%m/%d/%Y %H:%M")
        )

print(f"Order dates: {min(order_dates)} to {max(order_dates)}")
print(f"Shipping dates: {min(shipping_dates)} to {max(shipping_dates)}")