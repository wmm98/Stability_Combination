import allure
import pytest
import configparser
from Common.log import MyLog

log = MyLog()


class TestStabilityCombination:

    def setup_class(self):
        pass

    def teardown_class(self):
        log.info("压测运行完毕")

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