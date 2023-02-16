import customtkinter
from data import forecast, active_alerts
from config import update
import yaml

refresh_ms = 300000

# load the config file
def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    f.close()
    return config

# Set the appearance mode to dark
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

    # return the values of the input boxes
    def get_values(self):
        return self.entry1.get(), self.entry2.get()

class WeatherFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # add buttons to get weather and update location
        self.button = customtkinter.CTkButton(master=self, text='Set Location', command=self.display_weather)
        self.button.pack(pady=12, padx=12)

    def display_weather(self, city=None, postal_code=None):
        # unpack existing labels to clear the frame
        try:
            self.forecastLabel.pack_forget()
            self.alertLabel.pack_forget()
        except:
            pass

        # load the config file
        config = load_config()

        # if the config file is empty or doesn't contain all the required keys, update the location
        if not config or not all(key in config for key in ['city', 'county', 'gridX', 'gridY', 'latitude', 'longitude', 'office', 'postalCode', 'state']):
            app.update_location()
            config = load_config()

        # check that the city and postal code match the config file, and if not update the location
        if city != config['city'] or postal_code != config['postalCode']:
            app.update_location()
            config = load_config()
    
        # fetch forecast and alert data
        forecast_data = forecast(config)
        alerts_data = active_alerts(config)

        # add label to show the current temperature and forecast
        self.forecastLabel = customtkinter.CTkLabel(master=self, text='Weather for {city}, {state}\nTemperature: {temperature}°F\nForecast: {forecast}'.format(city=config['city'], state=config['state'], temperature=forecast_data['properties']['periods'][0]['temperature'], forecast=forecast_data['properties']['periods'][0]['shortForecast']))
        self.forecastLabel.pack(pady=12, padx=12)

        # update the label every minute
        self.forecastLabel.after(refresh_ms, self.display_weather)

        # add label to show active alerts if the alert contains the county name
        if len(alerts_data['features']) > 0:
            for alert in alerts_data['features']:
                if config['county'] in alert['properties']['areaDesc']:
                    self.alertLabel = customtkinter.CTkLabel(master=self, text='Active alerts: {alert}'.format(alert=alert['properties']['event']))
                    self.alertLabel.pack(pady=12, padx=12)
                    
                    # update the label every minute
                    self.alertLabel.after(refresh_ms, self.display_weather)
    
    # update the location and display the weather
    def update_location(self):
        app.update_location()

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
        update(self.input_frame.get_values()[0], self.input_frame.get_values()[1]) 

# run the app
if __name__ == '__main__':
    app = App()
    app.mainloop()