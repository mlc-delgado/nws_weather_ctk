import customtkinter
from data import forecast, active_alerts
from config import update
import yaml
import logging

# set up logger
logger = logging.getLogger(__name__)
# set the logging level
logging.basicConfig(level=logging.INFO)
# set the logging format
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# set the logging file
logging.basicConfig(filename='nws_weather_ctk.log')

# set the frame refresh rate in milliseconds
refresh_ms = 300000

# load the config file
def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    f.close()
    return config

# Set the appearance mode to system theme
customtkinter.set_appearance_mode('system')

# define InputFrame and WeatherFrame classes

class InputFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # provide input boxes for city and postal code
        self.entry1 = customtkinter.CTkEntry(master=self, placeholder_text='City')
        self.entry1.pack(pady=12, padx=12)

        self.entry2 = customtkinter.CTkEntry(master=self, placeholder_text='Postal Code')
        self.entry2.pack(pady=12, padx=12)

        # add button to set location
        self.button = customtkinter.CTkButton(master=self, text='Set Location', command=lambda: app.get_weather())
        self.button.pack(pady=12, padx=12)

    # return the values of the input boxes
    def get_values(self):
        return self.entry1.get(), self.entry2.get()

class WeatherFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    # display the forecast and alerts
    def display_weather(self, city=None, postal_code=None):
        # unpack existing labels to clear the frame
        try:
            self.forecastLabel.pack_forget()
            self.alertLabel.pack_forget()
        # ignore exceptions in case labels don't exist
        except Exception:
            pass

        # load the config file
        config = load_config()

        # if the config file is empty, or doesn't match the input city and postal code, or doesn't contain all the required keys, update the location config
        if not config or city != config['city'] or postal_code != config['postalCode'] or not all(key in config for key in ['city', 'county', 'gridX', 'gridY', 'latitude', 'longitude', 'office', 'postalCode', 'state']):
            app.update_location()
            config = load_config()
    
        # fetch forecast and alert data
        try:
            forecast_data = forecast(config)
            alerts_data = active_alerts(config)
        # log an error if the data cannot be fetched
        except Exception as e:
            logger.error(f'Error fetching forecast data: {e}')

        # add label to show the current temperature and forecast
        try:
            self.forecastLabel = customtkinter.CTkLabel(master=self, text='Weather for {city}, {state}\nTemperature: {temperature}°F\nForecast: {forecast}'.format(city=config['city'], state=config['state'], temperature=forecast_data['properties']['periods'][0]['temperature'], forecast=forecast_data['properties']['periods'][0]['shortForecast']))
            self.forecastLabel.pack(pady=12, padx=12)
        # log an error if the forecast data cannot be parsed
        except Exception as e:
            logger.error(f'Error reading forecast data: {e}')

        # update the label periodically
        self.forecastLabel.after(refresh_ms, self.display_weather)

        # add label to show active alerts if the alert contains the county name
        if len(alerts_data['features']) > 0:
            for alert in alerts_data['features']:
                if config['county'] in alert['properties']['areaDesc']:
                    self.alertLabel = customtkinter.CTkLabel(master=self, text='Active alerts: {alert}'.format(alert=alert['properties']['event']))
                    self.alertLabel.pack(pady=12, padx=12)
                    
                    # update the label periodically
                    self.alertLabel.after(refresh_ms, self.display_weather)

# define the main App class
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # set the window title
        self.title('NWS Weather CTk')

        # add a frame for input and a frame for weather
        self.input_frame = InputFrame(master=self)
        self.input_frame.pack(pady=20, padx=60, fill='both', expand=True)

        self.weather_frame = WeatherFrame(master=self)
        self.weather_frame.pack(pady=20, padx=60, fill='both', expand=True)

    # display the weather
    def get_weather(self):
        self.weather_frame.display_weather(self.input_frame.get_values()[0], self.input_frame.get_values()[1])

    # update the location
    def update_location(self):
        try:
            update(self.input_frame.get_values()[0], self.input_frame.get_values()[1])
        # log an error if the location cannot be set
        except Exception as e:
            logger.error(f'Error setting location: {e}')

# run the app
if __name__ == '__main__':
    app = App()
    app.mainloop()