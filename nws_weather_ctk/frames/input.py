import customtkinter
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
        self.entry1 = customtkinter.CTkEntry(master=self, font=('arial bold', 14),  placeholder_text=self.placeholder_city)
        self.entry1.pack(pady=12, padx=12)

        self.entry2 = customtkinter.CTkEntry(master=self, font=('arial bold', 14), placeholder_text=self.placeholder_state)
        self.entry2.pack(pady=12, padx=12)

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
        return self.entry1.get(), self.entry2.get()
    
    def update(self):
        self.refresh()
        self.entry1.configure(placeholder_text=self.placeholder_city)
        self.entry2.configure(placeholder_text=self.placeholder_state)