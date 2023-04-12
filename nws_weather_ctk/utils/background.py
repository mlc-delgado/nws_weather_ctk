import threading
from nws_weather_ctk.utils.data import hourly_forecast, detailed_forecast, active_alerts, filter_alerts
from nws_weather_ctk.utils.config import logger, load_config

class UpdateThread(threading.Thread):
    def __init__(self, lock, data, updated, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        self.threadID = 1
        self.name = 'UpdateThread'
        self.daemon = True
        self.lock = lock
        self.data = data
        self.event = threading.Event()
        self.initial_data_fetched = False
        self.stop_trigger = False
        self.updated = updated
        
    def start(self):
        if self.stop_trigger == False:
            with self.lock:
                self.check_for_updates()

    def stop(self):
        self.stop_trigger = True

    # get the forecast data for the configured location
    def update_forecast_data(self, hourly_forecast_data=None):
        config = load_config()
        # get new hourly forecast data
        if hourly_forecast_data == None:
            hourly_forecast_data = hourly_forecast(config)
        # get new detailed forecast data
        detailed_forecast_data = detailed_forecast(config)
        # get the active alerts data
        active_alerts_data = active_alerts(config)
        self.data = {
            'hourly_forecast_data': hourly_forecast_data,
            'detailed_forecast_data': detailed_forecast_data,
            'active_alerts_data': active_alerts_data
        }

    # check if the forecast data has changed
    def check_for_updates(self):
        config = load_config()
        # if the forecast data is not set, update it
        if self.data is None or self.data['hourly_forecast_data'] is None or self.data['detailed_forecast_data'] is None or self.data['active_alerts_data'] is None:
            self.update_forecast_data()
            self.initial_data_fetched = True
        else:
            # if the forecast data is set, check if it has changed           
            try:
                # get current forecast
                current_hourly_forecast = hourly_forecast(load_config())
                current_temp = current_hourly_forecast['properties']['periods'][0]['temperature']
                current_short_forecast = current_hourly_forecast['properties']['periods'][0]['shortForecast']
                current_alert_matches = filter_alerts(active_alerts(config))
            # raise an exception for errors
            except Exception as e:
                raise e
            # update the forecast data if either the temperature, short forecast, or active alerts has changed
            last_temp = self.data['hourly_forecast_data']['properties']['periods'][0]['temperature']
            last_short_forecast = self.data['hourly_forecast_data']['properties']['periods'][0]['shortForecast']
            last_alert_matches = filter_alerts(self.data['active_alerts_data'])
            if current_temp != last_temp or current_short_forecast != last_short_forecast or current_alert_matches != last_alert_matches:
                self.update_forecast_data(hourly_forecast_data=current_hourly_forecast)
                self.updated = True
            else:
                self.updated = False
        self.event.set()