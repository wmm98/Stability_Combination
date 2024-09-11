import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot
import configfile
import config_path
from PyQt5.QtCore import QTimer, QProcess, Qt
from PyQt5.QtWidgets import *

conf_path = config_path.UIConfigPath()


class DDR_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout_left = QtWidgets.QVBoxLayout(self.centralwidget)

        layout_device_info = QHBoxLayout()

        self.system_label = QtWidgets.QLabel("系统类型")
        self.system_type = QComboBox()
        self.system_type.addItem("Android")
        self.system_type.addItem("Linux")
        self.system_type.addItem("Debian")
        self.system_type.addItem("T31")

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
        self.mem_label = QtWidgets.QLabel("请输入可用的运行内存（M）：")
        self.verticalLayout_left.addWidget(self.mem_label)
        layout_mem_info = QHBoxLayout()
        self.check_mem_button = QtWidgets.QPushButton("查询")
        self.mem_free = QtWidgets.QLineEdit()
        layout_mem_info.addWidget(self.check_mem_button)
        layout_mem_info.addWidget(self.mem_free)
        self.verticalLayout_left.addLayout(layout_mem_info)

        # check_root_layout = QHBoxLayout()
        # self.check_root_lable = QtWidgets.QLabel("点击验证root:")
        # self.root_button = QtWidgets.QPushButton("一键验证")
        # check_root_layout.addWidget(self.check_root_lable)
        # check_root_layout.addWidget(self.root_button)
        # check_root_layout.addStretch(1)
        # self.verticalLayout_left.addLayout(check_root_layout)

        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("保存")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())
        # 添加左边部分
        # 右侧部件
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
        MainWindow.setWindowTitle(_translate("MainWindow", "DDR-EMMC压测配置"))


class DDRDisplay(QtWidgets.QMainWindow, DDR_MainWindow):

    def __init__(self):
        super(DDRDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        self.bg_config = configfile.ConfigP(self.background_config_file_path)
        # self.bg_config.create_config_file()
        self.ui_config = configfile.ConfigP(self.ui_config_file_path)
        # self.ui_config.create_config_file()
        # 初始化子界面
        self.ddr_window = DDR_MainWindow()
        self.setupUi(self)
        self.intiui()

    def intiui(self):
        # 添加字段
        self.ui_config.add_config_section(self.ui_config.section_DDR_EMMC)
        # 初始化进程
        self.root_process = QProcess()
        self.mem_free_process = QProcess()
        self.submit_button.clicked.connect(self.handle_submit)
        self.check_mem_button.clicked.connect(self.query_mem_free)
        self.mem_free_process.finished.connect(self.mem_free_finished_handle)

    def mem_free_finished_handle(self):
        with open(conf_path.mem_log_path, "r", encoding="utf-8") as f:
            text = f.read()
        if len(text) != 0:
            self.text_edit.insertPlainText(text)
        else:
            self.text_edit.insertPlainText("读取可用运行内存数据失败， 请检查！！！")
        self.text_edit.insertPlainText("查询结束.")

    def query_mem_free(self):
        # 保存root steps
        self.double_check_root()
        # self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_system_type, self.system_type.currentText())
        self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_system_type, self.system_type.currentText())
        # self.ui_config.add_config_option(self.ui_config.section_ui_to_background, self.ui_config.ui_option_device_name,
        #                                  self.edit_device_name.currentText())
        self.mem_free_process.start(conf_path.bat_mem_info_path)

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
                add_d = "-s %s" % self.edit_device_name.currentText()
                cmd_list = s_p.split(" ")
                cmd_list.insert(1, add_d)
                self.new_cmds.append(" ".join(cmd_list))
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC,
                                             self.ui_config.ui_option_root_steps,
                                             ",".join(self.new_cmds))
        else:
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC,
                                             self.ui_config.ui_option_root_steps, "")

    def handle_finished(self):
        self.stop_process()

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        pass

    def remove_file(self, path):
        if os.path.isfile(path):
            os.remove(path)

    def path_is_existed(self, path):
        if os.path.exists(path):
            return True
        else:
            return False

    def remove_space(self, s_tr):
        return s_tr.replace("", " ")

    def list_logcat_duration(self):
        duration = [10, 20, 30, 40, 50, 60]
        for dur in duration:
            self.adb_log_duration.addItem(str(dur))
        self.adb_log_duration.setCurrentText("30")

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
    myshow = DDRDisplay()
    myshow.show()
    app.exec_()
