import customtkinter
from config import logger, update, load_config,  clear_config, forecast, active_alerts

# set the frame refresh rate in milliseconds
# default 1 hour
refresh_ms = 3600000

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
    
        # get the forecast and active alerts data
        forecast_data = forecast(config)
        alerts_data = active_alerts(config)

        # add label to show the current temperature and forecast
        self.forecastLabel = customtkinter.CTkLabel(master=self, text='Weather for {city}, {state}\nTemperature: {temperature}°F\nForecast: {forecast}'.format(city=config['city'], state=config['state'], temperature=forecast_data['properties']['periods'][0]['temperature'], forecast=forecast_data['properties']['periods'][0]['shortForecast']))
        self.forecastLabel.pack(pady=12, padx=12)

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

        # add button to update location
        self.updateButton = UpdateButton(master=self, text='Update Location', command=lambda: app.show_input())
        self.updateButton.pack(pady=12, padx=12)

    # display a blank label if the location is not set
    def display_blank(self):
        # unpack the update button and forecast/alert labels to clear the frame
        try:
            self.updateButton.pack_forget()
            self.forecastLabel.pack_forget()
            self.alertLabel.pack_forget()
        # ignore exceptions in case button and labels don't exist
        except Exception:
            pass
        # add the blank location label
        self.blankLabel = customtkinter.CTkLabel(master=self, text='Location not set')
        self.blankLabel.pack(pady=12, padx=12)

# define UpdateButton class
class UpdateButton(customtkinter.CTkButton):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

# define the main App class
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # set the window title
        self.title('NWS Weather CTk')

        # add a frame for weather
        self.weather_frame = WeatherFrame(master=self)
        self.weather_frame.pack(pady=20, padx=60, fill='both', expand=True)

        # load the config file and check if the location is set
        config = load_config()
        if not config or not all(key in config for key in ['city', 'county', 'gridX', 'gridY', 'latitude', 'longitude', 'office', 'postalCode', 'state']):
            # if the location is not set, display 'Location not set'
            self.show_blank()
        else:
            # if the location is set, display the weather
            self.show_weather(config['city'], config['postalCode'])

    # display frame and input if location is not set
    def show_blank(self):
        self.weather_frame.display_blank()
        # add a frame for input
        self.input_frame = InputFrame(master=self)
        self.input_frame.pack(pady=20, padx=60, fill='both', expand=True)

    # display frame and button if location is set
    def show_weather(self, city, postal_code):
        self.weather_frame.display_weather(city, postal_code)

    # display the weather
    def get_weather(self):
        # unpack blank label and input frame
        try:
            self.weather_frame.blankLabel.pack_forget()
            self.input_frame.pack_forget()
        # ignore exceptions in case the label and frame don't exist
        except Exception:
            pass
        self.weather_frame.display_weather(self.input_frame.get_values()[0], self.input_frame.get_values()[1])

    # update the location
    def update_location(self):
        try:
            update(self.input_frame.get_values()[0], self.input_frame.get_values()[1])
        # log an error if the location cannot be set
        except Exception as e:
            logger.error(f'Error setting location: {e}')

    # unset the location and display the blank weather frame
    def show_input(self):
        # clear the config file
        clear_config()
        # display the blank weather frame
        self.show_blank()

# run the app
if __name__ == '__main__':
    app = App()
    app.mainloop()