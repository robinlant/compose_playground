import psycopg2

from src.configuration import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from src.dal.init_db import ensure_exists

print(f"Test db name: {DB_NAME}")


def connect_to_db(name: str) -> psycopg2.extensions.connection:
    return psycopg2.connect(
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=name)


connect_to_db("postgres").cursor().execute(""""
    CREATE DATABASE test;
""")

cur = connect_to_db(DB_NAME).cursor()
ensure_exists(cur)
