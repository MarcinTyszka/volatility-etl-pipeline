import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from datetime import timedelta, datetime
from ml_model import predict_next_day_volatility

DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'finance_data'

@st.cache_data
def get_data():
    # Fetches data from PostgreSQL and caches it for performance
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = "SELECT * FROM v_daily_returns WHERE daily_change_pct IS NOT NULL ORDER BY date;"
    df = pd.read_sql(query, engine)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

st.set_page_config(page_title="Market Analyzer", layout="wide")

st.title("Multi-Asset Volatility Analyzer")
st.markdown("Analyze historical performance, risk, and machine learning volatility predictions.")
st.markdown("---")

df_full = get_data()

if not df_full.empty:
    
    st.sidebar.header("Dashboard Configuration")
    
    available_tickers = df_full['ticker'].unique().tolist()
    default_tickers = ['BTC-USD', 'SPY'] if 'BTC-USD' in available_tickers and 'SPY' in available_tickers else available_tickers[:2]
    
    selected_tickers = st.sidebar.multiselect(
        "Select Assets:",
        options=available_tickers,
        default=default_tickers
    )
    
    st.sidebar.markdown("---")

    max_date = df_full['date'].max()
    min_date = df_full['date'].min()

    time_options = [
        "Last 7 Days", "Last 30 Days", "Last 3 Months", 
        "Last 1 Year", "Year To Date (YTD)", "All Time", "Custom Range"
    ]
    
    selected_range = st.sidebar.selectbox("Select Time Range:", time_options, index=1)

    start_date = min_date
    end_date = max_date

    # Date range logic
    if selected_range == "Last 7 Days":
        start_date = max_date - timedelta(days=7)
    elif selected_range == "Last 30 Days":
        start_date = max_date - timedelta(days=30)
    elif selected_range == "Last 3 Months":
        start_date = max_date - timedelta(days=90)
    elif selected_range == "Last 1 Year":
        start_date = max_date - timedelta(days=365)
    elif selected_range == "Year To Date (YTD)":
        start_date = datetime(max_date.year, 1, 1)
    elif selected_range == "Custom Range":
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(max_date - timedelta(days=30), max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

    mask = (
        (df_full['ticker'].isin(selected_tickers)) & 
        (df_full['date'] >= pd.to_datetime(start_date)) & 
        (df_full['date'] <= pd.to_datetime(end_date))
    )
    df_filtered = df_full.loc[mask]

    if df_filtered.empty:
        st.warning("No data found for the selected time range and assets.")
    else:
        # Dashboard layout using tabs
        tab1, tab2, tab3 = st.tabs(["Market Overview", "AI Volatility Prediction", "Raw Data"])

        with tab1:
            st.subheader(f"Volatility Overview ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
            
            volatility = df_filtered.groupby('ticker')['daily_change_pct'].std().sort_values(ascending=False)
            
            if not volatility.empty:
                cols = st.columns(len(selected_tickers))
                for i, ticker in enumerate(selected_tickers):
                    if ticker in volatility:
                        vol = volatility[ticker]
                        risk_label = "High Risk" if vol > 2.0 else "Stable"
                        delta_color = "inverse" if vol > 2.0 else "normal"
                        
                        cols[i % len(cols)].metric(
                            label=f"{ticker} Volatility", 
                            value=f"{vol:.2f}%",
                            delta=risk_label,
                            delta_color=delta_color
                        )

            st.markdown("---")
            st.subheader("Daily Returns Trend")
            
            fig = px.line(
                df_filtered, 
                x='date', 
                y='daily_change_pct', 
                color='ticker',
                template='plotly_white',
                labels={"daily_change_pct": "Daily Return (%)", "date": "Date"}
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), hovermode="x unified")
            
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("Machine Learning Insights")
            st.markdown("Predicting next day volatility using a Random Forest algorithm.")
            
            pred_cols = st.columns(len(selected_tickers))
            
            # Applying ML model for each selected asset
            for i, ticker in enumerate(selected_tickers):
                ticker_data = df_filtered[df_filtered['ticker'] == ticker].copy()
                
                # Ensure enough data points for the model
                if len(ticker_data) > 10:
                    predicted_vol = predict_next_day_volatility(ticker_data)
                    if predicted_vol is not None:
                        pred_cols[i % len(pred_cols)].metric(
                            label=f"{ticker} Predicted Vol", 
                            value=f"{predicted_vol:.2f}%",
                            delta="AI Forecast",
                            delta_color="off"
                        )
                else:
                    pred_cols[i % len(pred_cols)].warning(f"Not enough data to predict {ticker}")

        with tab3:
            st.subheader("Dataset Explorer")
            st.dataframe(df_filtered.sort_values(by='date', ascending=False), use_container_width=True)

else:
    st.error("Database connection successful, but no data found. Please run the ETL script first.")