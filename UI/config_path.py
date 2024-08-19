import os


class UIConfigPath:

    # project_path = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    project_path = os.path.join(str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))), "Stability")
    background_config_file_path = os.path.join(project_path, "UI", "background_config.ini")
    ui_config_file_path = os.path.join(project_path, "UI", "ui_config.ini")
    debug_log_path = os.path.join(project_path, "Log", "log.log")
    run_bat_path = os.path.join(project_path, "run.bat")
    # bat_pre_info_path = "bat_pre_info.bat"
    bat_pre_info_path = os.path.join(project_path, "UI", "bat_pre_info.bat")

    bat_mem_info_path = os.path.join(project_path, "UI", "bat_mem_free.bat")

    py_pre_info_path = os.path.join(project_path, "UI", "pre_info.py")

    mem_log_path = os.path.join(project_path, "UI", "mem_log.txt")

