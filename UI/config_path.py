import os

class UIConfigPath:
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    config_file_path = os.path.join(project_path, "UI", "config.ini")
    debug_log_path = os.path.join(project_path, "Log", "log.log")
    run_bat_path = os.path.join(project_path, "run.bat")

