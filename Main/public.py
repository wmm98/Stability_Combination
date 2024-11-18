import time


class publicInterface:
    def __init__(self):
        pass

    def read_ini_file(self, file_obj, file_path):
        return file_obj.read(file_path)

    def remove_info_space(self, info):
        return info.replace('\r', '').replace('\t', '').replace(' ', '').replace('\n', '')

    def deal_string(self, info):
        return self.remove_info_space(info).upper()

    def return_end_time(self, now_time, timeout=180):
        timedelta = 1
        end_time = now_time + timeout
        return end_time

    def get_current_time(self):
        return time.time()
