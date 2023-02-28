import requests
from config import logger
import time

retry_delay = 5

# get the current forecast
def forecast(config):
    # set the forecast url
    forecast_url = 'https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast'.format(office=config['office'], gridX=config['gridX'], gridY=config['gridY'])
    # get the forecast data
    try:
        data = requests.get(forecast_url).json()
    # log any errors from the request
    except Exception as e:
        logger.error('Error getting forecast data, retrying')
        time.sleep(retry_delay)
        # try again
        return forecast(config)        
    # check that the forecast data has properties, and if not log an error
    if 'properties' not in data:
        logger.error('Invalid forecast data, retrying')
        time.sleep(retry_delay)
        # try again
        return forecast(config)
    return data

# get the current alerts
def active_alerts(config):
    # set the active alerts url
    alerts_url = 'https://api.weather.gov/alerts/active?area={state}'.format(state=config['state'])
    # get the active alerts data
    try:
        data = requests.get(alerts_url).json()
    # log any errors from the request
    except Exception as e:
        logger.error('Error getting active alerts data, retrying')
        time.sleep(retry_delay)
        # try again
        return active_alerts(config)
    # check that the active alerts data has features, and if not log an error
    if 'features' not in data:
        logger.error('Invalid active alerts data, retrying')
        time.sleep(retry_delay)
        # try again
        return active_alerts(config)
    return data