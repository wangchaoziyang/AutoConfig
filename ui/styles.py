#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
样式表模块

该模块集中管理所有UI组件的样式，提高样式一致性和维护性。
"""

class Styles:
    """样式类，包含所有UI组件的样式定义"""
    
    @staticmethod
    def get_control_panel_style():
        """获取控制面板样式"""
        return """
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
            }
            QLabel {
                font-size: 12px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #0d8aee;
            }
            QPushButton:pressed {
                background-color: #0c7cd5;
            }
            QComboBox {
                background-color: white;
                border: 1px solid black;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-height: 25px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 1px solid #0078d4;
            }
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border: none;
                background-color: transparent;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
                margin-right: 6px;
            }
            QComboBox::down-arrow:hover {
                border-top: 6px solid #0078d4;
            }
            QComboBox QAbstractItemView {
                border: 1px solid black;
                selection-background-color: #0078d4;
                selection-color: white;
                background-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                padding: 2px 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e5f3ff;
            }
            QComboBox:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
        """
    
    @staticmethod
    def get_button_panel_style():
        """获取按钮面板样式"""
        return """
            QWidget {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #0d8aee;
            }
            QPushButton:pressed {
                background-color: #0c7cd5;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 1px 5px;
                min-height: 25px;
            }
        """
    
    @staticmethod
    def get_os_mod_panel_style():
        """获取OS MOD面板样式"""
        return """
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 1px solid #ddd;
            }
            QLabel, QComboBox, QLineEdit, QPushButton {
                margin: 0px;
                padding: 0px;
            }
        """
    
    @staticmethod
    def get_mod_block_style():
        """获取MOD区块样式"""
        return """
            background-color: #e6f3ff;
            padding: 5px;
        """
    
    @staticmethod
    def get_component_block_style():
        """获取组件区块样式"""
        return """
            background-color: #fff7e6;
            padding: 5px;
        """
    
    @staticmethod
    def get_right_block_style():
        """获取右侧区块样式"""
        return """
            background-color: #e6ffe6;
        """
    
    @staticmethod
    def get_label_style():
        """获取标签样式"""
        return """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                line-height: 25px;
                qproperty-alignment: 'AlignVCenter';
            }
        """
    
    @staticmethod
    def get_combobox_style():
        """获取下拉框样式"""
        return """
            QComboBox {
                background-color: white;
                border: 1px solid black;
                border-radius: 3px;
                padding: 0px 5px;
                margin: 0px;
                min-height: 25px;
                max-height: 25px;
                font-size: 12px;
                line-height: 25px;
            }
            QComboBox:hover {
                border: 1px solid #0078d4;
            }
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border: none;
                background-color: transparent;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
                margin-right: 6px;
            }
            QComboBox::down-arrow:hover {
                border-top: 6px solid #0078d4;
            }
            QComboBox QAbstractItemView {
                border: 1px solid black;
                selection-background-color: #0078d4;
                selection-color: white;
                background-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                padding: 2px 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e5f3ff;
            }
            QComboBox:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
        """
    
    @staticmethod
    def get_lineedit_style():
        """获取文本框样式"""
        return """
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 0px 5px;
                margin: 0px;
                min-height: 25px;
                max-height: 25px;
                line-height: 25px;
                qproperty-alignment: 'AlignVCenter';
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
        """
    
    @staticmethod
    def get_button_style():
        """获取按钮样式"""
        return """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 0px;
                min-height: 25px;
                max-height: 25px;
                line-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0d8aee;
            }
            QPushButton:pressed {
                background-color: #0c7cd5;
            }
        """
        
    @staticmethod
    def get_add_button_style():
        """获取添加按钮样式"""
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0px;
                min-height: 25px;
                max-height: 25px;
                line-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        
    @staticmethod
    def get_delete_button_style():
        """获取删除按钮样式"""
        return """
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """
    
    @staticmethod
    def get_main_window_style():
        """获取主窗口样式"""
        return """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QSplitter::handle {
                background-color: #cccccc;
                height: 1px;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
        """
        
    @staticmethod
    def get_toggle_button_style(is_active=False):
        """获取可切换按钮样式，默认红色，激活后为绿色
        
        @param {bool} is_active - 是否处于激活状态
        @return {str} - 按钮样式
        """
        if is_active:
            # 激活状态 - 绿色
            return """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 0px;
                    min-height: 25px;
                    max-height: 25px;
                    line-height: 25px;
                    text-align: center;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """
        else:
            # 未激活状态 - 红色
            return """
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 0px;
                    min-height: 25px;
                    max-height: 25px;
                    line-height: 25px;
                    text-align: center;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e53935;
                }
                QPushButton:pressed {
                    background-color: #d32f2f;
                }
            """ 