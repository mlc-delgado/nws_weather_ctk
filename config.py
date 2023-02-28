import requests
import os
import yaml
import time
import logging

# set up logger
logger = logging.getLogger(__name__)
# set the logging level
logging.basicConfig(level=logging.INFO)
# set the logging format
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# set the logging file
logging.basicConfig(filename='nws_weather_ctk.log', filemode='w')

retry_delay = 5

# load the config file
def load_config():
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
        config = yaml.safe_load(f)
    f.close()
    return config

# clear the config file
def clear_config():
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
        yaml.dump({}, f)
    f.close()

# Update the config file
def update(city, postalCode):
    config = {'city': city, 'postalCode': postalCode}
    # Set the geocoding url from MAPS
    geocode_url = 'https://geocode.maps.co/search?postalcode={postalCode}'.format(postalCode=config['postalCode'])

    # Get latitude and longitude from the geocoding API
    try:
        geocode_data = requests.get(geocode_url).json()
        # Set the latitude and longitude from the geocoding data
        config['latitude'] = geocode_data[0]['lat']
        config['longitude'] = geocode_data[0]['lon']
    # If the geocoding API fails, try again
    except Exception as e:
        logger.error('Error getting geocoding data, please check your location and try again. Error: {}'.format(e))
        exit(1)

    # Set the reverse geocoding url from MAPS
    reverse_geocode_url = 'https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}'.format(latitude=config['latitude'], longitude=config['longitude'])

    # Extract the county and state from the reverse geocoding API
    try:
        reverse_geocode_data = requests.get(reverse_geocode_url).json()
        config['county'] = reverse_geocode_data['address']['county']
        config['state'] = reverse_geocode_data['address']['state']
    # If the reverse geocoding API fails, try again
    except Exception as e:
        logger.error('Error getting reverse geocoding data, please check your location and try again. Error: {}'.format(e))
        exit(1)
    
    # Remove " County" from the county if it contains it
    if ' County' in config['county']:
        config['county'] = config['county'].replace(' County', '')

    # Fetch forecast data from the NWS API

    # set the points url
    points_url = 'https://api.weather.gov/points/{latitude},{longitude}'.format(latitude=config['latitude'], longitude=config['longitude'])

    try:
        # get the office and gridX, gridY from the points url
        points_data = requests.get(points_url).json()
        config['office'] = points_data['properties']['gridId']
        config['gridX'] = str(points_data['properties']['gridX'])
        config['gridY'] = str(points_data['properties']['gridY'])
    # If the points API fails log an error
    except Exception as e:
        logger.error('Error getting points data, please check your location and try again. Error: {}'.format(e))
        exit(1)

    # Load the list of state abbreviations from yaml file
    with open(os.path.join(os.path.dirname(__file__), 'state_abbreviations.yaml'), 'r') as f:
        state_abbreviations = yaml.safe_load(f)

    # Convert the state name to the state abbreviation
    config['state'] = state_abbreviations[config['state']]

    # Write the config file with the new data
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
        yaml.dump(config, f)
    f.close()

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