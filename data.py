import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Load historical data from the CSV file
@st.cache
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    return data

# Update historical data with live data
def update_data(historical_data, ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    live_data = ticker.history(period='1d', interval='1m')
    live_data['Dividends'] = 0.0
    live_data['Stock Splits'] = 0.0
    combined_data = pd.concat([historical_data, live_data])
    combined_data.reset_index(drop=True, inplace=True)
    return combined_data

# Main function
def main():
    st.title('AAPL Stock Analysis')

    # Load historical data
    csv_file = 'AAPL_stock_data.csv'
    historical_data = load_data(csv_file)

    # Update historical data with live data
    ticker_symbol = 'AAPL'
    combined_data = update_data(historical_data, ticker_symbol)

    # Display combined data
    st.write('**Combined Data:**')
    st.write(combined_data)

    # Plot closing price
    st.write('**Closing Price Chart:**')
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(combined_data['Date'], combined_data['Close'], label='AAPL Close Price')
    ax.set_title('Apple Inc. (AAPL) Stock Closing Price')
    ax.set_xlabel('Date')
    ax.set_ylabel('Closing Price (USD)')
    ax.legend()
    
    # Display Matplotlib plot
    st.pyplot(fig)
    
    # Clear the Matplotlib figure to prevent errors
    plt.close(fig)


if __name__ == '__main__':
    main()
