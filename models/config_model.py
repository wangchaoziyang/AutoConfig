#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置数据模型

该模块负责处理配置数据的加载、存储和操作。
"""

import os
import sys
import logging
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from processors.config_processor import ConfigProcessor
from utils.event_bus import event_bus
from utils.event_constants import (
    CONFIG_FILE_SELECTED,
    CONFIG_FILE_LOADED,
    SHEET_SELECTED,
    SHEET_LIST_UPDATED,
    PN_SELECTED,
    PN_LIST_UPDATED,
    CONFIG_DETAILS_UPDATED,
    ERROR_OCCURRED
)

logger = logging.getLogger(__name__)

class ConfigModel(QObject):
    """配置数据模型，负责处理配置数据"""
    
    # 定义信号
    file_loaded = pyqtSignal(str)  # 文件加载完成信号，参数为文件路径
    sheet_list_updated = pyqtSignal(list)  # 工作表列表更新信号
    pn_list_updated = pyqtSignal(list)  # PN列表更新信号
    config_details_updated = pyqtSignal(pd.DataFrame)  # 配置详情更新信号
    error_occurred = pyqtSignal(str)  # 错误信号，参数为错误信息
    
    def __init__(self, event_bus_instance=None):
        super().__init__()
        self.processor = ConfigProcessor()
        self.file_path = None
        self.current_sheet = None
        self.current_pn = None
        self.config_data = None
        self.component_keywords = [
            "CPU", 
            "GPU", 
            "Memory", 
            "LCD", 
            "WLAN", 
            "WWAN", 
            "SSD", 
            "Battery", 
            "Adaptor", 
            "KeyBoard", 
            "USH", 
            "Finger Print", 
            "Smart Card", 
            "RFID",
            "FIPS"
        ]
        
        # 设置事件总线
        self.event_bus = event_bus_instance if event_bus_instance else event_bus
        self._register_event_handlers()
        
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(CONFIG_FILE_SELECTED, self._handle_config_file_selected)
        self.event_bus.subscribe(SHEET_SELECTED, self._handle_sheet_selected)
        self.event_bus.subscribe(PN_SELECTED, self._handle_pn_selected)
        
    def _handle_config_file_selected(self, file_path):
        """处理配置文件选择事件"""
        try:
            self.load_file(file_path)
        except Exception as e:
            error_msg = f"处理配置文件选择事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        
    def _handle_sheet_selected(self, sheet_name):
        """处理工作表选择事件"""
        try:
            # 获取P/N列表
            pn_list = self.processor.get_pn_list(sheet_name)
            # 发布P/N列表更新事件
            self.event_bus.publish(PN_LIST_UPDATED, pn_list)
        except Exception as e:
            error_msg = f"获取P/N列表时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        
    def _handle_pn_selected(self, pn):
        """处理P/N选择事件"""
        try:
            # 获取配置详情
            config_details = self.processor.get_config_details(pn)
            # 发布配置详情更新事件
            self.event_bus.publish(CONFIG_DETAILS_UPDATED, config_details)
        except Exception as e:
            error_msg = f"获取配置详情时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        
    def load_file_sheets_only(self, file_path):
        """只加载配置文件的工作表列表，不进行数据分析
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            bool: 是否成功加载工作表列表
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
                
            # 检查文件扩展名
            if not file_path.endswith(('.xlsx', '.xlsm')):
                error_msg = f"不支持的文件类型: {file_path}"
                logger.error(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
                
            # 尝试加载Excel文件
            try:
                # 使用pandas读取Excel文件的工作表列表
                import pandas as pd
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                
                # 过滤出包含"_config"的工作表
                config_sheets = [sheet for sheet in sheet_names if "_config" in sheet.lower()]
                
                # 如果没有找到包含"_config"的工作表，则使用所有工作表
                if not config_sheets:
                    logger.warning(f"未找到包含'_config'的工作表，将使用所有工作表")
                    config_sheets = sheet_names
                
                # 设置文件路径
                self.file_path = file_path
                
                # 更新工作表列表
                self.sheet_list = config_sheets
                
                # 发送工作表列表更新信号
                self.sheet_list_updated.emit(config_sheets)
                self.event_bus.publish(SHEET_LIST_UPDATED, config_sheets)
                
                logger.info(f"成功加载配置文件工作表列表: {file_path}, 找到 {len(config_sheets)} 个包含'_config'的工作表")
                return True
                
            except Exception as e:
                error_msg = f"读取Excel文件工作表列表失败: {str(e)}"
                logger.error(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"加载配置文件工作表列表时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False
    
    def load_file(self, file_path, load_data=True):
        """加载配置文件
        
        Args:
            file_path: 配置文件路径
            load_data: 是否加载数据，默认为True。如果为False，则只加载工作表列表，不进行数据提取
            
        Returns:
            bool: 是否成功加载
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
                
            # 检查文件扩展名
            if not file_path.endswith(('.xlsx', '.xlsm')):
                error_msg = f"不支持的文件类型: {file_path}"
                logger.error(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
                
            # 尝试加载Excel文件
            try:
                # 先加载Excel文件，该方法返回配置工作表列表
                config_sheets = self.processor.load_excel_file(file_path)
                
                # 设置文件路径
                self.file_path = file_path
                
                # 如果没有找到配置工作表，则返回错误
                if not config_sheets:
                    error_msg = "未找到包含'config'的工作表"
                    logger.error(error_msg)
                    self.event_bus.publish(ERROR_OCCURRED, error_msg)
                    return False
            except Exception as e:
                error_msg = f"读取Excel文件失败: {str(e)}"
                logger.error(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
            
            # 更新工作表列表
            self.sheet_list = config_sheets
            
            # 发送工作表列表更新信号
            self.sheet_list_updated.emit(config_sheets)
            self.event_bus.publish(SHEET_LIST_UPDATED, config_sheets)
            
            # 发布文件加载成功事件
            self.event_bus.publish(CONFIG_FILE_LOADED, file_path)
            
            # 如果不需要加载数据，则到此为止
            if not load_data:
                logger.info(f"已加载工作表列表，共 {len(config_sheets)} 个工作表")
                return True
                
            # 如果需要加载数据，则选择第一个工作表并加载数据
            if config_sheets:
                self.select_sheet(config_sheets[0], analyze_data=load_data)
            
            return True
            
        except Exception as e:
            error_msg = f"加载配置文件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False
    
    def select_sheet(self, sheet_name, analyze_data=True):
        """选择工作表
        
        Args:
            sheet_name: 工作表名称
            analyze_data: 是否分析数据，默认为True。如果为False，则只设置当前工作表而不进行数据分析
        """
        try:
            self.current_sheet = sheet_name
            
            # 如果不需要分析数据，则到此为止
            if not analyze_data:
                logger.info(f"已选择工作表: {sheet_name}，不进行数据分析")
                return True
                
            # 加载选中sheet的数据
            if self.file_path and sheet_name:
                self.processor.load_sheet_data(self.file_path, sheet_name)
                
            pn_list = self.processor.get_pn_list(sheet_name)
            
            # 发送PN列表更新事件
            self.pn_list_updated.emit(pn_list)
            self.event_bus.publish(PN_LIST_UPDATED, pn_list)
            
            logger.info(f"已选择工作表: {sheet_name}")
            return True
        except Exception as e:
            error_msg = f"选择工作表时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False
    
    def select_pn(self, pn):
        """选择系统P/N"""
        try:
            self.current_pn = pn
            config_details = self.processor.get_config_details(pn)
            
            if config_details is not None:
                self.config_data = config_details
                
                # 发送配置详情更新事件
                self.config_details_updated.emit(config_details)
                self.event_bus.publish(CONFIG_DETAILS_UPDATED, config_details)
                
                logger.info(f"已选择系统P/N: {pn}")
                return True
            else:
                error_msg = f"找不到系统P/N的配置详情: {pn}"
                logger.warning(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
        except Exception as e:
            error_msg = f"选择系统P/N时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False
    
    def get_current_pn(self):
        """获取当前选择的系统P/N"""
        return self.current_pn 
    
    def get_pn_list(self):
        """获取当前工作表的P/N列表
        
        Returns:
            list: 系统P/N列表
        """
        if not self.current_sheet:
            logger.warning("尚未选择工作表，无法获取P/N列表")
            return []
            
        try:
            return self.processor.get_pn_list(self.current_sheet)
        except Exception as e:
            logger.error(f"获取P/N列表时出错: {str(e)}")
            return []
        
    def get_sheet_list(self):
        """获取工作表列表
        
        Returns:
            list: 工作表名称列表
        """
        if not self.processor or not self.file_path:
            logger.warning("尚未加载配置文件，无法获取工作表列表")
            return []
            
        try:
            return self.processor.get_sheet_names()
        except Exception as e:
            logger.error(f"获取工作表列表时出错: {str(e)}")
            return []
    
    def get_current_file_path(self):
        """获取当前加载的文件路径
        
        Returns:
            str: 文件路径，如果未加载则返回None
        """
        return self.file_path
        
    def get_component_keywords(self):
        """获取组件关键字列表"""
        return self.component_keywords 