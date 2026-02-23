import pandas as pd
from sqlalchemy import create_engine

# Database configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'finance_data'

def check_data():

    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(connection_string)
        

        query = "SELECT * FROM market_data;"
        df = pd.read_sql(query, engine)
        
        if not df.empty:
            print("--- Data from Database ---")
            print(df)
            print("--------------------------")
        else:
            print("Table exists but is empty.")
            
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_data()