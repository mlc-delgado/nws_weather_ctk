import requests
import os
import yaml
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

# check the config file for the location
def check_config(config):
    # if the config file is empty, or doesn't contain all the required keys, update the location config
    if not config or config == {} or not all(key in config for key in ['city', 'county', 'gridX', 'gridY', 'latitude', 'longitude', 'office', 'state']):
        return False
    else:
        return True

# Update the config file
def update(city, state):
    config = {'city': city, 'state': state}

    # Load the list of state abbreviations from yaml file
    with open(os.path.join(os.path.dirname(__file__), 'state_abbreviations.yaml'), 'r') as f:
        state_abbreviations = yaml.safe_load(f)

    # Check if the state was provided as full name or abbreviation

    # If it was provided as a full name, convert it to the abbreviation
    if config['state'] in state_abbreviations:
        config['state'] = state_abbreviations[config['state']]

    # if the state is 2 characters, assume it is an abbreviation
    if len(config['state']) == 2:
        config['state'] = config['state'].upper()

    # log an error and exit if the state is not a valid state name or abbreviation
    if config['state'] not in state_abbreviations.values():
        logger.error('Invalid state provided, please check your location and try again')
        exit(1)

    # create a city_string from the city that replaces any spaces with plus signs
    city_string = city.replace(' ', '+')
    # Set the geocoding url from MAPS
    geocode_url = 'https://geocode.maps.co/search?city={city}&state={state}&country=US'.format(city=city_string,state=config['state'])

    # Get latitude, longitude, and county from the geocoding API
    try:
        geocode_data = requests.get(geocode_url).json()
        # Set the latitude and longitude from the geocoding data, and round the values to 4 decimal places
        config['latitude'] = round(float(geocode_data[0]['lat']), 4)
        config['longitude'] = round(float(geocode_data[0]['lon']), 4)
        # set the county from the geocoding data
        # extract from the display_name field in the format "City, County, State, Country"
        config['county'] = geocode_data[0]['display_name'].split(',')[1].strip()
        # Remove " County" from the county if it contains it
        if ' County' in config['county']:
            config['county'] = config['county'].replace(' County', '')
    # If the geocoding API fails log an error and exit
    except Exception as e:
        logger.error('Error getting geocoding data, please check your location and try again. Error: {}'.format(e))
        exit(1)

    # Fetch forecast data from the NWS API

    # set the points url
    points_url = 'https://api.weather.gov/points/{latitude},{longitude}'.format(latitude=config['latitude'], longitude=config['longitude'])

    try:
        # get the office and gridX, gridY from the points url
        points_data = requests.get(points_url).json()
        config['office'] = points_data['properties']['gridId']
        config['gridX'] = str(points_data['properties']['gridX'])
        config['gridY'] = str(points_data['properties']['gridY'])
    # If the points API fails log an error and exit
    except Exception as e:
        logger.error('Error getting points data, please check your location and try again. Error: {}'.format(e))
        exit(1)

    # Write the config file with the new data
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
        yaml.dump(config, f)
    f.close()