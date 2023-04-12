import customtkinter
from nws_weather_ctk.utils.config import load_config, update_appearance

class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        config = load_config()
        self.theme = config['window_theme']
        self.icon_theme = config['icon_theme']

        self.create_widgets()

    def create_widgets(self):
        self.settings_label = customtkinter.CTkLabel(self, font=('arial bold', 14), text='Settings')
        self.settings_label.pack(padx=10, pady=10)

        self.sub_settings_frame = SubSettingsFrame(self)
        self.sub_settings_frame.pack(padx=10, pady=0)

    def set_icon_theme(self, value):
        self.master.set_icon_theme(value)

    def set_theme(self, value):
        self.master.set_theme(value)

class SubSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.window_theme = self.master.theme.capitalize()
        self.icon_theme = self.master.icon_theme.capitalize()

        self.create_widgets()

    def create_widgets(self):
        self.window_settings_label = customtkinter.CTkLabel(self, font=('arial bold', 14), text='Window Theme')
        self.window_settings_label.pack(padx=10, pady=5)

        self.theme_segmented_button = customtkinter.CTkSegmentedButton(self, values=['Light', 'Dark'], font=('arial', 14), command=self.theme)
        self.theme_segmented_button.set(self.window_theme)
        self.theme_segmented_button.pack(padx=10, pady=5)

        self.icon_settings_label = customtkinter.CTkLabel(self, font=('arial bold', 14), text='Icon Theme')
        self.icon_settings_label.pack(padx=10, pady=5)

        self.icon_segmented_button = customtkinter.CTkSegmentedButton(self, values=['Light', 'Dark'], font=('arial', 14), command=self.icon)
        self.icon_segmented_button.set(self.icon_theme.capitalize())
        self.icon_segmented_button.pack(padx=10, pady=5)

    def theme(self, value):
        update_appearance(window_theme=value.lower())
        self.master.set_theme(value)

    def icon(self, value):
        update_appearance(icon_theme=value.lower())
        self.master.set_icon_theme(value.lower())