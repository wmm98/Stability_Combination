from configfile import ConfigP
import process_shell
import os
import time
print("*****************************")

root_path = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
print("*****************************")
print(root_path)
bg_config_ui_path = os.path.join(root_path, "UI", "background_config.ini")
bg_conf_file = ConfigP(bg_config_ui_path)

ui_config_ui_path = os.path.join(root_path, "UI", "ui_config.ini")
ui_conf_file = ConfigP(ui_config_ui_path)
shell = process_shell.Shell()


class GetMemFree:
    def __init__(self):
        self.device_name = bg_conf_file.get_option_value(bg_conf_file.section_background_to_ui,
                                                    bg_conf_file.bg_option_devices_name)

        self.log = open("mem_log.txt", "w+")

    def root_devices(self):
        devices_lists = shell.invoke("adb devices").replace('\r', '').replace('\t', '').replace(' ', '')
        device_online = self.device_name + "device"
        cmd_raw = ui_conf_file.get_option_value(ui_conf_file.section_ui_to_background, ui_conf_file.ui_option_root_steps)
        if len(cmd_raw) != 0:
            cmds = ""
            if "," in cmd_raw:
                cmds = cmd_raw.split(",")
            elif "，" in cmd_raw:
                cmds = cmd_raw.split("，")

            for cmd in cmds:
                shell.invoke(cmd)
                if cmd == "reboot":
                    # if self.device_name + "device" in devices.replace('\r', '').replace('\t', '').replace(' ', ''):

                    seconds_flag = 0
                    boot_flag = 0
                    # adb 起来不能超过60s
                    while seconds_flag < 60:
                        if device_online in devices_lists:
                            break
                        time.sleep(1)
                        seconds_flag += 1

                    if seconds_flag >= 60:
                        self.log.write("重启超过60s过程中adb无法起来！！！" + "\n")
                        raise Exception

                    while boot_flag < 40:
                        boot_res = shell.invoke("adb -s %s shell getprop sys.boot_completed" % self.device_name)
                        if "1" in boot_res:
                            break
                        time.sleep(1)
                        boot_flag += 1
                else:
                    time.sleep(2)

        # 验证是否真的可root
        shell.invoke("adb -s %s shell touch /data/stress_test.txt" % self.device_name)
        if "stress_test.txt" in shell.invoke("adb -s %s shell ls /data" % self.device_name):
            self.log.write("root 成功" + "\n")
        else:
            self.log.write("root 失败， 请检查!!!")

        shell.invoke("adb -s %s shell rm /data/stress_test.txt" % self.device_name)

    def get_mem_free_info(self):
        self.root_devices()
        system_type = ui_conf_file.get_option_value(ui_conf_file.section_ui_to_background, ui_conf_file.ui_option_system_type)
        if system_type == "Android":
            self.log.write("\n %s" % shell.invoke("adb -s %s shell cat /proc/meminfo \"|grep MemFree\"" % self.device_name))
        else:
            self.log.write("\n %s" % shell.invoke("adb -s %s shell free -m" % self.device_name))


if __name__ == '__main__':
    mem_ = GetMemFree()
    mem_.get_mem_free_info()
