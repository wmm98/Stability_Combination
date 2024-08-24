import allure
import os
import time
import pytest
import configparser
from Common.log import MyLog
from Main.device import Device
from UI import configfile
from Common.config import Config

log = MyLog()


class TestStabilityCombination:

    def setup_class(self):
        self.bg_conf_file = configfile.ConfigP(Config.bg_config_ini_path)
        self.ui_conf_file = configfile.ConfigP(Config.ui_config_ini_path)
        self.device_name = self.bg_conf_file.get_option_value(self.bg_conf_file.section_background_to_ui,
                                                                self.bg_conf_file.bg_option_devices_name)
        self.device = Device(self.device_name)

    def teardown_class(self):
        log.info("压测运行完毕")

    @allure.feature("DDR-Integration-testing")
    @allure.title("DDR-memtester压力测试")
    def test_stability_combination(self):
        log.info("********测试开始*********")
        # root_steps = self.ui_conf_file.get_option_value(self.ui_conf_file.section_ui_to_background, self.ui_conf_file.ui_option_root_steps)
        # 1.推送memtester的相关
        # root设备
        if self.ui_conf_file.get_option_value(self.ui_conf_file.section_ui_to_background,
                                              self.ui_conf_file.ui_option_is_memtester) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_memtester_path, "memtester"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/memtester")

        # 2.推送stressapptest
        if self.ui_conf_file.get_option_value(self.ui_conf_file.section_ui_to_background,
                                              self.ui_conf_file.ui_option_is_stress_app_test) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_path, "stressapptest"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/stressapptest")
            time.sleep(2)
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_path, "libstlport.so"), "/system/lib/libstlport.so")
            self.device.send_adb_shell_command("chmod 644 /system/lib/libstlport.so")

        # 2.推送stressapptest-cut
        if self.ui_conf_file.get_option_value(self.ui_conf_file.section_ui_to_background,
                                              self.ui_conf_file.ui_option_is_stress_app_switch) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_switch_path, "stressapptest"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/stressapptest")
            time.sleep(2)
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_switch_path, "libstlport.so"),
                                      "/system/lib/libstlport.so")
            self.device.send_adb_shell_command("chmod 644 /system/lib/libstlport.so")

        # 推送shell脚本
        self.device.adb_push_file(os.path.join(Config.pretesting_path, "test_demo.sh"), "/data")
        self.device.send_adb_shell_command("./data/test_demo.sh")
        log.info("********测试结束*********")

    @allure.feature("DDR-memtester")
    @allure.title("DDR-memtester压力测试")
    def test_stability_combination_01(self):
        log.info("********测试开始*********")

        log.info("********测试结束*********")

    @allure.feature("DDR-stressapptest")
    @allure.title("DDR-stressapptest")
    def test_stability_combination_02(self):
        log.info("********测试开始*********")

        log.info("********测试结束*********")

    @allure.feature("DDR-stressapptest-switch")
    @allure.title("DDR-stressapptest-高低内存切换测试")
    def test_stability_combination_03(self):
        log.info("********测试开始*********")

        log.info("********测试结束*********")
