from sqlalchemy import create_engine
from sqlalchemy import text

# Database configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'finance_data'

def create_analytical_view():
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)


    ddl_query = """
    CREATE OR REPLACE VIEW v_daily_returns AS
    SELECT 
        date,
        ticker,
        close as close_price,
        LAG(close) OVER (PARTITION BY ticker ORDER BY date) as prev_close,
        (close - LAG(close) OVER (PARTITION BY ticker ORDER BY date)) 
            / NULLIF(LAG(close) OVER (PARTITION BY ticker ORDER BY date), 0) * 100 as daily_change_pct
    FROM market_data;
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(ddl_query))
            conn.commit()
        print("SQL View 'v_daily_returns' created successfully.")
    except Exception as e:
        print(f"Error executing SQL: {e}")

if __name__ == "__main__":
    create_analytical_view()