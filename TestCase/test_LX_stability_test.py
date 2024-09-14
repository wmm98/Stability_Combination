import pytest
import time
import configparser
from Common.log import MyLog
from Common.config import Config
import allure

log = MyLog()


class TestStabilityCombination:

    def setup_class(self):
        self.bg_conf_file = configparser.ConfigParser()
        self.bg_conf_file.read(Config.bg_config_ini_path)
        self.ui_conf_file = configparser.ConfigParser()
        self.ui_conf_file.read(Config.ui_config_ini_path)
        self.device_name = self.ui_conf_file.get(Config.section_ui_to_background,
                                                 Config.ui_option_device_name)

    def teardown_class(self):
        log.info("压测运行完毕")
        time.sleep(3)

    @allure.feature("开关机检查基本功能")
    @allure.title("开关机检查基本功能")
    def test_lx_stability_test(self):
        log.info("****************立项测试-开关机检查基本功能用例开始******************")
        log.info("****************立项测试-开关机检查基本功能用例结束******************")