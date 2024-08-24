import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot
import config_path


class Ui_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    # project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    # config_file_path = os.path.join(project_path, "UI", "config.ini")
    # debug_log_path = os.path.join(project_path, "Log", "log.log")
    # run_bat_path = os.path.join(project_path, "run.bat")

    def __init__(self):
        self.stop_process_button = QtWidgets.QPushButton("停止压测")

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1050, 600)
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

        self.system_label = QtWidgets.QLabel("系统类型")
        self.system_type = QComboBox()
        self.system_type.addItem("Android")
        self.system_type.addItem("Linux")
        self.system_type.addItem("Debian")
        self.system_type.addItem("T31")

        # 测试COM
        self.COM_tips = QtWidgets.QLabel("测试COM口:")
        self.test_COM = QComboBox()

        layout_device_info.addWidget(self.label_device_name)
        layout_device_info.addWidget(self.edit_device_name)
        layout_device_info.addWidget(self.system_label)
        layout_device_info.addWidget(self.system_type)
        layout_device_info.addWidget(self.COM_tips)
        layout_device_info.addWidget(self.test_COM)
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

        self.cases_tips = QtWidgets.QLabel("memtester、EMMC填测试轮数，其他的填测试时间，双击用例右侧即可填写")
        self.cases_tips.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(self.cases_tips)
        # 用例树
        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)  # 设置多选模式
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout_left.addWidget(self.treeWidget)

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("开始压测")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.stop_process_button.setDisabled(True)
        self.verticalLayout_left.addWidget(self.stop_process_button)

        # 添加左边部分
        # 右侧部件
        right_widget = QWidget()
        self.verticalLayout_right = QtWidgets.QVBoxLayout(right_widget)
        self.verticalLayout_right.addWidget(QtWidgets.QLabel("实时log打印:"))
        # 展示log
        self.text_edit = ScrollablePlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.verticalLayout_right.addWidget(self.text_edit)

        self.verticalLayout_left.addStretch(1)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStyleSheet("""
                                    QSplitter::handle {
                                        background: #f0f0f0;  /* 分割条的颜色为最浅的灰色 */
                                        width: 1px;           /* 分割条的最细宽度 */
                                        border: 1px solid #CCCCCC; /* 分割条的边框颜色为灰白色 */
                                    }
                                    QSplitter::handle:horizontal {
                                        height: 100%;  /* 垂直分割条的高度 */
                                    }
                                    QSplitter::handle:vertical {
                                        width: 100%;   /* 水平分割条的宽度 */
                                    }
                                """)

        # 设置伸展因子确保两侧距离一致
        splitter.setStretchFactor(0, 1)  # 左侧部件的伸展因子
        splitter.setStretchFactor(1, 1)  # 右侧部件的伸展因子

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
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 连接 rangeChanged 信号到 slot_scroll_to_bottom 槽
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        # 设置滚动条到底部
        self.verticalScrollBar().setValue(max)
