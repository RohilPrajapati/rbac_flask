from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = True if os.getenv("DEBUG") == "True" else False

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
