import allure
import os
import time
import pytest
from Common.log import MyLog
from Main.device import Device
from Common import image_analysis, camera_operate, m_serial, adb_timer
from Common.device_check import DeviceCheck
import configparser
from Common.config import Config
from Main.public import publicInterface
import shutil
from Common.process_shell import Shell, ConShell

con_shell = ConShell()
shell = Shell()
conf = Config()
log = MyLog()
public_interface = publicInterface()
analysis = image_analysis.Analysis()
cnns = image_analysis.CNNsAnalysis()
camera = camera_operate.Camera()
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


def clear_directory(dir_path):
    file_names = os.listdir(dir_path)
    if len(file_names) != 0:
        # 遍历文件名列表并删除文件
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)  # 文件路径
            os.remove(file_path)


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
        try:
            # 获取测试点的配置信息
            test_times = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_test_times))
            is_wifi = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_wifi_test))
            is_eth = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_eth_test))
            is_mobile = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_mobile_test))
            is_bt = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_bt_test))
            is_nfc = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_nfc_test))
            is_probability_test = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.is_probability_test))
            # usb待网络优先级完成后继续完成完善
            is_usb = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_usb_test))
            is_camera = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_camera_test))
            root_steps = self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_root_steps).split(",")

            bt_interval = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.bt_interval))
            rounds_interval = int(self.ui_conf_file.get(Config.section_ui_boot_check, Config.test_interval))

            if is_camera:
                is_double = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_front_and_rear)

                # 拍照相关
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

            open_fail_flag = 0
            compare_fail_flag = 0
            photograph_fail_flag = 0

            wifi_boot_not_existent = 0
            wifi_disable_fail_flag = 0
            wifi_enable_fail_flag = 0
            wifi_enable_no_network_fail = 0
            wifi_disable_network_fail = 0

            eth_boot_not_existent = 0
            eth_disable_fail_flag = 0
            eth_enable_fail_flag = 0
            eth_enable_no_network_fail = 0
            eth_disable_network_fail = 0

            mobile_boot_not_existent = 0
            mobile_disable_fail_flag = 0
            mobile_enable_fail_flag = 0
            mobile_no_network_fail = 0
            mobile_disable_network_fail = 0

            bt_boot_not_existent = 0
            bt_disable_fail_flag = 0
            bt_enable_fail_flag = 0
            bt_salve_fail_flag = 0

            nfc_boot_not_existent = 0
            nfc_disable_fail_flag = 0
            nfc_enable_fail_flag = 0

            usb_recognize_fail_flag = 0

            # 先root设备
            for cmd in root_steps:
                shell.invoke(cmd)
                if "reboot" in cmd:
                    if check_adb_online_with_thread(
                            self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name)):
                        if check_boot_complete_with_thread(
                                self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name),
                                timeout=120):
                            log.info("设备完全启动")
                time.sleep(2)

            # 设备里面创建一个文件
            txt_path = "/data/boot_debug.txt"
            self.device.send_adb_shell_command("echo \"automation test for test team\" > %s" % txt_path)
            log.info("创建文件：%s" % txt_path)
            txt_md5sum_value = self.device.get_file_md5_value(txt_path)

            # 测试前先检查所有的按钮开关
            if is_bt:
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

            # 检查蓝牙设备（从）是否连接上
            if not self.device.bt_is_connected():
                log.error("当前测试设备显示未连接上蓝牙设备（从）")
                time.sleep(3)
                raise Exception
            log.info("当前设备已连接上蓝牙设备（从）")

            # 需要跟彬哥确认NFC刷卡绑定app的问题
            if is_nfc:
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

            if is_eth:
                log.info("****检查以太网当前状态")
                self.device.disable_wifi_btn()
                self.device.disable_mobile_btn()
                time.sleep(1)
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                    time.sleep(3)
                log.info("以太网上电")
                if not self.device.ping_network(timeout=120):
                    log.error("以太网无法上网， 请见检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网可上网")

            if is_wifi:
                log.info("****检查wifi当前状态")
                self.device.disable_mobile_btn()
                self.device.disable_eth0_btn()
                time.sleep(1)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                log.info("wifi上电")

                if not self.device.ping_network(timeout=120):
                    log.error("wifi无法上网， 请见检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网可上网")

            if is_mobile:
                self.device.disable_wifi_btn()
                self.device.disable_eth0_btn()
                log.info("****检查移动数据流量当前状态")
                if is_wifi:
                    if self.device.wifi_is_enable():
                        self.device.disable_wifi_btn()
                        time.sleep(3)
                if is_eth:
                    if self.device.eth0_is_enable():
                        self.device.disable_eth0_btn()
                        time.sleep(3)

                if not self.device.ping_network(timeout=120):
                    log.error("4G卡无法上网， 请见检查！！！")
                    time.sleep(3)
                    raise Exception

            # wifi, 以太网上电
            if is_wifi:
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi无法上电，请检查！！！")
                    raise
                    #
            if is_eth:
                self.device.enable_eth0_btn()
                time.sleep(3)
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                    time.sleep(3)
                if not self.device.eth0_is_enable():
                    log.error("以太网无法上电，请检查！！！")
                    raise
            # U盘， 后续开发适配, sdcard数据检查后续开发

            # 1、关机开机检测卡logo，是否进入recovery模式等部分处理
            device_check = DeviceCheck(
                self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name))
            # 确认二部机器adb btn 开
            device_check.adb_btn_open()
            # 先对设备的时间进行修改，使用网络时间，方便看log
            # ?
            # # 图片处理相关
            # origin_logo_logo_img = os.path.join(conf.logo_logo_path, "Logo.png")
            # origin_logo_key_img = os.path.join(conf.logo_key_path, "Key.png")
            # # 需要在前端先删除存留的失败照片,调试的时候先在这里删除
            # failed_img_path = os.path.join(conf.camera_key_img_path, "Failed.png")
            # if os.path.exists(failed_img_path):
            #     os.remove(failed_img_path)

            # 用例说明
            """
            1 适配器开关机（适配器闭合开路开关机）
            2 适配器/电池+电源按键--正常关机（指令关机）
            3 适配器/电池+电源按键--异常关机（适配器开路关机）
            """

            flag = 0
            com_port = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_logo_COM)
            t_ser.loginSer(com_port)
            while flag < test_times:
                flag += 1
                # 上下电启动
                log.info("关机")

                if self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "1":
                    num = int(
                        self.ui_conf_file.get(Config.section_ui_boot_check,
                                              Config.option_logo_adapter_power_config).split(
                            "_")[1])
                    t_ser.open_relay(num)
                    log.info("适配器开路")
                    time.sleep(bt_interval)
                    if device_check.device_is_online():
                        raise Exception("设备关机失败，请接线是否正确！！！")
                    t_ser.close_relay(num)
                    log.info("适配器通路")
                elif self.ui_conf_file.get(Config.section_ui_boot_check, Config.ui_option_logo_cases) == "2":
                    # 关机
                    device_check.device_shutdown()
                    time.sleep(bt_interval - 2)
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
                    time.sleep(bt_interval - 2)
                    device_check.restart_adb()
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

                # 调试代码

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

                for cmd in root_steps:
                    shell.invoke(cmd)
                    if "reboot" in cmd:
                        if check_adb_online_with_thread(
                                self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name)):
                            if check_boot_complete_with_thread(
                                    self.ui_conf_file.get(Config.section_ui_to_background,
                                                          Config.ui_option_device_name),
                                    timeout=120):
                                log.info("设备完全启动")
                            else:
                                log.info("设备无法完全启动, 请检查!!!")
                                if self.ui_conf_file[Config.section_ui_boot_check][
                                    Config.option_only_boot_config] == "1":
                                    log.error("当前认为复现了卡logo情景，请检查！！！")
                                    time.sleep(3)
                                    break
                        else:
                            log.error("没检测到设备在线!!!")
                            if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "1":
                                log.error("当前认为复现了卡logo情景，请检查！！！")
                                time.sleep(3)
                                break
                        time.sleep(2)

                if self.ui_conf_file[Config.section_ui_boot_check][Config.option_only_boot_config] == "0":
                    # 拍照
                    time.sleep(30)
                    if not self.device.is_screen_on():
                        self.device.press_power_button()
                    time.sleep(1)
                    if not self.device.is_screen_on():
                        self.device.press_power_button()
                    time.sleep(1)
                    self.device.unlock()
                    self.device.unlock()
                    time.sleep(1)
                    self.device.back_home()
                    time.sleep(1)

                    # 单双屏情况
                    if self.ui_conf_file[Config.section_ui_boot_check][Config.option_logo_double_screen] == "1":
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
                                    self.ui_conf_file.get(Config.section_ui_boot_check,
                                                          Config.option_logcat_duration)) * 60)
                                log.info(
                                    "成功捕捉了%s 分钟 adb log" % self.ui_conf_file.get(Config.section_ui_boot_check,
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

                # 1、检查创建的文件md5值
                new_md5_value = self.device.get_file_md5_value(txt_path)
                if new_md5_value != txt_md5sum_value:
                    log.error("开机前后%s的md5值不一致，请检查！！！" % txt_path)
                    time.sleep(3)
                    raise Exception
                else:
                    log.info("开机前后%s的md5值一直" % txt_path)

                # 追加内容到txt
                self.device.send_adb_shell_command("echo \"debug\" >> %s" % txt_path)
                log.info("追加内容到%s" % txt_path)
                latest_md5_value = self.device.get_file_md5_value(txt_path)
                txt_md5sum_value = latest_md5_value
                # 2、检查wifi，蓝牙，usb,4G、以太网模块状态，关闭并且再次开启检查状态
                failed_flag = 0
                if is_bt:
                    log.info("********检查蓝牙开关状态")
                    if not self.device.bt_is_enable():
                        log.error("重启后蓝牙不是上电状态，请检查！！！")
                        if is_probability_test:
                            bt_boot_not_existent += 1
                        else:
                            failed_flag += 1
                    log.info("启动后蓝牙当前为上电状态")
                    # 检查蓝牙设备是否连接上
                    time.sleep(10)
                    if self.device.bt_is_connected():
                        log.info("当前显示已连接上蓝牙设备（从）")
                    else:
                        log.error("当前显示没连接上蓝牙设备，请检查！！！")
                        if is_probability_test:
                            bt_salve_fail_flag += 1
                        else:
                            failed_flag += 1

                    # 对蓝牙进行关开操作
                    log.info("给蓝牙下电")
                    self.device.disable_bt_btn()
                    time.sleep(3)
                    if self.device.bt_is_enable():
                        self.device.disable_bt_btn()
                        time.sleep(3)
                    if self.device.bt_is_enable():
                        log.error("蓝牙无法下电，请检查！！！")
                        if is_probability_test:
                            bt_disable_fail_flag += 1
                        else:
                            failed_flag += 1
                    log.info("蓝牙下电成功")
                    # 检查从机蓝牙设备连接情况
                    time.sleep(3)
                    if self.device.bt_is_connected():
                        log.error("显示连接上蓝牙设备，蓝牙未断开，请检查！！！")
                        if is_probability_test:
                            bt_salve_fail_flag += 1
                        else:
                            failed_flag += 1
                        # time.sleep(3)
                        # raise Exception
                    else:
                        log.info("已断开蓝牙设备（从）")

                    log.info("给蓝牙上电")
                    self.device.enable_bt_btn()
                    time.sleep(3)
                    if not self.device.bt_is_enable():
                        self.device.enable_bt_btn()
                        time.sleep(3)
                    if not self.device.bt_is_enable():
                        log.error("蓝牙无法上电，请检查！！！")
                        if is_probability_test:
                            bt_enable_fail_flag += 1
                        else:
                            failed_flag += 1

                    log.info("蓝牙上电成功")
                    # 检查蓝牙设备（从）连接情况
                    time.sleep(10)
                    if self.device.bt_is_connected():
                        log.info("已经连接上蓝牙设备")
                    else:
                        log.error("无法自动重连蓝牙设备，请检查！！！")
                        if is_probability_test:
                            bt_salve_fail_flag += 1
                        else:
                            failed_flag += 1

                if is_nfc:
                    log.info("********检查NFC开关状态")
                    if not self.device.nfc_is_enable():
                        log.error("启动后nfc不是上电状态，请检查！！！")
                        if is_probability_test:
                            nfc_boot_not_existent += 1
                        else:
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
                        if is_probability_test:
                            nfc_disable_fail_flag += 1
                        else:
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
                        if is_probability_test:
                            nfc_enable_fail_flag += 1
                        else:
                            failed_flag += 1
                    log.info("nfc上电成功")

                # 检查各网络模块是否上电状态
                if is_eth:
                    log.info("********检查以太网状态")
                    if not self.device.eth0_is_enable():
                        log.error("启动后的以太网不是上电状态， 请检查！！！")
                        if is_probability_test:
                            eth_boot_not_existent += 1
                        else:
                            failed_flag += 1
                            # time.sleep(3)
                            # raise Exception
                    log.info("启动后以太网为上电状态")

                if is_wifi:
                    log.info("********检查以wifi态")
                    if not self.device.wifi_is_enable():
                        log.error("启动后的以wifi不是上电状态， 请检查！！！")
                        if is_probability_test:
                            wifi_boot_not_existent += 1
                        else:
                            failed_flag += 1
                        # time.sleep(3)
                        # raise Exception
                    log.info("启动后wifi为上电状态")

                if is_mobile:
                    log.info("********检查以流量数据态")
                    if not self.device.mobile_is_enable():
                        log.error("启动后的移动数据网络不是上电状态， 请检查！！！")
                        if is_probability_test:
                            mobile_boot_not_existent += 1
                        else:
                            failed_flag += 1
                        # time.sleep(3)
                        # raise Exception
                    log.info("启动后移动网络为上电状态")

                # 停止测试
                if not is_probability_test:
                    if failed_flag > 1:
                        raise Exception
                # else:
                #     continue

                # if is_eth:
                #     log.info("*****检查以太网上网情况")
                #     if self.device.is_eth0_internet():
                #         log.info("当前以太网可上网")
                #     else:
                #         log.error("当前以太网不可以上网，请检查！！！")
                #         time.sleep(3)
                #         raise Exception

                if int(is_eth) and int(is_wifi) and int(is_mobile):
                    # 禁用wifi
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                    if self.device.wifi_is_enable():
                        self.device.disable_wifi_btn()
                        time.sleep(3)
                    if self.device.wifi_is_enable():
                        log.error("wifi模块无法下电，请检查！！！")
                        if is_probability_test:
                            wifi_disable_fail_flag += 1
                        else:
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
                        if is_probability_test:
                            mobile_disable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception

                    log.info("移动数据下电成功")
                    if not self.device.ping_network(5, 35):
                        log.error("启动后以太网无法上网， 请检查！！！")
                        if is_probability_test:
                            eth_enable_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            eth_disable_fail_flag += 1
                        else:
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
                        if is_probability_test:
                            eth_enable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("以太网模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("以太网无法上网， 请检查！！！")
                        if is_probability_test:
                            eth_enable_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            eth_disable_fail_flag += 1
                        else:
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
                        if is_probability_test:
                            wifi_enable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("wifi模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("wifi无法上网， 请检查！！！")
                        if is_probability_test:
                            wifi_enable_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            wifi_disable_fail_flag += 1
                        else:
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
                        if is_probability_test:
                            mobile_disable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("移动数据模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("移动数据无法上网， 请检查！！！")
                        if is_probability_test:
                            mobile_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            wifi_enable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("wifi模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("wifi无法上网， 请检查！！！")
                        if is_probability_test:
                            wifi_enable_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            eth_enable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("以太网模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("以太网无法上网， 请检查！！！")
                        if is_probability_test:
                            eth_enable_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            mobile_disable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("移动数据下电")

                    if not self.device.ping_network(5, 120):
                        log.error("wifi无法上网， 请检查！！！")
                        if is_probability_test:
                            wifi_enable_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            wifi_disable_fail_flag += 1
                        else:
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
                        if is_probability_test:
                            mobile_enable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("移动数据模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("移动数据无法上网， 请检查！！！")
                        if is_probability_test:
                            mobile_no_network_fail += 1
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
                        if is_probability_test:
                            mobile_disable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception

                    self.device.enable_wifi_btn()
                    time.sleep(3)
                    if not self.device.wifi_is_enable():
                        self.device.enable_wifi_btn()
                        time.sleep(3)
                    if not self.device.wifi_is_enable():
                        log.error("wifi模块无法上电，请检查！！！")
                        if is_probability_test:
                            wifi_enable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("wifi模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 120):
                        log.error("wifi无法上网， 请检查！！！")
                        if is_probability_test:
                            wifi_enable_no_network_fail += 1
                        else:
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
                        if is_probability_test:
                            mobile_enable_fail_flag += 1
                        else:
                            time.sleep(3)
                            raise Exception
                    log.info("移动数据模块上电成功")

                # 相机压测
                if is_camera:
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

                    if int(is_double):
                        # get x, y position for switch btn
                        x = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_switch_x_value)
                        y = self.ui_conf_file.get(Config.section_ui_boot_check, Config.option_switch_y_value)
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
                        if front_preview_score < 0.9:
                            log.error("前镜头预览画面预期和测试截图差异过大，请检查！！！")
                            if is_probability_test:
                                # 复制测试中异常的照片到Error文件夹地址
                                preview_file_name1 = os.path.basename(Config.camera_sta_test_front_preview_path)
                                preview_file_new_path1 = Config.camera_sta_err_front_preview_path
                                shutil.copy(Config.camera_sta_test_front_preview_path, preview_file_new_path1)
                                os.rename(os.path.join(preview_file_new_path1, preview_file_name1),
                                          os.path.join(preview_file_new_path1, "%d_%s" % (flag, preview_file_name1)))
                                compare_fail_flag += 1
                            else:
                                time.sleep(3)
                                raise

                        front_photograph_score = cnns.generateScore(Config.camera_sta_test_front_photograph_path,
                                                                    Config.camera_sta_exp_front_photograph_path)
                        log.info("前镜头拍照预期和测试拍照相似度分数为：%s" % str(front_photograph_score))
                        if front_photograph_score < 0.9:
                            log.error("前镜头拍照预期和测试拍照差异过大，请检查！！！")
                            if is_probability_test:
                                photograph_file_name1 = os.path.basename(Config.camera_sta_test_front_photograph_path)
                                photograph_file_new_path1 = Config.camera_sta_err_front_photograph_path
                                shutil.copy(Config.camera_sta_test_front_photograph_path, photograph_file_new_path1)
                                os.rename(os.path.join(photograph_file_new_path1, photograph_file_name1),
                                          os.path.join(photograph_file_new_path1,
                                                       "%d_%s" % (flag, photograph_file_name1)))
                                compare_fail_flag += 1
                            else:
                                time.sleep(3)
                                raise
                        # 对比后镜头
                        rear_preview_score = cnns.generateScore(Config.camera_sta_test_rear_preview_path,
                                                                Config.camera_sta_exp_rear_preview_path)
                        log.info("后镜头预览画面预期和测试截图相似度分数为：%s" % str(rear_preview_score))
                        if rear_preview_score < 0.9:
                            log.error("后镜头预览画面预期和测试截图差异过大，请检查！！！")
                            if is_probability_test:
                                preview_file_name2 = os.path.basename(Config.camera_sta_test_rear_preview_path)
                                preview_file_new_path2 = Config.camera_sta_err_rear_preview_path
                                shutil.copy(Config.camera_sta_test_rear_preview_path, preview_file_new_path2)
                                os.rename(os.path.join(preview_file_new_path2, preview_file_name2),
                                          os.path.join(preview_file_new_path2, "%d_%s" % (flag, preview_file_name2)))
                                compare_fail_flag += 1
                            else:
                                time.sleep(3)
                                raise
                        rear_photograph_score = cnns.generateScore(Config.camera_sta_test_rear_photograph_path,
                                                                   Config.camera_sta_exp_rear_photograph_path)
                        log.info("后镜头拍照预期和测试拍照相似度分数为：%s" % str(rear_photograph_score))
                        if rear_photograph_score < 0.9:
                            if is_probability_test:
                                photograph_file_name2 = os.path.basename(Config.camera_sta_test_rear_photograph_path)
                                photograph_file_new_path2 = Config.camera_sta_err_rear_photograph_path
                                shutil.copy(Config.camera_sta_test_rear_photograph_path, photograph_file_new_path2)
                                os.rename(os.path.join(photograph_file_new_path2, photograph_file_name2),
                                          os.path.join(photograph_file_new_path2,
                                                       "%d_%s" % (flag, photograph_file_name2)))
                                compare_fail_flag += 1
                            else:
                                log.error("后镜头拍照预期和测试拍照差异过大，请检查！！！")
                                time.sleep(3)
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
                        log_path = os.path.join(
                            "/sdcard/%s" % os.path.basename(Config.camera_sta_test_log_path))  # log名称
                        # self.device.rm_file(log_path)  # 清除已存在的
                        # self.device.logcat_thread(log_path)
                        # log.info("捕捉设备log")
                        # # 获取后台logcat进程id
                        # logcat_process_id = self.device.get_current_logcat_process_id()

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
                            if is_probability_test:
                                open_fail_flag += 1
                                self.device.force_stop_camera_app()
                                self.device.clear_camera_app()
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
                            if is_probability_test:
                                photograph_fail_flag += 1
                                self.device.force_stop_camera_app()
                                self.device.clear_camera_app()
                                continue
                            else:
                                time.sleep(3)
                                # self.device.kill_process(logcat_process_id)
                                # self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
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
                        if default_preview_score < 0.9:
                            log.error("镜头预览画面预期和测试截图差异过大，请检查！！！")
                            if is_probability_test:
                                compare_fail_flag += 1
                                self.device.force_stop_camera_app()
                                self.device.clear_camera_app()
                                # 复制测试中异常的照片到Error文件夹地址
                                preview_file_name = os.path.basename(Config.camera_sta_test_default_preview_path)
                                preview_file_new_path = Config.camera_sta_err_default_preview_path
                                shutil.copy(Config.camera_sta_test_default_preview_path, preview_file_new_path)
                                os.rename(os.path.join(preview_file_new_path, preview_file_name),
                                          os.path.join(preview_file_new_path, "%d_%s" % (flag, preview_file_name)))
                                # continue
                            else:
                                time.sleep(3)
                                # self.device.kill_process(logcat_process_id)
                                # self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                                raise
                        default_photograph_score = cnns.generateScore(Config.camera_sta_test_default_photograph_path,
                                                                      Config.camera_sta_exp_default_photograph_path)
                        log.info("镜头拍照预期和测试拍照相似度分数为：%s" % str(default_photograph_score))
                        if default_photograph_score < 0.9:
                            log.error("镜头拍照预期和测试拍照差异过大，请检查！！！")
                            if is_probability_test:
                                compare_fail_flag += 1
                                self.device.force_stop_camera_app()
                                self.device.clear_camera_app()
                                photograph_file_name = os.path.basename(Config.camera_sta_test_default_photograph_path)
                                photograph_file_new_path = Config.camera_sta_err_default_photograph_path
                                shutil.copy(Config.camera_sta_test_default_photograph_path, photograph_file_new_path)
                                os.rename(os.path.join(photograph_file_new_path, photograph_file_name),
                                          os.path.join(photograph_file_new_path,
                                                       "%d_%s" % (flag, photograph_file_name)))
                                # continue
                            else:
                                time.sleep(3)
                                # self.device.kill_process(logcat_process_id)
                                self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                                raise

                    # close and clear data to camera
                    self.device.force_stop_camera_app()
                    self.device.clear_camera_app()
                    if self.device.get_camera_id() != 3:
                        self.device.force_stop_camera_app()
                        self.device.clear_camera_app()
                    log.info("关闭相机")
                    # clear img
                    self.device.remove_img()
                    time.sleep(1)
                    if len(self.device.get_latest_img()) != 0:
                        self.device.remove_img()

                log.info("*******************压测完成%d次********************" % flag)
                time.sleep(rounds_interval)

            t_ser.logoutSer()
            if is_probability_test:
                # 相机概率问题显示
                if open_fail_flag > 0:
                    log.error("打开相机失败的次数为： %d次" % open_fail_flag)
                    # log.error("打开相机失败的概率为： %f" % (open_fail_flag / flag))

                if photograph_fail_flag > 0:
                    log.error("拍照失败的次数为： %d次" % photograph_fail_flag)
                    # log.error("拍照失败的概率为： %f" % (photograph_fail_flag / flag))

                if compare_fail_flag > 0:
                    log.error("预期图片和实际图片差异过大的次数： %d次" % compare_fail_flag)
                    # log.error("预期图片和实际图片差异过大的概率为： %f" % (compare_fail_flag / flag))

                if bt_boot_not_existent > 0:
                    log.error("蓝牙启动前后状态不一致的次数为： %d次" % bt_boot_not_existent)
                    # log.error("蓝牙启动前后状态不一致的概率： %f" % (bt_boot_not_existent / flag))

                if bt_enable_fail_flag > 0:
                    log.error("蓝牙上电失败次数为： %d次" % bt_enable_fail_flag)
                    # log.error("蓝牙上电失败的概率： %f" % (bt_enable_fail_flag / flag))

                if bt_disable_fail_flag > 0:
                    log.error("蓝牙下电失败次数为： %d次" % bt_disable_fail_flag)
                    # log.error("蓝牙下电失败的概率： %f" % (bt_disable_fail_flag / flag))

                if bt_salve_fail_flag > 0:
                    log.error("设备无法自动重连蓝牙次数为： %d次" % bt_salve_fail_flag)
                    # log.error("设备无法自动重连蓝牙的概率： %f" % (bt_salve_fail_flag / flag))

                if nfc_boot_not_existent > 0:
                    log.error("NFC启动前后状态不一致的次数为： %d次" % nfc_boot_not_existent)
                    # log.error("NFC启动前后状态不一致的概率： %f" % (nfc_boot_not_existent / flag))

                if nfc_enable_fail_flag > 0:
                    log.error("NFC上电失败次数为： %d次" % nfc_enable_fail_flag)
                    # log.error("NFC上电失败的概率： %f" % (nfc_enable_fail_flag / flag))

                if nfc_enable_fail_flag > 0:
                    log.error("NFC下电失败次数为： %d次" % nfc_disable_fail_flag)
                    # log.error("NFC下电失败的概率： %f" % (nfc_disable_fail_flag / flag))

                eth_boot_not_existent = 0
                eth_disable_fail_flag = 0
                eth_enable_fail_flag = 0
                eth_enable_no_network_fail = 0

                if eth_boot_not_existent > 0:
                    log.error("以太网启动前后状态不一致的次数为： %d次" % eth_boot_not_existent)
                    # log.error("以太网启动前后状态不一致的概率： %f" % (eth_boot_not_existent / flag))

                if eth_disable_fail_flag > 0:
                    log.error("以太网下电失败次数为： %d次" % eth_disable_fail_flag)
                    # log.error("以太网下电失败的概率： %f" % (eth_disable_fail_flag / flag))

                if eth_enable_fail_flag > 0:
                    log.error("以太网上电失败次数为： %d次" % eth_enable_fail_flag)
                    # log.error("以太网上电失败的概率： %f" % (eth_enable_fail_flag / flag))

                if eth_enable_no_network_fail > 0:
                    log.error("以太网上电后上网失败次数为： %d次" % eth_enable_no_network_fail)
                    # log.error("以太网上电后上网失败的概率： %f" % (eth_enable_no_network_fail / flag))

                if wifi_boot_not_existent > 0:
                    log.error("WIFI启动前后状态不一致的次数为： %d次" % wifi_boot_not_existent)
                    # log.error("WIFI启动前后状态不一致的概率： %f" % (wifi_boot_not_existent / flag))

                if wifi_disable_fail_flag > 0:
                    log.error("WIFI下电失败次数为： %d次" % wifi_disable_fail_flag)
                    # log.error("WIFI下电失败的概率： %f" % (wifi_disable_fail_flag / flag))

                if wifi_enable_fail_flag > 0:
                    log.error("WIFI上电失败次数为： %d次" % wifi_enable_fail_flag)
                    # log.error("WIFI上电失败的概率： %f" % (wifi_enable_fail_flag / flag))

                if wifi_enable_no_network_fail > 0:
                    log.error("WIFI上电后上网失败次数为： %d次" % wifi_enable_no_network_fail)
                    # log.error("WIFI上电后上网失败的概率： %f" % (wifi_enable_no_network_fail / flag))

                if mobile_boot_not_existent > 0:
                    log.error("4G启动前后状态不一致的次数为： %d次" % mobile_boot_not_existent)
                    # log.error("4G启动前后状态不一致的概率： %f" % (mobile_boot_not_existent / flag))

                if mobile_disable_fail_flag > 0:
                    log.error("4G下电失败次数为： %d次" % mobile_disable_fail_flag)
                    # log.error("4G下电失败的概率： %f" % (mobile_disable_fail_flag / flag))

                if mobile_enable_fail_flag > 0:
                    log.error("4G上电失败次数为： %d次" % mobile_enable_fail_flag)
                    # log.error("4G上电失败的概率： %f" % (mobile_enable_fail_flag / flag))

                if mobile_no_network_fail > 0:
                    log.error("4G上电后上网失败次数为： %d次" % mobile_no_network_fail)
                    # log.error("4G上电后上网失败的概率： %f" % (mobile_no_network_fail / flag))
        except Exception as e:
            log.error(str(e))
            log.error("用例运行过程中有异常，请检查！！！")
            time.sleep(3)
            assert False
        log.info("****************立项测试-开关机检查基本功能用例结束******************")

    @allure.feature("front_rear_camera_stability")
    @allure.title("前后摄像头拍照问题对比")
    def test_lx_front_rear_camera_test(self):
        log.info("************前后摄像头拍照问题对比用例开始*******")
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

        # 亮屏

        if not self.device.is_screen_on():
            self.device.press_power_button()
            time.sleep(1)
        self.device.unlock()
        self.device.back_home()

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
        rounds_interval = int(self.ui_conf_file.get(Config.section_ui_camera_check, Config.test_interval))
        open_fail_flag = 0
        compare_fail_flag = 0
        photograph_fail_flag = 0
        continue_flag = 0
        times = 0

        while times <= int(total_times):
            try:
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
                    if front_preview_score < 0.9:
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
                    if front_photograph_score < 0.9:
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
                    if rear_preview_score < 0.9:
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
                    if rear_photograph_score < 0.9:
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
                            self.device.force_stop_camera_app()
                            self.device.clear_camera_app()
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
                            self.device.force_stop_camera_app()
                            self.device.clear_camera_app()
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
                    if default_preview_score < 0.9:
                        log.error("镜头预览画面预期和测试截图差异过大，请检查！！！")
                        if is_probability:
                            compare_fail_flag += 1
                            self.device.force_stop_camera_app()
                            self.device.clear_camera_app()
                            # 复制测试中异常的照片到Error文件夹地址
                            preview_file_name = os.path.basename(Config.camera_sta_test_default_preview_path)
                            preview_file_new_path = Config.camera_sta_err_default_preview_path
                            shutil.copy(Config.camera_sta_test_default_preview_path, preview_file_new_path)
                            os.rename(os.path.join(preview_file_new_path, preview_file_name),
                                      os.path.join(preview_file_new_path, "%d_%s" % (times, preview_file_name)))
                            # continue
                        else:
                            time.sleep(3)
                            self.device.kill_process(logcat_process_id)
                            self.device.adb_pull_file(log_path, os.path.dirname(Config.camera_sta_test_log_path))
                            raise
                    default_photograph_score = cnns.generateScore(Config.camera_sta_test_default_photograph_path,
                                                                  Config.camera_sta_exp_default_photograph_path)
                    log.info("镜头拍照预期和测试拍照相似度分数为：%s" % str(default_photograph_score))
                    if default_photograph_score < 0.9:
                        log.error("镜头拍照预期和测试拍照差异过大，请检查！！！")
                        if is_probability:
                            compare_fail_flag += 1
                            self.device.force_stop_camera_app()
                            self.device.clear_camera_app()
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
                self.device.force_stop_camera_app()
                self.device.clear_camera_app()
                if self.device.get_camera_id() != 3:
                    self.device.force_stop_camera_app()
                    self.device.clear_camera_app()
                log.info("关闭相机")
                # clear img
                self.device.remove_img()
                time.sleep(1)
                if len(self.device.get_latest_img()) != 0:
                    self.device.remove_img()
                times += 1

                # if int(is_double):
                #     if os.path.exists(Config.camera_sta_test_front_preview_path):
                #         os.remove(Config.camera_sta_test_front_preview_path)
                #     if os.path.exists(Config.camera_sta_test_front_photograph_path):
                #         os.remove(Config.camera_sta_test_front_photograph_path)
                #     if os.path.exists(Config.camera_sta_test_rear_photograph_path):
                #         os.remove(Config.camera_sta_test_rear_photograph_path)
                #     if os.path.exists(Config.camera_sta_test_rear_preview_path):
                #         os.remove(Config.camera_sta_test_rear_preview_path)
                # else:
                #     if os.path.exists(Config.camera_sta_test_default_preview_path):
                #         os.remove(Config.camera_sta_test_default_preview_path)
                #     if os.path.exists(Config.camera_sta_test_default_photograph_path):
                #         os.remove(Config.camera_sta_test_default_photograph_path)
                log.info("******相机压测完成%d次*****" % times)
                time.sleep(rounds_interval)
            except Exception as e:
                log.error(str(e))

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
            self.device.enable_bt_btn()
            time.sleep(3)
            if not self.device.bt_is_enable():
                log.error("设备蓝牙无法打开，请检查！！！")
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
            time.sleep(10)
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
            time.sleep(10)
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
            time.sleep(10)
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
            time.sleep(10)
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

    @allure.feature("touch_event_stability")
    @allure.title("触摸事件稳定性测试")
    def test_touch_stability(self):
        try:
            log.info("***********触摸事件稳定性测试开始************")
            device_name = self.ui_conf_file.get(Config.section_ui_to_background, Config.ui_option_device_name)
            test_times = int(self.ui_conf_file.get(Config.section_touch, Config.option_touch_test_times))
            is_probability = int(self.ui_conf_file.get(Config.section_touch, Config.is_probability_test))
            test_interval = int(self.ui_conf_file.get(Config.section_touch, Config.test_interval))

            times = 0
            fail_flag = 0
            while times < test_times:
                times += 1
                self.device.reboot()
                self.device.restart_adb()

                # 检测设备90s内 adb是否在线
                now_time = time.time()
                while True:
                    if time.time() > now_time + 90:
                        log.error("设备无法重启，请检查!!!")
                        time.sleep(3)
                        raise
                    if self.device.device_is_online():
                        log.info("adb 在线")
                        break

                # 检查设备是否完全启动
                boot_time = time.time()
                while True:
                    if time.time() > boot_time + 120:
                        log.error("设备无法完全启动，请检查!!!")
                        time.sleep(3)
                        raise
                    if self.device.device_boot():
                        log.info("设备完全启动")
                        break

                # 先适配收银机，手持后续适配
                event_info = con_shell.invoke("adb -s %s shell getevent -lt" % device_name, timeout=5)
                log.info("获取触摸事件信息：+ \n %s" % event_info)
                if " EV_ABS" not in event_info and "EV_SYN" not in event_info:
                    fail_flag += 1
                    if is_probability:
                        log.error("触摸无响应，请检查!!!")
                        continue
                    log.error("触摸无响应，请检查!!!")
                    log.info("触摸事件成功次数为：%d" % (times - fail_flag))
                    log.info("触摸事件失败次数为：%d" % (fail_flag))
                    time.sleep(3)
                    break
                else:
                    log.info("触摸正常响应")
                log.info("***********第%d次触摸事件测试结束************" % times)
                time.sleep(test_interval)
            log.info("***********触摸事件稳定性测试结束************")
            if is_probability:
                if fail_flag > 0:
                    log.error("触摸无响应的次数为：%d" % fail_flag)
                    log.error("触摸无响应的概率为：%f" % (fail_flag / test_times))

            log.info("触摸事件成功次数为：%d" % (test_times - fail_flag))

        except Exception as e:
            log.error(str(e))
            log.error("触摸事件测试过程中有异常，请检查!!!")
            time.sleep(3)
            assert False
