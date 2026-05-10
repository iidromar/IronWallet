import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "cockroachdb+psycopg2://root@127.0.0.1:26257/payment_gateway?sslmode=disable",
)
OMNIBUS_URL = os.getenv("OMNIBUS_URL", "http://localhost:8084")
