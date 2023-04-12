import sys
from nws_weather_ctk.app import App

# run the app
if __name__ == '__main__':
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit()
    except EOFError:
        sys.exit()