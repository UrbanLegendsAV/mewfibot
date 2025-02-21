import requests
import logging
from config import COINMARKETCAP_API_KEY, COINMARKETCAP_URL, ERROR_MESSAGES

logger = logging.getLogger(__name__)

def get_crypto_prices():
    """Fetch XRP, BTC, and ETH prices from CoinMarketCap API"""
    try:
        headers = {
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
            'Accept': 'application/json'
        }
        params = {
            'symbol': 'XRP,BTC,ETH',
            'convert': 'USD'
        }
        
        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()['data']
        
        prices = {}
        for symbol in ['XRP', 'BTC', 'ETH']:
            crypto_data = data[symbol]
            quote = crypto_data['quote']['USD']
            prices[symbol] = {
                'price': round(quote['price'], 2 if symbol != 'XRP' else 4),
                'change_24h': round(quote['percent_change_24h'], 2)
            }
        
        return prices
    except Exception as e:
        logger.error(f'Error fetching crypto prices: {str(e)}')
        return None