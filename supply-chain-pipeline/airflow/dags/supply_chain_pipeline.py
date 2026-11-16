from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag


@dag(
    dag_id="supply_chain_pipeline",
    start_date=datetime(2026, 11, 12),
    schedule=None,
    catchup=False,
    tags=["supply-chain"],
)
def supply_chain_pipeline():
    connection_env = {
        "DBT_HOST": "{{ conn.supply_chain_postgres.host }}",
        "DBT_PORT": "{{ conn.supply_chain_postgres.port }}",
        "DBT_USER": "{{ conn.supply_chain_postgres.login }}",
        "DBT_ENV_SECRET_PASSWORD": "{{ conn.supply_chain_postgres.password }}",
        "DBT_DBNAME": "{{ conn.supply_chain_postgres.schema }}",
        "DBT_SCHEMA": "analytics_dev",
    }

    ingest_sources = BashOperator(
        task_id="ingest_sources",
        bash_command="python /opt/airflow/scripts/ingest_sources.py",
        env=connection_env.copy(),
        append_env=True,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "/home/airflow/dbt-venv/bin/dbt build "
            "--project-dir /opt/airflow/dbt/supply_chain_analytics "
            "--profiles-dir /opt/airflow/config/dbt "
            "--target dev "
            "--target-path /tmp/dbt-target "
            "--log-path /tmp/dbt-logs"
        ),
        env=connection_env.copy(),
        append_env=True,
    )

    ingest_sources >> dbt_build


supply_chain_pipeline()