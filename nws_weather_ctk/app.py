import customtkinter
import os
import time
import threading
from tkinter import PhotoImage
from nws_weather_ctk.utils.config import logger, update_config, update_appearance, load_config,  clear_config, check_config, REFRESH_MS, WAIT_SECONDS
from nws_weather_ctk.utils.icons import get_emoji
from nws_weather_ctk.utils.background import UpdateThread
from nws_weather_ctk.frames.weekly import WeeklyForecastFrame
from nws_weather_ctk.frames.hourly import TemperatureGraphFrame
from nws_weather_ctk.frames.weather import WeatherFrame
from nws_weather_ctk.frames.settings import SettingsFrame
from nws_weather_ctk.frames.input import InputFrame

# define the main App class
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        # Set default appearance mode to system theme
        customtkinter.set_appearance_mode('system')
        # Load the emoji font
        customtkinter.FontManager.load_font('nws_weather_ctk/fonts/Symbola.ttf')
        # set the window title
        self.title('NWS Weather CTk')
        # set the default frame
        self.currentFrame = None
        # set the default icon
        self.wm_iconphoto(True, PhotoImage(file='nws_weather_ctk/icons/mostlySunny_dark.png'))
        # safely shut down the app when the window is closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # shared with background thread
        self.lock = threading.Lock()
        self.data = None
        self.event = None
        self.stop_thread = False
        self.updated = False

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
            # if the location is set, show the main menu
            self.menu()

    def on_closing(self):
        # shut down the app and threads
        self.stop_background_thread()
        self.destroy()
        os._exit(0)

    # start the background thread
    def start_background_thread(self):
        self.update_thread = UpdateThread(self.lock, self.data, self.updated)
        self.event = self.update_thread.event
        self.update_thread.start()

    # stop the background thread
    def stop_background_thread(self):
        self.stop_thread = True

    # start the background thread and check for data changes
    def background_thread_loop(self):
        if not self.stop_thread:
            self.start_background_thread()
            self.event.wait()
            if self.update_thread.updated:
                self.check_for_updates()
            self.after(REFRESH_MS, self.background_thread_loop)

    #  check for initial forecast data
    def check_for_initial_data(self):
        with self.lock:
            self.event.wait()
            while True:
                if self.update_thread.initial_data_fetched:
                    self.data = self.update_thread.data
                    break
                time.sleep(WAIT_SECONDS)

    # check for updates to the forecast data
    def check_for_updates(self):
        with self.lock:
            # if the data has been updated, update the frame and wm icon
            self.data = self.update_thread.data
            self.update_icon()
            # reload the current frame
            if type(self.current_frame) == WeatherFrame or type(self.current_frame) == TemperatureGraphFrame or type(self.current_frame) == WeeklyForecastFrame:
                self.current_frame.pack_forget()
                self.current_frame.display_elements()
                self.current_frame.pack(pady=10, padx=20)

    # set the light or dark theme
    def set_theme(self, theme):
        customtkinter.set_appearance_mode(theme)

    # set the wm icon theme
    def set_icon_theme(self, theme):
        self.icon_theme = theme
        self.update_icon()

    # update the wm icon based on the forecast data
    def update_icon(self):
        short_forecast = self.data['hourly_forecast_data']['properties']['periods'][0]['shortForecast']
        isDaytime = self.data['hourly_forecast_data']['properties']['periods'][0]['isDaytime']
        # switch the app icon to the current weather icon
        filename, emoji = get_emoji(short_forecast, isDaytime)
        self.wm_iconphoto(True, PhotoImage(file='nws_weather_ctk/icons/{filename}_{theme}.png'.format(filename=filename, theme=self.icon_theme)))

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

        # start the background thread
        self.start_background_thread()

        # wait for the initial data to be fetched
        self.check_for_initial_data()

        # update the wm icon
        self.update_icon()

        # show the selected frame
        self.segmented_button_callback(choice)

        self.after(REFRESH_MS, self.background_thread_loop)

    # show the frame for a selected value
    def segmented_button_callback(self, value=None):
        with self.lock:
            # hide the current frame
            self.hide_current()
            # show the selected frame
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

    # set the location
    def set_location(self):
        try:
            update_config(self.current_frame.get_values()[0], self.current_frame.get_values()[1])
        # ignore exception when the input frame is not present
        except AttributeError:
            self.return_home()
        # log an error and display a toplevel window
        except Exception as e:
            error_text = 'Error updating location: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)
            # call show_input to display the input frame
            self.show_input(reset=True)
        else:
            self.return_home()

    def return_home(self):
        self.stop_background_thread()
        self.data = None
        # redirect to the menu and weather frames
        self.menu()

    # display weather
    def show_weather(self):
        try:
            # add a frame for weather
            self.current_frame = WeatherFrame(master=self)
            # pack the weather frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.display_elements()
        except Exception as e:
            error_text = 'Error displaying weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)

    # show weekly forecast
    def show_7day_forecast(self):
        try:
            # add the weekly forecast frame
            self.current_frame = WeeklyForecastFrame(master=self)
            # pack the weekly forecast frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.display_elements()
        except Exception as e:
            error_text = 'Error displaying weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)

    # show the hourly temperature forecast
    def show_hourly_temperature(self):
        try:
            # add the temperature forecast frame
            self.current_frame = TemperatureGraphFrame(master=self)
            # pack the temperature forecast frame
            self.current_frame.pack(pady=20, padx=20, fill='both', expand=True)
            self.current_frame.display_elements()
        except Exception as e:
            error_text = 'Error displaying weather data: {}'.format(e)
            # display a toplevel window
            self.show_error(error=error_text)

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