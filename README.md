# Financial Volatility Analyzer & ETL Pipeline

An end-to-end Data Engineering project that automates the extraction, storage, and visualization of financial market data.

The system tracks **Cryptocurrencies** (Bitcoin, Ethereum), **Stocks** (S&P 500, NASDAQ), and **Commodities** (Gold) to analyze volatility and risk across different asset classes.


## Architecture

The project follows a modern **ELT (Extract, Load, Transform)** pattern:

1.  **Extract:** Python scripts fetch historical and live market data via the `yfinance` API.
2.  **Load:** Raw data is stored in a **PostgreSQL** database running in a **Docker** container.
3.  **Transform:** SQL Window Functions (Views) calculate daily returns and volatility metrics directly within the database.
4.  **Visualize:** An interactive **Streamlit** dashboard allows users to filter data by date and asset type.

## Tech Stack

* **Language:** Python 3.9+
* **Containerization:** Docker & Docker Compose
* **Database:** PostgreSQL
* **Data Processing:** Pandas, SQLAlchemy
* **Visualization:** Streamlit, Plotly
* **Source:** Yahoo Finance API

## How to Run

### Prerequisites
* Docker & Docker Desktop installed
* Python installed





## Option 1: Automated Start (Recommended)

I have included an automation script that initializes the Docker container, installs dependencies, runs the ETL pipeline, and launches the dashboard in one go.

```bash
python run_project.py
```




## Option 2: Manual Execution


### Step 1: Start the Database
Spin up the PostgreSQL container using Docker Compose.

```bash
docker-compose up -d
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the ETL Pipeline
This script downloads data (handling backfilling and incremental loads) and saves it to the database.

```bash
python etl_finance.py
```

### Step 4: Create SQL Views (One-time setup)
This script creates the analytical views in the database for volatility calculations.

```bash
python create_view.py
```

### Step 5: Launch the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at http://localhost:8501.