import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot, QProcess
import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
import os
import shutil
from PyQt5.QtGui import QPixmap, QTextImageFormat, QTextDocument, QTextCursor
import serial.tools.list_ports
from PIL import Image
from PyQt5.QtCore import QUrl, QFileInfo
import configparser
import time
from configfile import ConfigP
import config_path

conf_path = config_path.UIConfigPath()


class Reboot_Logo_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # 创建水平布局
        self.main_layout = QHBoxLayout(self.centralwidget)

        # 创建 QSplitter 控件，分割两个子窗口
        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        # 左侧所有部件
        left_widget = QWidget()
        self.verticalLayout_left = QtWidgets.QVBoxLayout(left_widget)

        layout_device_info = QHBoxLayout()

        self.label_device_name = QtWidgets.QLabel("设备名称:")
        self.edit_device_name = QComboBox()

        # 测试COM
        self.COM_tips = QtWidgets.QLabel("测试COM口:")
        self.test_COM = QComboBox()
        # adb log 时长
        self.adb_log_lable = QtWidgets.QLabel("Logcat时长(min):")
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
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        layout_device_control = QHBoxLayout()
        self.boot_way = QtWidgets.QLabel("接线方式:")
        self.is_adapter = QCheckBox("适配器/电池")
        self.is_power_button = QCheckBox("电源按键")
        self.is_usb = QCheckBox("Type-c/mico-usb")
        self.usb_tips = QtWidgets.QLabel("usb接继电器仅限900P")
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
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        layout_COM_config = QHBoxLayout()
        self.ui_config_label = QtWidgets.QLabel("接线配置:")
        self.adapter_label = QtWidgets.QLabel("适配器/电池:")
        self.adapter_config = QComboBox()
        self.adapter_config.setDisabled(True)
        layout_COM_config.addWidget(self.ui_config_label)
        layout_COM_config.addWidget(self.adapter_label)
        layout_COM_config.addWidget(self.adapter_config)

        self.power_button_label = QtWidgets.QLabel("电源按键:")
        self.power_button_config = QComboBox()
        self.power_button_config.setDisabled(True)
        layout_COM_config.addWidget(self.power_button_label)
        layout_COM_config.addWidget(self.power_button_config)

        self.usb_label = QtWidgets.QLabel("USB:")
        self.usb_config = QComboBox()
        self.usb_config.setDisabled(True)
        self.ui_config_tips = QtWidgets.QLabel("接线提示:电源按键接常开端(COM,N0）,其他接常闭端(COM,NC)")
        self.ui_config_tips.setStyleSheet("color: blue;")
        layout_COM_config.addWidget(self.usb_label)
        layout_COM_config.addWidget(self.usb_config)
        layout_COM_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_COM_config)
        self.verticalLayout_left.addWidget(self.ui_config_tips)
        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        other_layout_device_info = QHBoxLayout()
        self.other_device_info = QtWidgets.QLabel("其他配置:")
        # 只测开关机，不拍照
        self.only_boot = QCheckBox("只开关机")

        self.double_screen = QCheckBox("双屏")
        # 按键开机时长
        self.button_boot_lable = QtWidgets.QLabel("按键开机时长(sec):")
        self.button_boot_time = QComboBox()
        self.button_boot_time.setDisabled(True)

        self.relay_reboot_label = QLabel("关机、开机之间的间隔(秒):")
        self.relay_reboot_duration = QComboBox()
        self.relay_reboot_duration.setEditable(True)

        other_layout_device_info.addWidget(self.other_device_info)
        other_layout_device_info.addWidget(self.only_boot)
        other_layout_device_info.addWidget(self.double_screen)
        other_layout_device_info.addWidget(self.button_boot_lable)
        other_layout_device_info.addWidget(self.button_boot_time)
        other_layout_device_info.addWidget(self.relay_reboot_label)
        other_layout_device_info.addWidget(self.relay_reboot_duration)
        other_layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(other_layout_device_info)
        self.button_boot_tips = QtWidgets.QLabel("提示：“只测开关机”不进行图片拍照对比，只查看adb是否起来")
        self.button_boot_tips.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(self.button_boot_tips)

        # 点击获取预期照片
        layout_get_image_info = QHBoxLayout()
        self.get_logo_image_button = QPushButton("点击获取预期照片")
        self.logo_image_tips = QLabel("未保存预期照片，请点击获取！")
        self.logo_image_tips.setStyleSheet("color: blue;")
        layout_get_image_info.addWidget(self.get_logo_image_button)
        layout_get_image_info.addWidget(self.logo_image_tips)
        self.verticalLayout_left.addLayout(layout_get_image_info)

        self.image_edit = ScrollablePlainTextEdit()
        self.image_edit.setFixedHeight(300)
        width = self.image_edit.viewport().width()
        height = self.image_edit.viewport().height()
        self.image_width = width
        self.image_height = 500
        # self.image_width = width
        # self.image_height = height
        self.document = self.image_edit.document()
        self.verticalLayout_left.addWidget(self.image_edit)

        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 压测次数
        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QtWidgets.QLabel("用例压测次数设置")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)

        # 是否测概率测试
        probability_test_label = QLabel("是否进行失败概率性统计")
        self.is_probability_test = QCheckBox()

        self.interval_lable = QLabel("每一轮的间隔时间(秒)：")
        self.interval = QComboBox()
        self.interval.setEditable(True)

        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)
        layout_test_times_info.addWidget(probability_test_label)
        layout_test_times_info.addWidget(self.is_probability_test)
        layout_test_times_info.addWidget(self.interval_lable)
        layout_test_times_info.addWidget(self.interval)
        layout_test_times_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info)

        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("保存配置")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.verticalLayout_left.addStretch(1)
        self.verticalLayout_left.setSpacing(10)  # 设置左侧垂直布局的间距为10像素

        splitter.addWidget(left_widget)

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
        MainWindow.setWindowTitle(_translate("MainWindow", "开关机卡logo相关用例参数配置"))


"""
添加关掉窗口检查保存配置是否成功/是否有进行配置保存
"""


class LogoDisplay(QtWidgets.QMainWindow, Reboot_Logo_MainWindow):
    def __init__(self):
        super(LogoDisplay, self).__init__()
        self.bg_config = ConfigP(self.background_config_file_path)
        self.ui_config = ConfigP(self.ui_config_file_path)
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        # 初始化进程
        self.get_exp_logo_process = QProcess()
        self.list_relay_reboot_interval_duration()
        self.list_interval_duration()
        self.list_COM()
        self.select_devices_name()
        self.list_logcat_duration()
        self.list_test_times_settings()
        self.is_adapter.clicked.connect(self.adapter_checkbox_change)
        self.is_power_button.clicked.connect(self.power_button_checkbox_change)
        self.is_usb.clicked.connect(self.usb_checkbox_change)
        self.submit_button.clicked.connect(self.handle_submit)
        # 进程完成
        self.only_boot.clicked.connect(self.only_boot_checkbox_change)
        self.get_exp_logo_process.finished.connect(self.get_logo_finished_handle)
        self.get_logo_image_button.clicked.connect(self.get_logo_image_button_change)

        # 初始化图片cursor
        self.cursor = QTextCursor(self.document)

    def list_interval_duration(self):
        times = [str(j * 60) for j in range(1, 200)]
        self.interval.addItems(times)

    def list_relay_reboot_interval_duration(self):
        times = [str(j * 5) for j in range(1, 200)]
        self.relay_reboot_duration.addItems(times)

    def get_logo_image_button_change(self):
        if self.double_screen.isChecked():
            self.ui_config.add_config_option(self.ui_config.section_ui_logo, self.ui_config.option_logo_double_screen,
                                             "1")
        else:
            self.ui_config.add_config_option(self.ui_config.section_ui_logo, self.ui_config.option_logo_double_screen,
                                             "0")
        self.ui_config.add_config_option(self.ui_config.section_ui_logo, self.ui_config.ui_option_device_name,
                                         self.edit_device_name.currentText())
        if os.path.exists(conf_path.logo_expect_screen0_path):
            os.remove(conf_path.logo_expect_screen0_path)
        if self.double_screen.isChecked():
            if os.path.exists(conf_path.logo_expect_screen1_path):
                os.remove(conf_path.logo_expect_screen1_path)
        # 调起来进程， 获取预期照片
        self.get_exp_logo_process.start(self.bat_logo_wh_stability_path)
        self.logo_image_tips.setText("正在拍照保存，请等待...")
        self.logo_image_tips.setStyleSheet("color: green;")
        self.document.clear()

    def add_logo_image(self, img_path):
        image_format = QTextImageFormat()
        image_url = QUrl.fromLocalFile(img_path)
        # 添加图片资源到 QTextDocument
        self.document.addResource(QTextDocument.ImageResource, image_url, image_url)
        # 设置图片格式的 ID
        image_format.setName(image_url.toString())
        # 设置图片的大小
        image_format.setWidth(200)
        image_format.setHeight(200)
        # # 插入图片到 QTextDocument
        self.cursor.insertImage(image_format)

    def get_logo_finished_handle(self):
        # self.file_timer.stop()
        if self.double_screen.isChecked():
            if os.path.exists(self.logo_expect_screen0_path) and os.path.exists(self.logo_expect_screen1_path):
                self.logo_image_tips.setText("已经获取到预期参照图片！")
                self.logo_image_tips.setStyleSheet("color: read;")
                self.add_logo_image(self.logo_expect_screen0_path)
                self.add_logo_image(self.logo_expect_screen1_path)
            else:
                self.logo_image_tips.setText("未获取到预期参照照片！！！")
                self.logo_image_tips.setStyleSheet("color: gray;")
        else:
            if os.path.exists(self.logo_expect_screen0_path):
                self.logo_image_tips.setText("已经获取到预期参照图片！")
                self.logo_image_tips.setStyleSheet("color: read;")
                self.add_logo_image(self.logo_expect_screen0_path)
            else:
                self.logo_image_tips.setText("未获取到预期参照照片！！！")
                self.logo_image_tips.setStyleSheet("color: gray;")

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
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

        if len(self.relay_reboot_duration.currentText()) == 0:
            self.get_message_box("请输入开机关机之间的间隔！！！")
            return

        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请设置压测次数")
            return

        if len(self.interval.currentText()) == 0:
            self.get_message_box("请输入每一轮之间的间隔时间！！！")
            return

        # 检查完保存配置
        self.save_config()
        self.submit_flag = True
        self.get_message_box("开机卡logo用例配置保存成功")

    def list_test_times_settings(self):
        times = [str(j * 50) for j in range(1, 500)]
        self.test_times.addItems(times)

    def only_boot_checkbox_change(self):
        if self.only_boot.isChecked():
            self.double_screen.setDisabled(True)
        else:
            self.double_screen.setEnabled(True)

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

    def get_COM_config(self):
        return ["1路", "2路", "3路", "4路"]

    def save_config(self):
        # config = ConfigP(self.ui_config_file_path)
        section = self.ui_config.section_ui_logo
        self.ui_config.add_config_section(section)

        self.ui_config.add_config_option(section, "COM", self.test_COM.currentText())
        self.ui_config.add_config_option(section, "logcat_duration", self.adb_log_duration.currentText())

        # 接线方式
        if self.is_adapter.isChecked():
            self.ui_config.add_config_option(section, "is_adapter", "1")
        else:
            self.ui_config.add_config_option(section, "is_adapter", "0")
        if self.is_power_button.isChecked():
            self.ui_config.add_config_option(section, "is_power_button", "1")
        else:
            self.ui_config.add_config_option(section, "is_power_button", "0")
        if self.is_usb.isChecked():
            self.ui_config.add_config_option(section, "is_usb", "1")
        else:
            self.ui_config.add_config_option(section, "is_usb", "0")

        # 接线配置
        if self.adapter_config.isEnabled():
            if self.adapter_config.currentText() == "1路":
                self.ui_config.add_config_option(section, "adapter_power_config", "relay_1")
            elif self.adapter_config.currentText() == "2路":
                self.ui_config.add_config_option(section, "adapter_power_config", "relay_2")
            elif self.adapter_config.currentText() == "3路":
                self.ui_config.add_config_option(section, "adapter_power_config", "relay_3")
            else:
                self.ui_config.add_config_option(section, "adapter_power_config", "relay_4")

        if self.power_button_config.isEnabled():
            if self.power_button_config.currentText() == "1路":
                self.ui_config.add_config_option(section, "power_button_config", "relay_1")
            elif self.power_button_config.currentText() == "2路":
                self.ui_config.add_config_option(section, "power_button_config", "relay_2")
            elif self.power_button_config.currentText() == "3路":
                self.ui_config.add_config_option(section, "power_button_config", "relay_3")
            else:
                self.ui_configconfig.add_config_option(section, "power_button_config", "relay_4")

        if self.usb_config.isEnabled():
            if self.usb_config.currentText() == "1路":
                self.ui_config.add_config_option(section, "usb_config", "relay_1")
            elif self.usb_config.currentText() == "2路":
                self.ui_config.add_config_option(section, "usb_config", "relay_2")
            elif self.usb_config.currentText() == "3路":
                self.ui_config.add_config_option(section, "usb_config", "relay_3")
            else:
                self.ui_config.add_config_option(section, "usb_config", "relay_4")

        # 其他配置信息
        if self.only_boot.isChecked():
            self.ui_config.add_config_option(section, "only_boot_config", "1")
        else:
            self.ui_config.add_config_option(section, "only_boot_config", "0")

        if self.double_screen.isChecked():
            self.ui_config.add_config_option(section, "double_screen_config", "1")
        else:
            self.ui_config.add_config_option(section, "double_screen_config", "0")

            # 开关机时间
            self.ui_config.add_config_option(section, self.ui_config.relay_reboot_interval, self.relay_reboot_duration.currentText())

        if self.button_boot_time.isEnabled():
            self.ui_config.add_config_option(section, "button_boot_time", self.button_boot_time.currentText())

        # 保存用例压测次数设置
        self.ui_config.add_config_option(section, "logo_test_times", self.test_times.currentText())

        if self.is_probability_test.isChecked():
            self.ui_config.add_config_option(section, self.ui_config.is_probability_test, "1")
        else:
            self.ui_config.add_config_option(section, self.ui_config.is_probability_test, "0")

        self.ui_config.add_config_option(section, self.ui_config.test_interval, self.interval.currentText())

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

    def select_devices_name(self):
        devices = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                  self.bg_config.bg_option_devices_name).split(",")
        for device in devices:
            self.edit_device_name.addItem(str(device))

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
    logo_show = LogoDisplay()
    logo_show.show()
    app.exec_()
