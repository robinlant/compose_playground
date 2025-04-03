import psycopg2

from src.configuration import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
from src.dal.init_db import ensure_exists


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

DB_NAME = "test_polls"

cur = connect_to_db(DB_NAME)
ensure_exists(cur)
