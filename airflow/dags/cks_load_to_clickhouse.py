from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
from clickhouse_driver import Client

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1)
}

dag = DAG(
    dag_id='cks_load_to_clickhouse',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
)

CSV_PATH_CKS = '/opt/airflow/data/cks_synthetic.csv'
CSV_PATH_EOBR = '/opt/airflow/data/e_obr_dummy.csv'
CSV_PATH_KEZEKTE = '/opt/airflow/data/kezekte_dummy.csv'

def load_to_clickhouse():
    print("📥 Загрузка CSV...")
    df = pd.read_csv(CSV_PATH_CKS)
    print(f"📊 Колонки в CSV: {len(df.columns)} → {df.columns.tolist()}")

    expected_columns = [
        "FULL_KATO_NAME", "KATO_2_NAME", "KATO_2", "KATO_4_NAME", "KATO_4",
        "FAMILY_CAT_NEW"
    ] + [f"filtr{i}" for i in list(range(1, 28)) + [65] + list(range(28, 35))] + [
        "count_iin", "KATO_42", "Rating"
    ]

    df = df[[col for col in expected_columns if col in df.columns]]

    string_columns = [
        "FULL_KATO_NAME", "KATO_2_NAME", "KATO_2", "KATO_4_NAME", "KATO_4",
        "FAMILY_CAT_NEW", "KATO_42"
    ] + [f"filtr{i}" for i in list(range(1, 28)) + [65] + list(range(28, 35))]

    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)

    client = Client(host='clickhouse', user='admin', password='dilnaz2510', database='default')

    create_query = """
    CREATE TABLE IF NOT EXISTS cks (
        FULL_KATO_NAME String,
        KATO_2_NAME String,
        KATO_2 String,
        KATO_4_NAME String,
        KATO_4 String,
        FAMILY_CAT_NEW String,
        """ + ",".join([f"filtr{i} String" for i in list(range(1, 28)) + [65] + list(range(28, 35))]) + "," + """
        count_iin UInt8,
        KATO_42 String,
        Rating UInt8
    ) ENGINE = MergeTree()
    ORDER BY FULL_KATO_NAME
    """
    client.execute(create_query)
    client.execute("TRUNCATE TABLE cks")

    client.execute("INSERT INTO cks VALUES", [tuple(row) for row in df.itertuples(index=False)])
    print("✅ cks загружен")

def load_eobr_to_clickhouse():
    df = pd.read_csv(CSV_PATH_EOBR, sep=';')
    df = df.astype(str)
    client = Client(host='clickhouse', user='admin', password='dilnaz2510', database='default')
    columns = ', '.join([f'{col} String' for col in df.columns])
    client.execute(f"CREATE TABLE IF NOT EXISTS e_obr ({columns}) ENGINE = MergeTree() ORDER BY tuple()")
    client.execute("TRUNCATE TABLE e_obr")
    client.execute(f"INSERT INTO e_obr ({', '.join(df.columns)}) VALUES", df.values.tolist())
    print("✅ e_obr загружен")

def load_kezekte_to_clickhouse():
    df = pd.read_csv(CSV_PATH_KEZEKTE, sep=';')
    df = df.astype(str)
    client = Client(host='clickhouse', user='admin', password='dilnaz2510', database='default')
    columns = ', '.join([f'{col} String' for col in df.columns])
    client.execute(f"CREATE TABLE IF NOT EXISTS kezekte ({columns}) ENGINE = MergeTree() ORDER BY tuple()")
    client.execute("TRUNCATE TABLE kezekte")
    client.execute(f"INSERT INTO kezekte ({', '.join(df.columns)}) VALUES", df.values.tolist())
    print("✅ kezekte загружен")

with dag:
    t1 = PythonOperator(
        task_id='load_cks_csv_to_clickhouse',
        python_callable=load_to_clickhouse
    )
    t2 = PythonOperator(
        task_id='load_eobr_csv_to_clickhouse',
        python_callable=load_eobr_to_clickhouse
    )
    t3 = PythonOperator(
        task_id='load_kezekte_csv_to_clickhouse',
        python_callable=load_kezekte_to_clickhouse
    )

    t1 >> [t2, t3]

