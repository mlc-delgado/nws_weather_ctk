import requests
import os
import yaml
import logging
import datetime as dt
from tzlocal import get_localzone
import pytz

# set up logger
logger = logging.getLogger(__name__)
# set the logging level
logging.basicConfig(level=logging.INFO)
# set the logging format
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# set the logging file
logging.basicConfig(filename='nws_weather_ctk.log', filemode='w')

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
    
def load_abbreviations():
    # Load the list of state abbreviations from yaml file
    with open(os.path.join(os.path.dirname(__file__), 'data.yaml'), 'r') as f:
        abbreviations = yaml.safe_load(f)['states']
    return abbreviations

# ensure the state is a valid state name or abbreviation    
def check_state_input(config):
    state_abbreviations = load_abbreviations()

    # Check if the state was provided as full name or abbreviation

    # If it was provided as a full name, convert it to the abbreviation
    if config['state'] in state_abbreviations:
        config['state'] = state_abbreviations[config['state']]

    # if the state is 2 characters, assume it is an abbreviation
    if len(config['state']) == 2:
        config['state'] = config['state'].upper()

    # log an error and raise exception if the state is not a valid state name or abbreviation
    if config['state'] not in state_abbreviations.values():
        logger.error('Invalid state provided: {}'.format(config['state']))
        raise Exception('Invalid state provided: {}. please check your location and try again'.format(config['state']))

    return config

# ensure the city is a valid city name
def check_city_input(config):
    # Set the geocoding url from MAPS
    geocode_url = 'https://geocode.maps.co/search?city={city}&state={state}&country=US'.format(city=config['city'],state=config['state'])
    # Get a sample geocode and check that it contains a valid combination of city and state
    geocode_data = requests.get(geocode_url).json()
    # load the abbreviations
    state_abbreviations = load_abbreviations()
    # get the state name from the abbreviations list
    state_name = [k for k, v in state_abbreviations.items() if v == config['state']][0]
    # check if the state name is in the display_name field
    if state_name not in geocode_data[0]['display_name']:
        logger.error('Invalid city provided: {}'.format(config['city']))
        raise Exception('Invalid city provided: {}. please check your location and try again'.format(config['city']))
        
# Update the config file
def update(city, state):
    config = {'city': city, 'state': state}

    # validate the state name or abbreviation
    config = check_state_input(config)

    # validate the city name
    check_city_input(config)

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
    # If the geocoding API fails log an error and raise exception
    except Exception as e:
        logger.error('Error getting geocoding data, please check your location and try again. Error: {}'.format(e))
        raise Exception('Error getting geocoding data, please check your location and try again. Error: {}'.format(e))

    # Fetch forecast data from the NWS API

    # set the points url
    points_url = 'https://api.weather.gov/points/{latitude},{longitude}'.format(latitude=config['latitude'], longitude=config['longitude'])

    try:
        # get the office and gridX, gridY from the points url
        points_data = requests.get(points_url).json()
        config['office'] = points_data['properties']['gridId']
        config['gridX'] = str(points_data['properties']['gridX'])
        config['gridY'] = str(points_data['properties']['gridY'])
    # If the points API fails log an error and raise exception
    except Exception as e:
        logger.error('Error getting points data, please check your location and try again. Error: {}'.format(e))
        raise Exception('Error getting points data, please check your location and try again. Error: {}'.format(e))

    # Write the config file with the new data
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
        yaml.dump(config, f)
    f.close()

# check if the forecast is for the selected day of the week
def is_weekday(start_time, day_of_week):
        # convert the forecast start time to a datetime object
        forecast_starttime = dt.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
        if forecast_starttime.weekday() == day_of_week:
            return True
        else:
            return False

# get the dates of today and the next 6 days
def get_week():
    # get the current date
    today = dt.datetime.now(get_localzone())
    # get the dates of the next 6 days
    dates = []
    for i in range(0, 7):
        dates.append(today + dt.timedelta(days=i))
    # convert the dates into a list of strings in the format 'YYYY-MM-DD'
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    return dates

# return the day of week integer from a day of the week string
def get_day_of_week(day_of_week):
    # convert the day of the week string to a day of the week integer
    if day_of_week == 'Monday':
        return 0
    elif day_of_week == 'Tuesday':
        return 1
    elif day_of_week == 'Wednesday':
        return 2
    elif day_of_week == 'Thursday':
        return 3
    elif day_of_week == 'Friday':
        return 4
    elif day_of_week == 'Saturday':
        return 5
    elif day_of_week == 'Sunday':
        return 6
    elif day_of_week == 'Today':
        return dt.datetime.now(get_localzone()).weekday()
    else:
        return None