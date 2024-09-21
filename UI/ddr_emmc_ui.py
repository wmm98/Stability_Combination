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
        self.mem_label = QtWidgets.QLabel("请输入可用的运行内存（KB、整数）：")
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

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 压测情况
        self.verticalLayout_left.addWidget(QtWidgets.QLabel("测试项："))
        # 压测次数
        layout_test_times_info1 = QHBoxLayout()
        self.is_DDR_memtester_test = QCheckBox("DDR_memtester测试")
        self.is_DDR_streessapptest_test = QCheckBox("DDR_streessapptest测试")
        self.is_DDR_streessapptest_switch_test = QCheckBox("DDR_streessapptest高低切换测试")
        self.is_EEMC_test = QCheckBox("EMMC测试")
        layout_test_times_info1.addWidget(self.is_DDR_streessapptest_test)
        layout_test_times_info1.addWidget(self.is_DDR_streessapptest_switch_test)
        layout_test_times_info1.addWidget(self.is_DDR_memtester_test)
        layout_test_times_info1.addWidget(self.is_EEMC_test)
        layout_test_times_info1.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info1)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        self.verticalLayout_left.addWidget(QtWidgets.QLabel("测试次数/持续时间："))
        layout_test_times_info2 = QHBoxLayout()
        self.DDR_memtester_label = QtWidgets.QLabel("memtester压测次数")
        self.DDR_memtester_test_times = QComboBox()
        self.DDR_memtester_test_times.setEditable(True)
        self.DDR_stressapptest_label = QtWidgets.QLabel("stressapptest压测小时")
        self.DDR_stressapptest_times = QComboBox()
        self.DDR_stressapptest_times.setEditable(True)
        self.DDR_stressapptest_switch_label = QtWidgets.QLabel("stressapptest高低切换压测小时")
        self.DDR_stressapptest_switch_times = QComboBox()
        self.DDR_stressapptest_switch_times.setEditable(True)
        self.EMMC_label = QtWidgets.QLabel("EMMC压测次数")
        self.EMMC_times = QComboBox()
        self.EMMC_times.setEditable(True)

        layout_test_times_info2.addWidget(self.DDR_memtester_label)
        layout_test_times_info2.addWidget(self.DDR_memtester_test_times)
        layout_test_times_info2.addWidget(self.DDR_stressapptest_label)
        layout_test_times_info2.addWidget(self.DDR_stressapptest_times)
        layout_test_times_info2.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info2)

        layout_test_times_info3 = QHBoxLayout()

        layout_test_times_info3.addWidget(self.DDR_stressapptest_switch_label)
        layout_test_times_info3.addWidget(self.DDR_stressapptest_switch_times)
        layout_test_times_info3.addWidget(self.EMMC_label)
        layout_test_times_info3.addWidget(self.EMMC_times)
        layout_test_times_info3.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info3)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # self.test_times = QComboBox()
        # self.test_times.setEditable(True)
        # layout_test_times_info.addWidget(self.test_times_label)
        # layout_test_times_info.addWidget(self.test_times)
        # layout_test_times_info.addStretch(1)
        # self.verticalLayout_left.addLayout(layout_test_times_info)

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
        MainWindow.setWindowTitle(_translate("MainWindow", "DDR-EMMC压测配置"))


class DDRDisplay(QtWidgets.QMainWindow, DDR_MainWindow):

    def __init__(self):
        super(DDRDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        self.bg_config = configfile.ConfigP(self.background_config_file_path)
        self.ui_config = configfile.ConfigP(self.ui_config_file_path)
        # 初始化子界面
        self.ddr_window = DDR_MainWindow()
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        # 添加字段
        self.ui_config.add_config_section(self.ui_config.section_DDR_EMMC)
        # 初始化进程
        self.root_process = QProcess()
        self.mem_free_process = QProcess()
        self.submit_button.clicked.connect(self.info_submit)
        self.check_mem_button.clicked.connect(self.query_mem_free)
        self.mem_free_process.finished.connect(self.mem_free_finished_handle)
        self.list_devices_name()
        self.list_test_times_settings()

    def list_test_times_settings(self):
        duration = [str(i) for i in range(1, 100)]
        times = [str(j*50) for j in range(1, 1000)]

        self.DDR_memtester_test_times.addItems(times)
        self.DDR_stressapptest_times.addItems(duration)
        self.DDR_stressapptest_switch_times.addItems(duration)
        self.EMMC_times.addItems(times)

    def list_devices_name(self):
        devices = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                  self.bg_config.bg_option_devices_name).split(",")
        self.device_name.addItems(devices)

    def mem_free_finished_handle(self):
        with open(conf_path.mem_log_path, "r") as f:
            text = f.read()
        if len(text) != 0:
            self.text_edit.insertPlainText(text)
        else:
            self.text_edit.insertPlainText("读取可用运行内存数据失败， 请检查！！！")
        self.text_edit.insertPlainText("查询结束.")

    def query_mem_free(self):
        # 保存root steps
        self.double_check_root()
        self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_system_type, self.system_type.currentText())
        self.ui_config.add_config_option(self.ui_config.section_ui_to_background, self.ui_config.ui_option_device_name,
                                         self.device_name.currentText())
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
                add_d = "-s %s" % self.device_name.currentText()
                cmd_list = s_p.split(" ")
                cmd_list.insert(1, add_d)
                self.new_cmds.append(" ".join(cmd_list))
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC,
                                             self.ui_config.ui_option_root_steps,
                                             ",".join(self.new_cmds))
        else:
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC,
                                             self.ui_config.ui_option_root_steps, "")

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def info_submit(self):
        if len(self.device_name.currentText()) == 0:
            self.get_message_box("没识别到相应的设备，请检查并且重启界面！！！")
            return
        #
        if len(self.mem_free.text()) == 0:
            self.get_message_box("请填入可运行的内存！！！")
            return

        if not (self.is_EEMC_test.isChecked() or self.is_DDR_memtester_test.isChecked() or self.is_DDR_streessapptest_test.isChecked()
                or self.is_DDR_streessapptest_switch_test.isChecked()):
            self.get_message_box("请勾选测试项！！！")
            return

        if self.is_EEMC_test.isChecked():
            if len(self.EMMC_times.currentText()) == 0:
                self.get_message_box("请设置EMMC压测次数！！！")
                return
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_emmc_test, "yes")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_emmmc_duration, self.EMMC_times.currentText())
        else:
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_emmc_test, "no")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_emmmc_duration, self.EMMC_times.currentText())

        if self.is_DDR_memtester_test.isChecked():
            if len(self.DDR_memtester_test_times.currentText()) == 0:
                self.get_message_box("请设置DDR Memtester压测次数！！！")
                return
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_memtester, "yes")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_memtester_duration, self.DDR_memtester_test_times.currentText())
        else:
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_memtester, "no")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_memtester_duration, self.DDR_memtester_test_times.currentText())

        if self.is_DDR_streessapptest_test.isChecked():
            if len(self.DDR_stressapptest_times.currentText()) == 0:
                self.get_message_box("请设置DDR streessapptest压测小时！！！")
                return
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_stress_app_test, "yes")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_stressapptest_duration, str(int(self.DDR_stressapptest_times.currentText()) * 3600))
        else:
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_stress_app_test, "no")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_stressapptest_duration, str(int(self.DDR_stressapptest_times.currentText()) * 3600))

        if self.is_DDR_streessapptest_switch_test.isChecked():
            if len(self.DDR_stressapptest_switch_times.currentText()) == 0:
                self.get_message_box("请设置DDR streessapptest高低切换压测时间！！！")
                return
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_stress_app_switch, "yes")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_switch_stressapptest_duration, str(int(int(self.DDR_stressapptest_switch_times.currentText()) * 3600 / 15)))
        else:
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_is_stress_app_switch, "no")
            self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_switch_stressapptest_duration, str(int(int(self.DDR_stressapptest_switch_times.currentText()) * 3600 / 15)))

        self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_mem_free_value, str(int(int(self.mem_free.text()) / 1024)))
        self.ui_config.add_config_option(self.ui_config.section_DDR_EMMC, self.ui_config.ui_option_system_type, self.system_type.currentText())
        self.submit_flag = True
        self.get_message_box("配置保存成功")

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
