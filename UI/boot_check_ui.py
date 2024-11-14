import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit, QLabel, QScrollArea
from PyQt5.QtCore import pyqtSlot, QProcess
import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
import os
import shutil
from PyQt5.QtGui import QPixmap
import serial.tools.list_ports
from PIL import Image
import rembg
from PyQt5.QtCore import QUrl, QFileInfo
import configparser
import time
from configfile import ConfigP
import config_path

conf_path = config_path.UIConfigPath()


class Boot_Check_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # 创建水平布局
        self.main_layout = QHBoxLayout(self.centralwidget)

        # 创建 QSplitter 控件，分割两个子窗口
        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        # 左侧所有部件
        left_widget = QWidget()
        self.verticalLayout_left = QtWidgets.QVBoxLayout(left_widget)

        # 配置滚动条
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.verticalLayout_left.addWidget(QLabel("开关机配置："))
        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        layout_device_info = QHBoxLayout()

        self.label_device_name = QtWidgets.QLabel("设备名称:")
        self.edit_device_name = QComboBox()

        # 测试COM
        self.COM_tips = QLabel("测试COM口:")
        self.test_COM = QComboBox()
        # adb log 时长
        self.adb_log_lable = QLabel("Logcat时长(min):")
        self.adb_log_duration = QComboBox()

        layout_device_info.addWidget(self.label_device_name)
        layout_device_info.addWidget(self.edit_device_name)
        layout_device_info.addWidget(self.COM_tips)
        layout_device_info.addWidget(self.test_COM)
        layout_device_info.addWidget(self.adb_log_lable)
        layout_device_info.addWidget(self.adb_log_duration)
        layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_info)
        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        layout_device_control = QHBoxLayout()
        self.boot_way = QLabel("接线方式:")
        self.is_adapter = QCheckBox("适配器/电池")
        self.is_power_button = QCheckBox("电源按键")
        self.is_usb = QCheckBox("Type-c/mico-usb")
        self.usb_tips = QLabel("usb接继电器仅限900P")
        self.usb_tips.setStyleSheet("color: blue;")

        layout_device_control.addWidget(self.boot_way)
        layout_device_control.addWidget(self.is_adapter)
        layout_device_control.addWidget(self.is_power_button)
        layout_device_control.addWidget(self.is_usb)
        layout_device_control.addWidget(self.usb_tips)
        layout_device_control.addStretch(1)
        # 将水平布局放入垂直布局
        self.verticalLayout_left.addLayout(layout_device_control)
        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        layout_COM_config = QHBoxLayout()
        self.config_label = QLabel("接线配置:")
        self.adapter_label = QLabel("适配器/电池:")
        self.adapter_config = QComboBox()
        self.adapter_config.setDisabled(True)
        layout_COM_config.addWidget(self.config_label)
        layout_COM_config.addWidget(self.adapter_label)
        layout_COM_config.addWidget(self.adapter_config)

        self.power_button_label = QLabel("电源按键:")
        self.power_button_config = QComboBox()
        self.power_button_config.setDisabled(True)
        layout_COM_config.addWidget(self.power_button_label)
        layout_COM_config.addWidget(self.power_button_config)

        self.usb_label = QLabel("USB:")
        self.usb_config = QComboBox()
        self.usb_config.setDisabled(True)
        self.config_tips = QLabel("接线提示:电源按键接常开端(COM,N0）,其他接常闭端(COM,NC)")
        self.config_tips.setStyleSheet("color: blue;")
        layout_COM_config.addWidget(self.usb_label)
        layout_COM_config.addWidget(self.usb_config)
        layout_COM_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_COM_config)
        self.verticalLayout_left.addWidget(self.config_tips)
        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        other_layout_device_info = QHBoxLayout()
        self.other_device_info = QLabel("其他配置:")
        # 只测开关机，不拍照
        self.only_boot = QCheckBox("只开关机")

        self.double_screen = QCheckBox("双屏")
        # 按键开机时长
        self.button_boot_lable = QLabel("按键开机时长(sec):")
        self.button_boot_time = QComboBox()
        self.button_boot_time.setDisabled(True)
        other_layout_device_info.addWidget(self.other_device_info)
        other_layout_device_info.addWidget(self.only_boot)
        other_layout_device_info.addWidget(self.double_screen)
        other_layout_device_info.addWidget(self.button_boot_lable)
        other_layout_device_info.addWidget(self.button_boot_time)
        other_layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(other_layout_device_info)
        self.button_boot_tips = QLabel("提示：“只测开关机”不进行图片拍照对比，只查看adb是否起来")
        self.button_boot_tips.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(self.button_boot_tips)

        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        # 开关机场景选择
        self.verticalLayout_left.addWidget(QLabel("开关机模式："))
        layout_boot_scenario = QHBoxLayout()
        self.adapter_boot = QCheckBox("适配器开关机")
        self.normal_boot = QCheckBox("适配器/电池+电源按键-正常关机")
        self.abnormal_boot = QCheckBox("适配器/电池+电源按键-异常关机")
        layout_boot_scenario.addWidget(self.adapter_boot)
        layout_boot_scenario.addWidget(self.normal_boot)
        layout_boot_scenario.addWidget(self.abnormal_boot)
        layout_boot_scenario.addStretch(1)
        self.scenario_group = QButtonGroup()
        self.scenario_group.addButton(self.adapter_boot, id=1)
        self.scenario_group.addButton(self.normal_boot, id=2)
        self.scenario_group.addButton(self.abnormal_boot, id=3)
        self.scenario_group.setExclusive(True)
        self.verticalLayout_left.addLayout(layout_boot_scenario)

        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        # 上传图片
        # self.reboot_logo_info = QLabel("上传设备开机后第一个画面的照片：")
        # self.verticalLayout_left.addWidget(self.reboot_logo_info)
        # layout_upload_logo = QHBoxLayout()
        # self.logo_path_edit = QtWidgets.QLineEdit()
        # layout_upload_logo.addWidget(self.logo_path_edit)
        # self.logo_upload_button = QtWidgets.QPushButton("点击上传")
        # layout_upload_logo.addWidget(self.logo_upload_button)
        # self.verticalLayout_left.addLayout(layout_upload_logo)

        # 创建 QLabel 用于显示照片
        # 显示图片
        # self.show_keying_button = QtWidgets.QPushButton("显示抠图")
        # self.verticalLayout_left.addWidget(self.show_keying_button)

        # 点击获取预期照片
        layout_get_image_info = QHBoxLayout()
        self.get_logo_image_button = QPushButton("点击获取预期照片")
        self.logo_image_tips = QLabel("未保存预期照片，请点击获取！")
        self.logo_image_tips.setStyleSheet("color: blue;")
        layout_get_image_info.addWidget(self.get_logo_image_button)
        layout_get_image_info.addWidget(self.logo_image_tips)
        self.verticalLayout_left.addLayout(layout_get_image_info)

        self.exp_image_label = QLabel()
        self.exp_image_label.setScaledContents(True)
        self.verticalLayout_left.addWidget(self.exp_image_label)

        self.test_image_label = QLabel()
        self.test_image_label.setScaledContents(True)
        self.verticalLayout_left.addWidget(self.test_image_label)
        self.verticalLayout_left.setSpacing(10)

        self.verticalLayout_left.addWidget(QLabel())
        # 设备信息配置
        layout_device_config = QHBoxLayout()
        self.device_config_info = QLabel("设备信息：")
        self.is_wifi_test = QCheckBox("wifi")
        self.is_eth_test = QCheckBox("以太网")
        self.is_mobile_test = QCheckBox("4G")
        self.is_bt_test = QCheckBox("蓝牙")
        self.is_nfc_test = QCheckBox("NFC")
        self.is_usb_test = QCheckBox("U盘")
        self.device_config_tips = QLabel("有些设备开启ADB不支持U盘")
        self.device_config_tips.setStyleSheet("color: blue;")
        layout_device_config.addWidget(self.device_config_info)
        layout_device_config.addWidget(self.is_wifi_test)
        layout_device_config.addWidget(self.is_eth_test)
        layout_device_config.addWidget(self.is_mobile_test)
        layout_device_config.addWidget(self.is_bt_test)
        layout_device_config.addWidget(self.is_nfc_test)
        layout_device_config.addWidget(self.is_usb_test)
        layout_device_config.addWidget(self.device_config_tips)
        layout_device_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_config)
        config_tips1 = QLabel("提示：测试时请根据勾选的测试项打开并且连接上wifi、打开连接上以太网，插入4G卡")
        config_tips1.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(config_tips1)
        config_tips2 = QLabel("      打开蓝牙并且连接上仅一台设备、打开NFC、插上U盘")
        config_tips2.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(config_tips2)

        self.verticalLayout_left.addWidget(QLabel())

        layout_device_type = QHBoxLayout()
        self.device_type_label = QLabel("设备分类：")
        self.is_team_one = QCheckBox("一部")
        self.is_team_two = QCheckBox("二部")
        self.device_type_group = QButtonGroup()
        self.device_type_group.addButton(self.is_team_one, id=1)
        self.device_type_group.addButton(self.is_team_two, id=2)
        layout_device_type.addWidget(self.device_type_label)
        layout_device_type.addWidget(self.is_team_one)
        layout_device_type.addWidget(self.is_team_two)
        layout_device_type.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_type)

        self.verticalLayout_left.addWidget(QLabel())

        self.usb_label = QtWidgets.QLabel("请输入U盘的路径，例如 mnt/media/E168、/storage/9b18-9E")
        self.verticalLayout_left.addWidget(self.usb_label)
        layout_usb_flash_info = QHBoxLayout()
        self.check_usb_flash_button = QtWidgets.QPushButton("查询U盘挂载的路径")
        self.usb_flash_path = QtWidgets.QLineEdit()
        self.check_usb_flash_button.setDisabled(True)
        self.usb_flash_path.setDisabled(True)
        layout_usb_flash_info.addWidget(self.check_usb_flash_button)
        layout_usb_flash_info.addWidget(self.usb_flash_path)
        self.verticalLayout_left.addLayout(layout_usb_flash_info)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 压测次数
        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QLabel("用例压测次数设置")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)
        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)
        layout_test_times_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info)

        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("保存配置")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())
        self.verticalLayout_left.addWidget(QtWidgets.QLabel("日志信息:"))

        # 展示log
        self.text_edit = ScrollablePlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.verticalLayout_left.addWidget(self.text_edit)

        self.verticalLayout_left.addStretch(1)
        self.verticalLayout_left.setSpacing(10)  # 设置左侧垂直布局的间距为10像素

        scroll_area.setWidget(left_widget)

        splitter.addWidget(scroll_area)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "开关机基本功能检查配置"))


"""
添加关掉窗口检查保存配置是否成功/是否有进行配置保存
"""


class BootCheckDisplay(QtWidgets.QMainWindow, Boot_Check_MainWindow):
    def __init__(self):
        super(BootCheckDisplay, self).__init__()
        self.bg_config = ConfigP(self.background_config_file_path)
        self.ui_config = ConfigP(self.ui_config_file_path)
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        # 初始化进程
        self.get_exp_logo_process = QProcess()
        self.usb_process = QProcess()
        self.select_devices_name()
        self.list_COM()
        self.list_logcat_duration()
        self.list_test_times_settings()
        self.is_adapter.clicked.connect(self.adapter_checkbox_change)
        self.is_power_button.clicked.connect(self.power_button_checkbox_change)
        self.is_usb.clicked.connect(self.usb_checkbox_change)
        # self.logo_upload_button.clicked.connect(self.upload_reboot_logo)
        # self.show_keying_button.clicked.connect(self.show_keying_image)
        self.submit_button.clicked.connect(self.handle_submit)
        # 进程完成
        self.only_boot.clicked.connect(self.only_boot_checkbox_change)
        self.is_usb_test.clicked.connect(self.enable_usb_ui)
        self.check_usb_flash_button.clicked.connect(self.query_usb_flash_path)
        self.usb_process.finished.connect(self.query_usb_boot_finished_handle)
        self.get_logo_image_button.clicked.connect(self.get_logo_image_button_change)

    def get_logo_image_button_change(self):
        self.ui_config.add_config_option(self.ui_config.section_ui_boot_check, self.ui_config.ui_option_device_name, self.edit_device_name.currentText())
        if os.path.exists(conf_path.logo_expect_screen0_path):
            os.remove(conf_path.logo_expect_screen0_path)
        if self.double_screen.isChecked():
            if os.path.exists(conf_path.logo_expect_screen1_path):
                os.remove(conf_path.logo_expect_screen1_path)

        # 调起来进程， 获取预期照片
        self.get_exp_logo_process.start(self.bat_logo_stability_path)
        self.phot_tips.setText("正在拍照保存，请等待...")
        self.logo_image_tips.setStyleSheet("color: green;")
        # self.document.clear()
        # self.file_timer = QTimer(self)
        # self.file_timer.timeout.connect(self.check_image_modification)
        # self.check_interval = 2000  # 定时器间隔，单位毫秒

        # self.file_timer.start(self.check_interval)

    def query_usb_boot_finished_handle(self):
        with open(conf_path.usb_boot_log_path, "r") as f:
            text = f.read()
        if len(text) != 0:
            self.text_edit.insertPlainText(text)
        else:
            self.text_edit.insertPlainText("读取可用运行内存数据失败， 请检查！！！")
        self.text_edit.insertPlainText("查询结束.")

    def query_usb_flash_path(self):
        # 保存root steps
        # self.double_check_root()
        self.ui_config.add_config_option(self.ui_config.section_ui_boot_check, self.ui_config.ui_option_device_name,
                                         self.edit_device_name.currentText())
        self.usb_process.start(conf_path.bat_boot_query_flash_path)

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        # 先删除原来存在的key图片
        if os.path.exists(self.camera_key_path):
            os.remove(self.camera_key_path)
        if os.path.exists(self.camera2_key_path):
            os.remove(self.camera2_key_path)

        if len(self.test_COM.currentText()) == 0:
            self.get_message_box("没检测到可用的串口，请检查或者重启界面！！！")
            return

        if not self.is_adapter.isChecked() and not self.is_power_button.isChecked() and not self.is_usb.isChecked():
            self.get_message_box("请选择接线方式！！！")
            return

        # 继电器路数不能相同
        config_list = []
        if self.adapter_config.isEnabled():
            config_list.append(self.adapter_config.currentText())
        if self.power_button_config.isEnabled():
            config_list.append(self.power_button_config.currentText())
        if self.usb_config.isEnabled():
            config_list.append(self.usb_config.currentText())
        if len(config_list) != len(set(config_list)):
            self.get_message_box("接线配置有相同，请检查！！！")
            return
        # 如果只测开关机，不进行图片比对
        if not self.only_boot.isChecked():
            if len(self.logo_path_edit.text()) == 0:
                self.get_message_box("请上传开机logo！！！")
                return
            # # 检查文件是否存在
            reboot_logo_path = self.logo_path_edit.text().strip()
            if not os.path.exists(reboot_logo_path):
                self.get_message_box("文件路径：%s不存在" % reboot_logo_path)
                return

        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请设置压测次数")
            return

        if not self.adapter_boot.isChecked() and not self.normal_boot.isChecked() and not self.abnormal_boot.isChecked():
            self.get_message_box("请选择开关机模式！！！")
            return

        # 检查是否抠图了
        if not os.path.exists(self.logo_key_path):
            self.get_message_box("请抠图检查图片是否完整！！！")
            return

        if not self.is_wifi_test.isChecked() and not self.is_eth_test.isChecked() and not self.is_mobile_test.isChecked() and not self.is_bt_test.isChecked() and not self.is_nfc_test.isChecked() and not self.is_usb_test.isChecked():
            self.get_message_box("请勾选设备信息！！！")
            return

        if not self.is_team_one.isChecked() and not self.is_team_two.isChecked():
            self.get_message_box("请勾选设备分类！！！")
            return

        if self.is_usb_test.isChecked():
            if len(self.usb_flash_path.text()) == 0:
                self.get_message_box("请填入U盘挂载的路径")
                return

        # 检查完保存配置
        self.save_config()
        self.submit_flag = True
        self.get_message_box("开机卡logo用例配置保存成功")
        # 每次提交先删除失败的照片，避免检错误
        if os.path.exists(self.failed_image_key_path):
            os.remove(self.failed_image_key_path)

    def enable_usb_ui(self):
        if self.is_usb_test.isChecked():
            self.check_usb_flash_button.setEnabled(True)
            self.usb_flash_path.setEnabled(True)
        else:
            self.check_usb_flash_button.setDisabled(True)
            self.usb_flash_path.setDisabled(True)

    def list_test_times_settings(self):
        times = [str(j * 50) for j in range(1, 500)]
        self.test_times.addItems(times)

    def only_boot_checkbox_change(self):
        if self.only_boot.isChecked():
            self.double_screen.setDisabled(True)
            self.logo_upload_button.setDisabled(True)
            self.show_keying_button.setDisabled(True)
        else:
            self.double_screen.setEnabled(True)
            self.logo_upload_button.setEnabled(True)
            self.show_keying_button.setEnabled(True)

    def adapter_checkbox_change(self):
        if self.adapter_config.isEnabled():
            self.adapter_config.setDisabled(True)
            self.adapter_config.clear()
        else:
            self.adapter_config.setEnabled(True)
            for line in self.get_COM_config():
                self.adapter_config.addItem(line)

    def power_button_checkbox_change(self):
        if self.power_button_config.isEnabled():
            self.power_button_config.setDisabled(True)
            self.power_button_config.clear()
            # 不显示开机时长
            self.button_boot_time.setDisabled(True)
            self.button_boot_time.clear()
        else:
            self.power_button_config.setEnabled(True)
            for line in self.get_COM_config():
                self.power_button_config.addItem(line)
            # 显示开机时长
            self.button_boot_time.setEnabled(True)
            for duration in [3, 5, 7, 10]:
                self.button_boot_time.addItem(str(duration))

    def usb_checkbox_change(self):
        if self.usb_config.isEnabled():
            self.usb_config.setDisabled(True)
            self.usb_config.clear()
        else:
            self.usb_config.setEnabled(True)
            for line in self.get_COM_config():
                self.usb_config.addItem(line)

    def select_devices_name(self):
        devices = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                  self.bg_config.bg_option_devices_name).split(",")
        for device in devices:
            self.edit_device_name.addItem(str(device))

    def get_COM_config(self):
        return ["1路", "2路", "3路", "4路"]

    def save_config(self):
        config = self.ui_config
        section = config.section_ui_boot_check
        config.add_config_section(section)

        config.add_config_option(section, "COM", self.test_COM.currentText())
        config.add_config_option(section, "logcat_duration", self.adb_log_duration.currentText())

        # 接线方式
        if self.is_adapter.isChecked():
            config.add_config_option(section, "is_adapter", "1")
        else:
            config.add_config_option(section, "is_adapter", "0")
        if self.is_power_button.isChecked():
            config.add_config_option(section, "is_power_button", "1")
        else:
            config.add_config_option(section, "is_power_button", "0")
        if self.is_usb.isChecked():
            config.add_config_option(section, "is_usb", "1")
        else:
            config.add_config_option(section, "is_usb", "0")

        # 接线配置
        if self.adapter_config.isEnabled():
            if self.adapter_config.currentText() == "1路":
                config.add_config_option(section, "adapter_power_config", "relay_1")
            elif self.adapter_config.currentText() == "2路":
                config.add_config_option(section, "adapter_power_config", "relay_2")
            elif self.adapter_config.currentText() == "3路":
                config.add_config_option(section, "adapter_power_config", "relay_3")
            else:
                config.add_config_option(section, "adapter_power_config", "relay_4")

        if self.power_button_config.isEnabled():
            if self.power_button_config.currentText() == "1路":
                config.add_config_option(section, "power_button_config", "relay_1")
            elif self.power_button_config.currentText() == "2路":
                config.add_config_option(section, "power_button_config", "relay_2")
            elif self.power_button_config.currentText() == "3路":
                config.add_config_option(section, "power_button_config", "relay_3")
            else:
                config.add_config_option(section, "power_button_config", "relay_4")

        if self.usb_config.isEnabled():
            if self.usb_config.currentText() == "1路":
                config.add_config_option(section, "usb_config", "relay_1")
            elif self.usb_config.currentText() == "2路":
                config.add_config_option(section, "usb_config", "relay_2")
            elif self.usb_config.currentText() == "3路":
                config.add_config_option(section, "usb_config", "relay_3")
            else:
                config.add_config_option(section, "usb_config", "relay_4")

        # 其他配置信息
        if self.only_boot.isChecked():
            config.add_config_option(section, "only_boot_config", "1")
        else:
            config.add_config_option(section, "only_boot_config", "0")

        if self.double_screen.isChecked():
            config.add_config_option(section, "double_screen_config", "1")
        else:
            config.add_config_option(section, "double_screen_config", "0")

        # 保存U盘挂载的路径
        config.add_config_option(section, config.ui_option_boot_usb_path, self.usb_flash_path.text().strip())

        if self.button_boot_time.isEnabled():
            config.add_config_option(section, "button_boot_time", self.button_boot_time.currentText())

        if self.adapter_boot.isChecked():
            config.add_config_option(section, config.ui_option_logo_cases, "1")
        elif self.normal_boot.isChecked():
            config.add_config_option(section, config.ui_option_logo_cases, "2")
        elif self.abnormal_boot.isChecked():
            config.add_config_option(section, config.ui_option_logo_cases, "3")

        # 保存用例压测次数设置
        config.add_config_option(section, "logo_test_times", self.test_times.currentText())
        # 保存测试点配置信息
        if self.is_wifi_test.isChecked():
            config.add_config_option(section, config.option_wifi_test, "1")
        else:
            config.add_config_option(section, config.option_wifi_test, "0")

        if self.is_eth_test.isChecked():
            config.add_config_option(section, config.option_eth_test, "1")
        else:
            config.add_config_option(section, config.option_eth_test, "0")

        if self.is_mobile_test.isChecked():
            config.add_config_option(section, config.option_mobile_test, "1")
        else:
            config.add_config_option(section, config.option_mobile_test, "0")

        if self.is_bt_test.isChecked():
            config.add_config_option(section, config.option_bt_test, "1")
        else:
            config.add_config_option(section, config.option_bt_test, "0")

        if self.is_nfc_test.isChecked():
            config.add_config_option(section, config.option_nfc_test, '1')
        else:
            config.add_config_option(section, config.option_nfc_test, "0")

        if self.is_usb_test.isChecked():
            config.add_config_option(section, config.option_usb_test, "1")
        else:
            config.add_config_option(section, config.option_usb_test, "0")

    def copy_file(self, origin, des):
        shutil.copy(origin, des)

    def rename_file(self, origin, des):
        shutil.move(origin, des)

    def remove_file(self, path):
        if os.path.isfile(path):
            os.remove(path)

    def path_is_existed(self, path):
        if os.path.exists(path):
            return True
        else:
            return False

    def upload_reboot_logo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Images (*.png *.jpg *.jpeg)')
        if file_name:
            self.logo_path_edit.setText(file_name)

    def list_COM(self):
        ports = self.get_current_COM()
        for port in ports:
            self.test_COM.addItem(port)

    def get_current_COM(self):
        base_config = ConfigP(self.background_config_file_path)
        COM_list = base_config.get_option_value(base_config.section_background_to_ui, base_config.bg_option_COM_ports)
        return COM_list.split(",")

    def list_logcat_duration(self):
        duration = [10, 20, 30, 40, 50, 60]
        for dur in duration:
            self.adb_log_duration.addItem(str(dur))
        self.adb_log_duration.setCurrentText("30")

    def show_keying_image(self):
        if len(self.logo_path_edit.text()) == 0:
            self.get_message_box("请上传logo！！！")
            return
        self.key_photo()
        pixmap = QPixmap(self.logo_key_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(439, 230)
            self.exp_image_label.setPixmap(scaled_pixmap)

    def key_photo(self):
        original_path = self.logo_path_edit.text().strip()
        self.save_key_photo(original_path, self.logo_key_path)

    def save_key_photo(self, orig_path, new_path):
        img = Image.open(orig_path)
        img_bg_remove = rembg.remove(img)
        img_bg_remove.save(new_path)

    def show_failed_image(self):
        pixmap = QPixmap(self.failed_image_key_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(429, 311)
            self.test_image_label.setPixmap(scaled_pixmap)


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        self.verticalScrollBar().setValue(max)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logo_show = BootCheckDisplay()
    logo_show.show()
    app.exec_()
