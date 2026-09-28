# Sales Data ETL Pipeline

This pipeline takes raw, messy sales data from a CSV file, cleans it, loads it into MySQL, and runs SQL queries to produce business insights.

```
Raw CSV  →  Extract (Pandas)  →  Transform (clean + revenue)  →  Load (MySQL)  →  Analyze (SQL)
```

## Tech stack
Python · Pandas · NumPy · MySQL · SQLAlchemy + mysql-connector-python · SQL · Git

## Project structure
```
sales-etl-pipeline/
├── data/
│   └── raw_sales.csv              # raw input (sample data or Kaggle Superstore)
├── scripts/
│   └── generate_sample_data.py    # generates a messy sample CSV
├── src/
│   ├── extract.py                 # reads the CSV, prints info()/head()
│   ├── transform.py               # cleaning + revenue/month/year columns
│   └── load.py                    # creates tables in MySQL, inserts data, runs analysis
├── sql/
│   ├── create_tables.sql          # sales_db, products, sales
│   └── analysis_queries.sql       # 4 business queries
├── main.py                        # runs the whole pipeline with one command
└── requirements.txt
```

## Setup
```bash
pip install -r requirements.txt
```

Set your MySQL credentials as environment variables. Never write a password in the code.

```powershell
# Windows PowerShell
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
# optional: MYSQL_HOST (default localhost), MYSQL_PORT (default 3306)
```

## Run
```bash
python main.py                                 # full pipeline: Extract → Transform → Load → Analyze
python main.py --skip-db                       # Extract + Transform only; no MySQL needed
python main.py --input "data/Sample - Superstore.csv"   # run on the Kaggle dataset
```

**Dataset:** download the [Superstore Sales dataset from Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) and put it in `data/`. If you don't have it, generate the sample data with `python scripts/generate_sample_data.py`. The sample file has deliberately messy rows: duplicates, nulls, mixed date formats, negative values, and inconsistent casing.

## Transform steps
| Problem | Fix |
|---|---|
| `Order Date`, `Sub-Category` | converted to lowercase_underscore names: `order_date`, `sub_category` |
| Extra spaces, `  east ` / `OFFICE SUPPLIES` | strip + title case |
| Duplicate rows | `drop_duplicates()` |
| Mixed date formats (`01/15/2024`, `2024-01-15`, `15-Jan-2024`) | `pd.to_datetime(format="mixed")`; an invalid date becomes NaT |
| Missing `order_id`, `order_date`, `product_id`, `quantity` | row is dropped |
| Missing `region`, `category`, `product_name` | filled with `"Unknown"` |
| Quantity or price zero/negative | row is filtered out |
| Superstore has no unit price, only a line total `sales` | `unit_price = sales / quantity` |
| New columns | `revenue = quantity × unit_price` (NumPy), `order_year`, `order_month` |

On the sample data: **1040 raw rows → 956 clean rows** (40 duplicates, 27 missing-required, 17 invalid).

## Database schema
- **products** (`product_id` PK, `product_name`, `category`)
- **sales** (`sale_id` PK, `order_id`, `order_date`, `product_id` FK, `region`, `quantity`, `price`, `revenue`)

`order_id` is not the primary key because one order can contain several products.

## Analysis queries (`sql/analysis_queries.sql`)
1. Monthly total sales: `GROUP BY` month
2. Top 5 best-selling products: `ORDER BY ... LIMIT 5`
3. Region-wise revenue, with each region's percentage share
4. Category-wise sales: `JOIN products + sales`

## Future improvements
- Schedule the pipeline to run automatically every day (cron / Airflow)
- Pull live data from an API
- Build a dashboard in Power BI or Tableau
