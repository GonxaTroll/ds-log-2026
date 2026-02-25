import duckdb
import pandas as pd
anime_conn = duckdb.connect(database = "data/anime.db")

# Open and read the schema file
with open("schema.sql", "r") as f:
    schema_sql = f.read()

anime_conn.execute(schema_sql)