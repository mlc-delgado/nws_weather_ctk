import customtkinter
from config import logger, update, load_config,  clear_config, check_config
from data import hourly_forecast, detailed_forecast, active_alerts
from frames import WeatherFrame, WeeklyForecastFrame, TemperatureGraphFrame
import sys

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

        self.currentFrame = None

        # load the config file and check if the location is set
        if not check_config(load_config()):
            # if the location is not set, prompt for input
            self.hide_current()
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

    # check temperature and shortForecast to determine if forecast is out of sync
    def check_for_updates(self):
        try:
            # get current forecast
            current_detailed_forecast = detailed_forecast(load_config())
            current_temp = current_detailed_forecast['properties']['periods'][0]['temperature']
            current_short_forecast = current_detailed_forecast['properties']['periods'][0]['shortForecast']
        # return false if the forecast data is not available
        except Exception as e:
            raise e
        if current_temp != self.detailed_forecast_data['properties']['periods'][0]['temperature'] or current_short_forecast != self.detailed_forecast_data['properties']['periods'][0]['shortForecast']:
            # update the forecast
            self.update_forecast_data()
        else:
            pass

    # show the main menu and selected weather frame
    def menu(self, choice=None):
        if choice is None:
            choice = 'Current'
        # unpack the segmented button if it exists
        try:
            self.segmented_button.pack_forget()
        # create if the segmented button does not exist
        except Exception:
            # set a default value for the segmented button
            segmented_button_var = customtkinter.StringVar(value=choice)
            # create a segmented button to select the weather data to display
            self.segmented_button = customtkinter.CTkSegmentedButton(master=self, font=('arial bold', 14), values=['Current', 'Hourly', '7-Day', 'Location'], command=self.segmented_button_callback, variable=segmented_button_var)
            self.segmented_button.pack(pady=10, padx=20)

        # update the forecast data
        self.update_forecast_data()

        # show the selected frame
        self.segmented_button_callback(choice)

    # show the frame for a selected value
    def segmented_button_callback(self, value=None):
        # hide the current frame
        self.hide_current()
        if value == 'Current':
            self.show_weather()
        elif value == '7-Day':
            self.show_weekly_forecast()
        elif value == 'Location':
            self.show_input()
        elif value == 'Hourly':
            self.show_hourly_temperature()

    # display input
    def show_input(self, reset=False):
        self.hide_current()
        # reset the config file if requested
        if reset:
            clear_config()
            # unpack the segmented button if it exists
            try:
                self.segmented_button.pack_forget()
            # ignore the error if the segmented button does not exist
            except Exception:
                pass
        # add the input frame
        self.current_frame = InputFrame(master=self)
        self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.current_frame.show_input()
        # refresh the frame periodically
        self.current_frame.after(refresh_ms, self.show_input)

    # set the location
    def set_location(self):
        try:
            update(self.current_frame.get_values()[0], self.current_frame.get_values()[1])
        # ignore exception when the input frame is not present
        except AttributeError:
            pass
        # log an error and display a toplevel window
        except Exception as e:
            error_text = 'Error updating location: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # call show_input to display the input frame
            self.show_input(reset=True)
        else:
            # redirect to the menu and weather frames
            self.menu()  

    # display weather
    def show_weather(self):
        self.hide_current()
        try:
            self.check_for_updates()
            # add a frame for weather
            self.current_frame = WeatherFrame(master=self)
            # pack the weather frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.display_weather(hourly_forecast_data=self.hourly_forecast_data, detailed_forecast_data=self.detailed_forecast_data, alerts_data=self.active_alerts_data)
            # update the frame periodically
            self.current_frame.after(refresh_ms, self.show_weather)
        except Exception as e:
            error_text = 'Error updating weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # reload the current frame
            self.segmented_button_callback(self.segmented_button.cget('variable'))

    # show weekly forecast
    def show_weekly_forecast(self):
        self.hide_current()
        try:
            self.check_for_updates()
            # add the weekly forecast frame
            self.current_frame = WeeklyForecastFrame(master=self)
            # pack the weekly forecast frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.show_weekly_forecast(forecast_data=self.detailed_forecast_data, current=self.detailed_forecast_data['properties']['periods'][0]['name'])
            # update the frame periodically
            self.current_frame.after(refresh_ms, self.show_weekly_forecast)
        except Exception as e:
            error_text = 'Error updating weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # reload the current frame
            self.segmented_button_callback(self.segmented_button.cget('variable'))

    # show the hourly temperature forecast
    def show_hourly_temperature(self):
        self.hide_current()
        try:
            self.check_for_updates()
            # add the temperature forecast frame
            self.current_frame = TemperatureGraphFrame(master=self)
            # pack the temperature forecast frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.show_hourly_graph(forecast_data=self.hourly_forecast_data)
            # update the frame periodically
            self.current_frame.after(refresh_ms, self.show_hourly_temperature)
        except Exception as e:
            error_text = 'Error updating weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # reload the current frame
            self.segmented_button_callback(self.segmented_button.cget('variable'))

    # hide the current frame
    def hide_current(self):
        try:
            self.current_frame.pack_forget()
        except Exception:
            pass

    # show an error message
    def show_error(self, error):
        logger.error(f'{error}')
        # create a toplevel window
        self.toplevel_window = customtkinter.CTkToplevel(self)
        self.toplevel_window.title('Error')
        self.toplevel_window.label = customtkinter.CTkLabel(self.toplevel_window, font=('arial bold', 14), text=error)
        self.toplevel_window.label.pack(pady=20, padx=20)
        # focus on it and update the text
        self.toplevel_window.focus()
        # wait for the window to close
        self.wait_window(self.toplevel_window)

# run the app
if __name__ == '__main__':
    try:
        app = App()
        app.protocol("WM_DELETE_WINDOW", sys.exit)
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit()
    except EOFError:
        sys.exit()