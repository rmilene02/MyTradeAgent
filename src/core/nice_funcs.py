"""
🌙 Moon Dev's Nice Functions - A collection of utility functions for trading
Built with love by Moon Dev 🚀
"""

from src.core.config import *
import requests
import pandas as pd
import pprint
import re as reggie
import sys
import os
import time
import json
import numpy as np
import datetime
# import pandas_ta as ta  # Comentado temporariamente devido a problemas de compatibilidade
from datetime import datetime, timedelta
from termcolor import colored, cprint
# import solders  # Removido temporariamente
from dotenv import load_dotenv
import shutil
import atexit

# Load environment variables
load_dotenv()

# Get API keys from environment
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
if not BIRDEYE_API_KEY:
    raise ValueError("🚨 BIRDEYE_API_KEY not found in environment variables!")

sample_address = "2yXTyarttn2pTZ6cwt4DqmrRuBw1G7pmFv9oT6MStdKP"

BASE_URL = "https://public-api.birdeye.so/defi"

# Create temp directory and register cleanup
os.makedirs('temp_data', exist_ok=True)

def cleanup_temp_data():
    if os.path.exists('temp_data'):
        print("🧹 Moon Dev cleaning up temporary data...")
        shutil.rmtree('temp_data')

atexit.register(cleanup_temp_data)

# Custom function to print JSON in a human-readable format
def print_pretty_json(data):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)

# Function to print JSON in a human-readable format - assuming you already have it as print_pretty_json
# Helper function to find URLs in text
def find_urls(string):
    # Regex to extract URLs
    return reggie.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

# UPDATED TO RMEOVE THE OTHER ONE so now we can just use this filter instead of filtering twice
def token_overview(address):
    """
    Fetch token overview for a given address and return structured information, including specific links,
    and assess if any price change suggests a rug pull.
    """

    print(f'Getting the token overview for {address}')
    overview_url = f"{BASE_URL}/token_overview?address={address}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    response = requests.get(overview_url, headers=headers)
    result = {}

    if response.status_code == 200:
        overview_data = response.json().get('data', {})

        # Retrieve buy1h, sell1h, and calculate trade1h
        buy1h = overview_data.get('buy1h', 0)
        sell1h = overview_data.get('sell1h', 0)
        trade1h = buy1h + sell1h

        # Add the calculated values to the result
        result['buy1h'] = buy1h
        result['sell1h'] = sell1h
        result['trade1h'] = trade1h

        # Calculate buy and sell percentages
        total_trades = trade1h  # Assuming total_trades is the sum of buy and sell
        buy_percentage = (buy1h / total_trades * 100) if total_trades else 0
        sell_percentage = (sell1h / total_trades * 100) if total_trades else 0
        result['buy_percentage'] = buy_percentage
        result['sell_percentage'] = sell_percentage

        # Check if trade1h is bigger than MIN_TRADES_LAST_HOUR
        result['minimum_trades_met'] = True if trade1h >= MIN_TRADES_LAST_HOUR else False

        # Extract price changes over different timeframes
        price_changes = {k: v for k, v in overview_data.items() if 'priceChange' in k}
        result['priceChangesXhrs'] = price_changes

        # Check for rug pull indicator
        rug_pull = any(value < -80 for key, value in price_changes.items() if value is not None)
        result['rug_pull'] = rug_pull
        if rug_pull:
            print("Warning: Price change percentage below -80%, potential rug pull")

        # Extract other metrics
        unique_wallet2hr = overview_data.get('uniqueWallet24h', 0)
        v24USD = overview_data.get('v24hUSD', 0)
        watch = overview_data.get('watch', 0)
        view24h = overview_data.get('view24h', 0)
        liquidity = overview_data.get('liquidity', 0)

        # Add the retrieved data to result
        result.update({
            'uniqueWallet2hr': unique_wallet2hr,
            'v24USD': v24USD,
            'watch': watch,
            'view24h': view24h,
            'liquidity': liquidity,
        })

        # Extract and process description links if extensions are not None
        extensions = overview_data.get('extensions', {})
        description = extensions.get('description', '') if extensions else ''
        urls = find_urls(description)
        links = []
        for url in urls:
            if 't.me' in url:
                links.append({'telegram': url})
            elif 'twitter.com' in url:
                links.append({'twitter': url})
            elif 'youtube' not in url:  # Assume other URLs are for website
                links.append({'website': url})

        # Add extracted links to result
        result['description'] = links


        # Return result dictionary with all the data
        return result
    else:
        print(f"Failed to retrieve token overview for address {address}: HTTP status code {response.status_code}")
        return None


def token_security_info(address):

    '''

    bigmatter
​freeze authority is like renouncing ownership on eth

    Token Security Info:
{   'creationSlot': 242801308,
    'creationTime': 1705679481,
    'creationTx': 'ZJGoayaNDf2dLzknCjjaE9QjqxocA94pcegiF1oLsGZ841EMWBEc7TnDKLvCnE8cCVfkvoTNYCdMyhrWFFwPX6R',
    'creatorAddress': 'AGWdoU4j4MGJTkSor7ZSkNiF8oPe15754hsuLmwcEyzC',
    'creatorBalance': 0,
    'creatorPercentage': 0,
    'freezeAuthority': None,
    'freezeable': None,
    'isToken2022': False,
    'isTrueToken': None,
    'lockInfo': None,
    'metaplexUpdateAuthority': 'AGWdoU4j4MGJTkSor7ZSkNiF8oPe15754hsuLmwcEyzC',
    'metaplexUpdateAuthorityBalance': 0,
    'metaplexUpdateAuthorityPercent': 0,
    'mintSlot': 242801308,
    'mintTime': 1705679481,
    'mintTx': 'ZJGoayaNDf2dLzknCjjaE9QjqxocA94pcegiF1oLsGZ841EMWBEc7TnDKLvCnE8cCVfkvoTNYCdMyhrWFFwPX6R',
    'mutableMetadata': True,
    'nonTransferable': None,
    'ownerAddress': None,
    'ownerBalance': None,
    'ownerPercentage': None,
    'preMarketHolder': [],
    'top10HolderBalance': 357579981.3372284,
    'top10HolderPercent': 0.6439307358062863,
    'top10UserBalance': 138709981.9366756,
    'top10UserPercent': 0.24978920911102176,
    'totalSupply': 555308143.3354646,
    'transferFeeData': None,
    'transferFeeEnable': None}
    '''

    # API endpoint for getting token security information
    url = f"{BASE_URL}/token_security?address={address}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    # Sending a GET request to the API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        security_data = response.json()['data']
        print_pretty_json(security_data)
    else:
        print("Failed to retrieve token security info:", response.status_code)

def token_creation_info(address):

    '''
    output sampel =

    Token Creation Info:
{   'decimals': 9,
    'owner': 'AGWdoU4j4MGJTkSor7ZSkNiF8oPe15754hsuLmwcEyzC',
    'slot': 242801308,
    'tokenAddress': '9dQi5nMznCAcgDPUMDPkRqG8bshMFnzCmcyzD8afjGJm',
    'txHash': 'ZJGoayaNDf2dLzknCjjaE9QjqxocA94pcegiF1oLsGZ841EMWBEc7TnDKLvCnE8cCVfkvoTNYCdMyhrWFFwPX6R'}
    '''
    # API endpoint for getting token creation information
    url = f"{BASE_URL}/token_creation_info?address={address}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    # Sending a GET request to the API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        creation_data = response.json()['data']
        print_pretty_json(creation_data)
    else:
        print("Failed to retrieve token creation info:", response.status_code)

def market_buy(token, amount, slippage):
    import requests
    import sys
    import json
    import base64
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts

    KEY = Keypair.from_base58_string(os.getenv("SOLANA_PRIVATE_KEY"))
    if not KEY:
        raise ValueError("🚨 SOLANA_PRIVATE_KEY not found in environment variables!")
    #print('key success')
    SLIPPAGE = slippage # 5000 is 50%, 500 is 5% and 50 is .5%

    QUOTE_TOKEN = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" # usdc

    http_client = Client(os.getenv("RPC_ENDPOINT"))
    #print('http client success')
    if not http_client:
        raise ValueError("🚨 RPC_ENDPOINT not found in environment variables!")

    quote = requests.get(f'https://quote-api.jup.ag/v6/quote?inputMint={QUOTE_TOKEN}&outputMint={token}&amount={amount}&slippageBps={SLIPPAGE}').json()
    #print(quote)

    txRes = requests.post('https://quote-api.jup.ag/v6/swap',
                          headers={"Content-Type": "application/json"},
                          data=json.dumps({
                              "quoteResponse": quote,
                              "userPublicKey": str(KEY.pubkey()),
                              "prioritizationFeeLamports": PRIORITY_FEE  # or replace 'auto' with your specific lamport value
                          })).json()
    #print(txRes)
    swapTx = base64.b64decode(txRes['swapTransaction'])
    #print(swapTx)
    tx1 = VersionedTransaction.from_bytes(swapTx)
    tx = VersionedTransaction(tx1.message, [KEY])
    txId = http_client.send_raw_transaction(bytes(tx), TxOpts(skip_preflight=True)).value
    print(f"https://solscan.io/tx/{str(txId)}")



def market_sell(QUOTE_TOKEN, amount, slippage):
    import requests
    import sys
    import json
    import base64
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts

    KEY = Keypair.from_base58_string(os.getenv("SOLANA_PRIVATE_KEY"))
    if not KEY:
        raise ValueError("🚨 SOLANA_PRIVATE_KEY not found in environment variables!")
    
    SLIPPAGE = slippage  # 5000 is 50%, 500 is 5% and 50 is .5%

    # token would be usdc for sell orders cause we are selling
    token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC

    http_client = Client(os.getenv("RPC_ENDPOINT"))
    if not http_client:
        raise ValueError("🚨 RPC_ENDPOINT not found in environment variables!")

    quote = requests.get(f'https://quote-api.jup.ag/v6/quote?inputMint={QUOTE_TOKEN}&outputMint={token}&amount={amount}&slippageBps={SLIPPAGE}').json()
    
    txRes = requests.post('https://quote-api.jup.ag/v6/swap',
                          headers={"Content-Type": "application/json"},
                          data=json.dumps({
                              "quoteResponse": quote,
                              "userPublicKey": str(KEY.pubkey()),
                              "prioritizationFeeLamports": PRIORITY_FEE
                          })).json()
    
    swapTx = base64.b64decode(txRes['swapTransaction'])
    tx1 = VersionedTransaction.from_bytes(swapTx)
    tx = VersionedTransaction(tx1.message, [KEY])
    txId = http_client.send_raw_transaction(bytes(tx), TxOpts(skip_preflight=True)).value
    print(f"https://solscan.io/tx/{str(txId)}")



def get_time_range():

    now = datetime.now()
    ten_days_earlier = now - timedelta(days=10)
    time_to = int(now.timestamp())
    time_from = int(ten_days_earlier.timestamp())
    #print(time_from, time_to)

    return time_from, time_to

import math
def round_down(value, decimals):
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def get_time_range(days_back):

    now = datetime.now()
    ten_days_earlier = now - timedelta(days=days_back)
    time_to = int(now.timestamp())
    time_from = int(ten_days_earlier.timestamp())
    #print(time_from, time_to)

    return time_from, time_to

def get_data(address, days_back_4_data, timeframe):
    time_from, time_to = get_time_range(days_back_4_data)

    # Check temp data first
    temp_file = f"temp_data/{address}_latest.csv"
    if os.path.exists(temp_file):
        print(f"📂 Moon Dev found cached data for {address[:4]}")
        return pd.read_csv(temp_file)

    url = f"https://public-api.birdeye.so/defi/ohlcv?address={address}&type={timeframe}&time_from={time_from}&time_to={time_to}"

    headers = {"X-API-KEY": BIRDEYE_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        items = json_response.get('data', {}).get('items', [])

        processed_data = [{
            'Datetime (UTC)': datetime.utcfromtimestamp(item['unixTime']).strftime('%Y-%m-%d %H:%M:%S'),
            'Open': item['o'],
            'High': item['h'],
            'Low': item['l'],
            'Close': item['c'],
            'Volume': item['v']
        } for item in items]

        df = pd.DataFrame(processed_data)

        # Remove any rows with dates far in the future
        current_date = datetime.now()
        df['datetime_obj'] = pd.to_datetime(df['Datetime (UTC)'])
        df = df[df['datetime_obj'] <= current_date]
        df = df.drop('datetime_obj', axis=1)

        # Pad if needed
        if len(df) < 40:
            print(f"🌙 MoonDev Alert: Padding data to ensure minimum 40 rows for analysis! 🚀")
            rows_to_add = 40 - len(df)
            first_row_replicated = pd.concat([df.iloc[0:1]] * rows_to_add, ignore_index=True)
            df = pd.concat([first_row_replicated, df], ignore_index=True)

        print(f"📊 MoonDev's Data Analysis Ready! Processing {len(df)} candles... 🎯")

        # Always save to temp for current run
        df.to_csv(temp_file)
        print(f"🔄 Moon Dev cached data for {address[:4]}")

        # Calculate indicators
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA40'] = ta.sma(df['Close'], length=40)

        df['Price_above_MA20'] = df['Close'] > df['MA20']
        df['Price_above_MA40'] = df['Close'] > df['MA40']
        df['MA20_above_MA40'] = df['MA20'] > df['MA40']

        return df
    else:
        print(f"❌ MoonDev Error: Failed to fetch data for address {address}. Status code: {response.status_code}")
        if response.status_code == 401:
            print("🔑 Check your BIRDEYE_API_KEY in .env file!")
        return pd.DataFrame()



def fetch_wallet_holdings_og(address):

    API_KEY = BIRDEYE_API_KEY  # Assume this is your API key; replace it with the actual one

    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=['Mint Address', 'Amount', 'USD Value'])

    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={address}"
    headers = {"x-chain": "solana", "X-API-KEY": API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_response = response.json()

        if 'data' in json_response and 'items' in json_response['data']:
            df = pd.DataFrame(json_response['data']['items'])
            df = df[['address', 'uiAmount', 'valueUsd']]
            df = df.rename(columns={'address': 'Mint Address', 'uiAmount': 'Amount', 'valueUsd': 'USD Value'})
            df = df.dropna()
            df = df[df['USD Value'] > 0.05]
        else:
            cprint("No data available in the response.", 'white', 'on_red')

    else:
        cprint(f"Failed to retrieve token list for {address}.", 'white', 'on_magenta')

    # Print the DataFrame if it's not empty
    if not df.empty:
        print(df)
        # Assuming cprint is a function you have for printing in color
        cprint(f'** Total USD balance is {df["USD Value"].sum()}', 'white', 'on_green')
        # Save the filtered DataFrame to a CSV file
        # TOKEN_PER_ADDY_CSV = 'filtered_wallet_holdings.csv'  # Define your CSV file name
        # df.to_csv(TOKEN_PER_ADDY_CSV, index=False)
    else:
        # If the DataFrame is empty, print a message or handle it as needed
        cprint("No wallet holdings to display.", 'white', 'on_red')

    return df

def fetch_wallet_token_single(address, token_mint_address):

    df = fetch_wallet_holdings_og(address)

    # filter by token mint address
    df = df[df['Mint Address'] == token_mint_address]

    return df


def token_price(address):
    url = f"https://public-api.birdeye.so/defi/price?address={address}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}
    response = requests.get(url, headers=headers)
    price_data = response.json()

    print(price_data)

    if price_data['success']:
        return price_data['data']['value']
    else:
        return None
    
# price = token_price('2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv')
# print(price)
# time.sleep(897)


def get_position(token_mint_address):
    """
    Fetches the balance of a specific token given its mint address from a DataFrame.

    Parameters:
    - dataframe: A pandas DataFrame containing token balances with columns ['Mint Address', 'Amount'].
    - token_mint_address: The mint address of the token to find the balance for.

    Returns:
    - The balance of the specified token if found, otherwise a message indicating the token is not in the wallet.
    """
    dataframe = fetch_wallet_token_single(address, token_mint_address)

    #dataframe = pd.read_csv('data/token_per_addy.csv')

    print('-----------------')
    #print(dataframe)

    #print(dataframe)

    # Check if the DataFrame is empty
    if dataframe.empty:
        print("The DataFrame is empty. No positions to show.")
        return 0  # Indicating no balance found

    # Ensure 'Mint Address' column is treated as string for reliable comparison
    dataframe['Mint Address'] = dataframe['Mint Address'].astype(str)

    # Check if the token mint address exists in the DataFrame
    if dataframe['Mint Address'].isin([token_mint_address]).any():
        # Get the balance for the specified token
        balance = dataframe.loc[dataframe['Mint Address'] == token_mint_address, 'Amount'].iloc[0]
        #print(f"Balance for {token_mint_address[-4:]} token: {balance}")
        return balance
    else:
        # If the token mint address is not found in the DataFrame, return a message indicating so
        print("Token mint address not found in the wallet.")
        return 0  # Indicating no balance found


def get_decimals(token_mint_address):
    import requests
    import base64
    import json
    # Solana Mainnet RPC endpoint
    url = "https://api.mainnet-beta.solana.com/"
    headers = {"Content-Type": "application/json"}

    # Request payload to fetch account information
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            token_mint_address,
            {
                "encoding": "jsonParsed"
            }
        ]
    })

    # Make the request to Solana RPC
    response = requests.post(url, headers=headers, data=payload)
    response_json = response.json()

    # Parse the response to extract the number of decimals
    decimals = response_json['result']['value']['data']['parsed']['info']['decimals']
    #print(f"Decimals for {token_mint_address[-4:]} token: {decimals}")

    return decimals

def pnl_close(token_mint_address):

    ''' this will check to see if price is > sell 1, sell 2, sell 3 and sell accordingly '''

    print(f'checking pnl close to see if its time to exit for {token_mint_address[:4]}...')
    # check solana balance


    # if time is on the 5 minute do the balance check, if not grab from data/current_position.csv
    balance = get_position(token_mint_address)

    # save to data/current_position.csv w/ pandas

    # get current price of token
    price = token_price(token_mint_address)

    usd_value = balance * price

    tp = sell_at_multiple * USDC_SIZE
    sl = ((1+stop_loss_percentage) * USDC_SIZE)
    sell_size = balance
    decimals = 0
    decimals = get_decimals(token_mint_address)
    #print(f'for {token_mint_address[-4:]} decimals is {decimals}')

    sell_size = int(sell_size * 10 **decimals)

    #print(f'bal: {balance} price: {price} usdVal: {usd_value} TP: {tp} sell size: {sell_size} decimals: {decimals}')

    while usd_value > tp:


        cprint(f'for {token_mint_address[:4]} value is {usd_value} and tp is {tp} so closing...', 'white', 'on_green')
        try:

            market_sell(token_mint_address, sell_size)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_green')
            time.sleep(2)
            market_sell(token_mint_address, sell_size)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_green')
            time.sleep(2)
            market_sell(token_mint_address, sell_size)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_green')
            time.sleep(15)

        except:
            cprint('order error.. trying again', 'white', 'on_red')
            time.sleep(2)

        balance = get_position(token_mint_address)
        price = token_price(token_mint_address)
        usd_value = balance * price
        tp = sell_at_multiple * USDC_SIZE
        sell_size = balance
        sell_size = int(sell_size * 10 **decimals)
        print(f'USD Value is {usd_value} | TP is {tp} ')


    else:
        #print(f'for {token_mint_address[-4:]} value is {usd_value} and tp is {tp} so not closing...')
        hi = 'hi'
        #time.sleep(10)

    # while usd_value < sl but bigger than .05

    if usd_value != 0:
        #print(f'for {token_mint_address[-4:]} value is {usd_value} and sl is {sl} so not closing...')

        while usd_value < sl and usd_value > 0:

            sell_size = balance
            sell_size = int(sell_size * 10 **decimals)

            cprint(f'for {token_mint_address[:4]} value is {usd_value} and sl is {sl} so closing as a loss...', 'white', 'on_blue')

            #print(f'for {token_mint_address[-4:]} value is {usd_value} and tp is {tp} so closing...')
            try:

                market_sell(token_mint_address, sell_size)
                cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
                time.sleep(1)
                market_sell(token_mint_address, sell_size)
                cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
                time.sleep(1)
                market_sell(token_mint_address, sell_size)
                cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
                time.sleep(15)

            except:
                cprint('order error.. trying again', 'white', 'on_red')
                # time.sleep(7)

            balance = get_position(token_mint_address)
            price = token_price(token_mint_address)
            usd_value = balance * price
            tp = sell_at_multiple * USDC_SIZE
            sl = ((1+stop_loss_percentage) * USDC_SIZE)
            sell_size = balance

            sell_size = int(sell_size * 10 **decimals)
            print(f'balance is {balance} and price is {price} and usd_value is {usd_value} and tp is {tp} and sell_size is {sell_size} decimals is {decimals}')

            # break the loop if usd_value is 0
            if usd_value == 0:
                print(f'successfully closed {token_mint_address[:4]} usd_value is {usd_value} so breaking loop AFTER putting it on my dont_overtrade.txt...')
                with open('dont_overtrade.txt', 'a') as file:
                    file.write(token_mint_address + '\n')
                break

        else:
            print(f'for {token_mint_address[:4]} value is {usd_value} and tp is {tp} so not closing...')
            #time.sleep(10)
    else:
        print(f'for {token_mint_address[:4]} value is {usd_value} and tp is {tp} so not closing...')

def chunk_kill(token_mint_address, max_usd_order_size, slippage):
    """Kill a position in chunks"""
    cprint(f"\n🔪 Moon Dev's AI Agent initiating position exit...", "white", "on_cyan")
    
    try:
        # Get current position using address from config
        df = fetch_wallet_token_single(address, token_mint_address)
        if df.empty:
            cprint("❌ No position found to exit", "white", "on_red")
            return
            
        # Get current token amount and value
        token_amount = float(df['Amount'].iloc[0])
        current_usd_value = float(df['USD Value'].iloc[0])
        
        # Get token decimals
        decimals = get_decimals(token_mint_address)
        
        cprint(f"📊 Initial position: {token_amount:.2f} tokens (${current_usd_value:.2f})", "white", "on_cyan")
        
        while current_usd_value > 0.1:  # Keep going until position is essentially zero
            # Calculate chunk size based on current position
            chunk_size = token_amount / 3  # Split remaining into 3 chunks
            cprint(f"\n🔄 Splitting remaining position into chunks of {chunk_size:.2f} tokens", "white", "on_cyan")
            
            # Execute sell orders in chunks
            for i in range(3):
                try:
                    cprint(f"\n💫 Executing sell chunk {i+1}/3...", "white", "on_cyan")
                    sell_size = int(chunk_size * 10**decimals)
                    market_sell(token_mint_address, sell_size, slippage)
                    cprint(f"✅ Sell chunk {i+1}/3 complete", "white", "on_green")
                    time.sleep(2)  # Small delay between chunks
                except Exception as e:
                    cprint(f"❌ Error in sell chunk: {str(e)}", "white", "on_red")
            
            # Check remaining position
            time.sleep(5)  # Wait for blockchain to update
            df = fetch_wallet_token_single(address, token_mint_address)
            if df.empty:
                cprint("\n✨ Position successfully closed!", "white", "on_green")
                return
                
            # Update position size for next iteration
            token_amount = float(df['Amount'].iloc[0])
            current_usd_value = float(df['USD Value'].iloc[0])
            cprint(f"\n📊 Remaining position: {token_amount:.2f} tokens (${current_usd_value:.2f})", "white", "on_cyan")
            
            if current_usd_value > 0.1:
                cprint("🔄 Position still open - continuing to close...", "white", "on_cyan")
                time.sleep(2)
            
        cprint("\n✨ Position successfully closed!", "white", "on_green")
        
    except Exception as e:
        cprint(f"❌ Error during position exit: {str(e)}", "white", "on_red")

def sell_token(token_mint_address, amount, slippage):
    """Sell a token"""
    try:
        cprint(f"📉 Selling {amount:.2f} tokens...", "white", "on_cyan")
        # Your existing sell logic here
        print(f"just made an order {token_mint_address[:4]} selling {int(amount)} ...")
    except Exception as e:
        cprint(f"❌ Error selling token: {str(e)}", "white", "on_red")

def kill_switch(token_mint_address):

    ''' this function closes the position in full

    if the usd_size > 10k then it will chunk in 10k orders
    '''

    # if time is on the 5 minute do the balance check, if not grab from data/current_position.csv
    balance = get_position(token_mint_address)

    # get current price of token
    price = token_price(token_mint_address)
    price = float(price)

    usd_value = balance * price

    if usd_value < 10000:
        sell_size = balance
    else:
        sell_size = 10000/price

    tp = sell_at_multiple * USDC_SIZE

    # round to 2 decimals
    sell_size = round_down(sell_size, 2)
    decimals = 0
    decimals = get_decimals(token_mint_address)
    sell_size = int(sell_size * 10 **decimals)

    #print(f'bal: {balance} price: {price} usdVal: {usd_value} TP: {tp} sell size: {sell_size} decimals: {decimals}')

    while usd_value > 0:


# 100 selling 70% ...... selling 30 left
        #print(f'for {token_mint_address[-4:]} closing position cause exit all positions is set to {EXIT_ALL_POSITIONS} and value is {usd_value} and tp is {tp} so closing...')
        try:

            market_sell(token_mint_address, sell_size)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
            time.sleep(1)
            market_sell(token_mint_address, sell_size)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
            time.sleep(1)
            market_sell(token_mint_address, sell_size)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
            time.sleep(15)

        except:
            cprint('order error.. trying again', 'white', 'on_red')
            # time.sleep(7)

        balance = get_position(token_mint_address)
        price = token_price(token_mint_address)
        usd_value = balance * price
        tp = sell_at_multiple * USDC_SIZE

        if usd_value < 10000:
            sell_size = balance
        else:
            sell_size = 10000/price

        # down downwards to 2 decimals
        sell_size = round_down(sell_size, 2)

        decimals = 0
        decimals = get_decimals(token_mint_address)
        #print(f'xxxxxxxxx for {token_mint_address[-4:]} decimals is {decimals}')
        sell_size = int(sell_size * 10 **decimals)
        print(f'balance is {balance} and usd_value is {usd_value} EXIT ALL POSITIONS TRUE and sell_size is {sell_size} decimals is {decimals}')


    else:
        print(f'for {token_mint_address[:4]} value is {usd_value} ')
        #time.sleep(10)

    print('closing position in full...')

def close_all_positions():

    # get all positions
    open_positions = fetch_wallet_holdings_og(address)

    # loop through all positions and close them getting the mint address from Mint Address column
    for index, row in open_positions.iterrows():
        token_mint_address = row['Mint Address']

        # Check if the current token mint address is the USDC contract address
        cprint(f'this is the token mint address {token_mint_address} this is don not trade list {dont_trade_list}', 'white', 'on_magenta')
        if token_mint_address in dont_trade_list:
            print(f'Skipping kill switch for USDC contract at {token_mint_address}')
            continue  # Skip the rest of the loop for this iteration

        print(f'Closing position for {token_mint_address}...')
        kill_switch(token_mint_address)

def delete_dont_overtrade_file():
    if os.path.exists('dont_overtrade.txt'):
        os.remove('dont_overtrade.txt')
        print('dont_overtrade.txt has been deleted')
    else:
        print('The file does not exist')

def supply_demand_zones(token_address, timeframe, limit):

    print('starting moons supply and demand zone calculations..')

    sd_df = pd.DataFrame()

    time_from, time_to = get_time_range()

    df = get_data(token_address, time_from, time_to, timeframe)

    # only keep the data for as many bars as limit says
    df = df[-limit:]
    #print(df)
    #time.sleep(100)

    # Calculate support and resistance, excluding the last two rows for the calculation
    if len(df) > 2:  # Check if DataFrame has more than 2 rows to avoid errors
        df['support'] = df[:-2]['Close'].min()
        df['resis'] = df[:-2]['Close'].max()
    else:  # If DataFrame has 2 or fewer rows, use the available 'close' prices for calculation
        df['support'] = df['Close'].min()
        df['resis'] = df['Close'].max()

    supp = df.iloc[-1]['support']
    resis = df.iloc[-1]['resis']
    #print(f'this is moons support for 1h {supp_1h} this is resis: {resis_1h}')

    df['supp_lo'] = df[:-2]['Low'].min()
    supp_lo = df.iloc[-1]['supp_lo']

    df['res_hi'] = df[:-2]['High'].max()
    res_hi = df.iloc[-1]['res_hi']

    #print(df)


    sd_df[f'dz'] = [supp_lo, supp]
    sd_df[f'sz'] = [res_hi, resis]

    print('here are moons supply and demand zones')
    #print(sd_df)

    return sd_df


def elegant_entry(symbol, buy_under):

    pos = get_position(symbol)
    price = token_price(symbol)
    pos_usd = pos * price
    size_needed = usd_size - pos_usd
    if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
    else: chunk_size = size_needed

    chunk_size = int(chunk_size * 10**6)
    chunk_size = str(chunk_size)

    print(f'chunk_size: {chunk_size}')

    if pos_usd > (.97 * usd_size):
        print('position filled')
        time.sleep(10)

    # add debug prints for next while
    print(f'position: {round(pos,2)} price: {round(price,8)} pos_usd: ${round(pos_usd,2)}')
    print(f'buy_under: {buy_under}')
    while pos_usd < (.97 * usd_size) and (price < buy_under):

        print(f'position: {round(pos,2)} price: {round(price,8)} pos_usd: ${round(pos_usd,2)}')

        try:

            for i in range(orders_per_open):
                market_buy(symbol, chunk_size, slippage)
                # cprint green background black text
                cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size} you my dawg moon dev', 'white', 'on_blue')
                time.sleep(1)

            time.sleep(tx_sleep)

            pos = get_position(symbol)
            price = token_price(symbol)
            pos_usd = pos * price
            size_needed = usd_size - pos_usd
            if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
            else: chunk_size = size_needed
            chunk_size = int(chunk_size * 10**6)
            chunk_size = str(chunk_size)

        except:

            try:
                cprint(f'trying again to make the order in 30 seconds.....', 'light_blue', 'on_light_magenta')
                time.sleep(30)
                for i in range(orders_per_open):
                    market_buy(symbol, chunk_size, slippage)
                    # cprint green background black text
                    cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size} you my dawg moon dev', 'white', 'on_blue')
                    time.sleep(1)

                time.sleep(tx_sleep)
                pos = get_position(symbol)
                price = token_price(symbol)
                pos_usd = pos * price
                size_needed = usd_size - pos_usd
                if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
                else: chunk_size = size_needed
                chunk_size = int(chunk_size * 10**6)
                chunk_size = str(chunk_size)


            except:
                cprint(f'Final Error in the buy, restart needed', 'white', 'on_red')
                time.sleep(10)
                break

        pos = get_position(symbol)
        price = token_price(symbol)
        pos_usd = pos * price
        size_needed = usd_size - pos_usd
        if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
        else: chunk_size = size_needed
        chunk_size = int(chunk_size * 10**6)
        chunk_size = str(chunk_size)


# like the elegant entry but for breakout so its looking for price > BREAKOUT_PRICE
def breakout_entry(symbol, BREAKOUT_PRICE):

    pos = get_position(symbol)
    price = token_price(symbol)
    price = float(price)
    pos_usd = pos * price
    size_needed = usd_size - pos_usd
    if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
    else: chunk_size = size_needed

    chunk_size = int(chunk_size * 10**6)
    chunk_size = str(chunk_size)

    print(f'chunk_size: {chunk_size}')

    if pos_usd > (.97 * usd_size):
        print('position filled')
        time.sleep(10)

    # add debug prints for next while
    print(f'position: {round(pos,2)} price: {round(price,8)} pos_usd: ${round(pos_usd,2)}')
    print(f'breakoutpurce: {BREAKOUT_PRICE}')
    while pos_usd < (.97 * usd_size) and (price > BREAKOUT_PRICE):

        print(f'position: {round(pos,2)} price: {round(price,8)} pos_usd: ${round(pos_usd,2)}')

        # for i in range(orders_per_open):
        #     market_buy(symbol, chunk_size, slippage)
        #     # cprint green background black text
        #     cprint(f'chunk buy submitted of {symbol[-4:]} sz: {chunk_size} you my dawg moon dev', 'white', 'on_blue')
        #     time.sleep(1)

        # time.sleep(tx_sleep)

        # pos = get_position(symbol)
        # price = token_price(symbol)
        # pos_usd = pos * price
        # size_needed = usd_size - pos_usd
        # if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
        # else: chunk_size = size_needed
        # chunk_size = int(chunk_size * 10**6)
        # chunk_size = str(chunk_size)

        try:

            for i in range(orders_per_open):
                market_buy(symbol, chunk_size, slippage)
                # cprint green background black text
                cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size} you my dawg moon dev', 'white', 'on_blue')
                time.sleep(1)

            time.sleep(tx_sleep)

            pos = get_position(symbol)
            price = token_price(symbol)
            pos_usd = pos * price
            size_needed = usd_size - pos_usd
            if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
            else: chunk_size = size_needed
            chunk_size = int(chunk_size * 10**6)
            chunk_size = str(chunk_size)

        except:

            try:
                cprint(f'trying again to make the order in 30 seconds.....', 'light_blue', 'on_light_magenta')
                time.sleep(30)
                for i in range(orders_per_open):
                    market_buy(symbol, chunk_size, slippage)
                    # cprint green background black text
                    cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size} you my dawg moon dev', 'white', 'on_blue')
                    time.sleep(1)

                time.sleep(tx_sleep)
                pos = get_position(symbol)
                price = token_price(symbol)
                pos_usd = pos * price
                size_needed = usd_size - pos_usd
                if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
                else: chunk_size = size_needed
                chunk_size = int(chunk_size * 10**6)
                chunk_size = str(chunk_size)


            except:
                cprint(f'Final Error in the buy, restart needed', 'white', 'on_red')
                time.sleep(10)
                break

        pos = get_position(symbol)
        price = token_price(symbol)
        pos_usd = pos * price
        size_needed = usd_size - pos_usd
        if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
        else: chunk_size = size_needed
        chunk_size = int(chunk_size * 10**6)
        chunk_size = str(chunk_size)



def ai_entry(symbol, amount):
    """AI agent entry function for Moon Dev's trading system 🤖"""
    cprint("🤖 Moon Dev's AI Trading Agent initiating position entry...", "white", "on_blue")
    
    # amount passed in is the target allocation (up to 30% of usd_size)
    target_size = amount  # This could be up to $3 (30% of $10)
    
    pos = get_position(symbol)
    price = token_price(symbol)
    pos_usd = pos * price
    
    cprint(f"🎯 Target allocation: ${target_size:.2f} USD (max 30% of ${usd_size})", "white", "on_blue")
    cprint(f"📊 Current position: ${pos_usd:.2f} USD", "white", "on_blue")
    
    # Check if we're already at or above target
    if pos_usd >= (target_size * 0.97):
        cprint("✋ Position already at or above target size!", "white", "on_blue")
        return
        
    # Calculate how much more we need to buy
    size_needed = target_size - pos_usd
    if size_needed <= 0:
        cprint("🛑 No additional size needed", "white", "on_blue")
        return
        
    # For order execution, we'll chunk into max_usd_order_size pieces
    if size_needed > max_usd_order_size: 
        chunk_size = max_usd_order_size
    else: 
        chunk_size = size_needed

    chunk_size = int(chunk_size * 10**6)
    chunk_size = str(chunk_size)
    
    cprint(f"💫 Entry chunk size: {chunk_size} (chunking ${size_needed:.2f} into ${max_usd_order_size:.2f} orders)", "white", "on_blue")

    while pos_usd < (target_size * 0.97):
        cprint(f"🤖 AI Agent executing entry for {symbol[:8]}...", "white", "on_blue")
        print(f"Position: {round(pos,2)} | Price: {round(price,8)} | USD Value: ${round(pos_usd,2)}")

        try:
            for i in range(orders_per_open):
                market_buy(symbol, chunk_size, slippage)
                cprint(f"🚀 AI Agent placed order {i+1}/{orders_per_open} for {symbol[:8]}", "white", "on_blue")
                time.sleep(1)

            time.sleep(tx_sleep)
            
            # Update position info
            pos = get_position(symbol)
            price = token_price(symbol)
            pos_usd = pos * price
            
            # Break if we're at or above target
            if pos_usd >= (target_size * 0.97):
                break
                
            # Recalculate needed size
            size_needed = target_size - pos_usd
            if size_needed <= 0:
                break
                
            # Determine next chunk size
            if size_needed > max_usd_order_size: 
                chunk_size = max_usd_order_size
            else: 
                chunk_size = size_needed
            chunk_size = int(chunk_size * 10**6)
            chunk_size = str(chunk_size)

        except Exception as e:
            try:
                cprint("🔄 AI Agent retrying order in 30 seconds...", "white", "on_blue")
                time.sleep(30)
                for i in range(orders_per_open):
                    market_buy(symbol, chunk_size, slippage)
                    cprint(f"🚀 AI Agent retry order {i+1}/{orders_per_open} for {symbol[:8]}", "white", "on_blue")
                    time.sleep(1)

                time.sleep(tx_sleep)
                pos = get_position(symbol)
                price = token_price(symbol)
                pos_usd = pos * price
                
                if pos_usd >= (target_size * 0.97):
                    break
                    
                size_needed = target_size - pos_usd
                if size_needed <= 0:
                    break
                    
                if size_needed > max_usd_order_size: 
                    chunk_size = max_usd_order_size
                else: 
                    chunk_size = size_needed
                chunk_size = int(chunk_size * 10**6)
                chunk_size = str(chunk_size)

            except:
                cprint("❌ AI Agent encountered critical error, manual intervention needed", "white", "on_red")
                return

    cprint("✨ AI Agent completed position entry", "white", "on_blue")

def get_token_balance_usd(token_mint_address):
    """Get the USD value of a token position for Moon Dev's wallet 🌙"""
    try:
        # Get the position data using existing function
        df = fetch_wallet_token_single(address, token_mint_address)  # Using address from config
        
        if df.empty:
            print(f"🔍 No position found for {token_mint_address[:8]}")
            return 0.0
            
        # Get the USD Value from the dataframe
        usd_value = df['USD Value'].iloc[0]
        return float(usd_value)
        
    except Exception as e:
        print(f"❌ Error getting token balance: {str(e)}")
        return 0.0