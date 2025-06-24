from superset.db_engine_specs.base import BaseEngineSpec

class ClickHouseEngineSpec(BaseEngineSpec):
    engine = "clickhouse"
    engine_name = "ClickHouse"

    default_driver = "clickhouse_connect"

    supports_subqueries = True
    supports_column_aliases = True
    supports_native_backends = True
    supports_dynamic_fetch = True
