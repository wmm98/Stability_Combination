import allure
import os
import time
import pytest
import configparser
from Common.log import MyLog
from Main.device import Device
from Common.config import Config

log = MyLog()


class TestStabilityCombination:

    def setup_class(self):
        self.bg_conf_file = configparser.ConfigParser()
        self.bg_conf_file.read(Config.bg_config_ini_path)
        self.ui_conf_file = configparser.ConfigParser()
        self.ui_conf_file.read(Config.ui_config_ini_path)
        self.device_name = self.ui_conf_file.get(Config.section_ui_to_background,
                                                 Config.ui_option_device_name)
        self.device = Device(self.device_name)

    def teardown_class(self):
        log.info("压测运行完毕")
        time.sleep(3)

    @allure.feature("DDR-Integration-testing")
    @allure.title("DDR-EMMC压力测试")
    def test_stability_combination_all(self):
        log.info("********测试开始*********")
        # try:
        # 1.推送memtester的相关
        # root设备
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_is_memtester) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_memtester_path, "memtester"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/memtester")
        # 2.推送stressapptest
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_is_stress_app_test) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_path, "stressapptest"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/stressapptest")
            time.sleep(2)
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_path, "libstlport.so"),
                                      "/system/lib/libstlport.so")
            self.device.send_adb_shell_command("chmod 644 /system/lib/libstlport.so")
        # 2.推送stressapptest-cut
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_is_stress_app_switch) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_switch_path, "stressapptest"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/stressapptest")
            time.sleep(2)
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_switch_path, "libstlport.so"),
                                      "/system/lib/")
            self.device.send_adb_shell_command("chmod 644 /system/lib/libstlport.so")
        # 推送shell脚本
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_system_type) == "Android":
            self.device.adb_push_file(os.path.join(Config.pretesting_path, "test_demo_Android.sh"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/test_demo_Android.sh")
            self.device.adb_push_file(Config.ui_config_ini_path, "/data")
            self.device.send_adb_shell_command("/data/test_demo_Android.sh")
        else:
            self.device.adb_push_file(os.path.join(Config.pretesting_path, "test_demo_Linux.sh"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/test_demo_Linux.sh")
            self.device.adb_push_file(Config.ui_config_ini_path, "/data")
            self.device.send_adb_shell_command("./data/test_demo_Linux.sh")
        time.sleep(10)
        if "debug.txt" in self.device.send_adb_shell_command("ls /data/stress_test_log"):
            log.info("可脱机测试")
        else:
            log.info(".sh脚本没跑起来，请检查！！！")
        # except Exception as e:
        #     print(e)
        log.info("测试结束")
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
