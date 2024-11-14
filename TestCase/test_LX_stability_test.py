import allure
import os
import time
import pytest
from Common.log import MyLog
from Main.device import Device
from Common import image_analysis, camera_operate, keying, m_serial, adb_timer
from Common.device_check import DeviceCheck
import configparser
from Common.config import Config
from Main.public import publicInterface
import shutil

conf = Config()
log = MyLog()
public_interface = publicInterface()
analysis = image_analysis.Analysis()
cnns = image_analysis.CNNsAnalysis()
camera = camera_operate.Camera()
key_ing = keying.KeyPhoto()
t_ser = m_serial.SerialD()
bg_conf_file = configparser.ConfigParser()
public_interface.read_ini_file(bg_conf_file, Config.bg_config_ini_path)
# bg_conf_file.read(Config.bg_config_ini_path, encoding="gbk")
ui_conf_file = configparser.ConfigParser()
# ui_conf_file.read(Config.ui_config_ini_path, encoding="gbk")
public_interface.read_ini_file(ui_conf_file, Config.ui_config_ini_path)


# 检查adb在线
def check_adb_online_with_thread(device, timeout=90):
    adb_checker = adb_timer.ADBChecker(device, timeout)
    if ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_is_is_usb) == "1":
        log.info("选了USB")
        adb_checker.usb = True
        adb_checker.usb_relay = int(
            ui_conf_file.get(Config.section_ui_boot_check, Config.option_usb_config).split("_")[1])

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


class TestLXStability:

    def setup_class(self):
        self.bg_conf_file = bg_conf_file
        self.ui_conf_file = ui_conf_file
        self.device_name = self.ui_conf_file.get(Config.section_ui_to_background,
                                                 Config.ui_option_device_name)
        self.device = Device(self.device_name)

    def teardown_class(self):
        log.info("压测运行完毕")
        time.sleep(3)

    @allure.feature("boot_check_stability")
    @allure.title("开关机检查基本功能")
    def test_lx_boot_check_stability_test(self):
        log.info("****立项测试-开关机检查基本功能用例开始******")
        # 获取测试点的配置信息
        test_times = self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_test_times)
        is_wifi = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_wifi_test)
        is_eth = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_eth_test)
        is_mobile = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_mobile_test)
        is_bt = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_bt_test)
        is_nfc = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_nfc_test)
        # usb后续完善
        is_usb = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_usb_test)

        # 测试前先检查所有的按钮开关
        if int(is_bt):
            log.info("****检查蓝牙当前状态")
            if not self.device.bt_is_enable():
                self.device.enable_bt_btn()
                time.sleep(3)
            if not self.device.bt_is_enable():
                self.device.enable_bt_btn()
                time.sleep(3)
            if not self.device.bt_is_enable():
                log.error("无法开启蓝牙，请检查！！！")
                time.sleep(3)
                raise Exception
            log.info("蓝牙上电成功")

        if int(is_nfc):
            log.info("****检查nfc当前状态")
            if not self.device.nfc_is_enable():
                self.device.enable_nfc_btn()
                time.sleep(3)
            if not self.device.nfc_is_enable():
                self.device.enable_nfc_btn()
                time.sleep(3)
            if not self.device.nfc_is_enable():
                log.error("无法开启NFC，请检查！！！")
                time.sleep(3)
                raise Exception
            log.info("NFC上电成功")

        if int(is_eth):
            log.info("****检查以太网当前状态")
            if not self.device.eth0_is_enable():
                if int(is_wifi):
                    self.device.disable_wifi_btn()
                    log.info("给wifi下电")
                    time.sleep(2)
                if int(is_mobile):
                    self.device.disable_mobile_btn()
                    log.info("给移动数据下电")
                    time.sleep(2)
                self.device.enable_eth0_btn()
                time.sleep(3)
                log.info("以太网上电")

            if not self.device.ping_network(5, 60):
                log.error("无法上网，请检查以太网！！！")
                time.sleep(3)
                raise Exception
            log.info("以太网可成功上网")
            if int(is_wifi):
                self.device.enable_wifi_btn()
                log.info("wifi上电")
            if int(is_mobile):
                self.device.enable_mobile_btn()
                log.info("移动数据上电")

        if int(is_wifi):
            log.info("****检查wifi当前状态")
            if not self.device.wifi_is_enable():
                if int(is_eth):
                    self.device.disable_eth0_btn()
                    log.info("以太网下电")
                    time.sleep(2)
                if int(is_mobile):
                    self.device.disable_mobile_btn()
                    log.info("移动数据流量下电")
                    time.sleep(2)
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                log.info("wifi上电成功")

            if not self.device.ping_network(5, 60):
                log.error("无法上网，请连接wifi！！！")
                time.sleep(3)
                raise Exception
            log.info("wifi可正常上网")
            if int(is_eth):
                self.device.enable_eth0_btn()
                log.info("以太网上电")
            if int(is_mobile):
                self.device.enable_mobile_btn()
                log.info("移动数据流量上电")

        if int(is_mobile):
            log.info("****检查移动数据流量当前状态")
            if int(is_wifi):
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi无法下电！！！")
                    time.sleep(1)
                    raise Exception
                log.info("wifi下电")

            if int(is_eth):
                self.device.disable_mobile_btn()
                log.info("以太网下电")
                time.sleep(3)
            self.device.enable_mobile_btn()
            time.sleep(3)
            if not self.device.mobile_is_enable():
                self.device.enable_mobile_btn()
                time.sleep(3)
            log.info("移动流量数据上电")

            if not self.device.ping_network(5, 60):
                log.error("无法上网，请插上4G卡！！！")
                time.sleep(3)
                raise
            log.info("移动流量数据可上网")
            if int(is_wifi):
                self.device.enable_wifi_btn()
                log.info("wifi上电")
            if int(is_mobile):
                self.device.enable_eth0_btn()
                log.info("移动流量数据上电")

            log.info("移动流量数据上电成功")

        # U盘， 后续开发适配, sdcard数据检查后续开发

        # 1、关机开机检测卡logo，是否进入recovery模式等部分处理
        device_check = DeviceCheck(
            self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name))
        # 确认二部机器adb btn 开
        device_check.adb_btn_open()
        # 先对设备的时间进行修改，使用网络时间，方便看log
        # ?
        # 图片处理相关
        origin_logo_logo_img = os.path.join(conf.logo_logo_path, "Logo.png")
        origin_logo_key_img = os.path.join(conf.logo_key_path, "Key.png")
        # 需要在前端先删除存留的失败照片,调试的时候先在这里删除
        failed_img_path = os.path.join(conf.camera_key_img_path, "Failed.png")
        if os.path.exists(failed_img_path):
            os.remove(failed_img_path)

            # 用例说明
            """
            1 适配器开关机（适配器闭合开路开关机）
            2 适配器/电池+电源按键--正常关机（指令关机）
            3 适配器/电池+电源按键--异常关机（适配器开路关机）
            """

        flag = 0
        while flag < int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_test_times)):
            flag += 1
            # 上下电启动
            # try:
            t_ser.loginSer(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_COM))
            # except Exception as e:
            #     log.error("串口已经被占用， 请检查！！！")
            #     log.error(str(e))
            #     break
            log.info("关机")

            if self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "1":
                num = int(
                    self.ui_conf_file.get(Config.section_ui_boot_check,
                                          Config.option_logo_adapter_power_config).split(
                        "_")[1])
                t_ser.open_relay(num)
                log.info("适配器开路")
                time.sleep(1)
                if device_check.device_is_online():
                    raise Exception("设备关机失败，请接线是否正确！！！")
                t_ser.close_relay(num)
                log.info("适配器通路")
            elif self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "2":
                # 关机
                device_check.device_shutdown()
                time.sleep(10)
                device_check.restart_adb()
                if device_check.device_is_online():
                    raise Exception("指令设备关机失败，请检查！！！")
                log.info("指令关机")
                # 开机
                num = int(
                    self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_power_button_config).split(
                        "_")[1])
                t_ser.open_relay(num)
                log.info("按下电源按键")
                time.sleep(int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_boot_time)))
                t_ser.close_relay(num)
                log.info("松开电源按键")
            # 适配器异常下电
            elif self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "3":
                num_adapter_power = int(
                    self.ui_conf_file.get(Config.section_ui_boot_check,
                                          Config.option_logo_adapter_power_config).split(
                        "_")[1])
                num_power_button = int(
                    self.ui_conf_file[Config.section_ui_boot_check][Config.option_power_button_config].split("_")[
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
                time.sleep(int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_boot_time)))
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
                    if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "1":
                        log.error("当前认为复现了卡logo情景，请检查！！！")
                        time.sleep(3)
                        break
            else:
                log.error("没检测到设备在线!!!")
                if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "1":
                    log.error("当前认为复现了卡logo情景，请检查！！！")
                    time.sleep(3)
                    break
            if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "0":
                # 拍照
                time.sleep(60)
                # time.sleep(interval[flag])
                origin_camera_path = os.path.join(conf.camera_origin_img_path, "Expect.png")
                # 双屏情况
                origin_camera2_path = os.path.join(conf.camera_origin_img_path, "Origin2.png")
                if os.path.exists(origin_camera_path):
                    os.remove(origin_camera_path)
                if os.path.exists(origin_camera2_path):
                    os.remove(origin_camera2_path)

                # 单双屏情况
                if self.ui_conf_file[Config.section_ui_boot_check][Config.option_logo_double_screen] == "1":
                    camera.take_photo(origin_camera_path, camera_id=1)
                    log.info("镜头2拍照完成")
                    # 抠图
                    log.info("抠图中， 请等待")
                    camera2_key_img_path = os.path.join(conf.camera_key_img_path, "Key2.png")
                    if os.path.exists(camera2_key_img_path):
                        os.remove(camera2_key_img_path)
                    key_ing.save_key_photo(origin_camera_path, camera2_key_img_path)
                    log.info("抠图完成")

                    score2 = cnns.generateScore(origin_logo_key_img, camera2_key_img_path)
                    log.info("当前相似度分数为：%s" % str(score2))
                    if score2 < 75:
                        log.error("当前认为复现了卡logo情景，请检查！！！")
                        if device_check.device_is_online():
                            log.info("设备在线")
                            device_check.logcat(int(
                                self.ui_conf_file.get(Config.section_ui_boot_check,
                                                      Config.option_logcat_duration)) * 60)
                            log.info("成功捕捉了%s 分钟 adb log" % self.ui_conf_file.get(Config.section_ui_boot_check,
                                                                                  Config.option_logcat_duration))
                            log.info("任务结束")
                        else:
                            log.info("设备不在线")
                            log.info("任务结束")
                        time.sleep(3)
                        break

                camera.take_photo(origin_camera_path)
                log.info("镜头1拍照完成")
                # 抠图
                log.info("抠图中， 请等待")
                camera_key_img_path = os.path.join(conf.camera_key_img_path, "Key.png")
                if os.path.exists(camera_key_img_path):
                    os.remove(camera_key_img_path)
                key_ing.save_key_photo(origin_camera_path, camera_key_img_path)
                log.info("抠图完成")

                score = cnns.generateScore(origin_logo_key_img, camera_key_img_path)
                log.info("当前相似度分数为：%s" % str(score))
                if score < 70:
                    log.error("当前认为复现了卡logo情景，请检查！！！")
                    if device_check.device_is_online():
                        log.info("设备在线")
                        device_check.logcat(
                            int(self.ui_conf_file.get(Config.section_ui_boot_check,
                                                      Config.option_logcat_duration)) * 60)
                        log.info("成功捕捉了%s 分钟 adb log" % self.ui_conf_file.get(Config.section_ui_boot_check,
                                                                              Config.option_logcat_duration))
                        log.info("任务结束")
                    else:
                        log.info("设备不在线")
                        log.info("任务结束")
                    time.sleep(3)
                    break

            # 调试代码
            # 重启代替硬开、关机
            # self.device.reboot()
            # log.info("重启...")
            # if check_adb_online_with_thread(
            #         self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name)):
            #     if check_boot_complete_with_thread(
            #             self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name),
            #             timeout=120):
            #         log.info("设备完全启动")
            #         # 后续查看是否要等待时间
            #         time.sleep(5)
            #     else:
            #         log.info("设备无法完全启动, 请检查!!!")
            #         if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "1":
            #             log.error("当前认为复现了卡logo情景，请检查！！！")
            #             time.sleep(3)
            #             raise Exception

            # 2、检查wifi，蓝牙，usb,4G、以太网模块状态，关闭并且再次开启检查状态
            failed_flag = 0
            if int(is_bt):
                log.info("********检查蓝牙开关状态")
                if not self.device.bt_is_enable():
                    log.error("重启后蓝牙不是上电状态，请检查！！！")
                    failed_flag += 1
                log.info("启动后蓝牙当前为上电状态")
                # 对蓝牙进行关开操作
                log.info("给蓝牙下电")
                self.device.disable_bt_btn()
                time.sleep(3)
                if self.device.bt_is_enable():
                    self.device.disable_bt_btn()
                    time.sleep(3)
                if self.device.bt_is_enable():
                    log.error("蓝牙无法下电，请检查！！！")
                    failed_flag += 1
                log.info("蓝牙下电成功")
                log.info("给蓝牙上电")
                self.device.enable_bt_btn()
                time.sleep(3)
                if not self.device.bt_is_enable():
                    self.device.enable_bt_btn()
                    time.sleep(3)
                if not self.device.bt_is_enable():
                    log.error("蓝牙无法上电，请检查！！！")
                    failed_flag += 1
                log.info("蓝牙上电成功")

            if int(is_nfc):
                log.info("********检查NFC开关状态")
                if not self.device.nfc_is_enable():
                    log.error("启动后nfc不是上电状态，请检查！！！")
                    failed_flag += 1
                log.info("启动后nfc当前为上电状态")
                # 对蓝牙进行关开操作
                log.info("给nfc下电")
                self.device.disable_nfc_btn()
                time.sleep(3)
                if self.device.nfc_is_enable():
                    self.device.disable_nfc_btn()
                    time.sleep(3)
                if self.device.nfc_is_enable():
                    log.error("nfc无法下电，请检查！！！")
                    failed_flag += 1
                log.info("nfc下电成功")
                log.info("给nfc上电")
                self.device.enable_nfc_btn()
                time.sleep(3)
                if not self.device.nfc_is_enable():
                    self.device.enable_nfc_btn()
                    time.sleep(3)
                if not self.device.nfc_is_enable():
                    log.error("nfc无法上电，请检查！！！")
                    failed_flag += 1
                log.info("nfc上电成功")

            if failed_flag > 1:
                raise Exception

            # 检查网络
            if int(is_eth):
                log.info("********检查以太网状态")
                if not self.device.eth0_is_enable():
                    log.error("启动后的以太网不是上电状态， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("启动后以太网为上电状态")

            if int(is_wifi):
                log.info("********检查以wifi态")
                if not self.device.wifi_is_enable():
                    log.error("启动后的以wifi不是上电状态， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("启动后wifi为上电状态")

            if int(is_mobile):
                log.info("********检查以流量数据态")
                if not self.device.mobile_is_enable():
                    log.error("启动后的移动数据网络不是上电状态， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("启动后移动网络为上电状态")

            if int(is_eth) and int(is_wifi) and int(is_mobile):
                # 禁用wifi
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                log.info("wifi下电")
                # 禁用4G
                self.device.disable_mobile_btn()
                time.sleep(3)
                if self.device.mobile_is_enable():
                    self.device.disable_mobile_btn()
                    time.sleep(3)
                if self.device.mobile_is_enable():
                    log.error("移动数据模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据下电成功")
                if not self.device.ping_network(5, 35):
                    log.error("启动后以太网无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("启动后以太网可正常上网")

                # 禁用以太网
                self.device.disable_eth0_btn()
                time.sleep(3)
                if self.device.eth0_is_enable():
                    self.device.disable_eth0_btn()
                    time.sleep(3)
                if self.device.eth0_is_enable():
                    log.error("以太网模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网下电成功")
                # 上电
                self.device.enable_eth0_btn()
                time.sleep(3)
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                    time.sleep(3)
                if not self.device.eth0_is_enable():
                    log.error("以太网模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("以太网无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网可正常上网")

                # 以太网下电
                self.device.disable_eth0_btn()
                time.sleep(3)
                if self.device.eth0_is_enable():
                    self.device.disable_eth0_btn()
                    time.sleep(3)
                if self.device.eth0_is_enable():
                    log.error("以太网模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                # wifi上电
                # 上电
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                # wifi下电
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                # 移动数据上电
                # 上电
                self.device.enable_mobile_btn()
                time.sleep(3)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(3)
                if not self.device.mobile_is_enable():
                    log.error("移动数据模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("移动数据无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据可正常上网")

                # 以太网上电，wifi上电
                # wifi上电
                # 上电
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                # 以太网上电
                self.device.enable_eth0_btn()
                time.sleep(3)
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                    time.sleep(3)
                if not self.device.eth0_is_enable():
                    log.error("以太网模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("以太网无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网可正常上网")

            if not int(is_eth) and int(is_wifi) and int(is_mobile):
                # 禁用4G
                self.device.disable_mobile_btn()
                time.sleep(3)
                if self.device.mobile_is_enable():
                    self.device.disable_mobile_btn()
                    time.sleep(3)
                if self.device.mobile_is_enable():
                    log.error("移动数据模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据下电")

                if not self.device.ping_network(5, 60):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                # wifi下电
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                # 移动数据上电
                # 上电
                self.device.enable_mobile_btn()
                time.sleep(3)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(3)
                if not self.device.mobile_is_enable():
                    log.error("移动数据模块无法上电，请检查！！！")
                    raise Exception
                log.info("移动数据模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("移动数据无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception

                log.info("移动数据可正常上网")

                # 以太网上电，wifi上电
                # wifi上电
                # 上电
                log.info("移动数据下电")
                if self.device.mobile_is_enable():
                    self.device.disable_mobile_btn()
                    time.sleep(3)
                if self.device.mobile_is_enable():
                    log.error("移动数据模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                self.device.enable_mobile_btn()
                time.sleep(3)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(3)
                if not self.device.mobile_is_enable():
                    log.error("移动数据模块无法上电，请检查！！！")
                    raise Exception
                log.info("移动数据模块上电成功")

            t_ser.logoutSer()
            log.info("*******************压测完成%d次********************" % flag)
            time.sleep(3)

        log.info("****************立项测试-开关机检查基本功能用例结束******************")

    @allure.feature("front_rear_camera_stability")
    @allure.title("前后摄像头拍照问题对比")
    def test_lx_front_rear_camera_test(self):
        log.info("************前后摄像头拍照问题对比用例开始*******")

        def clear_directory(dir_path):
            file_names = os.listdir(dir_path)
            if len(file_names) != 0:
                # 遍历文件名列表并删除文件
                for file_name in file_names:
                    file_path = os.path.join(dir_path, file_name)  # 文件路径
                    os.remove(file_path)

        # 删除异常照片
        # 获取文件夹中的所有文件名
        default_photograph_file_names = conf.camera_sta_err_default_photograph_path
        default_preview_file_names = conf.camera_sta_err_default_preview_path
        front_photograph_file_names = conf.camera_sta_err_front_photograph_path
        front_preview_file_names = conf.camera_sta_err_front_preview_path
        rear_photograph_file_names = conf.camera_sta_err_rear_photograph_path
        rear_preview_file_names = conf.camera_sta_err_rear_preview_path

        clear_directory(default_preview_file_names)
        clear_directory(default_photograph_file_names)
        clear_directory(front_preview_file_names)
        clear_directory(front_photograph_file_names)
        clear_directory(rear_photograph_file_names)
        clear_directory(rear_preview_file_names)

        # 删除已存在的logcat文件
        if os.path.exists(Config.camera_sta_test_log_path):
            os.remove(Config.camera_sta_test_log_path)
        # 后台启动捕捉log
        log_path = os.path.join("/sdcard/%s" % os.path.basename(Config.camera_sta_test_log_path))  # log名称
        self.device.rm_file(log_path)  # 清除已存在的
        self.device.logcat_thread(log_path)
        log.info("捕捉设备log")
        # 获取后台logcat进程id
        logcat_process_id = self.device.get_current_logcat_process_id()

        total_times = self.ui_conf_file.get(Config.section_ui_camera_check, Config.option_camera_test_times)
        # 是否统计失败概率
        is_probability = int(self.ui_conf_file.get(Config.section_ui_camera_check, Config.is_probability_test))
        open_fail_flag = 0
        compare_fail_flag = 0
        photograph_fail_flag = 0
        continue_flag = 0

        times = 0
        while times <= int(total_times):
            is_double = self.ui_conf_file.get(Config.section_ui_camera_check, Config.option_front_and_rear)
            # 测试前删除已存在的照片
            if int(is_double):
                if os.path.exists(Config.camera_sta_test_front_preview_path):
                    os.remove(Config.camera_sta_test_front_preview_path)
                if os.path.exists(Config.camera_sta_test_front_photograph_path):
                    os.remove(Config.camera_sta_test_front_photograph_path)
                if os.path.exists(Config.camera_sta_test_rear_photograph_path):
                    os.remove(Config.camera_sta_test_rear_photograph_path)
                if os.path.exists(Config.camera_sta_test_rear_preview_path):
                    os.remove(Config.camera_sta_test_rear_preview_path)
            else:
                if os.path.exists(Config.camera_sta_test_default_preview_path):
                    os.remove(Config.camera_sta_test_default_preview_path)
                if os.path.exists(Config.camera_sta_test_default_photograph_path):
                    os.remove(Config.camera_sta_test_default_photograph_path)

            is_double = self.ui_conf_file.get(Config.section_ui_camera_check, Config.option_front_and_rear)
            if int(is_double):

                # get x, y position for switch btn
                x = self.ui_conf_file.get(Config.section_ui_camera_check, Config.option_switch_x_value)
                y = self.ui_conf_file.get(Config.section_ui_camera_check, Config.option_switch_y_value)
                # clear img in device
                self.device.remove_img()
                time.sleep(1)
                if len(self.device.get_latest_img()) != 0:
                    self.device.remove_img()

                # front and rear camera
                # 1 open camera
                time.sleep(1)
                self.device.open_camera()
                time.sleep(2)
                if self.device.get_camera_id() == 3:
                    self.device.open_camera()
                time.sleep(2)
                if self.device.get_camera_id() == 3:
                    log.error("打开相机失败，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("打开相机")
                # switch front camera
                if not self.device.is_first_camera():
                    self.device.click_btn(x, y)
                # get camera app package name
                self.device.get_camera_package_name()
                # click center clear other button
                pos = self.device.get_screen_center_position()
                self.device.click_btn(str(pos[0]), str(pos[1]))
                time.sleep(3)
                log.info("当前为后镜头")
                # screenshot preview
                self.device.screen_shot(Config.camera_sta_test_rear_preview_path)
                time.sleep(1)
                if not os.path.exists(Config.camera_sta_test_rear_preview_path):
                    self.device.screen_shot(Config.camera_sta_test_rear_preview_path)
                log.info("后镜头预览界面截图完成")
                # clear img
                self.device.remove_img()
                time.sleep(3)
                if len(self.device.get_latest_img()) != 0:
                    self.device.remove_img()
                # # take photo
                self.device.take_photo()
                time.sleep(3)

                if len(self.device.get_latest_img()) == 0:
                    self.device.take_photo()
                    time.sleep(3)

                if len(self.device.get_latest_img()) == 0:
                    log.info("拍照失败，请检查！！！")
                    time.sleep(3)
                    self.device.kill_process(logcat_process_id)
                    self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                    raise

                log.info("后镜头拍照完成")
                self.device.pull_img(Config.camera_sta_test_rear_photograph_path)
                time.sleep(1)
                if not os.path.exists(Config.camera_sta_test_rear_photograph_path):
                    self.device.pull_img(Config.camera_sta_test_rear_photograph_path)

                # clear img
                self.device.remove_img()
                time.sleep(1)
                if len(self.device.get_latest_img()) != 0:
                    self.device.remove_img()
                #
                # switch front camera
                self.device.click_btn(x, y)
                time.sleep(2)
                if self.device.is_first_camera():
                    self.device.click_btn(x, y)
                log.info("切换镜头")
                # wait 2 sec
                time.sleep(3)
                # screenshot preview
                self.device.screen_shot(Config.camera_sta_test_front_preview_path)
                log.info("当前预览界面截图完成")
                time.sleep(1)
                if not os.path.exists(Config.camera_sta_test_front_preview_path):
                    self.device.screen_shot(Config.camera_sta_test_front_preview_path)
                # clear img
                self.device.remove_img()
                time.sleep(1)
                if len(self.device.get_latest_img()) != 0:
                    self.device.remove_img()
                # take photo
                time.sleep(3)
                self.device.take_photo()
                time.sleep(3)
                if len(self.device.get_latest_img()) == 0:
                    self.device.take_photo()
                    time.sleep(3)

                if len(self.device.get_latest_img()) == 0:
                    log.info("拍照失败，请检查！！！")
                    time.sleep(3)
                    self.device.kill_process(logcat_process_id)
                    self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                    raise

                log.info("前镜头拍照完成")
                self.device.pull_img(Config.camera_sta_test_front_photograph_path)
                time.sleep(1)
                if not os.path.exists(Config.camera_sta_test_front_photograph_path):
                    self.device.pull_img(Config.camera_sta_test_front_photograph_path)

                # 对比前镜头
                front_preview_score = cnns.generateScore(Config.camera_sta_test_front_preview_path,
                                                         Config.camera_sta_exp_front_preview_path)
                log.info("前镜头预览画面预期和测试截图相似度分数为：%s" % str(front_preview_score))
                if front_preview_score < 90:
                    log.error("前镜头预览画面预期和测试截图差异过大，请检查！！！")
                    if is_probability:
                        # 复制测试中异常的照片到Error文件夹地址
                        preview_file_name1 = os.path.basename(Config.camera_sta_test_front_preview_path)
                        preview_file_new_path1 = Config.camera_sta_err_front_preview_path
                        shutil.copy(Config.camera_sta_test_front_preview_path, preview_file_new_path1)
                        os.rename(os.path.join(preview_file_new_path1, preview_file_name1),
                                  os.path.join(preview_file_new_path1, "%d_%s" % (times, preview_file_name1)))
                        compare_fail_flag += 1
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                        raise

                front_photograph_score = cnns.generateScore(Config.camera_sta_test_front_photograph_path,
                                                            Config.camera_sta_exp_front_photograph_path)
                log.info("前镜头拍照预期和测试拍照相似度分数为：%s" % str(front_photograph_score))
                if front_photograph_score < 90:
                    log.error("前镜头拍照预期和测试拍照差异过大，请检查！！！")
                    if is_probability:
                        photograph_file_name1 = os.path.basename(Config.camera_sta_test_front_photograph_path)
                        photograph_file_new_path1 = Config.camera_sta_err_front_photograph_path
                        shutil.copy(Config.camera_sta_test_front_photograph_path, photograph_file_new_path1)
                        os.rename(os.path.join(photograph_file_new_path1, photograph_file_name1),
                                  os.path.join(photograph_file_new_path1, "%d_%s" % (times, photograph_file_name1)))
                        compare_fail_flag += 1
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                        raise
                # 对比后镜头
                rear_preview_score = cnns.generateScore(Config.camera_sta_test_rear_preview_path,
                                                        Config.camera_sta_exp_rear_preview_path)
                log.info("后镜头预览画面预期和测试截图相似度分数为：%s" % str(rear_preview_score))
                if rear_preview_score < 90:
                    log.error("后镜头预览画面预期和测试截图差异过大，请检查！！！")
                    if is_probability:
                        preview_file_name2 = os.path.basename(Config.camera_sta_test_rear_preview_path)
                        preview_file_new_path2 = Config.camera_sta_err_rear_preview_path
                        shutil.copy(Config.camera_sta_test_rear_preview_path, preview_file_new_path2)
                        os.rename(os.path.join(preview_file_new_path2, preview_file_name2),
                                  os.path.join(preview_file_new_path2, "%d_%s" % (times, preview_file_name2)))
                        compare_fail_flag += 1
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                        raise
                rear_photograph_score = cnns.generateScore(Config.camera_sta_test_rear_photograph_path,
                                                           Config.camera_sta_exp_rear_photograph_path)
                log.info("后镜头拍照预期和测试拍照相似度分数为：%s" % str(rear_photograph_score))
                if rear_photograph_score < 90:
                    if is_probability:
                        photograph_file_name2 = os.path.basename(Config.camera_sta_test_rear_photograph_path)
                        photograph_file_new_path2 = Config.camera_sta_err_rear_photograph_path
                        shutil.copy(Config.camera_sta_test_rear_photograph_path, photograph_file_new_path2)
                        os.rename(os.path.join(photograph_file_new_path2, photograph_file_name2),
                                  os.path.join(photograph_file_new_path2, "%d_%s" % (times, photograph_file_name2)))
                        compare_fail_flag += 1
                    else:
                        log.error("后镜头拍照预期和测试拍照差异过大，请检查！！！")
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                        raise
            else:
                # 测试前删除已存在的照片
                if os.path.exists(Config.camera_sta_test_default_preview_path):
                    os.remove(Config.camera_sta_test_default_preview_path)
                if os.path.exists(Config.camera_sta_test_default_photograph_path):
                    os.remove(Config.camera_sta_test_default_photograph_path)
                self.device.remove_img()
                time.sleep(1)
                if len(self.device.get_latest_img()) != 0:
                    self.device.remove_img()

                # 后台启动捕捉log
                log_path = os.path.join("/sdcard/%s" % os.path.basename(Config.camera_sta_test_log_path))  # log名称
                self.device.rm_file(log_path)  # 清除已存在的
                self.device.logcat_thread(log_path)
                log.info("捕捉设备log")
                # 获取后台logcat进程id
                logcat_process_id = self.device.get_current_logcat_process_id()

                # 1 open camera
                time.sleep(1)
                self.device.open_camera()
                time.sleep(2)
                log.info("打开相机")
                if self.device.get_camera_id() == 3:
                    self.device.open_camera()
                time.sleep(2)
                if self.device.get_camera_id() == 3:
                    log.error("打开相机失败，请检查！！！")
                    if is_probability:
                        open_fail_flag += 1
                        self.device.force_stop_app()
                        self.device.clear_app()
                        continue
                    else:
                        time.sleep(3)
                        raise Exception

                # get camera app package name
                self.device.get_camera_package_name()
                # click center clear other button
                pos = self.device.get_screen_center_position()
                self.device.click_btn(str(pos[0]), str(pos[1]))
                time.sleep(3)
                # screenshot preview
                self.device.screen_shot(Config.camera_sta_test_default_preview_path)
                time.sleep(1)
                if not os.path.exists(Config.camera_sta_test_default_preview_path):
                    self.device.screen_shot(Config.camera_sta_test_default_preview_path)
                log.info("当前预览界面截图完成")
                # clear img
                self.device.remove_img()
                time.sleep(3)
                if len(self.device.get_latest_img()) != 0:
                    self.device.remove_img()
                    time.sleep(1)
                # # take photo
                self.device.take_photo()
                time.sleep(3)
                if len(self.device.get_latest_img()) == 0:
                    self.device.take_photo()
                    time.sleep(3)

                if len(self.device.get_latest_img()) == 0:
                    log.info("拍照失败，请检查！！！")
                    if is_probability:
                        photograph_fail_flag += 1
                        self.device.force_stop_app()
                        self.device.clear_app()
                        continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                        raise

                log.info("拍照完成")
                self.device.pull_img(Config.camera_sta_test_default_photograph_path)
                time.sleep(1)
                if not os.path.exists(Config.camera_sta_test_default_photograph_path):
                    self.device.pull_img(Config.camera_sta_test_default_photograph_path)
                # 对比照片
                default_preview_score = cnns.generateScore(Config.camera_sta_test_default_preview_path,
                                                           Config.camera_sta_exp_default_preview_path)
                log.info("镜头预览画面预期和测试截图相似度分数为：%s" % str(default_preview_score))
                if default_preview_score < 90:
                    log.error("镜头预览画面预期和测试截图差异过大，请检查！！！")
                    if is_probability:
                        compare_fail_flag += 1
                        self.device.force_stop_app()
                        self.device.clear_app()
                        # 复制测试中异常的照片到Error文件夹地址
                        preview_file_name = os.path.basename(Config.camera_sta_test_default_preview_path)
                        preview_file_new_path = Config.camera_sta_err_default_preview_path
                        shutil.copy(Config.camera_sta_test_default_preview_path, preview_file_new_path)
                        os.rename(os.path.join(preview_file_new_path, preview_file_name), os.path.join(preview_file_new_path, "%d_%s" % (times, preview_file_name)))
                        # continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                        raise
                default_photograph_score = cnns.generateScore(Config.camera_sta_test_default_photograph_path,
                                                              Config.camera_sta_exp_default_photograph_path)
                log.info("镜头拍照预期和测试拍照相似度分数为：%s" % str(default_photograph_score))
                if default_photograph_score < 90:
                    log.error("镜头拍照预期和测试拍照差异过大，请检查！！！")
                    if is_probability:
                        compare_fail_flag += 1
                        self.device.force_stop_app()
                        self.device.clear_app()
                        photograph_file_name = os.path.basename(Config.camera_sta_test_default_photograph_path)
                        photograph_file_new_path = Config.camera_sta_err_default_photograph_path
                        shutil.copy(Config.camera_sta_test_default_photograph_path, photograph_file_new_path)
                        os.rename(os.path.join(photograph_file_new_path, photograph_file_name),
                                  os.path.join(photograph_file_new_path, "%d_%s" % (times, photograph_file_name)))
                        # continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                        raise

            # close and clear data to camera
            self.device.force_stop_app()
            self.device.clear_app()
            if self.device.get_camera_id() != 3:
                self.device.force_stop_app()
                self.device.clear_app()
            log.info("关闭相机")
            # clear img
            self.device.remove_img()
            time.sleep(1)
            if len(self.device.get_latest_img()) != 0:
                self.device.remove_img()
            times += 1
            log.info("******相机压测完成%d次*****" % times)

        if open_fail_flag > 0:
            log.error("打开相机失败的次数为： %d次" % open_fail_flag)
            log.error("打开相机失败的概率为： %f" % (open_fail_flag / times))

        if photograph_fail_flag > 0:
            log.error("拍照失败的次数为： %d次" % photograph_fail_flag)
            log.error("拍照失败的概率为： %f" % (photograph_fail_flag / times))

        if compare_fail_flag > 0:
            log.error("预期图片和实际图片差异过大的次数： %d次" % compare_fail_flag)
            log.error("预期图片和实际图片差异过大的概率为： %f" % (compare_fail_flag / times))

        self.device.kill_process(logcat_process_id)
        self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
        log.info("************前后摄像头拍照问题对比用例结束*******")

    @allure.feature("bt_connect_test")
    @allure.title("连接蓝牙音响开关测试")
    def test_bt_connect_test(self):
        log.info("***********连接蓝牙音响测试开始************")
        # 测试设备（主）开关蓝牙，查看蓝牙连接情况，从机（蓝牙音响）开关开关蓝牙，主机中蓝牙连接状况
        # 查看蓝牙打开、连接情况
        if not self.device.bt_is_enable():
            log.error("设备蓝牙没打开，请检查！！！")
            time.sleep(3)
            raise Exception

        if not self.device.bt_is_connected():
            log.error("当前没有连接到蓝牙设备，请检查！！！")
            time.sleep(3)
            raise Exception

        # slave_device_mac = self.device.get_connected_bt_mac()
        total_times = int(self.ui_conf_file.get(Config.section_bt_connect_test, Config.option_bt_connect_test_times))
        is_probability_test = int(self.ui_conf_file.get(Config.section_bt_connect_test, Config.is_probability_test))
        line_num = int(self.ui_conf_file.get(Config.section_bt_connect_test, Config.option_bt_com_config).split("_")[1])
        com_port = self.ui_conf_file.get(Config.section_bt_connect_test, Config.option_bt_connect_test_com)

        times = 0
        fail_flag = 0
        slave_fail_flag = 0
        t_ser.loginSer(com_port)
        while times < total_times:
            times += 1
            log.info("**********************第%d次测试开始********************" % times)
            # 蓝牙关
            self.device.disable_bt_btn()
            time.sleep(2)
            if self.device.bt_is_enable():
                self.device.disable_bt_btn()
                time.sleep(2)
            if self.device.bt_is_enable():
                log.error("无法关闭主设备蓝牙")
                continue

            log.info("已关主设备闭蓝牙")
            time.sleep(30)
            if not self.device.bt_is_connected():
                log.info("主设备显示已断开连接蓝牙设备(从)")
            else:
                if is_probability_test:
                    fail_flag += 1
                    log.info("主设备显示未断开连接蓝牙设备(从) %d 次" % fail_flag)
                    continue

            # now_time = time.time()
            # while True:
            #     if not self.device.bt_is_connected():
            #         log.info("已断开连接蓝牙设备")
            #         break
            #     if time.time() > now_time + 60:
            #         log.error("无法断连蓝牙设备")
            #         if is_probability_test:
            #             fail_flag += 1
            #             continue
            #         else:
            #             time.sleep(3)
            #             raise
            #     time.sleep(1)

            # 开启蓝牙
            self.device.enable_bt_btn()
            time.sleep(2)
            if not self.device.bt_is_enable():
                self.device.enable_bt_btn()
                time.sleep(2)
            if not self.device.bt_is_enable():
                log.error("无法打开主设备蓝牙")
                continue

            log.info("已打开主设备蓝牙")
            time.sleep(30)
            if self.device.bt_is_connected():
                log.info("主设备显示已经连接上蓝牙设备（从）")
            else:
                if is_probability_test:
                    fail_flag += 1
                    log.error("主设备显示未连接上蓝牙设备（从）%d 次" % fail_flag)
                    continue


            # now_time1 = time.time()
            # while True:
            #     if self.device.bt_is_connected():
            #         log.info("已经连接上蓝牙设备")
            #         break
            #     if time.time() > now_time1 + 120:
            #         log.error("无法连接上蓝牙设备")
            #         if is_probability_test:
            #             fail_flag += 1
            #             continue
            #         else:
            #             time.sleep(3)
            #             raise
            #     time.sleep(1)

            # 关闭蓝牙设备，暂时用等待来替代
            # 关闭蓝牙设备操作
            t_ser.open_relay(line_num)
            log.info("断开蓝牙设备（从）")
            time.sleep(30)
            if not self.device.bt_is_connected():
                log.error("主设备显示已经断连接蓝牙设备（从）")
            else:
                if is_probability_test:
                    slave_fail_flag += 1
                    log.error("主设备显示没断连蓝牙设备（从）%d 次" % slave_fail_flag)
                    continue

            # now_time2 = time.time()
            # while True:
            #     if not self.device.bt_is_connected():
            #         log.info("已经断连接蓝牙设备")
            #         break
            #     if time.time() > now_time2 + 60:
            #         log.error("无法断连蓝牙设备")
            #         if is_probability_test:
            #             slave_fail_flag += 1
            #             continue
            #         else:
            #             time.sleep(3)
            #             raise
            #     time.sleep(1)

            # 打开蓝牙设备，暂时用等待来替代
            # 打开蓝牙操作
            t_ser.close_relay(line_num)
            log.info("打开蓝牙设备（从）")
            time.sleep(30)
            if self.device.bt_is_connected():
                log.info("主设备显示已经连接上蓝牙设备（从）")
            else:
                if is_probability_test:
                    slave_fail_flag += 1
                    log.error("主设备显示没连接上蓝牙设备（从）%d 次" % slave_fail_flag)
                    continue

            # now_time3 = time.time()
            # while True:
            #     if self.device.bt_is_connected():
            #         log.info("已经连接上蓝牙设备")
            #         break
            #     if time.time() > now_time3 + 120:
            #         log.error("无法连接上蓝牙设备")
            #         if is_probability_test:
            #             slave_fail_flag += 1
            #             continue
            #         else:
            #             time.sleep(3)
            #             raise
            #     time.sleep(1)
            log.info("**********************第%d次测试结束********************" % times)

        t_ser.logoutSer()

        if is_probability_test:
            if fail_flag > 0:
                probability = fail_flag / times
                log.error("设备重开蓝牙连接不上蓝牙设备的次数为：%d" % fail_flag)
                log.error("设备重开蓝牙连接不上蓝牙设备的概率为%s" % probability)

            if slave_fail_flag > 0:
                slave_probability = slave_fail_flag / times
                log.error("蓝牙设备断连，显示异常的次数为：%d" % slave_fail_flag)
                log.error("蓝牙设备断连，显示异常的概率为%s" % slave_probability)

        log.info("***********连接蓝牙音响测试结束************")
