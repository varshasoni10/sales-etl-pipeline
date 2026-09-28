"""Step 3: Load - clean data ko MySQL (sales_db) me daalna."""
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
DB_NAME = "sales_db"


def get_engine(database: str | None = None) -> Engine:
    # Credentials environment variables se aate hain, code me password nahi likhte
    url = URL.create(
        "mysql+mysqlconnector",
        username=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=database,
    )
    return create_engine(url)


def run_sql_file(engine: Engine, path: Path) -> list[pd.DataFrame]:
    """SQL file ke har statement ko chalana; SELECT ka result DataFrame me lautana."""
    # Comment lines hatao, phir ';' pe split karo
    sql = "\n".join(line for line in path.read_text().splitlines() if not line.strip().startswith("--"))
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    results = []
    with engine.begin() as conn:
        for stmt in statements:
            result = conn.execute(text(stmt))
            if result.returns_rows:
                results.append(pd.DataFrame(result.fetchall(), columns=list(result.keys())))
    return results


def load(products: pd.DataFrame, sales: pd.DataFrame) -> None:
    # Database + tables banana (server level connection, abhi DB exist nahi karta)
    run_sql_file(get_engine(), SQL_DIR / "create_tables.sql")

    engine = get_engine(DB_NAME)
    # products pehle, kyunki sales ki foreign key usko refer karti hai
    products.to_sql("products", engine, if_exists="append", index=False, chunksize=1000)
    sales.to_sql("sales", engine, if_exists="append", index=False, chunksize=1000)
    print(f"[load] {len(products)} products aur {len(sales)} sales rows {DB_NAME} me load hue")


def analyze() -> list[pd.DataFrame]:
    """Step 4: analysis_queries.sql chalana."""
    return run_sql_file(get_engine(DB_NAME), SQL_DIR / "analysis_queries.sql")
