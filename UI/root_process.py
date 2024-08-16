from config_path import UIConfigPath
from configfile import ConfigP
import process_shell
import os

root_path = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
ui_config_path = os.path.join(root_path, "UI", "ui_config.ini")
bg_config_path = os.path.join(root_path, "UI", "background_config.ini")

ui_conf_file = ConfigP(ui_config_path)
bg_conf_file = ConfigP(bg_config_path)

shell = process_shell.Shell()


class RootSteps:

    def root_device(self):
        cmds = ""
        cmds_str = ui_conf_file.get_option_value(ui_conf_file.section_ui_to_background, ui_conf_file.ui_option_root_steps)
        if "," in cmds_str:
            cmds = cmds_str.split(",")
        elif "，" in cmds_str:
            cmds = cmds_str.split("，")

        # for cmd in cmds:
        #     shell.invoke(cmd)
        #     if cmd == "reboot":
        #         # if self.device_name + "device" in devices.replace('\r', '').replace('\t', '').replace(' ', ''):
        #         devices_lists = shell.invoke("adb devices").replace('\r', '').replace('\t', '').replace(' ', '')
        #         device_online = bg_conf_file.get_option_value(bg_conf_file.section_background_to_ui, bg_conf_file.bg_option_devices_name) + "device"
        #         if device_online in device_online:

    def devices_online(self):
        pass
