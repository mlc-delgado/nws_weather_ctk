import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import pandas as pd
import datetime as dt

periods = 24

# frame to show temperature graph
class TemperatureGraphFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

        self.hourly_forecast_data = None
        self.fig = None

    def refresh(self):
        # get the forecast data
        self.hourly_forecast_data = self.master.data['hourly_forecast_data']

    def build_graph(self, x_title=None, x_axis_labels=None, y_axis_labels=None, x_size=None, y_size=None):
        df = pd.DataFrame({x_title: x_axis_labels, '°F': y_axis_labels}, index=y_axis_labels)

        ax = df.plot(x=x_title, y='°F', kind='line', linestyle='dashed', marker='o', color='blue')

        # set locator on the x axis
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        # set the figure size
        fig = ax.get_figure()
        fig.set_size_inches(x_size, y_size)

        return fig

    # show the hourly temperature graph
    def display_elements(self):
        self.refresh()
        # periods = len(self.hourly_forecast_data['properties']['periods'])
        periods = 24
        # add a label for the temperature graph title
        self.titleLabel = customtkinter.CTkLabel(master=self, font=('arial bold', 14), text='24 Hour Forecast')
        self.titleLabel.pack(pady=12, padx=12)
        # create a figure for the temperature graph
        self.fig = self.set_values(periods)
        # display the figure in the frame
        self.show()

    def set_values(self, periods=None):
        # create the x axis and y axis values for startTime of each period
        self.x_axis_labels = []
        self.y_axis_labels = []
        self.x_title = 'Hour'
        self.x_size = 14
        self.y_size = 5
        for i in range(0, periods):
            # get startTime for each period
            startTime = self.hourly_forecast_data['properties']['periods'][i]['startTime']
            # convert the startTime to a datetime object
            startTime = dt.datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%S%z')
            # append the startTime to the x axis labels
            self.x_axis_labels.append(startTime.strftime('%-I %p'))
            # append the temperature for each period to the y axis labels
            self.y_axis_labels.append(int(self.hourly_forecast_data['properties']['periods'][i]['temperature']))
        return self.build_graph(self.x_title, self.x_axis_labels, self.y_axis_labels, self.x_size, self.y_size)

    def show(self):
        # create the canvas to show the graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=12, padx=12, fill='both', expand=True)

    # clear the frame
    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

