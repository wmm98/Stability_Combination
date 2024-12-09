import configparser
from config_path import UIConfigPath


class ConfigP(UIConfigPath):
    section_ui_to_background = "UI-Background"
    section_background_to_ui = "Background-UI"

    # 公共
    ui_option_device_name = "device_name"
    bg_option_devices_name = "devices_name"
    bg_option_COM_ports = "COM_ports"
    # 是否进行失败概率性统计测试
    is_probability_test = "is_probability_test"
    # 每一轮间隔时长
    test_interval = "rounds_interval"
    # 通用模块的关到开的时长
    bt_interval = "bt_interval"

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

    option_wifi_test = "is_wifi_test"
    option_eth_test = "is_eth_test"
    option_mobile_test = "is_mobile_test"
    option_bt_test = "is_bt_test"
    option_nfc_test = "is_nfc_test"
    option_usb_test = "is_usb_test"
    option_team_one = "is_team_one"
    option_team_two = "is_team_two"
    option_camera_test = "is_camera_test"

    ui_option_cases = "cases"
    ui_option_logo_cases = "logo_cases"
    ui_option_logo_test_times = "logo_test_times"

    # 开关机检查
    section_ui_boot_check = "Boot-Check"
    ui_option_boot_usb_path = "boot_usb_flash_path"
    relay_reboot_interval = bt_interval

    # 相机压测
    section_ui_camera_check = "Camera-Check"
    option_front_and_rear = "front_rear"
    option_switch_x_value = "x_value"
    option_switch_y_value = "y_value"
    option_camera_test_times = "camera_test_times"

    # wifi开关压测
    section_wifi_check = "WIFI-Check"
    option_wifi_btn_test_times = "wifi_btn_test_times"

    # 4G开关压测
    section_mobile_check = "Mobile-Check"
    option_mobile_btn_test_times = "mobile_btn_test_times"

    # 以太网
    section_eth_check = "Eth-check"
    option_eth_btn_test_times = "wth_btn_test_times"

    # U盘识别压测
    section_usb_recognize = "USB-recognition"
    # ui_option_root_steps 同EMMC, DDR
    ui_option_usb_path = "usb_flash_path"
    ui_option_usb_config_line = "com_line"
    ui_option_usb_com = "com"
    option_usb_recognition_test_times = "usb_recognition_test_duration"
    option_usb_flash_name = "usb_flash_name"
    option_usb_flash_base_name = "usb_flash_base_name"

    # U盘/TF卡读取速率
    section_storage_stability = "Storage_Stability"
    ui_option_storage_path = "storage_flash_path"
    ui_option_partition_path = "storage_flash_partition"
    ui_option_usb_ports_num = "usb_num"
    option_storage_test_times = "storage_stability_test_times"

    # 恢复出厂设置压测用例配置
    section_factory_reset_stability = "Factory_Reset"
    option_factory_reset_test_times = "reset_test_times"

    # 蓝牙连接测试
    section_bt_connect_test = "Bt_connect_test"
    option_bt_connect_test_times = "bt_connect_test_times"
    option_bt_connect_test_com = "bt_connect_com"
    option_bt_com_config = "com_config"
    slave_bt_reconnect_interval = bt_interval

    # 休眠唤醒
    section_sleep_wake = "Sleep-Awake"
    option_sleep_duration = "sleep_duration"
    option_sleep_config = "usb_config"
    option_sleep_test_times = "sleep_test_times"
    option_sleep_com_port = "sleep_com_port"

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
