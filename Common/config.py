import os


class Config:
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    xml_report_path = os.path.join(project_path, "Report", "xml")
    html_report_path = os.path.join(project_path, "Report", "html")
    environment_properties_path = os.path.join(project_path, "Report", "environment.properties")
    debug_log_path = os.path.join(project_path, "Log", "Debug", "log.log")

    # EMMC, DDR压测
    pretesting_path = os.path.join(project_path, "PreTesting")
    DDR_memtester_path = os.path.join(pretesting_path, "DDR", "memtester")
    DDR_stressapptest_path = os.path.join(pretesting_path, "DDR", "stressapptest")
    DDR_stressapptest_switch_path = os.path.join(pretesting_path, "DDR", "stressapptest_switch")
    EMMC_path = os.path.join(pretesting_path, "EMMC")

    # 开机卡logo
    camera_key_img_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key")
    camera_origin_img_path = os.path.join(project_path, "Photo", "CameraPhoto", "Take")

    logo_key_path = os.path.join(project_path, "Photo", "Logo", "Key")
    logo_logo_path = os.path.join(project_path, "Photo", "Logo", "Logo")
    # debug_log_path = os.path.join(project_path, "Log", "Debug", "debug_log.txt")
    system_failed_log_path = os.path.join(project_path, "Log", "Logcat", "failed_logcat.txt")
    flag_file_path = os.path.join(project_path, "UI", "flag.txt")
    config_file_path = os.path.join(project_path, "UI", "config.ini")

    bg_config_ini_path = os.path.join(project_path, "UI", "background_config.ini")
    ui_config_ini_path = os.path.join(project_path, "UI", "ui_config.ini")

    section_ui_to_background = "UI-Background"
    section_background_to_ui = "Background-UI"
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
    ui_option_device_name = "device_name"
    bg_option_devices_name = "devices_name"
    bg_option_COM_ports = "COM_ports"

    # 开关机卡logo
    # 开机卡Logo
    section_ui_logo = "Boot-Logo"
    option_logo_is_adapter = "is_adapter"
    option_logo_is_power_button = "is_power_button"
    option_logo_is_is_usb = "is_usb"
    option_logo_COM = "COM"
    option_logcat_duration = "logcat_duration"
    option_logo_adapter_power_config = "adapter_power_config"
    option_logo_boot_time = "button_boot_time"
    option_logo_double_screen = "double_screen_config"
    option_only_boot_config = "only_boot_config"
    option_usb_config = "usb_config"
    option_power_button_config = "power_button_config"

    ui_option_cases = "cases"





