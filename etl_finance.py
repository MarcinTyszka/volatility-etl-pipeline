import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
import time
from datetime import timedelta

DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'finance_data'

TICKERS = [
    # US Market Indices
    'SPY',       # S&P 500
    'QQQ',       # NASDAQ-100
    
    # Commodities (Safe Haven)
    'GLD',       # Gold

    # Polish Market (Warsaw Stock Exchange)
    'CDR.WA',    # CD Projekt Red
    'PKO.WA',    # PKO Bank Polski
    
    # Cryptocurrencies
    'BTC-USD',   # Bitcoin
    'ETH-USD',   # Ethereum
    'SOL-USD',   # Solana
    'DOGE-USD'   # Dogecoin
]

def get_last_date(ticker_symbol):

    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = text(f"SELECT MAX(date) FROM market_data WHERE ticker = '{ticker_symbol}'")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query).fetchone()
            return result[0]
    except Exception:
        return None

def extract_data(ticker_symbol, start_date=None):
    print(f"Downloading data for {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    
    if start_date:
        start_str = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"Incremental load from {start_str}...")
        df = ticker.history(start=start_str)
    else:
        print("Initial load (5 years history)...")
        df = ticker.history(period="5y")
    
    if df.empty:
        return df

    df.reset_index(inplace=True)
    df = df[['Date', 'Close', 'Volume']]
    df['ticker'] = ticker_symbol
    return df

def transform_data(df):
    df.columns = [c.lower() for c in df.columns]
    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    return df

def load_to_db(df, table_name):
    if df.empty:
        print("No new data to load.")
        return

    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Appended {len(df)} new rows to {table_name}.")
    except Exception as e:
        print(f"Error loading to database: {e}")

if __name__ == "__main__":
    for symbol in TICKERS:
        last_db_date = get_last_date(symbol)       
        raw_data = extract_data(symbol, start_date=last_db_date)
        if not raw_data.empty:
            clean_data = transform_data(raw_data)
            load_to_db(clean_data, "market_data")
        
        time.sleep(1)