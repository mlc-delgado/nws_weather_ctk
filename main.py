import customtkinter
from config import logger, update, load_config,  clear_config, check_config
from data import hourly_forecast, detailed_forecast, active_alerts
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
        self.entry1 = customtkinter.CTkEntry(master=self, font=('arial bold', 14),  placeholder_text='City')
        self.entry1.pack(pady=12, padx=12)

        self.entry2 = customtkinter.CTkEntry(master=self, font=('arial bold', 14), placeholder_text='State')
        self.entry2.pack(pady=12, padx=12)

        # add button to set location
        self.button = customtkinter.CTkButton(master=self, font=('arial bold', 14), text='Set Location', command=lambda: app.get_weather())
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
            self.iconLabel.pack_forget()
            self.button.pack_forget()
            self.forecastLabel.pack_forget()
            self.detailedButton.pack_forget()
            app.detailedForecastTextbox.pack_forget()
            app.hideButton.pack_forget()
            self.alertLabel.pack_forget()
            self.alertsListLabel.pack_forget()
        # ignore exceptions in case labels don't exist
        except Exception:
            pass

        # load the config file and check if the location is set
        config = load_config()

        # Update the config file if it differs from the input
        if not check_config(config):
            app.update_location()
            config = load_config()
    
        # get the hourly forecast and active alerts data
        forecast_data = hourly_forecast(config)
        alerts_data = active_alerts(config)

        # add a label for the current weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('arial',48), text=get_emoji(forecast_data['properties']['periods'][0]['shortForecast'], forecast_data['properties']['periods'][0]['isDaytime']))
        self.iconLabel.pack(pady=12, padx=12)

        # add label to show the current temperature and forecast
        self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='Weather for {city}, {state}\nTemperature: {temperature}°F\nForecast: {forecast}'.format(city=config['city'], state=config['state'], temperature=forecast_data['properties']['periods'][0]['temperature'], forecast=forecast_data['properties']['periods'][0]['shortForecast']))
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
                self.alertLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='Active alerts:')
                self.alertLabel.pack(pady=0, padx=12)
                # add the list of alerts
                self.alertsListLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='\n'.join(alert_matches))
                self.alertsListLabel.pack(pady=0, padx=12)

                # update the labels periodically
                self.alertLabel.after(refresh_ms, self.display_weather)
                self.alertsListLabel.after(refresh_ms, self.display_weather)

        # add a button to show the detailed forecast
        self.detailedButton = customtkinter.CTkButton(master=self, font=('arial bold',14), text='Detailed Forecast', command=lambda: app.show_detailed_forecast())
        self.detailedButton.pack(pady=12, padx=12)

        # add a button to update location
        self.button = customtkinter.CTkButton(master=self, font=('arial bold',14), text='Update Location', command=lambda: app.reset_config())
        self.button.pack(pady=12, padx=12)

# define ToplevelWindow class for displaying errors
class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)
        
        self.geometry('400x300')

        self.label = customtkinter.CTklabel(master=self, font=('arial bold', 14), text="Error updating location")
        self.label.pack(pady=20, padx=20)

    def close(self):
        self.destroy()

# define the main App class
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # set the window title
        self.title('NWS Weather CTk')

        # load the config file and check if the location is set
        config = load_config()

        if not check_config(config):
            # if the location is not set, prompt for input
            self.show_input()
        else:
            # if the location is set, display the weather
            self.show_weather(config['city'], config['state'])

    # clear location config and display input frame
    def show_input(self):
        # unpack the weather frame and existing input frame
        try:
            self.weather_frame.pack_forget()
            self.input_frame.pack_forget()
        # ignore exceptions in case the frames don't exist
        except Exception:
            pass
        # add the input frame
        self.input_frame = InputFrame(master=self)
        self.input_frame.pack(pady=20, padx=20, fill='both', expand=True)     

    # display weather
    def show_weather(self, city, state):
        # add a frame for weather
        self.weather_frame = WeatherFrame(master=self)
        self.weather_frame.pack(pady=20, padx=20, fill='both', expand=True)
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
        # ignore exception when the input frame is not present
        except AttributeError:
            pass
        # log an error and display a toplevel window
        except Exception as e:
            # unpack the weather frame
            try:
                self.weather_frame.pack_forget()
            # ignore exceptions in case the frame doesn't exist
            except Exception:
                pass
            # log the error
            logger.error('Error updating location: {}'.format(e))
            # display a toplevel window
            app.show_error(error='Error updating location: {}'.format(e))
            # wait for the window to close
            self.wait_window(app.toplevel_window)
            # call show_input to display the input frame
            self.show_input()

    # show the detailed forecast
    def show_detailed_forecast(self):
        # remove the existing detailed forecast textbox
        try:
            self.detailedForecastTextbox.pack_forget()
        # ignore exceptions in case the textbox doesn't exist
        except Exception:
            pass

        # get the detailed forecast data
        forecast_data = detailed_forecast(load_config())

        # add a textbox to show the detailed forecast
        text = 'Detailed forecast:\n{name}\n{forecast}'.format(name=forecast_data['properties']['periods'][0]['name'], forecast=forecast_data['properties']['periods'][0]['detailedForecast'])
        self.detailedForecastTextbox = customtkinter.CTkTextbox(master=self, wrap='word')
        self.detailedForecastTextbox.insert('0.0', text)
        self.detailedForecastTextbox.configure(state='disabled')
        self.detailedForecastTextbox.pack(pady=12, padx=12)

        # update textbox periodically
        self.detailedForecastTextbox.after(refresh_ms, self.show_detailed_forecast)

        # add a button to hide the detailed forecast
        self.hideButton = customtkinter.CTkButton(master=self, font=('arial bold',14), text='Hide', command=lambda: self.hide_detailed_forecast())
        self.hideButton.pack(pady=12, padx=12)

    # hide the detailed forecast   
    def hide_detailed_forecast(self):
        # remove the detailed forecast textbox and hide button
        try:
            self.detailedForecastTextbox.pack_forget()
            self.hidebutton.pack_forget()
        # ignore exceptions in case the textbox or button doesn't exist
        except Exception:
            pass

    # reset the location
    def reset_config(self):
        clear_config()
        self.show_input()

    # show an error message
    def show_error(self, error):
        # create the toplevel window
        self.toplevel_window = customtkinter.CTkToplevel(self)
        self.toplevel_window.title('Error')
        self.toplevel_window.label = customtkinter.CTkLabel(self.toplevel_window, font=('arial bold', 14), text=error)
        self.toplevel_window.label.pack(pady=20, padx=20)
        # focus on it and update the text
        self.toplevel_window.focus()

# run the app
if __name__ == '__main__':
    app = App()
    app.mainloop()