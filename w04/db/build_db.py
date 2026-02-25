"""build_db.py
Script to build the anime database by executing the schema SQL file.
"""
import duckdb
from config.config import DB_SCHEMA_PATH, ANIME_DB_PATH
def build_anime_db():
    anime_conn = duckdb.connect(database = ANIME_DB_PATH)
    with open(DB_SCHEMA_PATH, "r", encoding = "utf-8") as f:
        schema_sql = f.read()
    anime_conn.execute(schema_sql)
    anime_conn.close()
