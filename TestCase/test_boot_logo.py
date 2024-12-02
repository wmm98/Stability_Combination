import allure
import os
import time
import pytest
from Common.log import MyLog
from Main.device import Device
from Main.public import publicInterface
from Common import image_analysis, camera_operate, m_serial, adb_timer
from Common.device_check import DeviceCheck
import configparser
from Common.config import Config

conf = Config()
log = MyLog()
analysis = image_analysis.Analysis()
cnns = image_analysis.CNNsAnalysis()
camera = camera_operate.Camera()
t_ser = m_serial.SerialD()
public_interface = publicInterface()

bg_conf_file = configparser.ConfigParser()
public_interface.read_ini_file(bg_conf_file, Config.bg_config_ini_path)
ui_conf_file = configparser.ConfigParser()
public_interface.read_ini_file(ui_conf_file, Config.ui_config_ini_path)


# 检查adb在线
def check_adb_online_with_thread(device, timeout=90):
    adb_checker = adb_timer.ADBChecker(device, timeout)
    if ui_conf_file.get(Config.section_ui_logo, Config.option_logo_is_is_usb) == "1":
        log.info("选了USB")
        adb_checker.usb = True
        adb_checker.usb_relay = int(ui_conf_file.get(Config.section_ui_logo, Config.option_usb_config).split("_")[1])

    adb_checker.start_check()
    # Wait until timeout or ADB is found
    start_time = time.time()
    while time.time() - start_time < timeout:
        if adb_checker.result:
            adb_checker.timeout_handler()
            return True
        time.sleep(1)
    return False


# 检查adb在线
def check_boot_complete_with_thread(device, timeout=120):
    adb_checker = adb_timer.ADBChecker(device, timeout)
    adb_checker.start_check(boot=True)

    # Wait until timeout or ADB is found
    start_time = time.time()
    while time.time() - start_time < timeout:
        if adb_checker.result:
            adb_checker.timeout_handler()
            return True
        time.sleep(1)
    return False


class TestBootLogo:

    def setup_class(self):
        self.bg_conf_file = bg_conf_file
        self.ui_conf_file = ui_conf_file
        self.device_name = self.ui_conf_file.get(Config.section_ui_to_background,
                                                 Config.ui_option_device_name)
        self.device = Device(self.device_name)

    def teardown_class(self):
        log.info("压测运行完毕")
        time.sleep(3)

    @allure.feature("boot_logo")
    @allure.title("开关机卡logo测试")
    def test_boot_logo(self):
        log.info("开关机卡logo测试开始")
        device_check = DeviceCheck(self.ui_conf_file.get(Config.section_ui_logo, Config.ui_option_device_name))

        # 确认二部机器adb btn 开
        device_check.adb_btn_open()
        # 先对设备的时间进行修改，使用网络时间，方便看log
        # ?
        flag = 0
        t_ser.loginSer(self.ui_conf_file.get(Config.section_ui_logo, Config.option_logo_COM))
        while flag < int(self.ui_conf_file.get(Config.section_ui_logo, Config.ui_option_logo_test_times)):
            flag += 1
            # 上下电启动
            log.info("关机")

            if self.ui_conf_file.get(Config.section_ui_logo, Config.ui_option_logo_cases) == "1":
                num = int(
                    self.ui_conf_file.get(Config.section_ui_logo,
                                          Config.option_logo_adapter_power_config).split(
                        "_")[1])
                t_ser.open_relay(num)
                log.info("适配器开路")
                time.sleep(1)
                if device_check.device_is_online():
                    raise Exception("设备关机失败，请接线是否正确！！！")
                t_ser.close_relay(num)
                log.info("适配器通路")
            elif self.ui_conf_file.get(Config.section_ui_logo, Config.ui_option_logo_cases) == "2":
                # 关机
                device_check.device_shutdown()
                time.sleep(10)
                device_check.restart_adb()
                if device_check.device_is_online():
                    raise Exception("指令设备关机失败，请检查！！！")
                log.info("指令关机")
                # 开机
                num = int(
                    self.ui_conf_file.get(Config.section_ui_logo, Config.option_power_button_config).split(
                        "_")[1])
                t_ser.open_relay(num)
                log.info("按下电源按键")
                time.sleep(int(self.ui_conf_file.get(Config.section_ui_logo, Config.option_logo_boot_time)))
                t_ser.close_relay(num)
                log.info("松开电源按键")
            # 适配器异常下电
            elif self.ui_conf_file.get(Config.section_ui_logo, Config.ui_option_logo_cases) == "3":
                num_adapter_power = int(
                    self.ui_conf_file.get(Config.section_ui_logo,
                                          Config.option_logo_adapter_power_config).split(
                        "_")[1])
                num_power_button = int(
                    self.ui_conf_file[Config.section_ui_logo][Config.option_power_button_config].split("_")[
                        1])
                # 断开适配器/电池
                t_ser.open_relay(num_adapter_power)
                log.info("电池/适配器开路")
                time.sleep(1)
                if device_check.device_is_online():
                    raise Exception("设备关机失败，请检查接线是否正确！！！")
                # 闭合适配器 / 电池
                t_ser.close_relay(num_adapter_power)
                log.info("电池/适配器通路")
                # 按下电源按键开机
                time.sleep(1)
                t_ser.open_relay(num_power_button)
                log.info("按下电源健")
                time.sleep(int(self.ui_conf_file.get(Config.section_ui_logo, Config.option_logo_boot_time)))
                t_ser.close_relay(num_power_button)
                log.info("松开电源按键")

            log.info("正在开机，请等待...")
            if check_adb_online_with_thread(
                    self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name)):
                if check_boot_complete_with_thread(
                        self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name),
                        timeout=120):
                    log.info("设备完全启动")
                else:
                    log.info("设备无法完全启动, 请检查!!!")
                    if self.ui_conf_file[Config.section_ui_logo][Config.option_only_boot_config] == "1":
                        log.error("当前认为复现了卡logo情景，请检查！！！")
                        time.sleep(3)
                        break
            else:
                log.error("没检测到设备在线!!!")
                if self.ui_conf_file[Config.section_ui_logo][Config.option_only_boot_config] == "1":
                    log.error("当前认为复现了卡logo情景，请检查！！！")
                    time.sleep(3)
                    break
            if self.ui_conf_file[Config.section_ui_logo][Config.option_only_boot_config] == "0":
                # 拍照
                time.sleep(30)
                if not self.device.is_screen_on():
                    self.device.press_power_button()
                time.sleep(1)
                if not self.device.is_screen_on():
                    self.device.press_power_button()
                time.sleep(1)
                self.device.unlock()
                time.sleep(1)
                self.device.back_home()
                time.sleep(1)

                # 单双屏情况
                if self.ui_conf_file[Config.section_ui_logo][Config.option_logo_double_screen] == "1":
                    self.device.screen_shot(Config.logo_test_screen1_path, display_id=1)
                    log.info("副屏幕截桌面图完成")
                    # 抠图
                    score2 = cnns.generateScore(Config.logo_expect_screen1_path, Config.logo_test_screen1_path)
                    log.info("当前相似度分数为：%s" % str(score2))
                    if score2 < 0.9:
                        log.error("当前认为复现了卡logo情景，请检查！！！")
                        if device_check.device_is_online():
                            log.info("设备在线")
                            device_check.logcat(int(
                                self.ui_conf_file.get(Config.section_ui_logo,
                                                      Config.option_logcat_duration)) * 60)
                            log.info("成功捕捉了%s 分钟 adb log" % self.ui_conf_file.get(Config.section_ui_logo,
                                                                                  Config.option_logcat_duration))
                            log.info("任务结束")
                        else:
                            log.info("设备不在线")
                            log.info("任务结束")
                        time.sleep(3)
                        break

                # 截图主屏
                # print("截图照片：%s" % Config.logo_test_screen0_path)
                self.device.screen_shot(Config.logo_test_screen0_path)
                log.info("主屏桌面截图完成")

                score = cnns.generateScore(Config.logo_expect_screen0_path, Config.logo_test_screen0_path)
                log.info("当前相似度分数为：%s" % str(score))
                if score < 0.9:
                    log.error("当前认为复现了卡logo情景，请检查！！！")
                    if device_check.device_is_online():
                        log.info("设备在线")
                        device_check.logcat(
                            int(self.ui_conf_file.get(Config.section_ui_logo,
                                                      Config.option_logcat_duration)) * 60)
                        log.info("成功捕捉了%s 分钟 adb log" % self.ui_conf_file.get(Config.section_ui_logo,
                                                                              Config.option_logcat_duration))
                        log.info("任务结束")
                    else:
                        log.info("设备不在线")
                        log.info("任务结束")
                    time.sleep(3)
                    break
                log.info("*******************压测完成%d次********************" % flag)
        t_ser.logoutSer()
        log.info("停止压测.")
