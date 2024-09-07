import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot
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


class Reboot_Logo_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    # project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    # config_file_path = os.path.join(project_path, "UI", "config.ini")
    # logo_take_path = os.path.join(project_path, "Photo", "Logo", "Logo", "Logo.png")
    # logo_key_path = os.path.join(project_path, "Photo", "Logo", "Key", "Key.png")
    # camera_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Key.png")
    # camera2_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Key2.png")
    # debug_log_path = os.path.join(project_path, "Log", "Debug", "debug_log.txt")
    # # failed_logcat.txt
    # adb_log_path = os.path.join(project_path, "Log", "Logcat", "failed_logcat.txt")
    # run_bat_path = os.path.join(project_path, "Run", "bat_run.bat")
    # failed_image_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Failed.png")
    # 测试前先清除
    # if os.path.exists(debug_log_path):
    #     os.remove(debug_log_path)
    # if os.path.exists(adb_log_path):
    #     os.remove(adb_log_path)
    # if os.path.exists(logo_key_path):
    #     os.remove(logo_key_path)

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
        # 测试COM
        self.COM_tips = QtWidgets.QLabel("测试COM口:")
        self.test_COM = QComboBox()
        # adb log 时长
        self.adb_log_lable = QtWidgets.QLabel("Logcat时长(min):")
        self.adb_log_duration = QComboBox()

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
        self.config_label = QtWidgets.QLabel("接线配置:")
        self.adapter_label = QtWidgets.QLabel("适配器/电池:")
        self.adapter_config = QComboBox()
        self.adapter_config.setDisabled(True)
        layout_COM_config.addWidget(self.config_label)
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
        self.config_tips = QtWidgets.QLabel("接线提示:电源按键接常开端(COM,N0）,其他接常闭端(COM,NC)")
        self.config_tips.setStyleSheet("color: blue;")
        layout_COM_config.addWidget(self.usb_label)
        layout_COM_config.addWidget(self.usb_config)
        layout_COM_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_COM_config)
        self.verticalLayout_left.addWidget(self.config_tips)
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
        other_layout_device_info.addWidget(self.other_device_info)
        other_layout_device_info.addWidget(self.only_boot)
        other_layout_device_info.addWidget(self.double_screen)
        other_layout_device_info.addWidget(self.button_boot_lable)
        other_layout_device_info.addWidget(self.button_boot_time)
        other_layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(other_layout_device_info)
        self.button_boot_tips = QtWidgets.QLabel("提示：“只测开关机”不进行图片拍照对比，只查看adb是否起来")
        self.button_boot_tips.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(self.button_boot_tips)

        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 上传图片
        self.reboot_logo_info = QtWidgets.QLabel("上传开机logo照片：")
        self.verticalLayout_left.addWidget(self.reboot_logo_info)
        layout_upload_logo = QHBoxLayout()
        self.logo_path_edit = QtWidgets.QLineEdit()
        layout_upload_logo.addWidget(self.logo_path_edit)
        self.logo_upload_button = QtWidgets.QPushButton("点击上传")
        layout_upload_logo.addWidget(self.logo_upload_button)
        self.verticalLayout_left.addLayout(layout_upload_logo)

        # 创建 QLabel 用于显示照片
        # 显示图片
        self.show_keying_button = QtWidgets.QPushButton("显示抠图")
        self.verticalLayout_left.addWidget(self.show_keying_button)

        self.exp_image_label = QtWidgets.QLabel()
        self.exp_image_label.setScaledContents(True)
        self.verticalLayout_left.addWidget(self.exp_image_label)

        self.test_image_label = QtWidgets.QLabel()
        self.test_image_label.setScaledContents(True)
        self.verticalLayout_left.addWidget(self.test_image_label)
        self.verticalLayout_left.setSpacing(10)

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
        self.setupUi(self)
        self.intiui()

    def intiui(self):
        # 初始化进程
        self.list_COM()
        self.list_logcat_duration()
        self.is_adapter.clicked.connect(self.adapter_checkbox_change)
        self.is_power_button.clicked.connect(self.power_button_checkbox_change)
        self.is_usb.clicked.connect(self.usb_checkbox_change)
        self.logo_upload_button.clicked.connect(self.upload_reboot_logo)
        self.show_keying_button.clicked.connect(self.show_keying_image)
        self.submit_button.clicked.connect(self.handle_submit)
        # 进程完成
        self.only_boot.clicked.connect(self.only_boot_checkbox_change)

    def handle_finished(self):
        self.stop_process()

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

            # 检查是否抠图了
            if not os.path.exists(self.logo_key_path):
                self.get_message_box("请抠图检查图片是否完整！！！")
                return

        # 检查完保存配置
        self.save_config(self.config_file_path)

        # 每次提交先删除失败的照片，避免检错误
        if os.path.exists(self.failed_image_key_path):
            os.remove(self.failed_image_key_path)

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

    def get_COM_config(self):
        return ["1路", "2路", "3路", "4路"]

    def save_config(self, file_name):
        config = ConfigP(self.ui_config_file_path)
        section = config.section_ui_logo
        config.add_config_section(section)

        # config[section]['device_name'] = self.edit_device_name.currentText()
        config.add_config_option(section, "COM", self.test_COM.currentText())
        config.add_config_option(section, "logcat_duration", self.adb_log_duration.currentText())
        # config[section]["logcat_duration"] = self.adb_log_duration.currentText()

        # 接线方式
        if self.is_adapter.isChecked():
            # config[section]["is_adapter"] = "1"
            config.add_config_option(section, "is_adapter", "1")
        else:
            # config[section]["is_adapter"] = "0"
            config.add_config_option(section, "is_adapter", "0")
        if self.is_power_button.isChecked():
            # config[section]["is_power_button"] = "1"
            config.add_config_option(section, "is_power_button", "1")
        else:
            # config[section]["is_power_button"] = "0"
            config.add_config_option(section, "is_power_button", "0")
        if self.is_usb.isChecked():
            # config[section]["is_usb"] = "1"
            config.add_config_option(section, "is_usb", "1")
        else:
            # config[section]["is_usb"] = "0"
            config.add_config_option(section, "is_usb", "0")

        # 接线配置
        if self.adapter_config.isEnabled():
            if self.adapter_config.currentText() == "1路":
                # config[section]["adapter_power_config"] = "relay_1"
                config.add_config_option(section, "adapter_power_config", "relay_1")
            elif self.adapter_config.currentText() == "2路":
                # config[section]["adapter_power_config"] = "relay_2"
                config.add_config_option(section, "adapter_power_config", "relay_2")
            elif self.adapter_config.currentText() == "3路":
                # config[section]["adapter_power_config"] = "relay_3"
                config.add_config_option(section, "adapter_power_config", "relay_3")
            else:
                # config[section]["adapter_power_config"] = "relay_4"
                config.add_config_option(section, "adapter_power_config", "relay_4")

        if self.power_button_config.isEnabled():
            if self.power_button_config.currentText() == "1路":
                # config[section]["power_button_config"] = "relay_1"
                config.add_config_option(section, "power_button_config", "relay_1")
            elif self.power_button_config.currentText() == "2路":
                # config[section]["power_button_config"] = "relay_2"
                config.add_config_option(section, "power_button_config", "relay_2")
            elif self.power_button_config.currentText() == "3路":
                # config[section]["power_button_config"] = "relay_3"
                config.add_config_option(section, "power_button_config", "relay_3")
            else:
                # config[section]["power_button_config"] = "relay_4"
                config.add_config_option(section, "power_button_config", "relay_4")

        if self.usb_config.isEnabled():
            if self.usb_config.currentText() == "1路":
                # config[section]["usb_config"] = "relay_1"
                config.add_config_option(section, "usb_config", "relay_1")
            elif self.usb_config.currentText() == "2路":
                # config[section]["usb_config"] = "relay_2"
                config.add_config_option(section, "usb_config", "relay_2")
            elif self.usb_config.currentText() == "3路":
                # config[section]["usb_config"] = "relay_3"
                config.add_config_option(section, "usb_config", "relay_3")
            else:
                # config[section]["usb_config"] = "relay_4"
                config.add_config_option(section, "usb_config", "relay_4")

        # 其他配置信息
        if self.only_boot.isChecked():
            # config[section]["only_boot_config"] = "1"
            config.add_config_option(section, "only_boot_config", "1")
        else:
            # config[section]["only_boot_config"] = "0"
            config.add_config_option(section, "only_boot_config", "0")

        if self.double_screen.isChecked():
            # config[section]["double_screen_config"] = "1"
            config.add_config_option(section, "double_screen_config", "1")
        else:
            # config[section]["double_screen_config"] = "0"
            config.add_config_option(section, "double_screen_config", "0")

        if self.button_boot_time.isEnabled():
            # config[section]["button_boot_time"] = self.button_boot_time.currentText()
            config.add_config_option(section, "button_boot_time", self.button_boot_time.currentText())

    def stop_process(self):
        # 文件位置初始化
        self.force_task_kill()
        self.last_position = 0
        self.stop_process_button.setDisabled(True)
        self.submit_button.setEnabled(True)
        self.submit_button.setText("开始测试")
        self.timer.stop()
        self.file_timer.stop()

    def start_qt_process(self, file):
        # 启动 外部 脚本
        self.qt_process.start(file)

    def force_task_kill(self):
        res = self.qt_process.startDetached("taskkill /PID %s /F /T" % str(self.qt_process.processId()))
        if res:
            self.text_edit.insertPlainText("任务已经结束" + "\n")
        else:
            self.text_edit.insertPlainText("任务还没结束" + "\n")

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
    logo_show = LogoDisplay()
    logo_show.show()
    app.exec_()
