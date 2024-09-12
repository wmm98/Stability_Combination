import configparser
from config_path import UIConfigPath


class ConfigP(UIConfigPath):
    section_ui_to_background = "UI-Background"
    section_background_to_ui = "Background-UI"

    # 公共
    ui_option_device_name = "device_name"
    bg_option_devices_name = "devices_name"
    bg_option_COM_ports = "COM_ports"

    # EMMC, DDR
    section_DDR_EMMC = "DDR_EMMC"
    ui_option_root_steps = "root_steps"
    ui_option_system_type = "system"
    ui_option_mem_free_value = "mem_free_value"
    ui_option_test_duration = "test_duration"
    ui_option_memtester_duration = "memtester_duration"
    ui_option_stressapptest_duration = "stress_app_test_duration"
    ui_option_switch_stressapptest_duration = "stress_app_switch_duration"
    ui_option_emmmc_duration = "emmc_duration"
    ui_option_is_memtester = "is_memtester"
    ui_option_is_stress_app_test = "is_stress_app_test"
    ui_option_is_stress_app_switch = "is_stress_app_switch"
    ui_option_is_emmc_test = "is_emmc_test"
    ui_option_ddr_emmc_test_times = "emmc_test_times"

    # 开机卡Logo
    section_ui_logo = "Boot-Logo"
    option_logo_is_adapter = "is_adapter"
    option_logo_is_power_button = "is_power_button"
    option_logo_is_is_usb = "is_usb"
    option_logo_COM = "com"
    option_logcat_duration = "logcat_duration"
    option_logo_adapter_power_config = "adapter_power_config"
    option_logo_boot_time = "button_boot_time"
    option_logo_double_screen = "double_screen_config"
    option_only_boot_config = "only_boot_config"
    option_usb_config = "usb_config"
    option_power_button_config = "power_button_config"

    ui_option_cases = "cases"
    ui_option_logo_cases = "logo_cases"
    ui_option_logo_test_times = "logo_test_times"

    def __init__(self, ini_path):
        self.ini_path = ini_path
        self.config = configparser.ConfigParser()

    def init_config_file(self):
        with open(self.ini_path, 'w') as configfile:
            self.config.write(configfile)

    def add_config_section(self, section):
        self.config.read(self.ini_path)
        if section not in self.config:
            self.config.add_section(section)
        with open(self.ini_path, 'w') as configfile:
            self.config.write(configfile)

    def add_config_option(self, section, option, value):
        self.config.read(self.ini_path)
        self.add_config_section(section)
        self.config.set(section, option, value)
        with open(self.ini_path, 'w') as configfile:
            self.config.write(configfile)

    def get_option_value(self, section, option):
        self.config.read(self.ini_path)
        return self.config.get(section, option)
