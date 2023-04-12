import customtkinter
from nws_weather_ctk.utils.icons import get_emoji

# frame to show the daily forecast
class DailyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class contstructor
        super().__init__(*args, **kwargs)

    def show_daily_forecast(self, period=None):
        self.refresh(period)
        # add a label for the weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('Symbola',48), text=self.emoji)
        self.iconLabel.pack(pady=12, padx=12)

        # add label to show the current temperature and forecast
        self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=self.forecast_text)
        self.forecastLabel.pack(pady=12, padx=12)

    # set the icon and forecast text
    def refresh(self, period=None):
        self.filename, self.emoji = get_emoji(self.master.detailed_forecast_data['properties']['periods'][period]['shortForecast'], self.master.detailed_forecast_data['properties']['periods'][period]['isDaytime'])
        self.forecast_text = '{day}\n{temperature}°F\n{forecast}'.format(day=self.master.detailed_forecast_data['properties']['periods'][period]['name'], temperature=self.master.detailed_forecast_data['properties']['periods'][period]['temperature'], forecast=self.master.detailed_forecast_data['properties']['periods'][period]['shortForecast'])

# frame to show the weekly forecast
class WeeklyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        self.detailed_forecast_data = None

    def refresh(self):
        self.detailed_forecast_data = self.master.data['detailed_forecast_data']

    # show the weekly forecast
    def display_elements(self):
        self.refresh()
        current = self.detailed_forecast_data['properties']['periods'][0]['name']
        # for each period in the forecast
        for i in range(0, len(self.detailed_forecast_data['properties']['periods'])):
            # if the period name is today's current period or a day of the week
            if self.detailed_forecast_data['properties']['periods'][i]['name'] in [ current, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                # unpack the frame
                try:
                    self.daily_forecast_frame.pack_forget()
                except:
                    pass
                # create a frame to hold the weather icon and forecast
                self.daily_forecast_frame = DailyForecastFrame(master=self)
                self.daily_forecast_frame.grid(row=0, column=i, padx=12, pady=12)
                self.daily_forecast_frame.show_daily_forecast(i)