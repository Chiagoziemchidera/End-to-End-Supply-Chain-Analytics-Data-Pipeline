# Supply Chain Analytics Pipeline

An end-to-end data engineering project that prepares shipment, supplier, purchase-order, and inventory data for delivery, supplier, and stock-risk analysis.

## Architecture

<img width="1846" height="852" alt="Streamlined supply chain data architecture" src="https://github.com/user-attachments/assets/1d6f23fd-811e-4226-bd7d-1b5a6b751878" />

Airflow runs the Python ingestion task first, followed by `dbt build`. Python loads source records into PostgreSQL. dbt builds and tests SQL models in the database. Power BI connects to the resulting analytical views.

## Tools

- **Python** for CSV ingestion and data handling
- **PostgreSQL** for raw records and analytical views
- **dbt Core + PostgreSQL adapter** for SQL transformations and data tests
- **Apache Airflow** for task orchestration and run monitoring
- **Docker Compose** for running the Airflow services
- **Power BI** for analysis and reporting

## Data and models

The DataCo Smart Supply Chain dataset from Kaggle contains **180,519 order-item records** and **65,752 distinct orders**, covering order dates from **January 2015 to January 2018**. The pipeline also processes supplier, purchase-order, and inventory inputs.

Key dbt views in the `analytics_dev` schema include:

- `int_orders` for order-level delivery analysis
- `mart_monthly_delivery_performance`
- `mart_delivery_by_shipping_mode`
- `mart_delivery_by_region`
- `mart_supplier_reliability`
- `mart_inventory_stockout_risk`

Staging views provide cleaned order-item, product, supplier, purchase-order, and inventory records. The marts summarize data at their reporting grain and are ready to connect to Power BI.

## Data quality and validation

The dbt project includes uniqueness, not-null, accepted-value, and relationship tests. The latest recorded project-wide test run passed **32 tests**. The Airflow DAG completed successfully with both ingestion and dbt tasks green.

The ingestion process excludes customer email and password fields. Database credentials are supplied through environment/profile configuration and are not stored in model SQL.

## Repository layout

```text
airflow/dags/supply_chain_pipeline.py     Airflow workflow
airflow/scripts/ingest_sources.py         Pipeline ingestion entry point
supply_chain_analytics/                   dbt project, models, tests, and macros
Python scripts at the repository root    Source loading and data preparation
```

## Run overview

Start the project PostgreSQL server and Airflow Docker services, then trigger the `supply_chain_pipeline` DAG in Airflow. The DAG runs ingestion before `dbt build`. Review both task logs and confirm the dbt tests pass before refreshing Power BI.

The DAG is manually triggered. The project PostgreSQL database is `supply_chain_dev`; raw records are in `public` and dbt views are in `analytics_dev`.
