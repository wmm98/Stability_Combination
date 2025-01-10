from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QSplitter, QLabel
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from configfile import ConfigP
import config_path


class Touch_Event_MainWindow(config_path.UIConfigPath):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 200)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # 创建水平布局
        self.main_layout = QHBoxLayout(self.centralwidget)

        # 创建 QSplitter 控件，分割两个子窗口
        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        # 左侧所有部件
        left_widget = QWidget()
        self.verticalLayout_left = QtWidgets.QVBoxLayout(left_widget)
        self.boot_way_label = QLabel("启动方式:")
        self.verticalLayout_left.addWidget(self.boot_way_label)
        layout_boot_way = QHBoxLayout()
        self.soft_reboot_way = QCheckBox("软重启")
        self.power_button_reboot_way = QCheckBox("按钮硬重启")
        self.adpater_reboot_way = QCheckBox("适配器硬重启")
        layout_boot_way.addWidget(self.soft_reboot_way)
        layout_boot_way.addWidget(self.power_button_reboot_way)
        layout_boot_way.addWidget(self.adpater_reboot_way)
        layout_boot_way.addStretch(1)
        self.verticalLayout_left.addLayout(layout_boot_way)
        self.verticalLayout_left.addWidget(QLabel())
        # 只能勾选一个
        self.boot_group = QButtonGroup()
        self.boot_group.addButton(self.soft_reboot_way)
        self.boot_group.addButton(self.power_button_reboot_way)
        self.boot_group.addButton(self.adpater_reboot_way)

        # 选择COM
        self.com_label = QLabel("硬重启COM选择:")
        self.verticalLayout_left.addWidget(self.com_label)
        layout_com = QHBoxLayout()
        self.COM_tips = QtWidgets.QLabel("测试COM口:")
        self.test_COM = QComboBox()
        self.test_COM.setDisabled(True)
        # 接线配置
        self.line_config_label = QLabel("接线配置：")
        self.line_config = QComboBox()
        self.line_config.setDisabled(True)
        # 按钮时长
        self.boot_button_duration_label = QLabel("按钮时长：")
        self.boot_button_duration = QComboBox()
        self.boot_button_duration.setDisabled(True)
        layout_com.addWidget(self.COM_tips)
        layout_com.addWidget(self.test_COM)
        layout_com.addWidget(self.line_config_label)
        layout_com.addWidget(self.line_config)
        layout_com.addWidget(self.boot_button_duration_label)
        layout_com.addWidget(self.boot_button_duration)
        layout_com.addStretch(1)
        self.verticalLayout_left.addLayout(layout_com)
        self.verticalLayout_left.addWidget(QLabel())

        # 屏幕
        self.screen_label = QLabel("屏幕选择:")
        self.verticalLayout_left.addWidget(self.screen_label)
        layout_screen = QHBoxLayout()
        self.screen_single = QCheckBox("单屏")
        self.screen_double = QCheckBox("双屏")
        layout_screen.addWidget(self.screen_single)
        layout_screen.addWidget(self.screen_double)
        layout_screen.addStretch(1)
        self.verticalLayout_left.addLayout(layout_screen)
        self.verticalLayout_left.addWidget(QLabel())
        # 只能勾选一个
        self.screen_group = QButtonGroup()
        self.screen_group.addButton(self.screen_single)
        self.screen_group.addButton(self.screen_double)

        # 压测次数
        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QLabel("用例压测次数设置")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)
        probability_test_label = QLabel("是否进行失败概率性统计")
        self.is_probability_test = QCheckBox()
        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)
        layout_test_times_info.addWidget(probability_test_label)
        layout_test_times_info.addWidget(self.is_probability_test)
        layout_test_times_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info)

        self.verticalLayout_left.addWidget(QLabel())

        # 压测间隔相关
        layout_test_interval = QHBoxLayout()
        self.interval_lable = QLabel("每一轮的间隔时长(秒)：")
        self.interval = QComboBox()
        self.interval.setEditable(True)
        layout_test_times_info.addWidget(self.interval_lable)
        layout_test_times_info.addWidget(self.interval)
        self.verticalLayout_left.addLayout(layout_test_interval)


        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("保存配置")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.verticalLayout_left.addStretch(1)

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
        MainWindow.setWindowTitle(_translate("MainWindow", "触摸事件压测配置"))


class TouchEventDisplay(QtWidgets.QMainWindow, Touch_Event_MainWindow):
    def __init__(self):
        super(TouchEventDisplay, self).__init__()
        self.bg_config = ConfigP(self.background_config_file_path)
        self.ui_config = ConfigP(self.ui_config_file_path)
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        self.submit_button.clicked.connect(self.handle_submit)
        self.list_case_test_cases()
        self.list_interval_duration()
        self.power_button_reboot_way.clicked.connect(self.hard_reboot_way_checked)
        self.adpater_reboot_way.clicked.connect(self.hard_reboot_way_checked)
        self.soft_reboot_way.clicked.connect(self.soft_reboot_way_checked)

    def hard_reboot_way_checked(self):
        if self.power_button_reboot_way.isChecked() or self.adpater_reboot_way.isChecked():
            self.test_COM.setEnabled(True)
            self.line_config.setEnabled(True)
            self.boot_button_duration.setEnabled(True)
            com_ports = self.bg_config.get_option_value(self.bg_config.section_background_to_ui, self.bg_config.bg_option_COM_ports)
            com_list = com_ports.split(",")
            self.test_COM.addItems(com_list)

            line_config = self.get_line_config()
            self.line_config.addItems(line_config)

            boot_button_duration = self.get_boot_button_duration()
            self.boot_button_duration.addItems(boot_button_duration)
            self.boot_button_duration.setCurrentText(boot_button_duration[4])  # 默认选中5秒

    def soft_reboot_way_checked(self):
        if self.soft_reboot_way.isChecked():
            self.test_COM.setDisabled(True)
            self.line_config.setDisabled(True)
            self.test_COM.clear()
            self.line_config.clear()
            self.boot_button_duration.clear()

    def get_line_config(self):
        return ["1路", "2路", "3路", "4路"]

    def get_boot_button_duration(self):
        return [str(i) for i in range(1, 11)]

    def list_interval_duration(self):
        times = [str(j * 2) for j in range(1, 200)]
        self.interval.addItems(times)

    def get_message_box(self, text):
        QMessageBox.warning(self, "提示", text)

    def handle_submit(self):

        if not self.soft_reboot_way.isChecked() and not self.power_button_reboot_way.isChecked() and not self.adpater_reboot_way.isChecked():
            self.get_message_box("请选择启动方式!!!")
            return

        if self.power_button_reboot_way.isChecked() and self.adpater_reboot_way.isChecked() and not self.test_COM.currentText():
            self.get_message_box("请选择硬重启COM口!!!")
            return

        if not self.screen_single.isChecked() and not self.screen_double.isChecked():
            self.get_message_box("请选择屏幕选择!!!")
            return

        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请设置压测次数!!!")
            return

        if len(self.interval.currentText()) == 0:
            self.get_message_box("请输入每一轮的间隔时长！！！")
            return

        # 检查完保存配置
        self.save_config()

        self.submit_flag = True
        self.get_message_box("触摸事件压测配置保存成功！！！")

    def save_config(self):
        config = ConfigP(self.ui_config_file_path)
        section = config.section_touch
        config.add_config_section(section)

        # 保存用例配置
        if self.soft_reboot_way.isChecked():
            config.add_config_option(section, config.option_touch_soft_boot, "1")
        else:
            config.add_config_option(section, config.option_touch_soft_boot, "0")

        if self.power_button_reboot_way.isChecked():
            config.add_config_option(section, config.option_touch_power_boot, "1")
        else:
            config.add_config_option(section, config.option_touch_power_boot, "0")

        if self.adpater_reboot_way.isChecked():
            config.add_config_option(section, config.option_touch_dapter_boot, "1")
        else:
            config.add_config_option(section, config.option_touch_dapter_boot, "0")

        if self.screen_double.isChecked():
            config.add_config_option(section, config.option_touch_is_double_screen, "1")
        else:
            config.add_config_option(section, config.option_touch_is_double_screen, "0")

        config.add_config_option(section, config.option_touch_com_port, self.test_COM.currentText())
        if self.line_config.currentText() == "1路":
            config.add_config_option(section, config.option_touch_com_line, "relay_1")
        elif self.line_config.currentText() == "2路":
            config.add_config_option(section, config.option_touch_com_line, "relay_2")
        elif self.line_config.currentText() == "3路":
            config.add_config_option(section, config.option_touch_com_line, "relay_3")
        else:
            config.add_config_option(section, config.option_touch_com_line, "relay_4")
        config.add_config_option(section, config.option_touch_boot_button_duration, self.boot_button_duration.currentText())

        config.add_config_option(section, config.option_touch_test_times, self.test_times.currentText())
        if self.is_probability_test.isChecked():
            config.add_config_option(section, config.is_probability_test, "1")
        else:
            config.add_config_option(section, config.is_probability_test, "0")
        config.add_config_option(section, config.test_interval, self.interval.currentText())

    def list_case_test_cases(self):
        self.test_times.addItems([str(i * 50) for i in range(1, 101)])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logo_show = TouchEventDisplay()
    logo_show.show()
    app.exec_()
