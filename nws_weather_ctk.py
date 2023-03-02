import customtkinter
from config import logger, update, load_config,  clear_config, check_config
from data import hourly_forecast, detailed_forecast, active_alerts
from frames import WeatherFrame, WeeklyForecastFrame
import datetime
import pytz
from tzlocal import get_localzone

# set the frame refresh rate in milliseconds
# default 10 minutes
refresh_ms = 600000

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

    # return a possible timezone based on an offset
    def possible_timezones(self, tz_offset, common_only=True):
        # set the timezone collection to US timezones
        timezones = pytz.country_timezones['US']
        # convert the float hours offset to a timedelta
        offset_seconds = tz_offset * 3600
        offset_days = 0
        if offset_seconds < 0:
            offset_days = -1
            offset_seconds += 24 * 3600
        desired_delta = datetime.timedelta(offset_days, offset_seconds)
        # Loop through the timezones and find any with matching offsets
        null_delta = datetime.timedelta(0, 0)
        results = []
        for tz_name in timezones:
            tz = pytz.timezone(tz_name)
            non_dst_offset = getattr(tz, '_transition_info', [[null_delta]])[-1]
            if desired_delta == non_dst_offset[0]:
                results.append(tz_name) 
        # return the first result
        return results[0]

    # check local time to determine if forecast is out of sync, updates are published every 1 hour
    def check_for_updates(self):
        # use endTime of the current period to determine the timezone of the forecast
        offset_float = float(self.detailed_forecast_data['properties']['periods'][0]['endTime'][-6:-3])
        # get the current time in the timezone of the app location
        app_tz = self.possible_timezones(offset_float)
        # get the user local time
        user_tz = get_localzone()
        local_time = datetime.datetime.now(user_tz)
        # convert the local time to the timezone of the forecast
        local_time = local_time.astimezone(pytz.timezone(app_tz))
        # check the period end time to determine if the forecast is out of sync
        forecast_endtime = datetime.datetime.strptime(self.detailed_forecast_data['properties']['periods'][0]['endTime'], '%Y-%m-%dT%H:%M:%S%z')
        if local_time > forecast_endtime:
            # update the forecast
            logger.info('Forecast is out of sync, updating...')
            self.update_forecast_data
        else:
            pass

    # show the main menu and selected weather frame
    def menu(self, choice=None):
        if choice is None:
            choice = 'Current Conditions'
        # unpack the segmented button if it exists
        try:
            self.segmented_button.pack_forget()
        # ignore the error if the segmented button does not exist
        except:
            pass
        # set a default value for the segmented button
        segmented_button_var = customtkinter.StringVar(value=choice)
        # create a segmented button to select the weather data to display
        self.segmented_button = customtkinter.CTkSegmentedButton(master=self, font=('arial bold', 14), values=['Current Conditions', '7-Day Forecast', 'Location'], command=self.segmented_button_callback, variable=segmented_button_var)
        self.segmented_button.pack(pady=10, padx=20)

        # update the forecast data
        self.update_forecast_data()

        # show the selected frame
        self.segmented_button_callback(choice)

    # show the frame for a selected value
    def segmented_button_callback(self, value=None):
        # hide all frames
        self.hide_all()
        # check for updates to the forecast data
        self.check_for_updates()
        if value == 'Current Conditions':
            self.show_weather()
        elif value == '7-Day Forecast':
            self.show_weekly_forecast()
        elif value == 'Location':
            self.show_input()

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
        self.weather_frame.display_weather(hourly_forecast_data=self.hourly_forecast_data, detailed_forecast_data=self.detailed_forecast_data, alerts_data=self.active_alerts_data)
        # update the frame periodically
        self.weather_frame.after(refresh_ms, self.check_for_updates)

    # hide the weather frame
    def hide_weather(self):
        try:
            self.weather_frame.pack_forget()
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
        self.weekly_forecast_frame.after(refresh_ms, self.check_for_updates)

    # hide weekly forecast
    def hide_weekly_forecast(self):
        try:
            self.weekly_forecast_frame.pack_forget()
        # ignore exceptions in case the frame doesn't exist
        except Exception:
            pass

    # hide all frames
    def hide_all(self):
        self.hide_weather()
        self.hide_weekly_forecast()
        self.hide_input()

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