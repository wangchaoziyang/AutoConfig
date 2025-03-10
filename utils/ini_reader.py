#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
INI配置文件读取器

该模块提供读取INI格式配置文件的功能
"""

import os
import logging
import configparser

logger = logging.getLogger(__name__)

class INIReader:
    """INI配置文件读取器类"""
    
    def __init__(self, file_path=None):
        """初始化INI读取器
        
        Args:
            file_path: INI文件路径，如果提供则立即加载
        """
        self.config = configparser.ConfigParser()
        self.file_path = None
        
        if file_path and os.path.exists(file_path):
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """加载INI文件
        
        Args:
            file_path: INI文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
                
            self.config.read(file_path, encoding='utf-8')
            self.file_path = file_path
            logger.info(f"已加载INI文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"加载INI文件时出错: {str(e)}")
            return False
    
    def get_sections(self):
        """获取所有节点名称
        
        Returns:
            list: 节点名称列表
        """
        return self.config.sections()
    
    def get_section_options(self, section):
        """获取节点下的所有选项
        
        Args:
            section: 节点名称
            
        Returns:
            dict: 选项和值的字典
        """
        if not self.config.has_section(section):
            logger.warning(f"节点不存在: {section}")
            return {}
            
        return dict(self.config[section])
    
    def get_option_value(self, section, option, default=None):
        """获取特定选项的值
        
        Args:
            section: 节点名称
            option: 选项名称
            default: 默认值
            
        Returns:
            str: 选项值
        """
        if not self.config.has_section(section):
            logger.warning(f"节点不存在: {section}")
            return default
            
        if not self.config.has_option(section, option):
            logger.warning(f"选项不存在: {section}.{option}")
            return default
            
        return self.config[section][option] 