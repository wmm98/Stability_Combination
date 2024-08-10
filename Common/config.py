import os


class Config:
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    debug_log_path = os.path.join(project_path, "Log", "log.log")





