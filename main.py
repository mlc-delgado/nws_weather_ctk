import customtkinter
from tkinter import PhotoImage
from nws_weather_ctk.utils.config import logger, update_config, update_appearance, load_config,  clear_config, check_config, refresh_ms
from nws_weather_ctk.utils.data import hourly_forecast, detailed_forecast, active_alerts
from nws_weather_ctk.utils.icons import get_emoji
from nws_weather_ctk.frames.weekly import WeeklyForecastFrame
from nws_weather_ctk.frames.hourly import TemperatureGraphFrame
from nws_weather_ctk.frames.weather import WeatherFrame
from nws_weather_ctk.frames.settings import SettingsFrame
from nws_weather_ctk.frames.input import InputFrame
import sys

# Set the appearance mode to system theme
customtkinter.set_appearance_mode('system')

# Load the emoji font
customtkinter.FontManager.load_font('nws_weather_ctk/fonts/Symbola.ttf')

# define the main App class
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # set the window title
        self.title('NWS Weather CTk')
        # set the default frame
        self.currentFrame = None
        # set the default icon
        self.wm_iconphoto(True, PhotoImage(file='nws_weather_ctk/icons/mostlySunny_dark.png'))
        # safely shut down the app when the window is closed
        self.protocol("WM_DELETE_WINDOW", sys.exit)

        # load the config file and check if the window theme and icon theme have been set
        config = load_config()
        try:
            self.theme = config['window_theme']
        except Exception:
            self.theme = 'light'
        try:
            self.icon_theme = config['icon_theme']
        except Exception:
            self.icon_theme = 'dark'
        update_appearance(window_theme=self.theme, icon_theme=self.icon_theme)
        self.set_theme(self.theme)

        # load the config file and check if the location is set
        if not check_config(load_config()):
            # if the location is not set, prompt for input
            self.hide_current()
            self.show_input()
        else:
            # if the location is set, show the menu and weather frames
            self.update_forecast_data()
            self.update_icon()
            self.menu()
            # periodically update the wm_iconphoto
            self.after(refresh_ms, self.update_icon)

    def set_theme(self, theme):
        customtkinter.set_appearance_mode(theme)

    def set_icon_theme(self, theme):
        self.icon_theme = theme
        self.update_icon()

    def update_icon(self):
        short_forecast = self.hourly_forecast_data['properties']['periods'][0]['shortForecast']
        isDaytime = self.hourly_forecast_data['properties']['periods'][0]['isDaytime']
        # switch the app icon to the current weather icon
        filename, emoji = get_emoji(short_forecast, isDaytime)
        self.wm_iconphoto(True, PhotoImage(file='nws_weather_ctk/icons/{filename}_{theme}.png'.format(filename=filename, theme=self.icon_theme)))

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
        if self.hourly_forecast_data is None or self.detailed_forecast_data is None or self.active_alerts_data is None:
            self.update_forecast_data()
            return self.check_for_updates()
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
        return self.hourly_forecast_data, self.detailed_forecast_data, self.active_alerts_data

    # show the main menu and selected weather frame
    def menu(self, choice=None):
        if choice is None:
            choice = 'Current'
        # unpack the segmented button if it exists
        try:
            self.segmented_button.pack_forget()
        # ignore the error if the segmented button does not exist
        except Exception:
            pass
        # set a default value for the segmented button
        segmented_button_var = customtkinter.StringVar(value=choice)
        # create a segmented button to select the weather data to display
        self.segmented_button = customtkinter.CTkSegmentedButton(master=self, font=('arial bold', 14), values=['Current', 'Hourly', '7-Day', 'Location', 'Settings'], command=self.segmented_button_callback, variable=segmented_button_var)
        self.segmented_button.pack(pady=10, padx=20)

        # show the selected frame
        self.segmented_button_callback(choice)

    # show the frame for a selected value
    def segmented_button_callback(self, value=None):
        # hide the current frame
        self.hide_current()
        # check for updates to the forecast data
        self.check_for_updates()
        # update the icon
        self.update_icon()
        if value == 'Current':
            self.show_weather()
        elif value == '7-Day':
            self.show_7day_forecast()
        elif value == 'Location':
            self.show_input()
        elif value == 'Hourly':
            self.show_hourly_temperature()
        elif value == 'Settings':
            self.show_settings()

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
        self.current_frame.after(refresh_ms, self.current_frame.update)

    # set the location
    def set_location(self):
        try:
            update_config(self.current_frame.get_values()[0], self.current_frame.get_values()[1])
        # ignore exception when the input frame is not present
        except AttributeError:
            self.menu()
        # log an error and display a toplevel window
        except Exception as e:
            error_text = 'Error updating location: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # call show_input to display the input frame
            self.show_input(reset=True)
        else:
            # redirect to the menu and weather frames
            self.update_forecast_data()
            self.menu()  

    # display weather
    def show_weather(self):
        try:
            self.check_for_updates()
            # add a frame for weather
            self.current_frame = WeatherFrame(master=self)
            # pack the weather frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.display_weather(self.hourly_forecast_data, self.detailed_forecast_data, self.active_alerts_data)
            # update the frame periodically
            self.current_frame.after(refresh_ms, self.current_frame.update, self.hourly_forecast_data, self.detailed_forecast_data, self.active_alerts_data)
        except Exception as e:
            error_text = 'Error updating weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # reload the current frame
            self.segmented_button_callback(self.segmented_button.cget('variable'))

    # show weekly forecast
    def show_7day_forecast(self):
        try:
            self.check_for_updates()
            # add the weekly forecast frame
            self.current_frame = WeeklyForecastFrame(master=self)
            # pack the weekly forecast frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.show_weekly_forecast(self.detailed_forecast_data)
            # update the frame periodically
            self.current_frame.after(refresh_ms, self.current_frame.update, self.detailed_forecast_data)
        except Exception as e:
            error_text = 'Error updating weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # reload the current frame
            self.segmented_button_callback(self.segmented_button.cget('variable'))

    # show the hourly temperature forecast
    def show_hourly_temperature(self):
        try:
            self.check_for_updates()
            # add the temperature forecast frame
            self.current_frame = TemperatureGraphFrame(master=self)
            # pack the temperature forecast frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.show_hourly_graph(self.hourly_forecast_data)
            # update the frame periodically
            self.current_frame.after(refresh_ms, self.current_frame.update, self.hourly_forecast_data, 24)
        except Exception as e:
            error_text = 'Error updating weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # reload the current frame
            self.segmented_button_callback(self.segmented_button.cget('variable'))

    # show the settings frame
    def show_settings(self):
        # add the settings frame
        self.current_frame = SettingsFrame(master=self)
        # pack the settings frame
        self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)

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
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit()
    except EOFError:
        sys.exit()