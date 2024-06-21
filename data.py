import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from github import Github
from datetime import datetime, timedelta

# GitHub repository information
repo_owner = "DataSymphonist-Pranav"  # Replace with your GitHub username
repo_name = "data"  # Replace with your repository name

# GitHub authentication
github_token = st.secrets["GITHUB_TOKEN"]
g = Github(github_token)

# Function to load historical data from Yahoo Finance
@st.cache_data
def load_historical_data(ticker_symbol, start_date):
    ticker = yf.Ticker(ticker_symbol)
    historical_data = ticker.history(start=start_date, end=datetime.now().strftime('%Y-%m-%d'))
    return historical_data

# Function to update historical data with live data
def update_data(historical_data, ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    live_data = ticker.history(period='1d', interval='1m')
    live_data['Dividends'] = 0.0
    live_data['Stock Splits'] = 0.0
    combined_data = pd.concat([historical_data, live_data])
    combined_data.reset_index(drop=True, inplace=True)
    return combined_data

# Function to save DataFrame to GitHub as a CSV file
def save_to_github(dataframe, repo, file_name):
    csv_content = dataframe.to_csv(index=False)
    try:
        contents = repo.get_contents(file_name)
        repo.update_file(contents.path, "Updated historical data", csv_content, contents.sha)
    except:
        repo.create_file(file_name, "Created historical data CSV file", csv_content)

# Main function
def main():
    st.title('Stock Analysis')

    # User input for ticker symbol
    ticker_symbol = st.text_input('Enter the ticker symbol:', 'AAPL').upper()
    
    if ticker_symbol:
        # File name based on ticker symbol
        file_name = f"{ticker_symbol}_historical_data.csv"
        
        # Load historical data from GitHub if it exists
        repo = g.get_user(repo_owner).get_repo(repo_name)
        try:
            contents = repo.get_contents(file_name)
            historical_data = pd.read_csv(contents.download_url, parse_dates=['Date'])
            last_date = historical_data['Date'].max()
            start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        except:
            historical_data = pd.DataFrame()
            start_date = '1900-01-01'  # Fetch data from the earliest available date

        # Fetch and append new data
        new_data = load_historical_data(ticker_symbol, start_date)
        if not historical_data.empty:
            historical_data = pd.concat([historical_data, new_data])
        else:
            historical_data = new_data

        # Save updated historical data to GitHub
        save_to_github(historical_data, repo, file_name)
        
        # Update historical data with live data
        combined_data = update_data(historical_data, ticker_symbol)

        # Display combined data
        st.write('**Combined Data:**')
        st.write(combined_data)

        # Plot closing price
        st.write('**Closing Price Chart:**')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(combined_data.index, combined_data['Close'], label=f'{ticker_symbol} Close Price')
        ax.set_title(f'{ticker_symbol} Stock Closing Price')
        ax.set_xlabel('Date')
        ax.set_ylabel('Closing Price (USD)')
        ax.legend()
        st.pyplot(fig)

if __name__ == '__main__':
    main()
