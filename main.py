import customtkinter
from config import logger, update, load_config,  clear_config, forecast, active_alerts
from icons import get_emoji

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

        # provide input boxes for city and state
        self.entry1 = customtkinter.CTkEntry(master=self, placeholder_text='City')
        self.entry1.pack(pady=12, padx=12)

        self.entry2 = customtkinter.CTkEntry(master=self, placeholder_text='State')
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
    def display_weather(self, city=None, state=None):
        # unpack existing labels to clear the frame
        try:
            self.forecastLabel.pack_forget()
            self.alertLabel.pack_forget()
            self.alertsListLabel.pack_forget()
        # ignore exceptions in case labels don't exist
        except Exception:
            pass

        # load the config file
        config = load_config()

        # if the config file is empty, or doesn't match the input city and state, or doesn't contain all the required keys, update the location config
        if not config or city != config['city'] or state != config['state'] or not all(key in config for key in ['city', 'county', 'gridX', 'gridY', 'latitude', 'longitude', 'office', 'state']):
            app.update_location()
            config = load_config()
    
        # get the forecast and active alerts data
        forecast_data = forecast(config)
        alerts_data = active_alerts(config)

        # add a label for the current weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('arial',30),text=get_emoji(forecast_data['properties']['periods'][0]['shortForecast']))
        self.iconLabel.pack(pady=12, padx=12)

        # add label to show the current temperature and forecast
        self.forecastLabel = customtkinter.CTkLabel(master=self, text='Weather for {city}, {state}\nTemperature: {temperature}°F\nForecast: {forecast}'.format(city=config['city'], state=config['state'], temperature=forecast_data['properties']['periods'][0]['temperature'], forecast=forecast_data['properties']['periods'][0]['shortForecast']))
        self.forecastLabel.pack(pady=12, padx=12)

        # update the label periodically
        self.forecastLabel.after(refresh_ms, self.display_weather)

        # add label to show active alerts if the alert contains the county name
        if len(alerts_data['features']) > 0:
            # make a list of alerts that match the county name
            alert_matches = []
            for alert in alerts_data['features']:
                if config['county'] in alert['properties']['areaDesc']:
                    alert_matches.append(alert['properties']['event'])

            # display the alerts if there are any
            if len(alert_matches) > 0:
                # remove duplicates from the list
                alert_matches = list(set(alert_matches))
                # add the alert label
                self.alertLabel = customtkinter.CTkLabel(master=self, text='Active alerts:')
                self.alertLabel.pack(pady=0, padx=12)
                # add the list of alerts
                self.alertsListLabel = customtkinter.CTkLabel(master=self, text='\n'.join(alert_matches))
                self.alertsListLabel.pack(pady=0, padx=12)

                # update the labels periodically
                self.alertLabel.after(refresh_ms, self.display_weather)
                self.alertsListLabel.after(refresh_ms, self.display_weather)
                
        # add a button to update location
        self.button = customtkinter.CTkButton(master=self, text='Update Location', command=lambda: app.show_input())
        self.button.pack(pady=12, padx=12)

# define the main App class
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # set the window title
        self.title('NWS Weather CTk')

        # load the config file and check if the location is set
        config = load_config()
        if not config or not all(key in config for key in ['city', 'county', 'gridX', 'gridY', 'latitude', 'longitude', 'office', 'state']):
            # if the location is not set, prompt for input
            self.show_input()
        else:
            # if the location is set, display the weather
            self.show_weather(config['city'], config['state'])

    # clear location config and display input frame
    def show_input(self):
        # clear the config file
        clear_config()
        # unpack the weather frame
        try:
            self.weather_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass
        # add the input frame
        self.input_frame = InputFrame(master=self)
        self.input_frame.pack(pady=20, padx=60, fill='both', expand=True)     

    # display weather
    def show_weather(self, city, state):
        # add a frame for weather
        self.weather_frame = WeatherFrame(master=self)
        self.weather_frame.pack(pady=20, padx=60, fill='both', expand=True)
        self.weather_frame.display_weather(city, state)

    # set location from input
    def get_weather(self):
        self.show_weather(city=self.input_frame.get_values()[0], state=self.input_frame.get_values()[1])
        # unpack the input frame
        try:
            self.input_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass

    # update the location
    def update_location(self):
        try:
            update(self.input_frame.get_values()[0], self.input_frame.get_values()[1])
        # log an error if the location cannot be set
        except Exception as e:
            logger.error('Error setting location: {}'.format(e))

# run the app
if __name__ == '__main__':
    app = App()
    app.mainloop()