from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import matplotlib

matplotlib.use('Agg')  # Use a non-GUI backend for rendering

app = Flask(__name__)

# Load datasets
fundamentals = pd.read_csv('fundamentals.csv')
prices = pd.read_csv('prices.csv')
prices_adjusted = pd.read_csv('prices_split_adjusted.csv')
securities = pd.read_csv('security.csv')

# Rename columns for consistency
fundamentals.rename(columns={'Ticker Symbol': 'symbol'}, inplace=True)
securities.rename(columns={'Ticker symbol': 'symbol'}, inplace=True)

# Merge datasets
combined_data = prices_adjusted.merge(securities, on='symbol', how='inner')
combined_data = combined_data.merge(fundamentals, on='symbol', how='inner')

@app.route('/')
def index():
    # Verify and rename columns dynamically
    columns_mapping = {
        'Net Income': 'Net Income',
    }

    # Match exact column names
    available_columns = fundamentals.columns
    for key, value in columns_mapping.items():
        if key not in available_columns:
            columns_mapping[key] = None

    # Get the top 10 companies by Net Income
    selected_columns = ['symbol', 'Net Income']
    selected_columns = [col for col in selected_columns if col in fundamentals.columns]
    top_companies = fundamentals[selected_columns].copy()
    top_companies = top_companies.sort_values(by='Net Income', ascending=False).head(10)

    # Add company details from the securities dataset
    top_companies = top_companies.merge(securities[['symbol', 'Security']], on='symbol', how='inner')
    return render_template('index.html', companies=top_companies)
@app.route('/metrics', methods=['GET'])
def metrics():
    # Get the selected symbol from the query parameters
    symbol = request.args.get('symbol')
    if not symbol:
        return "Error: No company selected", 400  # Handle the case where no symbol is passed

    # Filter the stock's price data
    stock_data = combined_data[combined_data['symbol'] == symbol].sort_values(by='date')
    
    # Check if stock_data is empty
    if stock_data.empty:
        return f"Error: No data found for symbol {symbol}", 404

    # Calculate daily returns
    stock_data['daily_return'] = stock_data['close'].pct_change()
    
    # Calculate annualized return and volatility
    annual_return = stock_data['daily_return'].mean() * 252
    annual_volatility = stock_data['daily_return'].std() * np.sqrt(252)
    
    # Generate a plot for stock performance
    plt.figure(figsize=(10, 6))
    plt.plot(stock_data['date'], stock_data['close'], label='Close Price')
    plt.title(f"{symbol} Stock Performance")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.grid()
    
    # Save the plot to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    # Return metrics and plot
    return render_template('metrics.html', symbol=symbol, annual_return=annual_return,
                           annual_volatility=annual_volatility, plot_data=plot_data)

if __name__ == '__main__':
    app.run(debug=True)
