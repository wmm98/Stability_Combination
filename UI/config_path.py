import os


class UIConfigPath:

    # project_path = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    project_path = os.path.join(str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))), "Stability")
    print(project_path)
    background_config_file_path = os.path.join(project_path, "UI", "background_config.ini")
    ui_config_file_path = os.path.join(project_path, "UI", "ui_config.ini")
    debug_log_path = os.path.join(project_path, "Log", "Debug", "log.log")
    run_bat_path = os.path.join(project_path, "run.bat")

    # DDR,EMMC压测
    # bat_pre_info_path = "bat_pre_info.bat"
    bat_pre_info_path = os.path.join(project_path, "UI", "bat_pre_info.bat")
    bat_mem_info_path = os.path.join(project_path, "UI", "bat_mem_free.bat")
    py_pre_info_path = os.path.join(project_path, "UI", "pre_info.py")
    mem_log_path = os.path.join(project_path, "UI", "mem_log.txt")

    # 卡logo压测
    logo_take_path = os.path.join(project_path, "Photo", "Logo", "Logo", "Logo.png")
    logo_key_path = os.path.join(project_path, "Photo", "Logo", "Key", "Key.png")
    camera_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Key.png")
    camera2_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Key2.png")
    # failed_logcat.txt
    adb_log_path = os.path.join(project_path, "Log", "Logcat", "failed_logcat.txt")
    failed_image_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Failed.png")
