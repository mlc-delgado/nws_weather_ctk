import customtkinter
from config import load_config, is_weekday, get_day_of_week, get_week
from icons import get_emoji

# frame to show the current forecast and alerts
class WeatherFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def check_for_alerts(self, alerts_data=None):
        # load the config file
        config = load_config()

        # make a dictionary of alerts that match the location
        alert_matches = {}

        # check if there are active alerts for the state
        if len(alerts_data['features']) > 0:
            # for each alert check if the county name is in the alert area description
            for alert in alerts_data['features']:
                if config['county'] in alert['properties']['areaDesc']:
                    # store the alert in a dictionary with the event as the key
                    alert_matches[alert['properties']['event']] = {
                        'description': alert['properties']['description'],
                        'instruction': alert['properties']['instruction']
                    }
        return alert_matches

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    # display the forecast and alerts
    def display_weather(self, hourly_forecast_data=None, detailed_forecast_data=None, alerts_data=None):
        self.clear_frame()

        self.frame1 = IconFrame(master=self)
        self.frame1.grid(row=0, column=0, padx=12, pady=12)
        self.frame1.show_icon(hourly_forecast_data,detailed_forecast_data)

        self.frame2 = HourlyForecastFrame(master=self)
        self.frame2.grid(row=0, column=1, padx=12, pady=12)
        self.frame2.show_hourly_forecast(hourly_forecast_data, alerts_data)

        # set default row and span for detailed forecast frame
        detailedforecastcolumn, detailedforecast_span = 0, 2

        # check if there are active alerts
        if len(alerts_data['features']) > 0:
            alert_matches = self.check_for_alerts(alerts_data)
            if len(alert_matches) > 0:
                # add a frame to show the active alerts
                self.frame3 = ActiveAlertsFrame(master=self)
                self.frame3.grid(row=1, column=0, padx=12, pady=12)
                self.frame3.show_active_alerts(alert_matches)
                # move the detailed forecast frame to the second column
                detailedforecastcolumn += 1
                detailedforecast_span = 1

        self.frame4 = DetailedForecastFrame(master=self)
        self.frame4.grid(row=1, column=detailedforecastcolumn, padx=12, pady=12, columnspan=detailedforecast_span)
        self.frame4.show_detailed_forecast(detailed_forecast_data)

# frame to show the hourly forecast
class HourlyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    def show_hourly_forecast(self, forecast_data=None, alerts_data=None):
        self.clear_frame()
        # load the config file
        config = load_config()

        # add label to show the current temperature and forecast
        text='Humidity: {humidity}%\n\nWind speed: {wind}\n\nWind direction: {wind_direction}\n\nPrecipitation: {precipitation}%\n\nDew point: {dew_point}°F'.format(
            forecast=forecast_data['properties']['periods'][0]['shortForecast'],
            city=config['city'],
            state=config['state'],
            humidity=forecast_data['properties']['periods'][0]['relativeHumidity']['value'],
            wind=forecast_data['properties']['periods'][0]['windSpeed'],
            wind_direction=forecast_data['properties']['periods'][0]['windDirection'],
            precipitation=forecast_data['properties']['periods'][0]['probabilityOfPrecipitation']['value'],
            # convert dew point value from Celsius to Fahrenheit
            dew_point = round((forecast_data['properties']['periods'][0]['dewpoint']['value'] * 9/5) + 32)
            )
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

# frame to show the hourly forecast icon
class IconFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    def show_icon(self, forecast_data=None, detailed_forecast_data=None):
        self.clear_frame()
        # add a label for the current weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('arial',64), text=get_emoji(forecast_data['properties']['periods'][0]['shortForecast'], forecast_data['properties']['periods'][0]['isDaytime']))
        self.iconLabel.pack(pady=2, padx=12)
        # load the config file
        config = load_config()
        # make a list of all temperatures throughout the day
        temperatures = []
        # add the current temperature to the list
        temperatures.append(forecast_data['properties']['periods'][0]['temperature'])
        # for each period startTime that matches today's date
        for period in detailed_forecast_data['properties']['periods']:
            # if the startTime is in the list of dates in get_week()
            for date in get_week():
                if date in period['startTime']:
                    # if the startTime matches today's day of week
                    if is_weekday(period['startTime'], get_day_of_week('Today')):
                        # append the matching temperature to the list
                        temperatures.append(period['temperature'])
        # get the high and low temperatures
        high = max(temperatures)
        low = min(temperatures)
        # omit the high temperature if it is the same as the low temperature
        if high == low:
            high_low_text = 'Low: {low}°F'.format(low=low)
        else:
            high_low_text = 'High: {high}°F Low: {low}°F'.format( high=high, low=low)
        # add a label for the temperature
        self.temperatureLabel = customtkinter.CTkLabel(master=self, font=('arial bold',20), text='{temperature}°F'.format(temperature=forecast_data['properties']['periods'][0]['temperature']))
        self.temperatureLabel.pack(pady=2, padx=12)
        # add a label for the high and low temperatures
        self.highLowLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=high_low_text)
        self.highLowLabel.pack(pady=0, padx=12)
        # add a label for the location
        self.locationLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='{city}, {state}\n{forecast}'.format(city=config['city'], state=config['state'], forecast=forecast_data['properties']['periods'][0]['shortForecast']))
        self.locationLabel.pack(pady=12, padx=12)

# frame to show the detailed forecast
class DetailedForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    # hide the detailed forecast
    def hide(self):
        self.hideButton.pack_forget()
        self.showButton.pack(pady=12, padx=12)
        self.detailedForecastTextbox.pack_forget()

    # show the detailed forecast
    def show(self):
        self.showButton.pack_forget()
        self.hideButton.pack(pady=12, padx=12)
        self.detailedForecastTextbox.pack(pady=12, padx=12)

    # set defaults and objects for the frame
    def show_detailed_forecast(self, forecast_data=None):
        self.clear_frame()

        # add a textbox to show the detailed forecast
        text = 'Forecast for {name}:\n\n{forecast}'.format(name=forecast_data['properties']['periods'][0]['name'], forecast=forecast_data['properties']['periods'][0]['detailedForecast'])
        self.detailedForecastTextbox = customtkinter.CTkTextbox(master=self, wrap='word', fg_color='transparent', font=('arial bold', 14))
        self.detailedForecastTextbox.insert('0.0', text)
        self.detailedForecastTextbox.configure(state='disabled')

        # add a button to hide the detailed forecast
        self.hideButton = customtkinter.CTkButton(master=self, text='Hide', command=self.hide)

        # add a button to show the detailed forecast
        self.showButton = customtkinter.CTkButton(master=self, text='Forecast Details', command=self.show)

        # pack the show button by default
        self.showButton.pack(pady=12, padx=12)

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
            self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='{name}\n{temperature}°F\nForecast: {forecast}\n'.format(name=forecast_data['properties']['periods'][period]['name'], temperature=forecast_data['properties']['periods'][period]['temperature'], forecast=forecast_data['properties']['periods'][period]['shortForecast']))
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

    # hide the active alerts
    def hide(self):
        self.hideButton.pack_forget()
        self.showButton.pack(pady=12, padx=12)
        self.alertTextbox.pack_forget()

    # show the active alerts
    def show(self):
        self.showButton.pack_forget()
        self.hideButton.pack(pady=12, padx=12)
        self.alertTextbox.pack(pady=12, padx=12)

    # display the active alerts details
    def show_active_alerts(self, alert_matches=None):
        self.clear_frame()

        # add the alerts to the text
        text = 'Active alerts:\n\n'
        for alert in alert_matches:
            text += 'Description: {description}\nInstruction: {instruction}\n'.format(description=alert_matches[alert]['description'], instruction=alert_matches[alert]['instruction'])
        
        # add a textbox to show the alert details
        self.alertTextbox = customtkinter.CTkTextbox(master=self, wrap='word', fg_color='transparent', font=('arial bold', 14))
        self.alertTextbox.insert('0.0', text)
        self.alertTextbox.configure(state='disabled')

        # add a button to hide the active alerts
        self.hideButton = customtkinter.CTkButton(master=self, text='Hide', command=self.hide)

        # add a button to show the active alerts
        self.showButton = customtkinter.CTkButton(master=self, text='Alert Details', command=self.show)

        # pack the show button by default
        self.showButton.pack(pady=12, padx=12)