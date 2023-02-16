import requests
import os
import yaml

# Update the config file
def update(city, postalCode):
    config = {'city': city, 'postalCode': postalCode}
    # Set the geocoding url from MAPS
    geocode_url = 'https://geocode.maps.co/search?postalcode={postalCode}'.format(postalCode=config['postalCode'])

    # Get latitude and longitude from the geocoding API
    geocode_data = requests.get(geocode_url).json()
    # Set the latitude and longitude from the geocoding data
    config['latitude'] = geocode_data[0]['lat']
    config['longitude'] = geocode_data[0]['lon']

    # Set the reverse geocoding url from MAPS
    reverse_geocode_url = 'https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}'.format(latitude=config['latitude'], longitude=config['longitude'])

    # Extract the county and state from the reverse geocoding API
    reverse_geocode_data = requests.get(reverse_geocode_url).json()
    config['county'] = reverse_geocode_data['address']['county']
    config['state'] = reverse_geocode_data['address']['state']

    # Remove " County" from the county if it contains it
    if ' County' in config['county']:
        config['county'] = config['county'].replace(' County', '')

    # Fetch forecast data from the NWS API

    # set the points url
    points_url = 'https://api.weather.gov/points/{latitude},{longitude}'.format(latitude=config['latitude'], longitude=config['longitude'])

    # get the office and gridX, gridY from the points url
    points_data = requests.get(points_url).json()
    config['office'] = points_data['properties']['gridId']
    config['gridX'] = str(points_data['properties']['gridX'])
    config['gridY'] = str(points_data['properties']['gridY'])

    # Load the list of state abbreviations from yaml file
    with open(os.path.join(os.path.dirname(__file__), 'state_abbreviations.yaml'), 'r') as f:
        state_abbreviations = yaml.safe_load(f)

    # Convert the state name to the state abbreviation
    config['state'] = state_abbreviations[config['state']]

    # Write the config file with the new data
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
        yaml.dump(config, f)
    f.close()