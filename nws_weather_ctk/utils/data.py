import requests
from nws_weather_ctk.utils.config import logger, load_config
import time

# retry delay in seconds
retry_delay = 5

# get the current forecast
def hourly_forecast(config):
    # set the forecast url
    # ignore the error if the office, gridX, or gridY are not available
    try:
        forecast_url = 'https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast/hourly'.format(office=config['office'], gridX=config['gridX'], gridY=config['gridY'])
    except Exception:
        pass
    else:
        # get the forecast data
        try:
            data = requests.get(forecast_url).json()
        # log any errors from the request
        except Exception as e:
            logger.error('Failed to fetch hourly forecast data, retrying')
            time.sleep(retry_delay)
            # try again
            return hourly_forecast(config)        
        # check that the forecast data has properties, and if not log an error
        if 'properties' not in data:
            logger.error('Failed to fetch hourly forecast data, retrying')
            time.sleep(retry_delay)
            # try again
            return hourly_forecast(config)
        return data

# get the detailed forecast
def detailed_forecast(config):
    # set the detailed forecast url
    # ignore the error if the office, gridX, or gridY are not available
    try:
        forecast_url = 'https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast'.format(office=config['office'], gridX=config['gridX'], gridY=config['gridY'])
    except Exception:
        pass
    else:
        # get the detailed forecast data
        try:
            data = requests.get(forecast_url).json()
        # log any errors from the request
        except Exception as e:
            logger.error('Failed to fetch detailed forecast data, retrying')
            time.sleep(retry_delay)
            # try again
            return detailed_forecast(config)
        # check that the detailed forecast data has properties, and if not log an error
        if 'properties' not in data:
            logger.error('Failed to fetch detailed forecast data, retrying')
            time.sleep(retry_delay)
            # try again
            return detailed_forecast(config)
        return data

# get the current alerts
def active_alerts(config):
    # set the active alerts url
    # ignore the error if the state is not available
    try:
        alerts_url = 'https://api.weather.gov/alerts/active?area={state}'.format(state=config['state'])
    except Exception:
        pass
    else:
        # get the active alerts data
        try:
            data = requests.get(alerts_url).json()
        # log any errors from the request
        except Exception as e:
            logger.error('Failed to fetch active alerts data, retrying')
            time.sleep(retry_delay)
            # try again
            return active_alerts(config)
        # check that the active alerts data has features, and if not log an error
        if 'features' not in data:
            logger.error('Failed to fetch active alerts data, retrying')
            time.sleep(retry_delay)
            # try again
            return active_alerts(config)
        return data
    
def filter_alerts(active_alerts_data):
    # load the config file
    config = load_config()

    # make a dictionary of alerts that match the location
    alert_matches = {}

    # for each alert check if the county name is in the alert area description
    for alert in active_alerts_data['features']:
        if config['county'] in alert['properties']['areaDesc']:
            # store the alert in a dictionary with the event as the key
            alert_matches[alert['properties']['event']] = {
                'description': alert['properties']['description'],
                'instruction': alert['properties']['instruction'],
                'event': alert['properties']['event']
            }
    return alert_matches