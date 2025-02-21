import requests
import logging
from config import COINMARKETCAP_API_KEY, COINMARKETCAP_URL, ERROR_MESSAGES

logger = logging.getLogger(__name__)

def get_xrp_price():
    """Fetch XRP price from CoinMarketCap API"""
    try:
        headers = {
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
            'Accept': 'application/json'
        }
        params = {
            'symbol': 'XRP',
            'convert': 'USD'
        }
        
        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        xrp_data = data['data']['XRP']
        
        price = xrp_data['quote']['USD']['price']
        change_24h = xrp_data['quote']['USD']['percent_change_24h']
        
        return {
            'price': round(price, 4),
            'change_24h': round(change_24h, 2)
        }
    except Exception as e:
        logger.error(f'Error fetching XRP price: {str(e)}')
        return None
