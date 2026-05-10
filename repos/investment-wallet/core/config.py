import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "cockroachdb+psycopg2://root@127.0.0.1:26257/investment_wallet?sslmode=disable",
)
PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "http://localhost:8082")
SERVICE_BASE_URL = os.getenv("SERVICE_BASE_URL", "http://localhost:8083")
