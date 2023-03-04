import customtkinter
from config import load_config, is_weekday, get_day_of_week, get_week, refresh_ms
from icons import get_emoji
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import pandas as pd
import datetime as dt

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

    # display the forecast and alerts
    def display_weather(self, hourly_forecast_data=None, detailed_forecast_data=None, alerts_data=None):
        # create the frame for the weather icon
        self.frame1 = IconFrame(master=self)
        self.frame1.grid(row=0, column=0, padx=12, pady=12)
        self.frame1.show_icon(hourly_forecast_data, detailed_forecast_data)
        # create the frame for the hourly forecast details
        self.frame2 = HourlyForecastFrame(master=self)
        self.frame2.grid(row=0, column=1, padx=12, pady=12)
        self.frame2.show_hourly_forecast(hourly_forecast_data, alerts_data)

        # set default column and span for detailed forecast frame
        detailedforecast_span = 2

        # check if there are active alerts
        if len(alerts_data['features']) > 0:
            alert_matches = self.check_for_alerts(alerts_data)
            if len(alert_matches) > 0:
                # add a frame to show the active alerts
                self.frame4 = ActiveAlertsFrame(master=self)
                self.frame4.grid(row=1, column=1, padx=12, pady=12)
                self.frame4.show_active_alerts(alert_matches)
                # add the alerts alerts next to the detailed forecast
                detailedforecast_span = 1

        # add a frame to show the detailed forecast
        self.frame4 = DetailedForecastFrame(master=self)
        self.frame4.grid(row=1, column=0, padx=12, pady=12, columnspan=detailedforecast_span)
        self.frame4.show_detailed_forecast(detailed_forecast_data)

    def update(self, hourly_forecast_data=None, detailed_forecast_data=None, alerts_data=None):
        self.frame1.update(hourly_forecast_data,detailed_forecast_data)
        self.frame2.update(hourly_forecast_data,alerts_data)
        self.frame4.update(detailed_forecast_data)

# frame to show the hourly forecast
class HourlyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        self.alerts = []
        self.alertTitle = 'Active Alerts:'

    def show_hourly_forecast(self, hourly_forecast_data=None, alerts_data=None):
        # add label to show the current temperature and forecast
        self.refresh(hourly_forecast_data, alerts_data)
        self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=self.text)
        self.forecastLabel.pack(pady=12, padx=12)

        if self.alerts != []:
            # add the alert label
            self.alertLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=self.alertTitle)
            self.alertLabel.pack(pady=0, padx=12)
            # add the list of alerts
            self.alertsListLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='\n'.join(self.alerts))
            self.alertsListLabel.pack(pady=0, padx=12)

    # set the label texts
    def refresh(self, hourly_forecast_data=None, alerts_data=None):
        config = load_config()

        self.text='Humidity: {humidity}%\n\nWind speed: {wind}\n\nWind direction: {wind_direction}\n\nPrecipitation: {precipitation}%\n\nDew point: {dew_point}°F'.format(
            forecast=hourly_forecast_data['properties']['periods'][0]['shortForecast'],
            city=config['city'],
            state=config['state'],
            humidity=hourly_forecast_data['properties']['periods'][0]['relativeHumidity']['value'],
            wind=hourly_forecast_data['properties']['periods'][0]['windSpeed'],
            wind_direction=hourly_forecast_data['properties']['periods'][0]['windDirection'],
            precipitation=hourly_forecast_data['properties']['periods'][0]['probabilityOfPrecipitation']['value'],
            # convert dew point value from Celsius to Fahrenheit
            dew_point = round((hourly_forecast_data['properties']['periods'][0]['dewpoint']['value'] * 9/5) + 32)
            )
        
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
                self.alerts = list(set(alert_matches))
        else:
            self.alerts = []
            self.alertTitle = 'No Active Alerts'

    # update the label text
    def update(self, hourly_forecast_data=None, alerts_data=None):
        self.refresh(hourly_forecast_data, alerts_data)
        self.forecastLabel.configure(text=self.text)
        try:
            self.alertLabel.configure(text=self.alertTitle)
        except:
            pass
        try:
            self.alertsListLabel.configure(text='\n'.join(self.alerts))
        except:
            pass

# frame to show the hourly forecast icon
class IconFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    # show the current weather icon
    def show_icon(self, hourly_forecast_data=None, detailed_forecast_data=None):
        self.refresh(hourly_forecast_data, detailed_forecast_data)
        config = load_config()

        # add a label for the current weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('arial',64), text=self.emoji)
        self.iconLabel.pack(pady=2, padx=12)

        # add a label for the temperature
        self.temperatureLabel = customtkinter.CTkLabel(master=self, font=('arial bold',20), text='{temperature}°F'.format(temperature=self.current_temperature))
        self.temperatureLabel.pack(pady=2, padx=12)
        # add a label for the high and low temperatures
        self.highLowLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=self.high_low_text)
        self.highLowLabel.pack(pady=0, padx=12)
        # add a label for the location
        self.locationLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text='{city}, {state}\n{forecast}'.format(city=config['city'], state=config['state'], forecast=self.hourly_forecast))
        self.locationLabel.pack(pady=12, padx=12)

    # set the label texts
    def refresh(self, hourly_forecast_data=None, detailed_forecast_data=None):
        # make a list of all temperatures throughout the day
        temperatures = []
        # add the current temperature to the list
        temperatures.append(hourly_forecast_data['properties']['periods'][0]['temperature'])
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
            self.high_low_text = 'Low: {low}°F'.format(low=low)
        else:
            self.high_low_text = 'High: {high}°F Low: {low}°F'.format( high=high, low=low)
        # set the emoji for the current forecast
        self.emoji = get_emoji(hourly_forecast_data['properties']['periods'][0]['shortForecast'], hourly_forecast_data['properties']['periods'][0]['isDaytime'])
        self.current_temperature = hourly_forecast_data['properties']['periods'][0]['temperature']
        self.hourly_forecast = hourly_forecast_data['properties']['periods'][0]['shortForecast']

    # update the label text
    def update(self, hourly_forecast_data=None, detailed_forecast_data=None):
        config = load_config()
        self.refresh(hourly_forecast_data, detailed_forecast_data)
        self.iconLabel.configure(text=self.emoji)
        self.temperatureLabel.configure(text='{temperature}°F'.format(temperature=self.current_temperature))
        self.highLowLabel.configure(text=self.high_low_text)
        self.locationLabel.configure(text='{city}, {state}\n{forecast}'.format(city=config['city'], state=config['state'], forecast=self.hourly_forecast))


# frame to show the detailed forecast
class DetailedForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

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
    def show_detailed_forecast(self, detailed_forecast_data):
        self.refresh(detailed_forecast_data)
        # add a textbox to show the detailed forecast
        self.detailedForecastTextbox = customtkinter.CTkTextbox(master=self, wrap='word', fg_color='transparent', font=('arial bold', 14))
        self.detailedForecastTextbox.insert('0.0', self.text)
        self.detailedForecastTextbox.configure(state='disabled')

        # add a button to hide the detailed forecast
        self.hideButton = customtkinter.CTkButton(master=self, text='Hide', command=self.hide)

        # add a button to show the detailed forecast
        self.showButton = customtkinter.CTkButton(master=self, text='Forecast Details', command=self.show)

        # pack the show button by default
        self.showButton.pack(pady=12, padx=12)

    # set the text for the textbox
    def refresh(self, detailed_forecast_data=None):
        self.text = 'Forecast for {name}:\n\n{forecast}'.format(name=detailed_forecast_data['properties']['periods'][0]['name'], forecast=detailed_forecast_data['properties']['periods'][0]['detailedForecast'])

    # update the text for the textbox
    def update(self, detailed_forecast_data=None):
        self.refresh(detailed_forecast_data)
        self.detailedForecastTextbox.configure(state='normal')
        self.detailedForecastTextbox.delete('0.0', 'end')
        self.detailedForecastTextbox.insert('0.0', self.text)
        self.detailedForecastTextbox.configure(state='disabled')

# frame to show the daily forecast
class DailyForecastFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class contstructor
        super().__init__(*args, **kwargs)

    def show_daily_forecast(self, detailed_forecast_data=None, period=None):
        self.refresh(detailed_forecast_data, period)
        # add a label for the weather icon
        # display the emoji for the forecast
        self.iconLabel = customtkinter.CTkLabel(master=self, font=('arial',48), text=self.emoji)
        self.iconLabel.pack(pady=12, padx=12)

        # add label to show the current temperature and forecast
        self.forecastLabel = customtkinter.CTkLabel(master=self, font=('arial bold',14), text=self.forecast_text)
        self.forecastLabel.pack(pady=12, padx=12)

        # refresh the icon and forecast label periodically
        self.iconLabel.after(refresh_ms, self.update, detailed_forecast_data, period)
        self.forecastLabel.after(refresh_ms, self.update, detailed_forecast_data, period)

    # set the icon and forecast text
    def refresh(self, detailed_forecast_data=None, period=None):
        self.emoji = get_emoji(detailed_forecast_data['properties']['periods'][period]['shortForecast'], detailed_forecast_data['properties']['periods'][period]['isDaytime'])
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
        # set a starting var for the column
        column = 0
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
                self.daily_forecast_frame.grid(row=0, column=column, padx=12, pady=12)
                self.daily_forecast_frame.show_daily_forecast(detailed_forecast_data, i)
                # increment the column
                column += 1

    def update(self, detailed_forecast_data=None):
        # destroy all the daily forecast frames
        for child in self.winfo_children():
            child.destroy()
        # show the weekly forecast
        self.show_weekly_forecast(detailed_forecast_data)

# frame to show the active alerts
class ActiveAlertsFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        self.text = 'No active alerts.'
        # add a textbox to show the alert details
        self.alertTextbox = customtkinter.CTkTextbox(master=self, wrap='word', fg_color='transparent', font=('arial bold', 14))

    # hide the active alerts
    def hide(self):
        self.hideButton.pack_forget()
        self.showButton.pack(pady=12, padx=12)
        self.alertTextbox.pack_forget()

    # show the active alerts
    def show(self, alert_matches=None):
        self.showButton.pack_forget()
        self.hideButton.pack(pady=12, padx=12)
        self.alertTextbox.pack(pady=12, padx=12)
        self.alertTextbox.after(refresh_ms, self.update, alert_matches)

    # display the active alerts details
    def show_active_alerts(self, alert_matches=None):
        self.update(alert_matches)
        self.alertTextbox.insert('0.0', self.text)
        self.alertTextbox.configure(state='disabled')

        # add a button to hide the active alerts
        self.hideButton = customtkinter.CTkButton(master=self, text='Hide', command=self.hide)

        # add a button to show the active alerts
        self.showButton = customtkinter.CTkButton(master=self, text='Alert Details', command=self.show)

        # pack the show button by default
        self.showButton.pack(pady=12, padx=12)

    # set the active alerts text
    def set_alerts(self, alert_matches=None):
        # add the alerts to the text if there are any in the alert_matches list
        if alert_matches:
            self.text = 'Active alerts:\n\n'
            for alert in alert_matches:
                self.text += 'Description: {description}\nInstruction: {instruction}\n'.format(description=alert_matches[alert]['description'], instruction=alert_matches[alert]['instruction'])

    # update the active alerts text
    def update(self, alert_matches=None):
        self.set_alerts(alert_matches)
        self.alertTextbox.configure(state='normal')
        self.alertTextbox.delete('0.0', 'end')
        self.alertTextbox.insert('0.0', self.text)
        self.alertTextbox.configure(state='disabled')

# frame to show temperature graph
class TemperatureGraphFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def build_graph(self, x_title=None, x_axis_labels=None, y_axis_labels=None, x_size=None, y_size=None, locator=None):
        df = pd.DataFrame({x_title: x_axis_labels, '°F': y_axis_labels})

        ax = df.plot(x=x_title, y='°F', kind='line', linestyle='dashed', marker='o', color='blue')

        # set locator on the x axis
        if locator == 'day':
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        elif locator == 'hour':
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        # set the figure size
        fig = ax.get_figure()
        fig.set_size_inches(x_size, y_size)

        return fig
    
    # show the daily temperature graph
    def show_daily_graph(self, hourly_forecast_data=None):
        periods = len(hourly_forecast_data['properties']['periods'])
        self.update(hourly_forecast_data, periods)
        # add a label for the temperature graph title
        self.titleLabel = customtkinter.CTkLabel(master=self, font=('arial bold', 14), text='Weekly Temperature Forecast')
        self.titleLabel.pack(pady=12, padx=12)

        self.fig = self.set_values(hourly_forecast_data, periods)

        self.show(self.fig)

    def show_hourly_graph(self, hourly_forecast_data=None):
        periods = 24
        self.update(hourly_forecast_data, periods)
        # add a label for the temperature graph title
        self.titleLabel = customtkinter.CTkLabel(master=self, font=('arial bold', 14), text='24 Hour Forecast')
        self.titleLabel.pack(pady=12, padx=12)

        self.fig = self.set_values(hourly_forecast_data, periods)

        self.show(self.fig)

    def set_values(self, hourly_forecast_data=None, periods=None):
        # create the x axis and y axis values for startTime of each period
        self.x_axis_labels = []
        self.y_axis_labels = []
        for i in range(0, periods):
            # get startTime for each period
            startTime = hourly_forecast_data['properties']['periods'][i]['startTime']
            # convert the startTime to a datetime object
            startTime = dt.datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%S%z')
            # append the startTime to the x axis labels
            self.x_axis_labels.append(startTime)
            # append the temperature for each period to the y axis labels
            self.y_axis_labels.append(int(hourly_forecast_data['properties']['periods'][i]['temperature']))
        if periods != 24:
            self.x_title = 'Day'
            self.x_size = 14
            self.y_size = 5
            self.locator = 'day'
        else:
            self.x_title = 'Hour'
            self.x_size = 14
            self.y_size = 5
            self.locator = 'hour'
        return self.build_graph(self.x_title, self.x_axis_labels, self.y_axis_labels, self.x_size, self.y_size, self.locator)

    def show(self, fig=None):
        # remove the canvas from the frame
        try:
            self.canvas.get_tk_widget().pack_forget()
        except:
            pass
        # create the canvas to show the graph
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=12, padx=12, fill='both', expand=True)

    def update(self, hourly_forecast_data=None, periods=None):
        self.fig = self.set_values(hourly_forecast_data, periods)
        self.show(self.fig)

