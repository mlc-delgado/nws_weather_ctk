import requests

def forecast(config):
    # set the forecast url
    forecast_url = 'https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast'.format(office=config['office'], gridX=config['gridX'], gridY=config['gridY'])
    # get the forecast data
    return requests.get(forecast_url).json()

def active_alerts(config):
    # set the active alerts url
    alerts_url = 'https://api.weather.gov/alerts/active?area={state}'.format(state=config['state'])
    # get the active alerts data
    return requests.get(alerts_url).json()