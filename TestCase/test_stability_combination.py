import allure
import pytest
import configparser
from Stability.Common.log import MyLog

log = MyLog()


class TestStabilityCombination:

    def setup_class(self):
        pass

    def teardown_class(self):
        log.info("压测运行完毕")

    @allure.feature("stability_case0")
    @allure.title("")
    # @pytest.mark.flaky(reruns=1, reruns_delay=3)
    def test_stability_combination_01(self):
        log.info("********测试开始*********")

        log.info("********测试结束*********")