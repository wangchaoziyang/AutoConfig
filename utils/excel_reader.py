#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel文件读取工具

这个模块提供了Excel文件读取的基本功能，包括：
- 读取Excel文件
- 获取工作表列表
- 读取指定工作表的数据
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

class ExcelReader:
    """Excel文件读取器类"""
    
    def __init__(self):
        """初始化Excel读取器"""
        self.excel_file = None
        self.current_sheet = None
        
    def load_file(self, file_path):
        """
        加载Excel文件
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            bool: 是否成功加载文件
        """
        try:
            self.excel_file = pd.ExcelFile(file_path)
            logger.debug(f"成功加载Excel文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"加载Excel文件失败: {str(e)}")
            return False
            
    def get_sheet_names(self):
        """
        获取所有工作表名称
        
        Returns:
            list: 工作表名称列表
        """
        if self.excel_file:
            return self.excel_file.sheet_names
        return []
        
    def read_sheet(self, sheet_name):
        """
        读取指定工作表的数据
        
        Args:
            sheet_name (str): 工作表名称
            
        Returns:
            pandas.DataFrame: 工作表数据
        """
        try:
            if self.excel_file:
                self.current_sheet = pd.read_excel(self.excel_file, sheet_name)
                return self.current_sheet
        except Exception as e:
            logger.error(f"读取工作表 {sheet_name} 失败: {str(e)}")
        return None 