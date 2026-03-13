import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

def predict_next_day_volatility(df):
    # Prepares data, trains a Random Forest model, and predicts next day volatility
    
    df = df.copy()
    df['Daily_Return'] = df['close_price'].pct_change()
    df['Volatility'] = df['Daily_Return'].rolling(window=5).std()
    df['Target_Volatility'] = df['Volatility'].shift(-1)
    
    df = df.dropna()
    
    if df.empty:
        return None
        
    X = df[['close_price', 'Daily_Return', 'Volatility']]
    y = df['Target_Volatility']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    latest_data = X.iloc[-1:]
    prediction = model.predict(latest_data)
    
    return prediction[0]