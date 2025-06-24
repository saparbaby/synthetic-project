#  Synthetic Data Analytics Project


##  Project Objective

- Simulate real-world data analysis using synthetic datasets
- Apply theoretical knowledge in Python, ETL, and visualization tools
- Practice end-to-end integration of data platforms (Airflow → ClickHouse → Superset)
- Build informative dashboards based on simulated social datasets

---

##  Tools & Technologies

| Category        | Tools Used                            |
|----------------|----------------------------------------|
| Programming     | Python 3.8+                           |
| Data Processing | Pandas, NumPy                         |
| Synthetic Data  | SDV, CTGAN, GaussianCopulaSynthesizer |
| ETL             | Apache Airflow                        |
| Database        | ClickHouse                            |
| BI Dashboard    | Apache Superset                       |
| Containerization| Docker, Docker Compose                |








---

## 📦 Dataset Descriptions

| File               | Description                                      |
|--------------------|--------------------------------------------------|
| `cks_synthetic.csv`| Family categories and filters dataset            |
| `kezekte_dummy.csv`| Social queue data of families in need            |
| `e_obr_dummy.csv`  | Government service application history           |

---

## ⚙️ How to Run Locally

1. **Clone the repo**:
   ```bash
   git clone https://github.com/your-username/synthetic-project.git
   cd synthetic-project



Start the services:

docker-compose up --build
Upload the CSV files (if not already in /data/).

Access the services:

Airflow: http://localhost:8080

Superset: http://localhost:8088

ClickHouse UI: http://localhost:8123

Run the Airflow DAG:
cks_load_to_clickhouse will load all .csv files into ClickHouse.

Log into Superset, connect to ClickHouse DB, and build or explore dashboards.
