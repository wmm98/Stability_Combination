from configfile import ConfigP
import os
import process_shell
import time

time.sleep(1)
root_path = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
bg_config_ui_path = os.path.join(root_path, "UI", "background_config.ini")
bg_conf_file = ConfigP(bg_config_ui_path)

ui_config_ui_path = os.path.join(root_path, "UI", "ui_config.ini")
ui_conf_file = ConfigP(ui_config_ui_path)
shell = process_shell.Shell()

logo_base_path = os.path.join(root_path, "Photo", "BootLogo")
logo_expect_path = os.path.join(logo_base_path, "Expect")
logo_test_path = os.path.join(logo_base_path, "Test")
logo_error_path = os.path.join(logo_base_path, "Error")
logo_expect_screen0_path = os.path.join(logo_expect_path, "screen0", "expect.png")
logo_expect_screen1_path = os.path.join(logo_expect_path, "screen1", "expect.png")
logo_test_screen0_path = os.path.join(logo_expect_path, "screen0", "test.png")
logo_test_screen1_path = os.path.join(logo_expect_path, "screen1", "test.png")


class BootLogo:
    def __init__(self):
        self.device_name = ui_conf_file.get_option_value(ui_conf_file.section_ui_boot_check,
                                                         ui_conf_file.ui_option_device_name)

    def save_img(self):
        is_double = int(ui_conf_file.get_option_value(ui_conf_file.section_ui_boot_check,
                                                      ui_conf_file.option_logo_double_screen))

        if not self.is_screen_on():
            self.press_power_button()
        time.sleep(1)
        self.unlock()
        self.back_home()
        time.sleep(1)
        self.screen_shot(logo_expect_screen0_path)
        if int(is_double):
            self.screen_shot(logo_expect_screen1_path, display_id=1)

    def is_screen_on(self):
        res = shell.invoke("adb -s %s shell \"dumpsys window | grep mAwake\"" % self.device_name)
        if "mAwake=true" in res:
            return True
        else:
            return False

    def back_home(self):
        shell.invoke("adb -s %s shell input keyevent KEYCODE_BACK" % self.device_name)

    def unlock(self):
        shell.invoke("adb -s %s shell input swipe 300 500 300 0" % self.device_name)

    def screen_shot(self, des_path, display_id=0):
        if display_id == 0:
            cmd = "adb -s %s exec-out screencap -p > %s" % (self.device_name, des_path)
        else:
            cmd = "adb -s %s exec-out screencap -d %d -p > %s" % (self.device_name, 1, des_path)
        shell.invoke(cmd)

    def press_power_button(self):
        shell.invoke("adb -s %s shell input keyevent KEYCODE_POWER" % self.device_name)


if __name__ == '__main__':
    photo = BootLogo()
    photo.save_img()
