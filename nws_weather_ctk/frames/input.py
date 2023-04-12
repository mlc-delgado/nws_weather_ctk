import customtkinter
import tkinter
from nws_weather_ctk.utils.config import load_config, check_config

# frame to show the user input
class InputFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        # call the parent class constructor
        super().__init__(*args, **kwargs)

    def clear_frame(self):
        # clear the frame
        for widget in self.winfo_children():
            widget.destroy()

    # display the input boxes
    def show_input(self):
        # set the placeholder texts
        self.refresh()
        # clear the frame
        self.clear_frame()

        # provide input boxes for city and state
        self.city_entry = customtkinter.CTkEntry(master=self, font=('arial bold', 14))
        self.city_entry.pack(pady=12, padx=12)
        self.state_entry = customtkinter.CTkEntry(master=self, font=('arial bold', 14))
        self.state_entry.pack(pady=12, padx=12)

        # if the city has not been set, set the placeholder text to 'City'
        if self.placeholder_city == 'City':
            self.city_entry.configure(placeholder_text=self.placeholder_city)
        # auto fill the entry box if the placeholder is not the default
        else:
            self.city_var = tkinter.StringVar(self, value=self.placeholder_city)
            self.city_entry.configure(textvariable=self.city_var)
        # if the state has not been set, set the placeholder text to 'State'
        if self.placeholder_state == 'State':
            self.state_entry.configure(placeholder_text=self.placeholder_state)
        # auto fill the entry box if the placeholder is not the default
        else:
            self.state_var = tkinter.StringVar(self, value=self.placeholder_state)
            self.state_entry.configure(textvariable=self.state_var)

        # add button to set location
        self.button = customtkinter.CTkButton(master=self, font=('arial bold', 14), text='Set Location', command=lambda: self.master.set_location())
        self.button.pack(pady=12, padx=12)

    # refresh the placeholder texts
    def refresh(self):
        # load the config and check if location has been set
        config = load_config()
        if check_config(config):
            # set the placeholder text to the current location
            self.placeholder_city = config['city']
            self.placeholder_state = config['state']
        else:
            # set the placeholder text to the default location
            self.placeholder_city = 'City'
            self.placeholder_state = 'State'

    # return the values of the input boxes
    def get_values(self):
        return self.city_entry.get(), self.state_entry.get()
    
    def update(self):
        try:
            self.city_entry.pack_forget()
            self.state_entry.pack_forget()
            self.button.pack_forget()
        except:
            pass
        self.show_input()