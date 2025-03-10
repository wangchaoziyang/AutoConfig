#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口视图模块

该模块包含应用程序的主窗口UI类，负责显示和组织各个UI组件。
"""

import os
import logging
import pandas as pd
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QSplitter, QMessageBox,
    QApplication, QFileDialog, QLabel, QComboBox, QLineEdit, 
    QCheckBox, QSizePolicy, QStatusBar
)
from PyQt6.QtCore import Qt, QSize, QTimer, QEvent
from PyQt6.QtGui import QResizeEvent

from ui.components import ControlPanel, ModulePanel
from ui.config_table import ConfigTable
from ui.styles import Styles
from utils.event_bus import EventBus, EventType

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self, controller=None):
        """初始化主窗口"""
        super().__init__()
        
        # 设置控制器引用
        self.controller = controller
        
        # 设置窗口标题
        self.setWindowTitle('自动化配置工具')
        
        # 初始化窗口几何
        self._setup_window_geometry()
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 设置UI组件
        self.setup_ui(layout)
        
        # 窗口最大化
        self.showMaximized()
    
    def _setup_window_geometry(self):
        """设置窗口几何属性"""
        # 设置窗口大小策略
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        
        # 设置窗口最小尺寸为屏幕尺寸的75%
        min_width = int(screen_size.width() * 0.75)
        min_height = int(screen_size.height() * 0.75)
        self.setMinimumSize(QSize(min_width, min_height))
        
    def setup_ui(self, layout):
        """设置UI界面"""
        # 创建主分割器
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setChildrenCollapsible(False)
        
        # 创建顶部控制面板
        self.control_panel = ControlPanel()
        main_splitter.addWidget(self.control_panel)
        
        # 创建配置表格
        self.config_table = ConfigTable()
        main_splitter.addWidget(self.config_table)
        
        # 创建模块面板
        self.module_panel = ModulePanel()
        main_splitter.addWidget(self.module_panel)
        
        # 设置分割器大小策略 - 使用屏幕高度的百分比
        screen_height = QApplication.primaryScreen().availableGeometry().height()
        main_splitter.setSizes([
            int(screen_height * 0.05),  # 顶部区域 5%
            int(screen_height * 0.40),  # 表格区域 40%
            int(screen_height * 0.55)   # 模块面板区域 55%
        ])
        
        # 设置分割器的伸缩因子
        main_splitter.setStretchFactor(0, 1)   # 顶部区域
        main_splitter.setStretchFactor(1, 8)   # 表格区域
        main_splitter.setStretchFactor(2, 11)  # 模块面板区域
        
        # 将主分割器添加到布局
        layout.addWidget(main_splitter)
        
        # 设置样式
        self.setStyleSheet(Styles.get_main_window_style())
        
        # 设置信号连接
        self._connect_signals()
        
        # 显式更新OS MOD下拉框
        logger.info("显式更新OS MOD下拉框")
        
        # 延迟一点时间再更新，确保UI已完全初始化
        QTimer.singleShot(100, self._update_os_mod_combo)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接控制面板信号
        if self.control_panel:
            self.control_panel.file_selected.connect(lambda file_path: self.controller.select_config_file(file_path) if self.controller else None)
            self.control_panel.sheet_changed.connect(lambda index: self.controller.select_sheet(self.control_panel.sheet_combo.currentText()) if self.controller and index >= 0 else None)
            self.control_panel.pn_changed.connect(lambda index: self.controller.select_pn(self.control_panel.pn_combo.currentText()) if self.controller and index >= 0 else None)
            # 注释掉这行，因为我们已经通过事件总线处理了这个事件
            # self.control_panel.load_phbom_clicked.connect(lambda: self.controller.load_phbom() if self.controller else None)
            # self.control_panel.clear_mod_clicked.connect(lambda: self.controller.clear_mod_file() if self.controller else None)
            # self.control_panel.generate_clicked.connect(lambda: self.controller.generate_content() if self.controller else None)

        # 连接模块面板信号
        if self.module_panel:
            self.module_panel.os_mod_changed.connect(self.on_os_mod_changed)
            self.module_panel.bypass_whql_clicked.connect(self.on_bypass_whql_clicked)
            self.module_panel.check_clicked.connect(self.on_check_clicked)
            self.module_panel.mod_load_clicked.connect(lambda: self.controller.load_mod_data() if self.controller else None)
            self.module_panel.mod_add_clicked.connect(lambda: self.controller.add_mod_data() if self.controller else None)
            self.module_panel.keyparts_load_clicked.connect(lambda: self.controller.keyparts_load_data() if self.controller else None)
            self.module_panel.keyparts_search_clicked.connect(lambda: self.controller.keyparts_search_data() if self.controller else None)
            self.module_panel.keyparts_add_clicked.connect(lambda: self.controller.keyparts_add_data() if self.controller else None)
            self.module_panel.keyparts_clear_clicked.connect(lambda: self.controller.keyparts_clear_data() if self.controller else None)
            self.module_panel.app_mod_add_clicked.connect(lambda: self.controller.app_mod_add_data() if self.controller else None)
        
    def update_display_box(self, text):
        """更新显示框内容（已弃用）
        
        由于已删除显示框，此方法仅记录信息到日志
        """
        logger.info(f"显示信息: {text}")
    
    def update_config_table(self, config_data, pn, component_keywords):
        """更新配置表格"""
        if hasattr(self, 'config_table'):
            self.config_table.update_content(config_data, pn, component_keywords)
        
    def select_file(self, file_path):
        """选择配置文件"""
        if self.controller:
            self.controller.select_config_file(file_path)
                
    def on_sheet_changed(self, index):
        """处理工作表变更事件"""
        if self.controller:
            self.controller._on_sheet_changed(index)
            
    def on_pn_changed(self, index):
        """处理P/N变更事件"""
        if self.controller:
            self.controller._on_pn_changed(index)
            
    def update_pn_list(self, sheet_name=None):
        """更新System P/N下拉框"""
        try:
            # 清空下拉框
            self.control_panel.pn_combo.clear()

            # 如果没有提供sheet_name，则使用当前选中的工作表
            if sheet_name is None:
                index = self.control_panel.sheet_combo.currentIndex()
                if index >= 0:
                    sheet_name = self.control_panel.sheet_combo.itemText(index)
                    # 通过控制器获取PN列表
                    if hasattr(self, 'controller') and self.controller is not None:
                        # 控制器会处理PN列表的更新，并通过模型的信号通知UI
                        self.controller.select_sheet(sheet_name)
                        return True
                return False
            
            # 如果提供了sheet_name，直接使用
            if hasattr(self, 'controller') and self.controller is not None:
                # 控制器会处理PN列表的更新，并通过模型的信号通知UI
                self.controller.select_sheet(sheet_name)
                return True
            return False
        except Exception as e:
            logger.error(f"更新System P/N列表时出错: {str(e)}")
            QMessageBox.critical(self, '错误', f"更新System P/N列表时出错: {str(e)}")
            return False
        
    def show_config_details(self, pn):
        """显示选中System P/N的配置详情"""
        try:
            # 通过控制器获取配置详情
            if hasattr(self, 'controller') and self.controller is not None:
                # 控制器会处理配置详情的更新，并通过模型的信号通知UI
                self.controller.select_pn(pn)
                return True
        except Exception as e:
            logger.error(f"显示配置详情时出错: {str(e)}")
            QMessageBox.critical(self, '错误', f"显示配置详情时出错: {str(e)}")
            return False
        return False

    def clear_mod_file(self):
        """清除MOD文件"""
        if self.controller:
            self.controller.clear_mod_file()
            
    def load_phbom(self):
        """加载PHBOM文件"""
        if self.controller:
            self.controller.load_phbom()
            
    def generate_content(self):
        """生成内容"""
        if self.controller:
            self.controller.generate_content()
            
    def resizeEvent(self, event: QResizeEvent):
        """处理窗口大小变化事件"""
        super().resizeEvent(event)
        
        # 获取当前窗口尺寸
        width = event.size().width()
        height = event.size().height()
        
        # 根据窗口大小动态调整UI组件
        if width < 1200:
            # 小窗口模式
            if hasattr(self, 'module_panel'):
                self.module_panel.os_mod_combo.setFixedWidth(127)
                self.module_panel.os_mod_text.setFixedWidth(300)
        else:
            # 大窗口模式
            if hasattr(self, 'module_panel'):
                self.module_panel.os_mod_combo.setMinimumWidth(157)
                self.module_panel.os_mod_combo.setMaximumWidth(277)
                self.module_panel.os_mod_text.setMinimumWidth(350)
                self.module_panel.os_mod_text.setMaximumWidth(450)
        
        # 动态调整表格列宽
        if hasattr(self, 'config_table') and hasattr(self.config_table, 'table'):
            table = self.config_table.table
            available_width = table.width() - 20  # 预留一些边距
            # 组件名称和P/N列分别占15%
            component_width = int(available_width * 0.15)  # 组件列宽15%
            pn_width = int(available_width * 0.15)       # P/N列宽15%
            
            # 设置列宽
            table.setColumnWidth(0, component_width)  # 左侧组件列
            table.setColumnWidth(2, pn_width)        # 左侧P/N列
            table.setColumnWidth(3, component_width)  # 右侧组件列
            table.setColumnWidth(5, pn_width)        # 右侧P/N列
            
            # 规格列自动拉伸
            # 在QHeaderView中已设置为Stretch模式，会自动调整
    
    def _update_os_mod_combo(self):
        """更新OS MOD下拉框"""
        logger.info("更新OS MOD下拉框")
        if self.controller and self.module_panel:
            # 获取OS MOD选项
            options = self.controller.os_mod_model.get_options()
            if options:
                self.module_panel.update_os_mod_combo(options)
                logger.info(f"OS MOD下拉框已更新，选项数量: {len(options)}")
            else:
                logger.warning("未获取到OS MOD选项")
                
    def on_sheet_changed(self, index):
        """处理工作表变更事件"""
        if self.controller:
            self.controller._on_sheet_changed(index)
            
    def on_pn_changed(self, index):
        """处理P/N变更事件"""
        if self.controller:
            self.controller._on_pn_changed(index)
            
    def on_os_mod_changed(self, index):
        """处理OS MOD下拉框选择变化"""
        if self.controller and index >= 0:
            self.controller.on_os_mod_changed(index)
            
    def on_bypass_whql_clicked(self, is_active):
        """处理Bypass WHQL按钮点击事件"""
        if self.controller:
            self.controller.on_bypass_whql_clicked(is_active)
            
    def on_check_clicked(self, check_value):
        """处理Check按钮点击事件"""
        if self.controller:
            self.controller.check_number(check_value) 