#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OS MOD 数据模型

该模块负责读取和解析OS.INI文件，提供OS MOD选项和对应的参数。
"""

import os
import logging
import configparser
from PyQt6.QtCore import QObject, pyqtSignal

from utils.event_bus import event_bus
from utils.event_constants import (
    OS_MOD_OPTIONS_UPDATED,
    OS_MOD_SELECTED,
    ERROR_OCCURRED
)

logger = logging.getLogger(__name__)

class OSModModel(QObject):
    """OS MOD数据模型类，用于管理OS.INI文件中的OS MOD选项"""
    
    # 单例实例
    _instance = None
    
    # 信号定义
    options_updated = pyqtSignal(list)  # OS MOD选项更新信号
    
    def __new__(cls, event_bus_instance=None):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super(OSModModel, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, event_bus_instance=None):
        """初始化OS MOD模型
        
        Args:
            event_bus_instance: 事件总线实例，如果为None则使用全局实例
        """
        # 避免重复初始化
        if getattr(self, '_initialized', False):
            logger.debug("OSModModel已经初始化，跳过")
            return
            
        super().__init__()
        
        # 设置事件总线
        self.event_bus = event_bus_instance if event_bus_instance else event_bus
        
        # 初始化数据
        self.options = []
        self.parameters = {}
        self._is_updating = False
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 配置文件路径
        self.ini_path = os.path.join('config', 'OS.INI')
        
        # 初始化时加载数据
        self._load_os_ini()
        
        # 标记为已初始化
        self._initialized = True
        
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(OS_MOD_SELECTED, self._handle_os_mod_selected)
        
    def _handle_os_mod_selected(self, index):
        """处理OS MOD选择事件
        
        Args:
            index: 选择的选项索引，可能是整数或字符串
        """
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            
            # 确保index是整数类型
            try:
                index = int(index)
            except (ValueError, TypeError):
                logger.warning(f"无效的索引值: {index}，已跳过处理")
                return
                
            if 0 <= index < len(self.options):
                selected = self.options[index]
                parameters = self.parameters.get(selected, {})
                # 发布参数更新事件
                self.event_bus.publish(OS_MOD_OPTIONS_UPDATED, parameters)
        except Exception as e:
            logger.error(f"处理OS MOD选择事件时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.event_bus.publish(ERROR_OCCURRED, f"处理OS MOD选择事件时出错: {str(e)}")
        finally:
            self._is_updating = False
            
    def _load_os_ini(self):
        """加载并解析OS.INI文件"""
        try:
            # 检查文件是否存在
            logger.info(f"尝试加载OS.INI文件: {self.ini_path}")
            if not os.path.exists(self.ini_path):
                logger.error(f"OS.INI文件不存在: {self.ini_path}")
                return False
            
            logger.info(f"OS.INI文件存在，开始解析")
                
            # 创建配置解析器
            config = configparser.ConfigParser()
            # 保留原始大小写
            config.optionxform = str
            
            # 读取INI文件
            config.read(self.ini_path, encoding='utf-8')
            
            # 检查解析结果
            sections = config.sections()
            logger.info(f"解析到以下节: {sections}")
            
            # 清空当前数据
            self.sections = {}
            
            # 提取所有有效的节和参数
            valid_sections = {}
            for section in sections:
                # 跳过空节或只包含空格的节
                if not section or section.isspace():
                    logger.warning(f"跳过无效的节名: '{section}'")
                    continue
                    
                # 获取节的所有参数
                params = dict(config[section])
                # 只保存有参数的节，或者是特殊节（如Ubuntu）
                if params or section in ['Ubuntu', 'Ubuntu2']:
                    valid_sections[section] = params
                    logger.info(f"添加有效节 '{section}' 及其参数: {params}")
                else:
                    logger.warning(f"跳过空节: '{section}'")
            
            # 更新sections
            self.sections = valid_sections
            
            # 提取节名作为选项列表
            self.options = list(self.sections.keys())
            logger.info(f"最终的有效选项列表: {self.options}")
            
            if not self.options:
                logger.warning("没有找到有效的OS MOD选项")
                return False
            
            # 发布选项更新事件
            logger.info(f"发布选项更新信号，选项数量: {len(self.options)}")
            self.options_updated.emit(self.options)
            
            # 发布事件总线事件
            logger.info("发布事件总线事件: OS_MOD_OPTIONS_UPDATED")
            self.event_bus.publish(OS_MOD_OPTIONS_UPDATED, self.options)
            
            # 提取参数
            self.parameters = {option: self.sections[option] for option in self.sections}
            
            logger.info(f"成功加载 {len(self.options)} 个OS MOD选项")
            return True
            
        except Exception as e:
            logger.error(f"加载OS.INI文件时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def get_options(self):
        """获取OS MOD选项列表"""
        try:
            # 直接返回从INI文件读取的选项
            if not self.options:
                self._load_os_ini()
            return self.options
        except Exception as e:
            error_msg = f"获取OS MOD选项时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return []
    
    def get_params(self, option):
        """获取指定选项的参数"""
        if option in self.sections:
            return self.sections[option]
        return {}
    
    def get_params_text(self, option):
        """获取选项对应的参数文本"""
        try:
            # 使用self.sections而不是self.parameters，保持与get_params方法一致
            if option in self.sections:
                params = self.sections[option]
                return " ".join([f"{k}={v}" for k, v in params.items()])
            
            # 如果在sections中找不到，尝试在parameters中查找（向后兼容）
            if hasattr(self, 'parameters') and option in self.parameters:
                params = self.parameters[option]
                return " ".join([f"{k}={v}" for k, v in params.items()])
                
            return ""
        except Exception as e:
            error_msg = f"获取OS MOD参数时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return ""
    
    def get_os_mod_by_index(self, index):
        """根据索引获取OS MOD信息
        
        Args:
            index: 选项索引，可能是整数或字符串
            
        Returns:
            dict: 包含选项名称和参数的字典，如果索引无效则返回None
        """
        try:
            # 确保index是整数类型
            try:
                index = int(index)
            except (ValueError, TypeError):
                logger.warning(f"无效的索引值: {index}，无法获取OS MOD信息")
                return None
                
            if 0 <= index < len(self.options):
                selected = self.options[index]
                # 优先使用sections中的参数
                parameters = self.sections.get(selected, {})
                # 如果sections中没有，尝试从parameters中获取（向后兼容）
                if not parameters and hasattr(self, 'parameters'):
                    parameters = self.parameters.get(selected, {})
                return {
                    'name': selected,
                    'parameters': parameters
                }
            return None
        except Exception as e:
            logger.error(f"获取OS MOD信息时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None 