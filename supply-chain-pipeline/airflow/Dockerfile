FROM apache/airflow:3.4.0
COPY requirements.txt /requirements.txt
RUN python -m venv /home/airflow/dbt-venv && /home/airflow/dbt-venv/bin/pip install --no-cache-dir -r /requirements.txt