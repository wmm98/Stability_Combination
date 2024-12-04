import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot
import config_path


class Ui_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def __init__(self):
        self.stop_process_button = QtWidgets.QPushButton("停止压测")

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 700)
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

        # self.system_label = QtWidgets.QLabel("系统类型")
        # self.system_type = QComboBox()
        # self.system_type.addItem("Android")
        # self.system_type.addItem("Linux")
        # self.system_type.addItem("Debian")
        # self.system_type.addItem("T31")

        # 测试COM
        self.COM_tips = QtWidgets.QLabel("测试COM口:")
        self.test_COM = QComboBox()

        layout_device_info.addWidget(self.label_device_name)
        layout_device_info.addWidget(self.edit_device_name)
        # layout_device_info.addWidget(self.system_label)
        # layout_device_info.addWidget(self.system_type)
        layout_device_info.addWidget(self.COM_tips)
        layout_device_info.addWidget(self.test_COM)
        layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_info)
        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 用例树
        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)  # 设置多选模式
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.setFixedHeight(400)
        self.verticalLayout_left.addWidget(self.treeWidget)

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("开始压测")
        self.verticalLayout_left.addWidget(self.submit_button)
        #
        self.stop_process_button.setDisabled(True)
        self.verticalLayout_left.addWidget(self.stop_process_button)

        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        # 提示
        self.tips_title = QtWidgets.QLabel("温馨提示：")
        self.tips_label1 = QtWidgets.QLabel("1、USB拔插识别 手持设备压测脱机前需要需要用wifi adb进行配置查询操作.")
        self.tips_label2 = QtWidgets.QLabel("2、不涉及硬开关机、网络操作的用例可选择wifi adb进行测试.")
        self.tips_title.setStyleSheet("color: blue;")
        self.tips_label1.setStyleSheet("color: blue;")
        self.tips_label2.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(self.tips_title)
        self.verticalLayout_left.addWidget(self.tips_label1)
        self.verticalLayout_left.addWidget(self.tips_label2)

        # 添加左边部分
        # 右侧部

        right_widget = QWidget()
        self.verticalLayout_right = QtWidgets.QVBoxLayout(right_widget)
        self.verticalLayout_right.addWidget(QtWidgets.QLabel("实时log打印:"))
        # 展示log
        self.text_edit = ScrollablePlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.verticalLayout_right.addWidget(self.text_edit)

        # 最右边的
        final_widget = QWidget()
        self.verticalLayout_final = QtWidgets.QVBoxLayout(final_widget)
        self.verticalLayout_final.addWidget(QtWidgets.QLabel("logo照片显示:"))
        # 展示log
        self.text_edit_final = ScrollablePlainTextEdit()
        self.text_edit_final.setReadOnly(True)
        width = self.text_edit_final.viewport().width()
        height = self.text_edit_final.viewport().height()
        self.image_width = width / 2
        self.image_height = height / 2
        self.document = self.text_edit_final.document()
        self.verticalLayout_final.addWidget(self.text_edit_final)

        self.verticalLayout_final.addWidget(QtWidgets.QLabel("相机照片显示:"))
        self.text_edit_final_camera = ScrollablePlainTextEdit()
        self.text_edit_final_camera.setReadOnly(True)
        width_camera = self.text_edit_final_camera.viewport().width()
        height_camera = self.text_edit_final_camera.viewport().height()
        self.image_width_camera = width_camera / 3
        self.image_height_camera = height_camera / 3
        self.document_camera = self.text_edit_final_camera.document()
        self.verticalLayout_final.addWidget(self.text_edit_final_camera)

        self.verticalLayout_left.addStretch(1)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.addWidget(final_widget)
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
        MainWindow.setWindowTitle(_translate("MainWindow", "压测用例配置界面"))


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 连接 rangeChanged 信号到 slot_scroll_to_bottom 槽
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        # 设置滚动条到底部
        self.verticalScrollBar().setValue(max)
