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

# exp camera relate path
camera_stability_path = os.path.join(root_path, "Photo", "CameraStability")
camera_sta_exp_path = os.path.join(camera_stability_path, "Expect")
camera_sta_test_path = os.path.join(camera_stability_path, "Test")
# exp camera front and rear path
camera_sta_exp_front_path = os.path.join(camera_sta_exp_path, "Front")
camera_sta_exp_rear_path = os.path.join(camera_sta_exp_path, "Rear")
camera_sta_exp_front_photograph_path = os.path.join(camera_sta_exp_front_path, "Photograph", "exp_front_photograph.jpg")
camera_sta_exp_front_preview_path = os.path.join(camera_sta_exp_front_path, "PreView", "exp_front_preview.png")
camera_sta_exp_rear_photograph_path = os.path.join(camera_sta_exp_rear_path, "Photograph", "exp_rear_photograph.jpg")
camera_sta_exp_rear_preview_path = os.path.join(camera_sta_exp_rear_path, "PreView", "exp_rear_preview.png")
# test camera front and rear
# camera_sta_test_front_path = os.path.join(camera_sta_test_path, "Front")
# camera_sta_test_rear_path = os.path.join(camera_sta_test_path, "Rear")
# camera_sta_test_front_photograph_path = os.path.join(camera_sta_test_front_path, "Photograph", "test_front_photograph.jpg")
# camera_sta_test_front_preview_path = os.path.join(camera_sta_test_front_path, "PreView", "test_front_preview.png")
# camera_sta_test_rear_photograph_path = os.path.join(camera_sta_test_rear_path, "Photograph", "test_rear_photograph.jpg")
# camera_sta_test_rear_preview_path = os.path.join(camera_sta_test_rear_path, "PreView", "test_rear_preview.png")


class Photograph:
    def __init__(self):
        self.device_name = ui_conf_file.get_option_value(ui_conf_file.section_ui_camera_check, ui_conf_file.ui_option_device_name)

    def save_img(self):
        is_double = ui_conf_file.get_option_value(ui_conf_file.section_ui_camera_check, ui_conf_file.option_front_and_rear)
        if int(is_double):

            # clear img in device
            self.remove_img()
            time.sleep(1)
            if len(self.get_latest_img()) != 0:
                self.remove_img()

            # front and rear camera
            # 1 open camera
            self.open_camera()
            if len(self.get_latest_img()) == 0:
                self.open_camera()
            # 2 adjust current is rea camera or not
            if not self.is_first_camera():
                self.click_switch_btn()
            time.sleep(1)
            if not self.is_first_camera():
                self.click_switch_btn()
            # save rear camera preview and photograph
            # screenshot preview
            self.screen_shot(camera_sta_exp_rear_preview_path)
            time.sleep(1)
            if not os.path.exists(camera_sta_exp_rear_preview_path):
                self.screen_shot(camera_sta_exp_rear_preview_path)
            # clear img
            self.remove_img()
            time.sleep(1)
            if len(self.get_latest_img()) != 0:
                self.remove_img()
            # take photo
            self.take_photo()
            time.sleep(1)
            if len(self.get_latest_img()) == 0:
                self.take_photo()
            self.pull_img(camera_sta_exp_rear_photograph_path)
            time.sleep(1)
            if not os.path.exists(camera_sta_exp_rear_photograph_path):
                self.pull_img(camera_sta_exp_rear_photograph_path)

            # clear img
            self.remove_img()
            time.sleep(1)
            if len(self.get_latest_img()) != 0:
                self.remove_img()

            # switch front camera
            self.click_switch_btn()
            time.sleep(1)
            if not self.is_second_camera():
                self.click_switch_btn()

            # wait 2 sec
            time.sleep(2)
            # screenshot preview
            self.screen_shot(camera_sta_exp_front_preview_path)
            time.sleep(1)
            if not os.path.exists(camera_sta_exp_front_preview_path):
                self.screen_shot(camera_sta_exp_front_preview_path)
            # clear img
            self.remove_img()
            time.sleep(1)
            if len(self.get_latest_img()) != 0:
                self.remove_img()
            # take photo
            self.take_photo()
            time.sleep(1)
            if len(self.get_latest_img()) == 0:
                self.take_photo()
            self.pull_img(camera_sta_exp_front_photograph_path)
            time.sleep(1)
            if not os.path.exists(camera_sta_exp_rear_photograph_path):
                self.pull_img(camera_sta_exp_front_photograph_path)

    def open_camera(self):
        shell.invoke("adb -s %s shell \"am start -a android.media.action.STILL_IMAGE_CAMERA\"" % self.device_name)

    def take_photo(self):
        shell.invoke("adb -s %s shell \"input keyevent 27\"" % self.device_name)

    def screen_shot(self, des_path):
        shell.invoke("adb -s %s exec-out screencap -p > %s" % (self.device_name, des_path))

    def remove_img(self):
        shell.invoke("adb -s %s shell \"rm * /sdcard/DCIM/Camera/\"" % self.device_name)

    def click_switch_btn(self):
        x = ui_conf_file.get_option_value(ui_conf_file.section_ui_camera_check, ui_conf_file.option_switch_x_value)
        y = ui_conf_file.get_option_value(ui_conf_file.section_ui_camera_check, ui_conf_file.option_switch_y_value)
        shell.invoke("adb -s %s shell \"input tab %s %s\"" % (self.device_name, x, y))

    def is_first_camera(self):
        if self.get_camera_id() == 1:
            return True
        else:
            return False

    def is_second_camera(self):
        if self.get_camera_id() == 2:
            return True
        else:
            return False

    def get_camera_id(self):
        camera_info = shell.invoke("adb -s %s shell \"dumpsys media.camera |grep Camera ID\"")
        clear_info = camera_info.replace('\r', '').replace('\t', '').replace(' ', '').replace('\n', '')
        if "CameraId:0".upper() in clear_info.upper():
            return 1
        elif "CameraId:1".upper() in clear_info.upper() or "CameraId:2".upper() in clear_info.upper():
            return 2
        else:
            # no open camera
            return 3

    def get_latest_img(self):
        cmd = "adb -s %s shell \"ls /sdcard/DCIM/Camera\""
        img_info = shell.invoke(cmd)
        if len(img_info) == 0:
            return ""
        else:
            return img_info.strip()

    def pull_img(self, des_path):
        shell.invoke("adb -s %s pull /sdcard/DCIM/Camera/%s %s" % (self.device_name, self.get_latest_img(), des_path))


if __name__ == '__main__':
    photo = Photograph()
    photo.save_img()