import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import pandas as pd
import datetime as dt

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
        self.master.check_for_updates()
        self.fig = self.set_values(hourly_forecast_data, periods)
        self.show(self.fig)

