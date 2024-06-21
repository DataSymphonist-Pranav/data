import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from github import Github
import os

# Function to get the GitHub token from Streamlit secrets
def get_github_token():
    return st.secrets["GITHUB_TOKEN"]

# Function to get the repository
def get_repo(github_token, repo_name):
    g = Github(github_token)
    repo = g.get_user().get_repo(repo_name)
    return repo

# Load historical data from the CSV file
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    return data

# Save data to CSV file
def save_data(csv_file, data):
    data.to_csv(csv_file, index=False)

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
    st.title('Stock Analysis')

    # User input for ticker symbol
    ticker_symbol = st.text_input('Enter the ticker symbol:', 'AAPL')

    # Fetch historical data
    ticker = yf.Ticker(ticker_symbol)
    historical_data = ticker.history(period='max')

    # Save historical data to CSV file
    csv_file = f'{ticker_symbol}_stock_data.csv'
    if not os.path.exists(csv_file):
        save_data(csv_file, historical_data)

    # Load historical data
    historical_data = load_data(csv_file)

    # Update historical data with live data
    combined_data = update_data(historical_data, ticker_symbol)

    # Save the updated data
    save_data(csv_file, combined_data)

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

    # Upload the CSV file to GitHub
    github_token = get_github_token()
    repo = get_repo(github_token, 'data')
    with open(csv_file, 'r') as file:
        content = file.read()
        try:
            contents = repo.get_contents(csv_file)
            repo.update_file(contents.path, f"Update {ticker_symbol} data", content, contents.sha)
        except:
            repo.create_file(csv_file, f"Create {ticker_symbol} data", content)

if __name__ == '__main__':
    main()
