import configparser
from config_path import UIConfigPath


class ConfigP(UIConfigPath):
    section_ui_to_background = "UI-Background"
    section_background_to_ui = "Background-UI"
    ui_option_root_steps = "root_steps"
    ui_option_system_type = "system"
    ui_option_mem_free_value = "mem_free_value"
    ui_option_test_duration = "test_duration"
    ui_option_memtester_duration = "memtester_duration"
    ui_option_stressapptest_duration = "stress_app_test_duration"
    ui_option_switch_stressapptest_duration = "stress_app_switch_duration"
    ui_option_is_memtester = "is_memtester"
    ui_option_is_stress_app_test = "is_stress_app_test"
    ui_option_is_stress_app_switch = "is_stress_app_switch"
    bg_option_devices_name = "devices_name"
    bg_option_COM_ports = "COM_ports"

    ui_option_cases = "cases"

    def __init__(self, ini_path):
        self.ini_path = ini_path
        self.config = configparser.ConfigParser()
        self.config.read(self.ini_path)
        print(self.config.sections())

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
        return self.config.get(section, option)
