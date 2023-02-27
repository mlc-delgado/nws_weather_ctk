# NWS Weather CTk

This is a simple Python application written with customtkinter that fetches weather data from the U.S. National Weather Service.

## Usage

Start the application by running main.py.

Once started, simply enter your city name and postal code, and then click on **Set Location**. The app will use geocoding from MAPS and the NWS API to fetch current forecast data and active alerts for your region. Active alerts will only show if your county name is mentioned in the alert details. Weather data is refreshed every 1 hour. 

To change location click on **Update Location** and enter a new city and postal code. Location data is cached locally in a config yaml and updated only when the location changes. 
