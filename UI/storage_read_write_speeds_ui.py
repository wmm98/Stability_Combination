import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot
import configfile
import config_path
from PyQt5.QtCore import QTimer, QProcess, Qt
from PyQt5.QtWidgets import *
from configfile import ConfigP

conf_path = config_path.UIConfigPath()


class Storage_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout_left = QtWidgets.QVBoxLayout(self.centralwidget)

        layout_device_info = QHBoxLayout()

        self.device_label = QtWidgets.QLabel("设备名称")
        self.device_name = QtWidgets.QComboBox()

        self.system_label = QtWidgets.QLabel("系统类型")
        self.system_type = QComboBox()
        self.system_type.addItem("Android")
        self.system_type.addItem("Linux")
        self.system_type.addItem("Debian")
        self.system_type.addItem("T31")

        layout_device_info.addWidget(self.device_label)
        layout_device_info.addWidget(self.device_name)
        layout_device_info.addWidget(self.system_label)
        layout_device_info.addWidget(self.system_type)
        layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_info)
        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 填入root方式
        root_layout_tips = QHBoxLayout()
        self.root_lable = QtWidgets.QLabel("请填入root步骤：")
        self.root_step_tips = QtWidgets.QLabel("步骤之间请以逗号隔开，例如：adb root,adb remount")
        self.root_steps_edit = QtWidgets.QComboBox()
        self.root_steps_edit.setEditable(True)
        # 添加原本存在的root方式
        self.root_steps_edit.addItem("adb root,adb remount")
        self.root_steps_edit.addItem("adb shell setprop persist.debuggable 1,adb reboot")
        self.root_step_tips.setStyleSheet("color: blue;")
        root_layout_tips.addWidget(self.root_lable)
        root_layout_tips.addWidget(self.root_step_tips)
        root_layout_tips.addStretch(1)
        self.verticalLayout_left.addLayout(root_layout_tips)
        self.verticalLayout_left.addWidget(self.root_steps_edit)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())
        self.usb_label = QtWidgets.QLabel("请输入U盘/TF卡的路径，例如 mnt/media/E168，多个U口/TF卡压测请以英文分号分隔开，例如:mnt/media/E168;mnt/media/E34H")
        self.verticalLayout_left.addWidget(self.usb_label)
        layout_usb_flash_info = QHBoxLayout()
        self.check_usb_flash_button = QtWidgets.QPushButton("查询U盘/TF卡挂载的路径")
        self.usb_flash_path = QtWidgets.QLineEdit()
        layout_usb_flash_info.addWidget(self.check_usb_flash_button)
        layout_usb_flash_info.addWidget(self.usb_flash_path)
        self.verticalLayout_left.addLayout(layout_usb_flash_info)

        self.usb_partition_label = QtWidgets.QLabel("请输入U盘/TF卡的分区节点，例如 /dev/block/vold/public:8,17，多个U口/TF卡压测请以分号分隔开，例如:/dev/block/vold/public:8,17;/dev/block/vold/public:8,1")
        self.verticalLayout_left.addWidget(self.usb_partition_label)
        layout_usb_partition_node_info = QHBoxLayout()
        self.partition_node_button = QtWidgets.QLabel("                        ")
        self.partition_node_edit = QtWidgets.QLineEdit()
        layout_usb_partition_node_info.addWidget(self.partition_node_button)
        layout_usb_partition_node_info.addWidget(self.partition_node_edit)
        self.verticalLayout_left.addLayout(layout_usb_partition_node_info)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 压测次数
        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QLabel("用例压测次数设置:")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)
        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)
        layout_test_times_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        self.tf_card_tips = QtWidgets.QLabel("注意：TF卡压测，需要使用不同速率的卡进行压测")
        self.tf_card_tips.setStyleSheet("color: red;")
        self.verticalLayout_left.addWidget(self.tf_card_tips)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("保存")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())
        self.verticalLayout_left.addWidget(QtWidgets.QLabel("日志信息:"))

        # 展示log
        self.text_edit = ScrollablePlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.verticalLayout_left.addWidget(self.text_edit)

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
        MainWindow.setWindowTitle(_translate("MainWindow", "U盘/TF卡读取速率压测"))


class StorageTestDisplay(QtWidgets.QMainWindow, Storage_MainWindow):

    def __init__(self):
        super(StorageTestDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        self.bg_config = configfile.ConfigP(self.background_config_file_path)
        self.ui_config = configfile.ConfigP(self.ui_config_file_path)
        # 初始化子界面
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        # 初始化进程
        self.root_process = QProcess()
        self.usb_recognize_process = QProcess()
        self.submit_button.clicked.connect(self.info_submit)
        self.check_usb_flash_button.clicked.connect(self.query_usb_flash_path)
        self.usb_recognize_process.finished.connect(self.query_usb_flash_finished_handle)
        self.list_devices_name()
        self.list_test_times_settings()

    def list_test_times_settings(self):
        times = [str(j * 50) for j in range(1, 1000)]
        self.test_times.addItems(times)

    def list_devices_name(self):
        devices = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                  self.bg_config.bg_option_devices_name).split(",")
        self.device_name.addItems(devices)

    def query_usb_flash_finished_handle(self):
        with open(conf_path.storage_query_log_path, "r") as f:
            text = f.read()
        if len(text) != 0:
            self.text_edit.insertPlainText(text)
        else:
            self.text_edit.insertPlainText("读取可用运行内存数据失败， 请检查！！！")
        self.text_edit.insertPlainText("查询结束.")

    def query_usb_flash_path(self):
        # 保存root steps
        self.double_check_root()
        self.ui_config.add_config_option(self.ui_config.section_storage_stability, self.ui_config.ui_option_system_type,
                                         self.system_type.currentText())
        self.ui_config.add_config_option(self.ui_config.section_ui_to_background, self.ui_config.ui_option_device_name,
                                         self.device_name.currentText())
        self.usb_recognize_process.start(conf_path.bat_query_storage_path)

    def double_check_root(self):
        # adb shell setprop persist.debuggable 1,adb reboot
        cmd = self.root_steps_edit.currentText()
        cmd_split = []
        if len(cmd) != 0:
            if "," in cmd:
                cmd_split = cmd.split(",")
            elif "，" in cmd:
                cmd_split = cmd.split("，")
            else:
                cmd_split.append(cmd)

            # 给指令加上设备区别 ['adb -s 5eea0becf3b0f513 root', 'adb -s 5eea0becf3b0f513 remount']
            self.new_cmds = []
            for s_p in cmd_split:
                add_d = "-s %s" % self.device_name.currentText()
                cmd_list = s_p.split(" ")
                cmd_list.insert(1, add_d)
                self.new_cmds.append(" ".join(cmd_list))
            self.ui_config.add_config_option(self.ui_config.section_storage_stability,
                                             self.ui_config.ui_option_root_steps,
                                             ",".join(self.new_cmds))
        else:
            self.ui_config.add_config_option(self.ui_config.section_storage_stability,
                                             self.ui_config.ui_option_root_steps, "")

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def info_submit(self):
        if len(self.device_name.currentText()) == 0:
            self.get_message_box("没识别到相应的设备，请检查并且重启界面！！！")
            return

        if len(self.usb_flash_path.text()) == 0:
            self.get_message_box("请填入U盘/TF卡挂载的路径！！！")
            return

        if len(self.partition_node_edit.text()) == 0:
            self.get_message_box("请填入U盘/TF卡对应的设备分区节点！！！")
            return

        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请填入用力压测次数！！！")
            return

        if len(self.usb_flash_path.text().split(";")) != len(self.partition_node_edit.text().split(";")):
            self.get_message_box("挂载路径和分区节点数量对不上，请检查！！！")
            return

        self.save_config()
        self.submit_flag = True
        self.get_message_box("配置保存成功")

    def save_config(self):
        config = ConfigP(self.ui_config_file_path)
        section = config.section_storage_stability
        config.add_config_section(section)

        # 保存多个U盘的挂载的路径和对应设备分区
        config.add_config_option(section, config.ui_option_storage_path, self.usb_flash_path.text().strip())
        config.add_config_option(section, config.ui_option_partition_path, self.partition_node_edit.text().strip())
        # 保存U口的个数
        num = str(len(self.usb_flash_path.text().split(";")))
        config.add_config_option(section, config.ui_option_usb_ports_num, num)

        # 保存用例压测次数设置
        config.add_config_option(section, config.option_storage_test_times, self.test_times.currentText())

    def select_devices_name(self):
        devices = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                  self.bg_config.bg_option_devices_name).split(",")
        for device in devices:
            self.edit_device_name.addItem(str(device))

    def update_debug_log(self):
        try:
            log_file = self.debug_log_path
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as file:
                    file.seek(self.last_position)
                    new_content = file.read()
                    if new_content:
                        self.text_edit.insertPlainText(new_content + "\n")
                        self.last_position = file.tell()
        except Exception as e:
            self.log_edit.insertPlainText(str(e) + "\n")

    def download_adb_file(self):
        if not self.stop_process_button.isEnabled():
            # 选择源文件
            source_file = self.adb_log_path
            if not os.path.exists(source_file):
                self.get_message_box("不存在adb log 文件！！！")
                return

            # 获取源文件的名字
            file_name = os.path.basename(source_file)

            # 选择目标保存位置，默认文件名为源文件名
            target_file, _ = QFileDialog.getSaveFileName(self, 'Save File As', file_name,
                                                         'Text Files (*.txt);;All Files (*)')
            if not target_file:
                return

            self.copy_file(source_file, target_file)
            self.get_message_box("成功下载adb log文件！")
        else:
            self.get_message_box("请等待压测停止再下载adb log！！！")


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 连接 rangeChanged 信号到 slot_scroll_to_bottom 槽
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        # 设置滚动条到底部
        self.verticalScrollBar().setValue(max)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    myshow = StorageTestDisplay()
    myshow.show()
    app.exec_()
