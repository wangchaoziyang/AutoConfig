#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PHBOM数据模型

该模块负责处理PHBOM数据的加载、存储和操作。
"""

import os
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog

from processors.phbom_processor import PHBOMProcessor
from utils.event_bus import event_bus
from utils.event_constants import (
    PHBOM_FILE_SELECTED,
    PHBOM_FILE_LOADED,
    PHBOM_DATA_UPDATED,
    ERROR_OCCURRED
)

logger = logging.getLogger(__name__)

class PHBOMModel(QObject):
    """PHBOM数据模型类，用于管理PHBOM数据"""
    
    # 信号定义
    file_loaded = pyqtSignal(str)  # 文件加载成功信号
    data_processed = pyqtSignal(bool)  # 数据处理成功信号
    
    def __init__(self, event_bus_instance=None):
        """初始化PHBOM模型
        
        Args:
            event_bus_instance: 事件总线实例，如果为None则使用全局实例
        """
        super().__init__()
        
        # 设置事件总线
        self.event_bus = event_bus_instance if event_bus_instance else event_bus
        self._register_event_handlers()
        
        # 初始化处理器
        self.processor = PHBOMProcessor()
        
        # 当前文件路径
        self.current_file = None
        
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(PHBOM_FILE_SELECTED, self._handle_phbom_file_selected)
        
    def _handle_phbom_file_selected(self, file_path):
        """处理PHBOM文件选择事件"""
        try:
            # 发布文件选择事件
            self.event_bus.publish(PHBOM_FILE_SELECTED, file_path)
            
            # 加载文件
            if self.load_phbom_file(file_path):
                # 发布文件加载成功事件
                self.event_bus.publish(PHBOM_FILE_LOADED, file_path)
                # 发布数据更新事件
                self.event_bus.publish(PHBOM_DATA_UPDATED, True)
            else:
                error_msg = "加载PHBOM文件失败"
                logger.error(error_msg)
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                
        except Exception as e:
            error_msg = f"处理PHBOM文件选择事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            
    def load_phbom_file(self, file_path):
        """加载并处理PHBOM文件
        
        Args:
            file_path: PHBOM文件路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                # 发布错误事件
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
                
            logger.info(f"开始处理PHBOM文件: {file_path}")
            
            # 处理文件
            success, result = self.processor.process_file(file_path)
            
            if success:
                # 保存当前文件路径
                self.current_file = file_path
                
                # 发射文件加载成功信号
                self.file_loaded.emit(file_path)
                
                # 发射数据处理成功信号
                self.data_processed.emit(True)
                
                # 发布文件加载完成事件
                self.event_bus.publish(PHBOM_FILE_LOADED, file_path)
                
                # 发布数据更新事件
                self.event_bus.publish(PHBOM_DATA_UPDATED, True)
                
                logger.info(f"PHBOM文件处理完成: {result}")
                return True
            else:
                error_msg = f"处理PHBOM文件失败: {result}"
                # 发布错误事件
                self.event_bus.publish(ERROR_OCCURRED, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"加载PHBOM文件时出错: {str(e)}"
            logger.error(error_msg)
            # 发布错误事件
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False 