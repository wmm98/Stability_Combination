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

    @allure.feature("开关机检查基本功能")
    @allure.title("开关机检查基本功能")
    def test_lx_boot_check_stability_test(self):
        log.info("****立项测试-开关机检查基本功能用例开始******")
        # 获取测试点的配置信息
        is_wifi = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_wifi_test)
        is_eth = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_eth_test)
        is_mobile = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_mobile_test)
        is_bt = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_bt_test)
        is_nfc = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_nfc_test)
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
                raise
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
                raise
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
                raise
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
                raise
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
                    raise
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

        # U盘， 后续开发适配

        # 1、关机开机检测卡logo，是否进入recovery模式等部分处理
        device_check = DeviceCheck(self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name))
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
        # """
        # 1 适配器开关机（适配器闭合开路开关机）
        # 2 适配器/电池+电源按键--正常关机（指令关机）
        # 3 适配器/电池+电源按键--异常关机（适配器开路关机）
        # """
        # # try:
        # #     flag = 0
        # #     while flag < int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_test_times)):
        # #         flag += 1
        # #         # 上下电启动
        # #         try:
        # #             t_ser.loginSer(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_COM))
        # #         except Exception as e:
        # #             log.error("串口已经被占用， 请检查！！！")
        # #             log.error(str(e))
        # #             break
        # #         log.info("关机")
        # #
        # #         if self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "1":
        # #             num = int(
        # #                 self.ui_conf_file.get(Config.section_ui_boot_check,
        # #                                       Config.option_logo_adapter_power_config).split(
        # #                     "_")[1])
        # #             t_ser.open_relay(num)
        # #             log.info("适配器开路")
        # #             time.sleep(1)
        # #             if device_check.device_is_online():
        # #                 raise Exception("设备关机失败，请接线是否正确！！！")
        # #             t_ser.close_relay(num)
        # #             log.info("适配器通路")
        # #         elif self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "2":
        # #             # 关机
        # #             device_check.device_shutdown()
        # #             time.sleep(10)
        # #             device_check.restart_adb()
        # #             if device_check.device_is_online():
        # #                 raise Exception("指令设备关机失败，请检查！！！")
        # #             log.info("指令关机")
        # #             # 开机
        # #             num = int(
        # #                 self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_power_button_config).split(
        # #                     "_")[1])
        # #             t_ser.open_relay(num)
        # #             log.info("按下电源按键")
        # #             time.sleep(int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_boot_time)))
        # #             t_ser.close_relay(num)
        # #             log.info("松开电源按键")
        # #         # 适配器异常下电
        # #         elif self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "3":
        # #             num_adapter_power = int(
        # #                 self.ui_conf_file.get(Config.section_ui_boot_check,
        # #                                       Config.option_logo_adapter_power_config).split(
        # #                     "_")[1])
        # #             num_power_button = int(
        # #                 self.ui_conf_file[Config.section_ui_boot_check][Config.option_power_button_config].split("_")[
        # #                     1])
        # #             # 断开适配器/电池
        # #             t_ser.open_relay(num_adapter_power)
        # #             log.info("电池/适配器开路")
        # #             time.sleep(1)
        # #             if device_check.device_is_online():
        # #                 raise Exception("设备关机失败，请检查接线是否正确！！！")
        # #             # 闭合适配器 / 电池
        # #             t_ser.close_relay(num_adapter_power)
        # #             log.info("电池/适配器通路")
        # #             # 按下电源按键开机
        # #             time.sleep(1)
        # #             t_ser.open_relay(num_power_button)
        # #             log.info("按下电源健")
        # #             time.sleep(int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_boot_time)))
        # #             t_ser.close_relay(num_power_button)
        # #             log.info("松开电源按键")
        # #
        # #         log.info("正在开机，请等...")
        # #         if check_adb_online_with_thread(
        # #                 self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name)):
        # #             if check_boot_complete_with_thread(
        # #                     self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name),
        # #                     timeout=120):
        # #                 log.info("设备完全启动")
        # #             else:
        # #                 log.info("设备无法完全启动, 请检查!!!")
        # #                 if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "1":
        # #                     log.error("当前认为复现了卡logo情景，请检查！！！")
        # #                     time.sleep(3)
        # #                     break
        # #         else:
        # #             log.error("没检测到设备在线!!!")
        # #             if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "1":
        # #                 log.error("当前认为复现了卡logo情景，请检查！！！")
        # #                 time.sleep(3)
        # #                 break
        # #         if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "0":
        # #             # 拍照
        # #             time.sleep(60)
        # #             # time.sleep(interval[flag])
        # #             origin_camera_path = os.path.join(conf.camera_origin_img_path, "Origin.png")
        # #             # 双屏情况
        # #             origin_camera2_path = os.path.join(conf.camera_origin_img_path, "Origin2.png")
        # #             if os.path.exists(origin_camera_path):
        # #                 os.remove(origin_camera_path)
        # #             if os.path.exists(origin_camera2_path):
        # #                 os.remove(origin_camera2_path)
        # #
        # #             # 单双屏情况
        # #             if self.ui_conf_file[Config.section_ui_boot_check][Config.option_logo_double_screen] == "1":
        # #                 camera.take_photo(origin_camera_path, camera_id=1)
        # #                 log.info("镜头2拍照完成")
        # #                 # 抠图
        # #                 log.info("抠图中， 请等待")
        # #                 camera2_key_img_path = os.path.join(conf.camera_key_img_path, "Key2.png")
        # #                 if os.path.exists(camera2_key_img_path):
        # #                     os.remove(camera2_key_img_path)
        # #                 key_ing.save_key_photo(origin_camera_path, camera2_key_img_path)
        # #                 log.info("抠图完成")
        # #
        # #                 score2 = cnns.generateScore(origin_logo_key_img, camera2_key_img_path)
        # #                 log.info("当前相似度分数为：%s" % str(score2))
        # #                 if score2 < 75:
        # #                     log.error("当前认为复现了卡logo情景，请检查！！！")
        # #                     if device_check.device_is_online():
        # #                         log.info("设备在线")
        # #                         device_check.logcat(int(
        # #                             self.ui_conf_file.get(Config.section_ui_boot_check,
        # #                                                   Config.option_logcat_duration)) * 60)
        # #                         log.info("成功捕捉了%s 分钟 adb log" % self.ui_conf_file.get(Config.section_ui_boot_check,
        # #                                                                               Config.option_logcat_duration))
        # #                         log.info("任务结束")
        # #                     else:
        # #                         log.info("设备不在线")
        # #                         log.info("任务结束")
        # #                     time.sleep(3)
        # #                     break
        # #
        # #             camera.take_photo(origin_camera_path)
        # #             log.info("镜头1拍照完成")
        # #             # 抠图
        # #             log.info("抠图中， 请等待")
        # #             camera_key_img_path = os.path.join(conf.camera_key_img_path, "Key.png")
        # #             if os.path.exists(camera_key_img_path):
        # #                 os.remove(camera_key_img_path)
        # #             key_ing.save_key_photo(origin_camera_path, camera_key_img_path)
        # #             log.info("抠图完成")
        # #
        # #             score = cnns.generateScore(origin_logo_key_img, camera_key_img_path)
        # #             log.info("当前相似度分数为：%s" % str(score))
        # #             if score < 70:
        # #                 log.error("当前认为复现了卡logo情景，请检查！！！")
        # #                 if device_check.device_is_online():
        # #                     log.info("设备在线")
        # #                     device_check.logcat(
        # #                         int(self.ui_conf_file.get(Config.section_ui_boot_check,
        # #                                                   Config.option_logcat_duration)) * 60)
        # #                     log.info("成功捕捉了%s 分钟 adb log" % self.ui_conf_file.get(Config.section_ui_boot_check,
        # #                                                                           Config.option_logcat_duration))
        # #                     log.info("任务结束")
        # #                 else:
        # #                     log.info("设备不在线")
        # #                     log.info("任务结束")
        # #                 time.sleep(3)
        # #                 break
        # #
        # #         t_ser.logoutSer()
        # #         log.info("*******************压测完成%d次********************" % flag)
        # #         time.sleep(3)
        # # except Exception as e:
        # #     log.info(str(e))
        #
        # # 2、检查wifi，蓝牙，usb,4G、以太网模块状态，关闭并且再次开启检查状态
        #
        # # 调试代码
        # # 重启代替硬开、关机
        # # self.device.reboot()
        log.info("重启...")
        if check_adb_online_with_thread(
                self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name)):
            if check_boot_complete_with_thread(
                    self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name),
                    timeout=120):
                log.info("设备完全启动")
                # 后续查看是否要等待时间
                time.sleep(5)
            else:
                log.info("设备无法完全启动, 请检查!!!")
                if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "1":
                    log.error("当前认为复现了卡logo情景，请检查！！！")
                    time.sleep(3)
                    raise

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


        log.info("****************立项测试-开关机检查基本功能用例结束******************")

    @allure.feature("前后摄像头拍照问题对比")
    @allure.title("前后摄像头拍照问题对比")
    def test_lx_front_rear_camera_test(self):
        log.info("************前后摄像头拍照问题对比用例开始*******")
        log.info("************前后摄像头拍照问题对比用例结束*******")
