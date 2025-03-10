#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV文件读取工具

这个模块提供了CSV文件读取的基本功能，包括：
- 读取CSV文件
- 自动处理编码
- 基本的数据验证
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

class CSVReader:
    """CSV文件读取器类"""
    
    def __init__(self):
        """初始化CSV读取器"""
        self.data = None
        
    def read_file(self, file_path, encoding='utf-8', fallback_encoding='gbk'):
        """
        读取CSV文件，自动处理编码
        
        Args:
            file_path (str): CSV文件路径
            encoding (str): 首选编码
            fallback_encoding (str): 备选编码
            
        Returns:
            pandas.DataFrame: CSV数据，如果读取失败则返回None
        """
        try:
            # 首先尝试首选编码
            self.data = pd.read_csv(file_path, encoding=encoding)
            logger.debug(f"使用 {encoding} 编码成功读取CSV文件")
            return self.data
        except UnicodeDecodeError:
            try:
                # 如果失败，尝试备选编码
                self.data = pd.read_csv(file_path, encoding=fallback_encoding)
                logger.debug(f"使用 {fallback_encoding} 编码成功读取CSV文件")
                return self.data
            except Exception as e:
                logger.error(f"读取CSV文件失败: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"读取CSV文件失败: {str(e)}")
            return None
            
    def validate_columns(self, required_columns):
        """
        验证CSV文件是否包含所需列
        
        Args:
            required_columns (list): 必需的列名列表
            
        Returns:
            tuple: (bool, list) - 是否验证通过，缺失的列名列表
        """
        if self.data is None:
            return False, []
            
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        return len(missing_columns) == 0, missing_columns
        
    def get_data(self):
        """
        获取CSV数据
        
        Returns:
            pandas.DataFrame: CSV数据
        """
        return self.data 