import customtkinter
from config import logger, update, load_config,  clear_config, check_config
from data import hourly_forecast, detailed_forecast, active_alerts
from icons import get_emoji

# set the frame refresh rate in milliseconds
# default 1 hour
refresh_ms = 3600000

# Set the appearance mode to system theme
customtkinter.set_appearance_mode('system')

# frame to show the user input
class InputFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    # display the input boxes
    def show_input(self):
        # clear the frame
        self.clear_frame()
        # load the config and check if location has been set
        config = load_config()
        if check_config(config):
            # set the placeholder text to the current location
            placeholder_city = config['city']
            placeholder_state = config['state']
        else:
            # set the placeholder text to the default location
            placeholder_city = 'City'
            placeholder_state = 'State'
        
        # provide input boxes for city and state
        self.entry1 = customtkinter.CTkEntry(master=self, font=('arial bold', 14),  placeholder_text=placeholder_city)
        self.entry1.pack(pady=12, padx=12)

        self.entry2 = customtkinter.CTkEntry(master=self, font=('arial bold', 14), placeholder_text=placeholder_state)
        self.entry2.pack(pady=12, padx=12)

        # add button to set location
        self.button = customtkinter.CTkButton(master=self, font=('arial bold', 14), text='Set Location', command=lambda: app.set_location())
        self.button.pack(pady=12, padx=12)

    # return the values of the input boxes
    def get_values(self):
        return self.entry1.get(), self.entry2.get()

# frame to show the current forecast and alerts
class WeatherFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    # display the forecast and alerts
    def display_weather(self, forecast_data=None, alerts_data=None):
        self.clear_frame()

        # load the config file
        config = load_config()

        # add a label for the current weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('arial',48), text=get_emoji(forecast_data['properties']['periods'][0]['shortForecast'], forecast_data['properties']['periods'][0]['isDaytime']))
        self.iconLabel.pack(pady=12, padx=12)

        # add label to show the current temperature and forecast
        text='Weather for {city}, {state}\nTemperature: {temperature}°F\nForecast: {forecast}\nHumidity: {humidity}%\nWind speed: {wind}'.format(forecast=forecast_data['properties']['periods'][0]['shortForecast'], city=config['city'], state=config['state'], temperature=forecast_data['properties']['periods'][0]['temperature'], humidity=forecast_data['properties']['periods'][0]['relativeHumidity']['value'], wind=forecast_data['properties']['periods'][0]['windSpeed'])
        self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=text)
        self.forecastLabel.pack(pady=12, padx=12)

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

# frame to show the detailed forecast
class DetailedForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    def show_detailed_forecast(self, forecast_data=None):
        self.clear_frame()

        # add a textbox to show the detailed forecast
        text = 'Detailed forecast:\n{name}\n{forecast}'.format(name=forecast_data['properties']['periods'][0]['name'], forecast=forecast_data['properties']['periods'][0]['detailedForecast'])
        self.detailedForecastTextbox = customtkinter.CTkTextbox(master=self, wrap='word', fg_color='transparent', font=('arial bold', 14))
        self.detailedForecastTextbox.insert('0.0', text)
        self.detailedForecastTextbox.configure(state='disabled')
        self.detailedForecastTextbox.pack(pady=12, padx=12)

# frame to show the daily forecast
class DailyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class contstructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    def show_daily_forecast(self, forecast_data=None, period=None):
        self.clear_frame()
        if forecast_data is not None and period is not None:
            # add a label for the weather icon
            # display the emoji for the forecast
            self.iconLabel = customtkinter.CTkLabel(master=self, font=('arial',48), text=get_emoji(forecast_data['properties']['periods'][period]['shortForecast'], forecast_data['properties']['periods'][period]['isDaytime']))
            self.iconLabel.pack(pady=12, padx=12)

            # add label to show the current temperature and forecast
            self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='{name}\nTemperature: {temperature}°F\nForecast: {forecast}\n'.format(name=forecast_data['properties']['periods'][period]['name'], temperature=forecast_data['properties']['periods'][period]['temperature'], forecast=forecast_data['properties']['periods'][period]['shortForecast']))
            self.forecastLabel.pack(pady=12, padx=12)

# frame to show the weekly forecast
class WeeklyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    def show_weekly_forecast(self, forecast_data=None, current=None):
        self.clear_frame()

        # set a starting var for the column
        column = 0
        # for each period in the forecast
        for i in range(0, len(forecast_data['properties']['periods'])):
            # if the period name is today's current period or a day of the week
            if forecast_data['properties']['periods'][i]['name'] in [ current, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                # create a frame to hold the weather icon and forecast
                self.daily_forecast_frame = DailyForecastFrame(master=self)
                self.daily_forecast_frame.grid(row=0, column=column, padx=12, pady=12)
                self.daily_forecast_frame.show_daily_forecast(forecast_data, i)
                # increment the column
                column += 1

# frame to show the active alerts
class ActiveAlertsFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    # display the active alerts details
    def show_active_alerts(self, alerts_data=None):
        self.clear_frame()

        config = load_config()

        # add a textbox to show the alert details
        if len(alerts_data['features']) > 0:
            # make a dictionary of alerts that match the county name
            alert_matches = {}
            for alert in alerts_data['features']:
                if config['county'] in alert['properties']['areaDesc']:
                    # store the alert in a dictionary with the event as the key
                    alert_matches[alert['properties']['event']] = {
                        'description': alert['properties']['description'],
                        'instruction': alert['properties']['instruction']
                    }
            # add the alerts to the text
            if alert_matches != {}:
                text = 'Active alerts:\n'
                for alert in alert_matches:
                    text += 'Description: {description}\nInstruction: {instruction}\n'.format(description=alert_matches[alert]['description'], instruction=alert_matches[alert]['instruction'])
            else:
                text = 'No active alerts'
            self.alertTextbox = customtkinter.CTkTextbox(master=self, wrap='word', fg_color='transparent', font=('arial bold', 14))
            self.alertTextbox.insert('0.0', text)
            self.alertTextbox.configure(state='disabled')
            self.alertTextbox.pack(pady=12, padx=12)

# define the main App class
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # set the window title
        self.title('NWS Weather CTk')

        # load the config file and check if the location is set
        if not check_config(load_config()):
            # if the location is not set, prompt for input
            self.show_input()
        else:
            # if the location is set, show the menu and weather frames
            self.menu()

    # update all forecast, detailed forecast, and alerts data
    def update_forecast_data(self):
        config = load_config()
        # get the hourly forecast data
        self.hourly_forecast_data = hourly_forecast(config)
        # get the detailed forecast data
        self.detailed_forecast_data = detailed_forecast(config)
        # get the active alerts data
        self.active_alerts_data = active_alerts(config)

    # show the main menu and selected weather frame
    def menu(self, choice=None):
        if choice is None:
            choice = 'Current Forecast'
        # unpack the segmented button if it exists
        try:
            self.segmented_button.pack_forget()
        # ignore the error if the segmented button does not exist
        except:
            pass
        # set a default value for the segmented button
        segmented_button_var = customtkinter.StringVar(value=choice)
        # create a segmented button to select the weather data to display
        self.segmented_button = customtkinter.CTkSegmentedButton(master=self, font=('arial bold', 14), values=['Current Forecast', 'Detailed Forecast', 'Weekly Forecast', 'Active Alerts', 'Location'], command=self.segmented_button_callback, variable=segmented_button_var)
        self.segmented_button.pack(pady=10, padx=20)
        # update the forecast data for initial display
        self.update_forecast_data()
        # show the selected frame
        self.segmented_button_callback(choice)

    # show the frame for a selected value
    def segmented_button_callback(self, value=None):
        # hide all frames
        self.hide_all()
        if value == 'Current Forecast':
            self.show_weather()
        elif value == 'Detailed Forecast':
            self.show_detailed_forecast()
        elif value == 'Weekly Forecast':
            self.show_weekly_forecast()
        elif value == 'Location':
            self.show_input()
        elif value == 'Active Alerts':
            self.show_alerts()

    # display input
    def show_input(self, reset=False):
        # clear existing input frame
        self.hide_input()
        # reset the config file if requested
        if reset:
            clear_config()
            # unpack the segmented button if it exists
            try:
                self.segmented_button.pack_forget()
            # ignore the error if the segmented button does not exist
            except:
                pass
            # hide all other frames
            self.hide_all()
        # add the input frame
        self.input_frame = InputFrame(master=self)
        self.input_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.input_frame.show_input()

    # set the location
    def set_location(self):
        try:
            update(self.input_frame.get_values()[0], self.input_frame.get_values()[1])
        # ignore exception when the input frame is not present
        except AttributeError:
            pass
        # log an error and display a toplevel window
        except Exception as e:
            # log the error
            logger.error('Error updating location: {}'.format(e))
            # display a toplevel window
            self.show_error(error='Error updating location: {}'.format(e))
            # wait for the window to close
            self.wait_window(self.toplevel_window)
            # call show_input to display the input frame
            self.show_input(reset=True)
        else:
            # redirect to the menu and weather frames
            self.menu()

    # hide the input frame
    def hide_input(self):
        try:
            self.input_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass     

    # display weather
    def show_weather(self):
        # clear existing weather frame
        self.hide_weather()
        # add a frame for weather
        self.weather_frame = WeatherFrame(master=self)
        self.weather_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.weather_frame.display_weather(forecast_data=self.hourly_forecast_data, alerts_data=self.active_alerts_data)
        # update the frame periodically
        self.weather_frame.after(refresh_ms, self.update_forecast_data)

    # hide the weather frame
    def hide_weather(self):
        try:
            self.weather_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass

    # display detailed forecast
    def show_detailed_forecast(self):
        # clear existing detailed forecast frame
        self.hide_detailed_forecast()
        # add the detailed forecast frame
        self.detailed_forecast_frame = DetailedForecastFrame(master=self)
        self.detailed_forecast_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.detailed_forecast_frame.show_detailed_forecast(forecast_data=self.detailed_forecast_data)
        # update the frame periodically
        self.detailed_forecast_frame.after(refresh_ms, self.update_forecast_data)

    # hide detailed forecast   
    def hide_detailed_forecast(self):
        try:
            self.detailed_forecast_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass

    # show weekly forecast
    def show_weekly_forecast(self):
        # clear existing weekly forecast frame
        self.hide_weekly_forecast()
        # add the weekly forecast frame
        self.weekly_forecast_frame = WeeklyForecastFrame(master=self)
        self.weekly_forecast_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.weekly_forecast_frame.show_weekly_forecast(forecast_data=self.detailed_forecast_data, current=self.detailed_forecast_data['properties']['periods'][0]['name'])
        # update the frame periodically
        self.weekly_forecast_frame.after(refresh_ms, self.update_forecast_data)

    # hide weekly forecast
    def hide_weekly_forecast(self):
        try:
            self.weekly_forecast_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass

    # show active alert details
    def show_alerts(self):
        # clear existing active alerts frame
        self.hide_alerts()
        # add the active alerts frame
        self.alerts_frame = ActiveAlertsFrame(master=self)
        self.alerts_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.alerts_frame.show_active_alerts(self.active_alerts_data)
        # update the frame periodically
        self.alerts_frame.after(refresh_ms, self.update_forecast_data)

    # hide active alert details
    def hide_alerts(self):
        # hide the active alerts frame
        try:
            self.alerts_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass

    # hide all frames
    def hide_all(self):
        self.hide_weather()
        self.hide_detailed_forecast()
        self.hide_weekly_forecast()
        self.hide_alerts()
        self.hide_input()

    # reset location
    def reset_config(self):
        clear_config()
        self.show_input()

    # show an error message
    def show_error(self, error):
        # create a toplevel window
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