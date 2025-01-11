import pandas as pd

# Load datasets
fundamentals = pd.read_csv('fundamentals.csv')
prices = pd.read_csv('prices-split-adjusted.csv')
securities = pd.read_csv('securities.csv')

# Rename columns for consistency
fundamentals.rename(columns={'Ticker Symbol': 'symbol'}, inplace=True)
securities.rename(columns={'Ticker symbol': 'symbol'}, inplace=True)

# Merge datasets
prices['date'] = pd.to_datetime(prices['date'])  # Ensure 'date' is in datetime format
combined_data = prices.merge(fundamentals, on='symbol', how='inner')
combined_data = combined_data.merge(securities, on='symbol', how='inner')

# Verify the merged data
print(combined_data.info())
print(combined_data.head())
