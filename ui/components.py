#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI组件模块

这个模块包含了所有自定义的UI组件类，用于构建主窗口界面
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                          QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox, QTextEdit, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal

from ui.styles import Styles
from utils.event_bus import event_bus
from utils.event_constants import (
    OS_MOD_OPTIONS_UPDATED,
    OS_MOD_SELECTED,
    OS_MOD_CHANGED,
    OS_MOD_ADD_CLICKED,
    WHQL_CHANGED,
    MOD_LOAD_CLICKED,
    MOD_ADD_CLICKED,
    KEYPARTS_LOAD_CLICKED,
    KEYPARTS_SEARCH_CLICKED,
    KEYPARTS_ADD_CLICKED,
    KEYPARTS_CLEAR_CLICKED,
    APP_MOD_ADD_CLICKED,
    CONFIG_FILE_SELECT_CLICKED,
    CONFIG_FILE_OK_CLICKED,
    SHEET_CHANGED,
    PN_CHANGED,
    LOAD_PHBOM_CLICKED,
    CLEAR_MOD_CLICKED,
    GENERATE_CLICKED,
    CHECK_CLICKED,
    BYPASS_WHQL_CLICKED
)

class ControlPanel(QWidget):
    """顶部控制面板组件"""
    
    # 定义信号
    file_selected = pyqtSignal(str)
    sheet_changed = pyqtSignal(int)
    pn_changed = pyqtSignal(int)
    load_phbom_clicked = pyqtSignal()  # 添加LOAD PHBOM按钮信号
    clear_mod_clicked = pyqtSignal()   # 添加Clear MOD.TXT按钮信号
    generate_clicked = pyqtSignal()    # 添加Generate按钮信号
    
    def __init__(self, parent=None):
        """初始化控制面板"""
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 左侧容器
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 加载按钮
        self.select_file_btn = QPushButton('Load Config Table')
        self.select_file_btn.setMinimumWidth(120)
        left_layout.addWidget(self.select_file_btn)
        
        # 工作表下拉框 - 宽度30像素增加到80
        sheet_container = self._create_combo_container('Sheet:', 180)  # 宽度50增加到80
        self.sheet_combo = sheet_container.findChild(QComboBox)
        left_layout.addWidget(sheet_container)
        
        # 添加OK按钮 - 宽度30像素增加到70
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFixedWidth(70)  # 宽度50增加到70
        self.ok_btn.setEnabled(False)  # 初始状态禁用
        left_layout.addWidget(self.ok_btn)
        
        # System P/N 下拉框 - 宽度增加80像素增加到180
        pn_container = self._create_combo_container('System P/N:', 180)  # 宽度100增加到180
        self.pn_combo = pn_container.findChild(QComboBox)
        left_layout.addWidget(pn_container)
        
        # 添加LOAD PHBOM按钮
        self.load_phbom_btn = QPushButton('Load PHBOM')
        self.load_phbom_btn.setMinimumWidth(120)
        left_layout.addWidget(self.load_phbom_btn)
        
        # 添加Clear MOD.TXT按钮
        self.clear_mod_btn = QPushButton('Clear MOD.TXT')
        self.clear_mod_btn.setMinimumWidth(120)
        left_layout.addWidget(self.clear_mod_btn)
        
        # 添加Generate按钮
        self.generate_btn = QPushButton('Generate')
        self.generate_btn.setMinimumWidth(120)
        left_layout.addWidget(self.generate_btn)
        
        # 添加弹性空间，使组件左对齐
        left_layout.addStretch(1)
        
        # 将左侧容器添加到主布局
        layout.addWidget(left_container)
        
        # 设置样式
        self.setStyleSheet(Styles.get_control_panel_style())
        
        # 连接信号
        self.select_file_btn.clicked.connect(self.select_file)
        self.sheet_combo.currentIndexChanged.connect(self.on_sheet_changed)
        self.pn_combo.currentIndexChanged.connect(self.on_pn_changed)
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.load_phbom_btn.clicked.connect(self._on_load_phbom_clicked)
        self.clear_mod_btn.clicked.connect(self._on_clear_mod_clicked)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        
    def _create_combo_container(self, label_text, combo_width):
        """创建下拉框容器"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        combo = QComboBox()
        combo.setMinimumWidth(combo_width)
        
        layout.addWidget(label)
        layout.addWidget(combo)
        
        return container

    def select_file(self):
        """处理选择文件按钮点击事件"""
        self.ok_btn.setEnabled(False)  # 重置OK按钮状态
        event_bus.publish(CONFIG_FILE_SELECT_CLICKED)
        
    def on_ok_clicked(self):
        """处理确定按钮点击事件"""
        event_bus.publish(CONFIG_FILE_OK_CLICKED)
        
    def on_sheet_changed(self, index):
        """处理工作表下拉框变更事件"""
        if index >= 0:
            event_bus.publish(SHEET_CHANGED, index)
            self.sheet_changed.emit(index)
        
    def on_pn_changed(self, index):
        """处理P/N下拉框变更事件"""
        if index >= 0:
            event_bus.publish(PN_CHANGED, index)
            self.pn_changed.emit(index)
        
    def enable_ok_button(self):
        """启用OK按钮"""
        self.ok_btn.setEnabled(True)

    def _on_load_phbom_clicked(self):
        """处理点击PHBOM按钮的事件"""
        # 只通过事件总线发布事件，避免双重触发
        event_bus.publish(LOAD_PHBOM_CLICKED)
        # self.load_phbom_clicked.emit()  # 移除信号发射，避免双重触发
    
    def _on_clear_mod_clicked(self):
        """处理点击Clear MOD.TXT按钮的事件"""
        # 只通过事件总线发布事件，避免双重触发
        event_bus.publish(CLEAR_MOD_CLICKED)
        # self.clear_mod_clicked.emit()  # 移除信号发射，避免双重触发
    
    def _on_generate_clicked(self):
        """处理点击Generate按钮的事件"""
        # 只通过事件总线发布事件，避免双重触发
        event_bus.publish(GENERATE_CLICKED)
        # self.generate_clicked.emit()  # 移除信号发射，避免双重触发

class ButtonPanel(QWidget):
    """中间按钮面板组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 创建一个空的容器，保持布局结构
        empty_container = QWidget()
        empty_layout = QHBoxLayout(empty_container)
        empty_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加弹性空间
        empty_layout.addStretch(1)
        
        # 将空容器添加到主布局
        layout.addWidget(empty_container)
        
        # 添加弹性空间
        layout.addStretch(1)

class ModulePanel(QWidget):
    """模块面板，包含OS MOD、MOD和组件选择"""
    
    # 信号定义
    os_mod_changed = pyqtSignal(int)
    os_mod_add_clicked = pyqtSignal()
    mod_load_clicked = pyqtSignal()
    mod_add_clicked = pyqtSignal()
    keyparts_load_clicked = pyqtSignal()
    keyparts_search_clicked = pyqtSignal()
    keyparts_add_clicked = pyqtSignal()
    keyparts_clear_clicked = pyqtSignal()
    app_mod_add_clicked = pyqtSignal()
    bypass_whql_clicked = pyqtSignal(bool)  # 添加新信号，传递当前状态
    check_clicked = pyqtSignal(str)  # 添加Check按钮信号，传递检查值
    
    def __init__(self, parent=None):
        """初始化模块面板"""
        super().__init__(parent)

        # 初始化UI组件
        self.os_mod_combo = None
        self.os_mod_text = None
        self.whql_checkbox = None
        self.bypass_whql_btn = None  # 添加Bypass WHQL按钮引用
        self._bypass_whql_active = False  # 添加状态跟踪变量

        # 组件字典
        self.mod_combos = {}
        self.mod_texts = {}
        self.component_combos = {}
        self.component_inputs = {}
        self.component_texts = {}

        # 防止递归更新标志
        self._is_updating = False

        # 设置UI
        self.setup_ui()

        # 订阅事件
        event_bus.subscribe(OS_MOD_OPTIONS_UPDATED, self._on_os_mod_options_updated)
        
    def _on_os_mod_options_updated(self, options):
        """处理OS MOD选项更新事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            
            # 清空当前选项
            self.os_mod_combo.clear()
            
            # 添加新选项
            if isinstance(options, list):
                self.os_mod_combo.addItems(options)
        finally:
            self._is_updating = False
            
    def _on_os_mod_changed(self, index):
        """处理OS MOD下拉框变更事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            
            # 发布事件
            event_bus.publish(OS_MOD_CHANGED, index)
            self.os_mod_changed.emit(index)
        finally:
            self._is_updating = False
        
    def _create_standard_label(self, text):
        """创建标准标签
        
        @param {str} text - 标签文本
        @return {QLabel} - 标准化的标签
        """
        label = QLabel(text)
        label.setFixedWidth(80)  # 统一标签宽度为80像素
        label.setFixedHeight(25)  # 设置固定高度与其他组件一致
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中对齐
        label.setStyleSheet(Styles.get_label_style())
        return label
        
    def _create_standard_combo(self, min_width=180):
        """创建标准下拉框
        @param {int} min_width - 最小宽度，默认为180像素
        @return {QComboBox} - 标准化的下拉框
        """
        combo = QComboBox()
        combo.setFixedHeight(25)  # 统一高度为25像素
        combo.setMinimumWidth(min_width)  # 设置最小宽度
        combo.setStyleSheet(Styles.get_combobox_style())
        return combo
        
    def _create_standard_text(self, width=80, read_only=True):
        """创建标准文本输入框
        @param {int} width - 控件宽度，默认80像素
        @param {bool} read_only - 是否只读，默认True
        @return {QLineEdit} - 标准化的文本框
        """
        text_box = QLineEdit()
        text_box.setReadOnly(read_only)
        text_box.setFixedHeight(25)  # 统一高度为25像素
        text_box.setFixedWidth(width)  # 设置固定宽度
        text_box.setPlaceholderText("...")
        text_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中对齐
        text_box.setStyleSheet(Styles.get_lineedit_style())
        return text_box
        
    def _create_standard_button(self, text, width=80, button_type="normal"):
        """创建标准按钮
        
        @param {str} text - 按钮文本
        @param {int} width - 按钮宽度，默认80像素
        @param {str} button_type - 按钮类型，可选值：normal, add, delete
        @return {QPushButton} - 按钮对象
        """
        button = QPushButton(text)
        button.setFixedHeight(25)  # 设置固定高度为25像素
        button.setFixedWidth(width)  # 设置固定宽度
        
        # 根据按钮类型设置不同的样式
        if button_type == "add":
            button.setStyleSheet(Styles.get_add_button_style())
        elif button_type == "delete":
            button.setStyleSheet(Styles.get_delete_button_style())
        else:  # normal
            button.setStyleSheet(Styles.get_button_style())
        
        # 设置内边距，使文本在按钮中垂直居中
        button.setContentsMargins(0, 0, 0, 0)
        
        return button
        
    def setup_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建OS MOD和WHQL区域
        self.os_mod_panel = self._create_os_mod_panel()
        main_layout.addWidget(self.os_mod_panel)
        
        # 创建底部区域容器
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        # 创建左侧MOD区块 (比例4)
        self.left_block = self._create_mod_block()
        bottom_layout.addWidget(self.left_block, 40)  # 使用40表示4的比例
        
        # 创建中间组件区块 (比例4.5)
        self.middle_block = self._create_component_block()
        bottom_layout.addWidget(self.middle_block, 45)  # 使用45表示4.5的比例
        
        # 创建右侧APP MOD区块 (比例1.5)
        self.right_block = self._create_app_mod_block()
        bottom_layout.addWidget(self.right_block, 15)  # 使用15表示1.5的比例
        
        main_layout.addWidget(bottom_container)
        
        # 添加事件连接
        self.os_mod_combo.currentIndexChanged.connect(self.os_mod_changed.emit)
        
    def _create_os_mod_panel(self):
        """创建OS MOD和WHQL面板"""
        panel = QWidget()
        panel.setFixedHeight(50)  # 设置面板高度为50
        
        # 使用QVBoxLayout作为主布局，便于垂直居中
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除所有边距
        main_layout.setSpacing(0)  # 移除间距
        
        # 创建水平布局用于放置组件
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(10, 0, 5, 0)  # 左、上、右、下边距
        h_layout.setSpacing(5)  # 设置5像素间距
        
        # OS MOD标签
        os_mod_label = self._create_standard_label('OS  MOD')
        h_layout.addWidget(os_mod_label)
        
        # 下拉框，设置最小和最大宽度
        self.os_mod_combo = self._create_standard_combo()
        self.os_mod_combo.setMinimumWidth(180)  # 设置最小宽度
        self.os_mod_combo.setMaximumWidth(300)  # 设置最大宽度
        self.os_mod_combo.currentIndexChanged.connect(self._on_os_mod_changed)
        h_layout.addWidget(self.os_mod_combo)
        
        # 文本框，设置固定宽度
        self.os_mod_text = self._create_standard_text(250)  # 设置宽度为250像素
        self.os_mod_text.setFixedWidth(300)  # 设置固定宽度为300像素
        h_layout.addWidget(self.os_mod_text)
        
        # 添加ADD按钮 - 增加宽度5个像素
        self.os_mod_add_btn = self._create_standard_button("ADD", 85, "add")  # 从80增加到85
        self.os_mod_add_btn.clicked.connect(self._on_os_mod_add_clicked)
        h_layout.addWidget(self.os_mod_add_btn)
        
        # 增加按钮之间的间距
        h_layout.addSpacing(10)  # 添加10像素的间距
        
        # 添加Bypass WHQL按钮
        self.bypass_whql_btn = self._create_standard_button("Bypass WHQL", 100)
        self.bypass_whql_btn.setStyleSheet(Styles.get_toggle_button_style(self._bypass_whql_active))
        self.bypass_whql_btn.clicked.connect(self._on_bypass_whql_clicked)
        h_layout.addWidget(self.bypass_whql_btn)
        
        # 添加弹性空间，使组件靠左对齐
        h_layout.addStretch(1)
        
        # 添加右侧文本输入框和Check按钮
        # 文本输入框 - 可编辑
        self.check_input = self._create_standard_text(120, False)  # 宽度120，非只读
        self.check_input.setPlaceholderText("输入检查值")
        h_layout.addWidget(self.check_input)
        
        # 添加Check按钮
        self.check_btn = self._create_standard_button("Check", 70)
        self.check_btn.clicked.connect(self._on_check_clicked)
        h_layout.addWidget(self.check_btn)
        
        # 将水平布局添加到主布局，并设置垂直居中
        main_layout.addLayout(h_layout)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # 设置样式
        panel.setStyleSheet(Styles.get_os_mod_panel_style())
        
        return panel
        
    def _on_os_mod_add_clicked(self):
        """处理OS MOD ADD按钮点击事件"""
        # 发布事件
        event_bus.publish(OS_MOD_ADD_CLICKED)
        # 为了向后兼容，仍然发射信号
        self.os_mod_add_clicked.emit()
        
    def _create_mod_block(self):
        """创建Platform MOD区块"""
        block = QWidget()
        block.setStyleSheet(Styles.get_mod_block_style())
        
        layout = QVBoxLayout(block)
        layout.setContentsMargins(10, 5, 5, 5)
        layout.setSpacing(5)  # 修改为5像素
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # MOD标签列表
        mod_labels = [
            "BASE NBK", "ASSY MOD", "SRV MOD", "PWA MOD", "PLM MOD",
            "DIMM MOD", "BZL MOD", "KYBD MOD", "NTWK MOD", "SPL1 MOD"
        ]
        
        for text in mod_labels:
            row = self._create_row(text)
            layout.addWidget(row)
        
        # 创建按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)  # 顶部增加一些间距
        
        # 添加按钮
        self.mod_load_btn = self._create_standard_button("LOAD")
        self.mod_load_btn.clicked.connect(self._on_mod_load_clicked)
        
        self.mod_add_btn = self._create_standard_button("ADD", 80, "add")
        self.mod_add_btn.clicked.connect(self._on_mod_add_clicked)
        
        # 添加弹性空间实现居中
        button_layout.addStretch()
        button_layout.addWidget(self.mod_load_btn)
        button_layout.addSpacing(10)  # 按钮之间的间距
        button_layout.addWidget(self.mod_add_btn)
        button_layout.addStretch()
        
        # 将按钮容器添加到主布局
        layout.addWidget(button_container)
            
        # 添加弹性空间
        layout.addStretch()
        return block
        
    def _on_mod_load_clicked(self):
        """处理MOD LOAD按钮点击事件"""
        # 发布事件
        event_bus.publish(MOD_LOAD_CLICKED)
        # 为了向后兼容，仍然发射信号
        self.mod_load_clicked.emit()
    
    def _on_mod_add_clicked(self):
        """处理MOD ADD按钮点击事件"""
        # 发布事件
        event_bus.publish(MOD_ADD_CLICKED)
        # 为了向后兼容，仍然发射信号
        self.mod_add_clicked.emit()
        
    def _create_component_block(self):
        """创建组件区块"""
        block = QWidget()
        block.setStyleSheet(Styles.get_component_block_style())
        
        layout = QVBoxLayout(block)
        layout.setContentsMargins(10, 5, 5, 5)
        layout.setSpacing(5)  # 修改为5像素
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 组件标签列表
        component_labels = [
            "LCD", "WLAN", "WWAN", "SIM Card", "SSD#1", "SSD#2",
            "Battery", "Adaptor", "Other#1", "Other#2"
        ]
        
        for text in component_labels:
            row = self._create_component_row(text)
            layout.addWidget(row)
        
        # 创建按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)  # 顶部增加一些间距
        
        # 添加按钮
        self.keyparts_load_btn = self._create_standard_button("LOAD", 70)
        self.keyparts_load_btn.clicked.connect(self.keyparts_load_clicked.emit)
        
        self.keyparts_search_btn = self._create_standard_button("Search", 70)
        self.keyparts_search_btn.clicked.connect(self.keyparts_search_clicked.emit)
        
        self.keyparts_add_btn = self._create_standard_button("ADD", 70, "add")
        self.keyparts_add_btn.clicked.connect(self.keyparts_add_clicked.emit)
        
        self.keyparts_clear_btn = self._create_standard_button("Clear", 70, "delete")
        self.keyparts_clear_btn.clicked.connect(self.keyparts_clear_clicked.emit)
        
        # 添加弹性空间实现居中
        button_layout.addStretch()
        button_layout.addWidget(self.keyparts_load_btn)
        button_layout.addSpacing(5)  # 按钮之间的间距
        button_layout.addWidget(self.keyparts_search_btn)
        button_layout.addSpacing(5)  # 按钮之间的间距
        button_layout.addWidget(self.keyparts_add_btn)
        button_layout.addSpacing(5)  # 按钮之间的间距
        button_layout.addWidget(self.keyparts_clear_btn)
        button_layout.addStretch()
        
        # 将按钮容器添加到主布局
        layout.addWidget(button_container)
            
        layout.addStretch()
        return block
        
    def _create_row(self, text):
        """创建MOD行"""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 标签
        label = self._create_standard_label(text)
        layout.addWidget(label)
        
        # 下拉框
        combo = self._create_standard_combo(180)  # 使用标准下拉框，最小宽度180
        layout.addWidget(combo)
        self.mod_combos[text] = combo
        
        # 文本显示框
        text_box = self._create_standard_text(80)  # 使用标准文本框，宽度80
        layout.addWidget(text_box)
        self.mod_texts[text] = text_box
        
        return row
        
    def _create_component_row(self, text):
        """创建组件行"""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 标签
        label = self._create_standard_label(text)
        layout.addWidget(label)
        
        # 文本输入框
        input_box = self._create_standard_text(80, False)  # 使用标准文本框，宽度80，非只读
        layout.addWidget(input_box)
        self.component_inputs[text] = input_box
        
        # 下拉框
        combo = self._create_standard_combo(100)  # 使用标准下拉框，最小宽度100
        layout.addWidget(combo)
        self.component_combos[text] = combo
        
        # 文本显示框
        text_box = self._create_standard_text(80)  # 使用标准文本框，宽度80
        layout.addWidget(text_box)
        self.component_texts[text] = text_box
        
        return row

    def _create_app_mod_block(self):
        """创建APP MOD区块"""
        block = QWidget()
        block.setStyleSheet(Styles.get_right_block_style())
        
        layout = QVBoxLayout(block)
        layout.setContentsMargins(10, 5, 5, 5)  # 与其他区块保持一致的内边距
        layout.setSpacing(5)  # 修改为5像素
        
        # 首先添加一些顶部空间
        layout.addStretch(1)
        
        # 创建文本框容器，用于水平居中
        text_container = QWidget()
        text_layout = QHBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        
        # 添加文本输入框
        self.app_mod_text = QTextEdit()  # 改为QTextEdit以支持多行文本
        self.app_mod_text.setFixedHeight(300)  # 进一步增加高度
        self.app_mod_text.setFixedWidth(140)  # 设置固定宽度，方便居中显示
        self.app_mod_text.setPlaceholderText("App MOD信息")
        self.app_mod_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 1px solid #4a90e2;
            }
        """)
        
        # 通过在文本框两侧添加弹性空间实现居中
        text_layout.addStretch()
        text_layout.addWidget(self.app_mod_text)
        text_layout.addStretch()
        
        # 将文本框容器添加到主布局
        layout.addWidget(text_container)
        
        # 添加伸缩空间，将按钮放在中间位置
        layout.addStretch(2)
        
        # 创建按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)  # 移除所有内边距
        
        # 添加按钮
        self.app_mod_add_btn = self._create_standard_button("ADD", 70, "add")
        # 确保所有控件高度一致
        self.app_mod_add_btn.setFixedHeight(25)  # 与其他控件保持一致的高度
        self.app_mod_add_btn.clicked.connect(self.app_mod_add_clicked.emit)
        
        # 添加弹性空间实现居中
        button_layout.addStretch()
        button_layout.addWidget(self.app_mod_add_btn)
        button_layout.addStretch()
        
        # 将按钮容器添加到主布局
        layout.addWidget(button_container)
        
        # 底部留出一些空间
        layout.addStretch(2)
        
        return block 

    def update_os_mod_combo(self, options=None):
        """更新下拉框的OS MOD选项列表
        
        Args:
            options (list): 选项列表，如果为None则自动获取
        
        Returns:
            bool: 是否成功更新
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not hasattr(self, 'os_mod_combo'):
            logger.error("os_mod_combo不存在，无法更新")
            return False
            
        # 如果没有提供选项，则尝试从模型获取
        if options is None:
            try:
                from models.os_mod_model import OSModModel
                model = OSModModel(event_bus)
                options = model.get_options()
                logger.info(f"自动获取OS MOD选项: {options}")
            except Exception as e:
                logger.error(f"获取选项出错: {str(e)}")
                return False
                
        # 检查选项是否有效
        if not options:
            logger.warning("选项列表为空，无法更新下拉框")
            return False
            
        # 更新下拉框
        try:
            self.os_mod_combo.clear()
            
            # 添加一个空选项作为默认选项
            self.os_mod_combo.addItem("")
            
            # 添加其他选项
            self.os_mod_combo.addItems(options)
            
            logger.info(f"成功更新OS MOD下拉框，共{len(options)+1}个选项")
            return True
        except Exception as e:
            logger.error(f"更新下拉框出错: {str(e)}")
            return False

    def _on_bypass_whql_clicked(self):
        """处理Bypass WHQL按钮点击事件"""
        # 切换状态
        self._bypass_whql_active = not self._bypass_whql_active
        
        # 更新按钮样式
        self.bypass_whql_btn.setStyleSheet(Styles.get_toggle_button_style(self._bypass_whql_active))
        
        # 发送信号
        event_bus.publish(BYPASS_WHQL_CLICKED, self._bypass_whql_active)
        self.bypass_whql_clicked.emit(self._bypass_whql_active) 

    def _on_check_clicked(self):
        """处理Check按钮点击事件"""
        check_value = self.check_input.text()
        # 只保留信号方式，移除事件总线发布
        # event_bus.publish(CHECK_CLICKED, check_value)
        self.check_clicked.emit(check_value) 