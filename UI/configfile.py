import configparser
from config_path import UIConfigPath


class ConfigP(UIConfigPath):
    section_ui_to_background = "UI-Background"
    section_background_to_ui = "Background-UI"
    ui_option_root_steps = "root_steps"
    bg_option_devices_name = "devices_name"
    bg_option_COM_ports = "COM_ports"

    def __init__(self, ini_path):
        self.ini_path = ini_path
        self.config = configparser.ConfigParser()
        self.config.read(self.ini_path)

    def add_config_section(self, section):
        if section not in self.config:
            self.config.add_section(section)
        with open(self.ini_path, 'w') as configfile:
            self.config.write(configfile)

    def add_config_option(self, section, option, value):
        self.config.set(section, option, value)
        with open(self.ini_path, 'w') as configfile:
            self.config.write(configfile)

    def get_option_value(self, section, option):
        self.config.read(self.ini_path)
        return self.config.get(section, option)
