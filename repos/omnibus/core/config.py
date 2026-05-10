import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "cockroachdb+psycopg2://root@127.0.0.1:26257/omnibus?sslmode=disable",
)
INVESTMENT_WALLET_URL = os.getenv("INVESTMENT_WALLET_URL", "http://localhost:8083")
