import customtkinter
from nws_weather_ctk.utils.config import refresh_ms
from nws_weather_ctk.utils.icons import get_emoji

# frame to show the daily forecast
class DailyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class contstructor
        super().__init__(*args, **kwargs)

    def show_daily_forecast(self, detailed_forecast_data=None, period=None):
        self.refresh(detailed_forecast_data, period)
        # add a label for the weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('Symbola',48), text=self.emoji)
        self.iconLabel.pack(pady=12, padx=12)

        # add label to show the current temperature and forecast
        self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=self.forecast_text)
        self.forecastLabel.pack(pady=12, padx=12)

        # refresh the icon and forecast label periodically
        self.iconLabel.after(refresh_ms, self.update, detailed_forecast_data, period)
        self.forecastLabel.after(refresh_ms, self.update, detailed_forecast_data, period)

    # set the icon and forecast text
    def refresh(self, detailed_forecast_data=None, period=None):
        self.filename, self.emoji = get_emoji(detailed_forecast_data['properties']['periods'][period]['shortForecast'], detailed_forecast_data['properties']['periods'][period]['isDaytime'])
        self.forecast_text = '{day}\n{temperature}°F\n{forecast}'.format(day=detailed_forecast_data['properties']['periods'][period]['name'], temperature=detailed_forecast_data['properties']['periods'][period]['temperature'], forecast=detailed_forecast_data['properties']['periods'][period]['shortForecast'])

    # update the icon and forecast text
    def update(self, detailed_forecast_data=None, period=None):
        self.refresh(detailed_forecast_data, period)
        self.iconLabel.configure(text=self.emoji)
        self.forecastLabel.configure(text=self.forecast_text)

# frame to show the weekly forecast
class WeeklyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    # show the weekly forecast
    def show_weekly_forecast(self, detailed_forecast_data=None):
        current = detailed_forecast_data['properties']['periods'][0]['name']
        # for each period in the forecast
        for i in range(0, len(detailed_forecast_data['properties']['periods'])):
            # if the period name is today's current period or a day of the week
            if detailed_forecast_data['properties']['periods'][i]['name'] in [ current, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                # unpack the frame
                try:
                    self.daily_forecast_frame.pack_forget()
                except:
                    pass
                # create a frame to hold the weather icon and forecast
                self.daily_forecast_frame = DailyForecastFrame(master=self)
                self.daily_forecast_frame.grid(row=0, column=i, padx=12, pady=12)
                self.daily_forecast_frame.show_daily_forecast(detailed_forecast_data, i)
                self.after(refresh_ms, self.daily_forecast_frame.update, detailed_forecast_data, i)

    def update(self, detailed_forecast_data=None):
        self.master.check_for_updates()
        self.detailed_forecast_data = detailed_forecast_data