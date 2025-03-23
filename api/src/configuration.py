import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Required env var is missing: {var_name}")
    return value


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = get_required_env("DB_NAME")
DB_USER = get_required_env("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", None)
PW_SALT = os.getenv("PW_SALT", "default_password_salt")
APP_SECRET_KEY = bytes(get_required_env("APP_SECRET_KEY"), "utf-8")
