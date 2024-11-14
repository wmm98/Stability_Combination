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

# ¿¨logoÑ¹²â
logo_base_path = os.path.join(root_path, "BootLogo")
logo_expect_path = os.path.join(logo_base_path, "Expect")
logo_test_path = os.path.join(logo_base_path, "Test")
logo_error_path = os.path.join(logo_base_path, "Error")
logo_expect_screen0_path = os.path.join(logo_expect_path, "screen0", "expect.png")
logo_expect_screen1_path = os.path.join(logo_expect_path, "screen1", "expect.png")
logo_test_screen0_path = os.path.join(logo_expect_path, "screen0", "test.png")
logo_test_screen1_path = os.path.join(logo_expect_path, "screen1", "test.png")


class BootLogo:
    def __init__(self):
        self.camera_package_name = ""
        self.device_name = ui_conf_file.get_option_value(ui_conf_file.section_ui_camera_check,
                                                         ui_conf_file.ui_option_device_name)

    def save_img(self):
        is_double = ui_conf_file.get_option_value(ui_conf_file.section_ui_camera_check,
                                                  ui_conf_file.option_front_and_rear)

        if int(is_double):
            self.screen_shot(camera_sta_exp_rear_preview_path)

    def screen_shot(self, des_path, display_id=0):
        shell.invoke("adb -s %s exec-out screencap -d %d -p > %s" % (self.device_name, display_id, des_path))


if __name__ == '__main__':
    photo = BootLogo()
    photo.save_img()