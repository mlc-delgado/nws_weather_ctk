# NWS Weather CTk

This is a simple Python application written with customtkinter that fetches weather data from the U.S. National Weather Service.

## Usage

Start the application by running nws_weather_ctk.py.

Once started, simply enter your city name and state, and then click on **Set Location**. The app will use geocoding from MAPS and the NWS API to fetch current forecast data and active alerts for your region. Active alerts will only show if your county name is mentioned in the alert details. Weather data is refreshed every 1 hour. 

Click on **Forecast Details** to view a detailed forecast for your region. To get a 7-day forecast, click on **7-Day Forecast**. If there are active alerts for your region, click on **Alert Details** to view more details on the alerts.

To change location click on **Location** and enter a new city and state. Location data is cached locally in a config yaml and updated only when the location changes. 
