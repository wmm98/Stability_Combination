import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QProcess, Qt, pyqtSlot
from tree_widget import Ui_MainWindow
import os
import shutil
from PyQt5.QtGui import QPixmap
import serial.tools.list_ports
from PIL import Image
import rembg
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextImageFormat
import configparser
import time
import configfile
import config_path

conf_path = config_path.UIConfigPath()


# subprocess.Popen(conf_path.bat_pre_info_path, shell=True, stdout=subprocess.PIPE,
#                     stderr=subprocess.PIPE).communicate(timeout=120)

class AllCertCaseValue:
    ROOT_PROTOCON = 0
    ROOT_PROTOCON_STA_CHILD = 1
    ROOT_PROTOCON_STA_TMISCAN_B0 = 2
    ROOT_PROTOCON_STA_TMISCAN_B1 = 3
    ROOT_PROTOCON_STA_TMISCAN_B2 = 4


DictCommandInfo = {

    "A": AllCertCaseValue.ROOT_PROTOCON,
    "DDR-memtester压力测试": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B0,
    "DDR-stressapptest": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B1,
    "DDR-stressapptest-高低内存切换测试": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B2,
}


class UIDisplay(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(UIDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        self.bg_config = configfile.ConfigP(self.background_config_file_path)
        self.ui_config = configfile.ConfigP(self.ui_config_file_path)
        # 初始化读取内容读取指针在开始位置
        self.setupUi(self)
        self.AllTestCase = None
        self.intiui()
        self.cases_selected_sum = 0

    def intiui(self):
        # 初始化
        self.ui_config.add_config_section(self.ui_config.section_ui_to_background)

        # 初始化进程
        self.qt_process = QProcess()
        self.root_process = QProcess()
        # 用例数结构
        # 设置列数
        self.treeWidget.setColumnCount(1)
        # 设置树形控件头部的标题
        self.treeWidget.setHeaderLabels(['测试场景'])
        self.treeWidget.setColumnWidth(0, 120)

        # 设置根节点
        self.AllTestCase = QTreeWidgetItem(self.treeWidget)
        self.AllTestCase.setText(0, '测试项')

        for value in DictCommandInfo.keys():
            if DictCommandInfo[value] > AllCertCaseValue.ROOT_PROTOCON_STA_CHILD:
                item_sta_father = QTreeWidgetItem(self.AllTestCase)
                item_sta_father.setText(0, value)
                item_sta_father.setCheckState(0, Qt.Unchecked)
                item_sta_father.setFlags(item_sta_father.flags() | Qt.ItemIsSelectable)

        # 节点全部展开
        self.treeWidget.expandAll()
        # 链槽
        self.select_devices_name()
        self.list_COM()

        self.root_button.clicked.connect(self.double_check_root)
        self.submit_button.clicked.connect(self.handle_submit)
        self.stop_process_button.clicked.connect(self.stop_process)
        # 进程完成
        self.qt_process.finished.connect(self.handle_finished)

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
            self.ui_config.add_config_option(self.ui_config.section_ui_to_background,
                                             self.ui_config.ui_option_root_steps,
                                             ",".join(self.new_cmds))
        else:
            self.ui_config.add_config_option(self.ui_config.section_ui_to_background,
                                             self.ui_config.ui_option_root_steps, "")

            # 计时器
            self.index_flag = 0
            self.reboot_finished = False
            self.reboot_timer = QTimer(self)
            self.reboot_timeout_limit = 30 * 1000  # 超时限制，单位毫秒, 10秒超时
            self.elapsed_time = 0  # 已经过的时间
            self.check_interval = 1000

    def handle_finished(self):
        self.stop_process()

    # 获取所有节点的状态
    def get_tree_item_status(self, tree_item):
        status = tree_item.checkState(0)
        if status == 2:
            self.cases_selected_sum += 1
        result = {
            "text": tree_item.text(0),
            "status": status,
            "children": []
        }
        # 我添加的
        for i in range(tree_item.childCount()):
            child_item = tree_item.child(i)
            result["children"].append(self.get_tree_item_status(child_item))
        return result

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        # 初始化log文件
        with open(self.debug_log_path, "w") as f:
            f.close()

        # 检查用例是否为空
        self.tree_status = []
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            # 2 表示已勾选，0 表示未勾选，1 表示半选中
            self.tree_status.append(self.get_tree_item_status(item))

        # 保存要跑的用例
        self.cases = []
        for slave in self.tree_status[0]["children"]:
            if slave["status"] == 2:
                if "DDR-memtester" in slave["text"]:
                    self.cases.append("DDR-memtester")
                elif "DDR-stressapptest" in slave["text"]:
                    self.cases.append("DDR-stressapptest")
                elif "DDR-stressapptest-高低内存切换测试" in slave["text"]:
                    self.cases.append("DDR-stressapptest-switch")

        if len(self.cases) == 0:
            self.get_message_box("请勾选用例！！！")
            return

        self.ui_config.add_config_option(self.ui_config.section_ui_to_background,
                                         self.ui_config.ui_option_cases, ",".join(self.cases))

        # 检查完保存配置
        # self.save_config(self.config_file_path)
        # 启动
        # self.start_qt_process(self.run_bat_path)

        # self.file_timer = QTimer(self)
        # self.file_timer.timeout.connect(self.check_image_modification)
        #
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_debug_log)
        #
        # self.check_interval = 1000  # 定时器间隔，单位毫秒
        # self.timer.start(self.check_interval)  # 启动定时器
        # self.file_timer.start(self.check_interval)
        #
        # self.stop_process_button.setEnabled(True)
        # self.submit_button.setDisabled(True)
        # self.submit_button.setText("测试中...")

    def get_COM_config(self):
        return ["1路", "2路", "3路", "4路"]

    def get_file_modification_time(self, file_path):
        """获取文件的最后修改时间"""
        file_info = QFileInfo(file_path)
        last_modify = file_info.lastModified()
        return last_modify

    def check_image_modification(self):
        """检查图片文件是否有修改"""
        if os.path.exists(self.camera_key_path):
            current_mod_time = self.get_file_modification_time(self.camera_key_path)
            if current_mod_time != self.last_modify_time:
                self.last_modify_time = current_mod_time  # 更新为新的修改时间
                self.add_logo_image()

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

    def closeEvent(self, event):
        # 在窗口关闭时停止定时器,关闭任务运行
        # 停止 QProcess 进程
        self.qt_process.startDetached("taskkill /PID %s /F /T" % str(self.qt_process.processId()))
        if os.path.exists(self.ui_config_file_path):
            os.remove(self.ui_config_file_path)
        if os.path.exists(self.background_config_file_path):
            os.remove(self.background_config_file_path)
        self.timer.stop()
        self.file_timer.stop()
        event.accept()

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

    def remove_space(self, s_tr):
        return s_tr.replace("", " ")

    def list_COM(self):
        ports = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                self.bg_config.bg_option_COM_ports).split(",")
        for port in ports:
            self.test_COM.addItem(port)

    def get_current_COM(self):
        serial_list = []
        ports = list(serial.tools.list_ports.comports())
        if len(ports) != 0:
            for port in ports:
                if 'SERIAL' in port.description:
                    COM_name = port.device.replace("\n", "").replace(" ", "").replace("\r", "")
                    serial_list.append(COM_name)
            return serial_list
        else:
            return []

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


if __name__ == '__main__':
    # import subprocess
    # QProcess().start(conf_path.bat_pre_info_path)
    # print(conf_path.project_path)
    # print(conf_path.py_pre_info_path)
    subprocess.Popen("python %s" % conf_path.py_pre_info_path, shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE).communicate(timeout=120)
    print("******************************************************")
    print(conf_path.project_path)
    print(conf_path.py_pre_info_path)
    # print(conf_path.bat_pre_info_path)
    # subprocess.Popen(conf_path.bat_pre_info_path, shell=True, stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE).communicate(timeout=120)
    # time.sleep(3)
    app = QtWidgets.QApplication(sys.argv)
    myshow = UIDisplay()
    myshow.show()
    app.exec_()
