import os


class Config:
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    xml_report_path = os.path.join(project_path, "Report", "xml")
    html_report_path = os.path.join(project_path, "Report", "html")
    environment_properties_path = os.path.join(project_path, "Report", "environment.properties")
    debug_log_path = os.path.join(project_path, "Log", "Debug", "log.log")
    logcat_path = os.path.join(project_path, "Log", "Logcat")

    # EMMC, DDR压测
    pretesting_path = os.path.join(project_path, "PreTesting")
    DDR_memtester_path = os.path.join(pretesting_path, "DDR", "memtester")
    DDR_stressapptest_path = os.path.join(pretesting_path, "DDR", "stressapptest")
    DDR_stressapptest_switch_path = os.path.join(pretesting_path, "DDR", "stressapptest_switch")
    EMMC_path = os.path.join(pretesting_path, "EMMC")

    # U盘压测
    USB_flash_path = os.path.join(pretesting_path, "USBFlash")
    USB_recognition_demo_path = os.path.join(USB_flash_path, "test_demo_usb_recognition.sh")

    # 开机卡logo
    camera_key_img_path = os.path.join(project_path, "Photo", "BootLogo", "CameraPhoto", "Key")
    camera_origin_img_path = os.path.join(project_path, "Photo", "BootLogo", "CameraPhoto", "Take")

    logo_key_path = os.path.join(project_path, "Photo", "BootLogo", "Logo", "Key")
    logo_logo_path = os.path.join(project_path, "Photo", "BootLogo", "Logo", "Logo")
    # debug_log_path = os.path.join(project_path, "Log", "Debug", "debug_log.txt")
    system_failed_log_path = os.path.join(project_path, "Log", "Logcat", "failed_logcat.txt")
    flag_file_path = os.path.join(project_path, "UI", "flag.txt")
    config_file_path = os.path.join(project_path, "UI", "config.ini")

    bg_config_ini_path = os.path.join(project_path, "UI", "background_config.ini")
    ui_config_ini_path = os.path.join(project_path, "UI", "ui_config.ini")

    # 摄像头压测
    camera_stability_path = os.path.join(project_path, "Photo", "CameraStability")
    camera_sta_exp_path = os.path.join(camera_stability_path, "Expect")
    camera_sta_test_path = os.path.join(camera_stability_path, "Test")
    camera_sta_exp_default_path = os.path.join(camera_sta_exp_path, "Default")
    # 预期前、后镜头
    camera_sta_exp_front_path = os.path.join(camera_sta_exp_path, "Front")
    camera_sta_exp_rear_path = os.path.join(camera_sta_exp_path, "Rear")
    camera_sta_exp_front_photograph_path = os.path.join(camera_sta_exp_front_path, "Photograph", "exp_front_photograph.jpg")
    camera_sta_exp_front_preview_path = os.path.join(camera_sta_exp_front_path, "PreView", "exp_front_preview.png")
    camera_sta_exp_rear_photograph_path = os.path.join(camera_sta_exp_rear_path, "Photograph", "exp_rear_photograph.jpg")
    camera_sta_exp_rear_preview_path = os.path.join(camera_sta_exp_rear_path, "PreView", "exp_rear_preview.png")
    camera_sta_exp_default_photograph_path = os.path.join(camera_sta_exp_default_path, "Photograph", "exp_default_photograph.jpg")
    camera_sta_exp_default_preview_path = os.path.join(camera_sta_exp_default_path, "PreView", "exp_default_preview.png")
    # 测试前后镜头
    camera_sta_test_front_path = os.path.join(camera_sta_test_path, "Front")
    camera_sta_test_rear_path = os.path.join(camera_sta_test_path, "Rear")
    camera_sta_test_default_path = os.path.join(camera_sta_test_path, "Default")
    camera_sta_test_front_photograph_path = os.path.join(camera_sta_test_front_path, "Photograph", "test_front_photograph.jpg")
    camera_sta_test_front_preview_path = os.path.join(camera_sta_test_front_path, "PreView", "test_front_preview.png")
    camera_sta_test_rear_photograph_path = os.path.join(camera_sta_test_rear_path, "Photograph", "test_rear_photograph.jpg")
    camera_sta_test_rear_preview_path = os.path.join(camera_sta_test_rear_path, "PreView", "test_rear_preview.png")
    camera_sta_test_default_photograph_path = os.path.join(camera_sta_test_default_path, "Photograph", "test_default_photograph.jpg")
    camera_sta_test_default_preview_path = os.path.join(camera_sta_test_default_path, "PreView", "test_default_preview.png")
    # camera_preview_photograph.txt
    camera_sta_test_log_path = os.path.join(logcat_path, "camera_preview_photograph.txt")

    # wifi,mobile, eth0  btn failed log path
    wifi_btn_sta_test_log_path = os.path.join(logcat_path, "wifi_btn_stability_test.txt")
    mobile_btn_sta_test_log_path = os.path.join(logcat_path, "mobile_btn_stability_test.txt")
    eth_btn_sta_test_log_path = os.path.join(logcat_path, "eth_btn_stability_test.txt")

    # U盘拔插压测
    bat_query_flash_path = os.path.join(project_path, "UI", "bat_query_flash.bat")
    process_usb_flash_path = os.path.join(project_path, "UI", "process_usb_flash_path.py")
    usb_recognize_log_path = os.path.join(project_path, "UI", "usb_recognize_log.txt")

    section_ui_to_background = "UI-Background"
    section_background_to_ui = "Background-UI"
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
    ui_option_device_name = "device_name"
    bg_option_devices_name = "devices_name"
    bg_option_COM_ports = "COM_ports"

    # 开关机卡logo
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

    ui_option_cases = "cases"
    ui_option_logo_cases = "logo_cases"
    ui_option_logo_test_times = "logo_test_times"

    # 开关机检查
    section_ui_boot_check = "Boot-Check"

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





