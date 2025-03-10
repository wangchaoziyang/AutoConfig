#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置处理器模块

这个模块负责处理系统配置文件，包括：
- 读取Excel配置文件
- 解析配置信息
- 提取所需数据
"""

import sys
import os
import logging
import pandas as pd
import re

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

logger = logging.getLogger(__name__)

class ConfigProcessor:
    """配置处理器类，负责处理Excel配置文件"""
    
    def __init__(self):
        """初始化配置处理器"""
        self.excel_file = None
        self.current_sheet = None
        self.config_data = None
        self.sheet_data = {}
        self.sheet_configs = {}  # 添加sheet_configs的初始化
        
        # 添加组件关键字列表
        self.component_keywords = [
            "CPU", "GPU", "Memory", "LCD", "WLAN", "WWAN", "SSD",
            "Battery", "Adaptor", "KeyBoard", "USH", "Finger Print",
            "Smart Card", "RFID", "FIPS"
        ]
        
    def load_excel_file(self, file_path):
        """加载Excel文件
        
        Args:
            file_path: Excel文件路径
        """
        try:
            logger.info(f"开始加载Excel文件: {file_path}")
            
            # 使用pandas读取Excel文件
            self.excel_file = pd.ExcelFile(file_path)
            
            # 获取所有sheet名称
            all_sheets = self.excel_file.sheet_names
            logger.debug(f"找到工作表: {all_sheets}")
            
            # 过滤包含config的sheet
            config_sheets = [sheet for sheet in all_sheets if 'config' in sheet.lower()]
            logger.info(f"找到{len(config_sheets)}个配置工作表: {config_sheets}")
            
            if not config_sheets:
                error_msg = "未找到包含'config'的工作表"
                logger.warning(error_msg)
                raise ValueError(error_msg)
            
            # 返回可用的config sheets列表，但不立即加载数据
            return config_sheets
            
        except Exception as e:
            error_msg = f"加载Excel文件失败: {str(e)}"
            logger.error(error_msg)
            raise
            
    def load_sheet_data(self, file_path, sheet_name):
        """加载指定工作表的数据
        
        Args:
            file_path: Excel文件路径
            sheet_name: 要加载的工作表名称
        """
        try:
            logger.info(f"加载工作表数据: {sheet_name}")
            
            # 设置当前sheet
            self.current_sheet = sheet_name
            
            # 清除之前的数据
            self.sheet_data.clear()
            self.sheet_configs.clear()
            self.config_data = {}
            
            # 加载指定的sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.sheet_data[sheet_name] = df
            logger.debug(f"成功加载工作表 {sheet_name}")
            
            # 分析当前工作表结构
            success = self._analyze_sheet(sheet_name, df)
            if not success:
                raise ValueError(f"工作表 {sheet_name} 分析失败")
            
            return True
            
        except Exception as e:
            error_msg = f"加载工作表 {sheet_name} 失败: {str(e)}"
            logger.error(error_msg)
            raise

    def _analyze_sheet(self, sheet_name, df):
        """分析单个工作表的结构
        
        Args:
            sheet_name: 工作表名称
            df: 工作表数据DataFrame
        Returns:
            bool: 分析是否成功
        """
        try:
            logger.debug(f"开始分析工作表: {sheet_name}")
            
            # 分析工作表结构
            header_row, config_col = self.analyze_sheet_structure(df)
            
            if header_row == -1 or config_col == -1:
                logger.error(f"工作表 {sheet_name} 未找到System P/N行")
                return False
                
            logger.debug(f"工作表 {sheet_name} 的标题行: {header_row}, 配置列: {config_col}")
            
            # 获取组件列表（第一列，从标题行后开始）
            components_map = {}
            row = header_row + 1
            while row < len(df) and pd.notna(df.iloc[row, 0]):
                component = str(df.iloc[row, 0]).strip()
                if component:  # 只添加非空组件
                    # 尝试匹配组件名称
                    for keyword in self.component_keywords:
                        if keyword.lower() in component.lower():
                            if keyword not in components_map:
                                components_map[keyword] = []
                            components_map[keyword].append({
                                'name': component,
                                'row': row
                            })
                row += 1
            
            # 保存工作表配置信息
            self.sheet_configs[sheet_name] = {
                'header_row': header_row,
                'config_col': config_col,
                'components_map': components_map
            }
            
            # 获取每个System P/N的配置
            self.config_data = {}
            for col in range(config_col, df.shape[1]):
                pn = df.iloc[header_row, col]
                if pd.notna(pn) and str(pn).strip():
                    pn = str(pn).strip()
                    config = self._extract_pn_config(df, pn, col, components_map)
                    if config:
                        self.config_data[pn] = {
                            'sheet': sheet_name,
                            'config': config
                        }
            
            logger.debug(f"工作表 {sheet_name} 分析完成")
            return True
            
        except Exception as e:
            logger.error(f"分析工作表 {sheet_name} 时出错: {str(e)}")
            return False
            
    def _extract_pn_config(self, df, pn, col, components_map):
        """提取指定PN的配置信息
        
        Args:
            df: 工作表数据
            pn: 系统PN
            col: PN所在列
            components_map: 组件映射
        Returns:
            dict: 配置信息
        """
        try:
            config = {}
            for keyword in self.component_keywords:
                config[keyword] = []
                if keyword in components_map:
                    for comp in components_map[keyword]:
                        row = comp['row']
                        spec = df.iloc[row, col]
                        pn_value = df.iloc[row, col + 1] if col + 1 < df.shape[1] else None
                        
                        if pd.notna(spec):
                            spec_str = str(spec).strip()
                            pn_str = str(pn_value).strip() if pd.notna(pn_value) else ''
                            config[keyword].append({
                                'name': comp['name'],
                                'spec': spec_str,
                                'pn': pn_str
                            })
            return config
        except Exception as e:
            logger.error(f"提取PN配置时出错: {str(e)}")
            return None

    def get_sheet_names(self):
        """获取所有工作表名称"""
        if self.excel_file is None:
            return []
        return list(self.sheet_data.keys())
        
    def get_pn_list(self, sheet_name):
        """获取指定工作表的PN列表
        
        Args:
            sheet_name: 工作表名称
        """
        try:
            if sheet_name not in self.sheet_data:
                logger.error(f"工作表不存在: {sheet_name}")
                return []
                
            # 获取工作表数据
            df = self.sheet_data[sheet_name]
            
            # 查找System P/N列
            pn_column = None
            for col in df.columns:
                if 'system p/n' in str(col).lower():
                    pn_column = col
                    break
                    
            if pn_column is None:
                logger.error("未找到System P/N列")
                return []
                
            # 获取PN列表，跳过空值和重复值
            pn_list = df[pn_column].dropna().unique().tolist()
            
            # 移除可能的标题行
            if 'System P/N' in pn_list:
                pn_list.remove('System P/N')
                
            return pn_list
            
        except Exception as e:
            logger.error(f"获取PN列表失败: {str(e)}")
            return []
            
    def get_config_details(self, pn):
        """获取指定PN的配置详情
        
        Args:
            pn: 系统PN
        """
        try:
            if not self.current_sheet or not self.config_data:
                logger.error("未选择工作表或配置数据为空")
                return None
                
            if pn not in self.config_data:
                logger.error(f"未找到PN的配置: {pn}")
                return None
                
            # 从已分析的配置数据中获取
            config = self.config_data[pn]
            if not config:
                logger.error(f"PN {pn} 的配置数据为空")
                return None
                
            # 转换为DataFrame格式
            details = []
            for component_type, components in config['config'].items():
                for component in components:
                    details.append({
                        'Component': component_type,
                        'Name': component.get('name', ''),
                        'Specification': component.get('spec', ''),
                        'P/N': component.get('pn', '')
                    })
            
            return pd.DataFrame(details) if details else None
            
        except Exception as e:
            logger.error(f"获取配置详情失败: {str(e)}")
            return None
        
    def analyze_sheet_structure(self, df):
        """分析工作表结构，找到关键行和列"""
        logger.debug(f"开始分析工作表结构，形状: {df.shape}")
        
        # 查找System P/N所在行
        header_row = -1
        config_col = -1
        
        # 首先尝试查找完整匹配的"System P/N"
        for i in range(min(30, len(df))):  # 扩大搜索范围到30行
            for j in range(min(10, df.shape[1])):  # 只搜索前10列
                cell_value = str(df.iloc[i, j]).strip()
                logger.debug(f"检查单元格 [{i}, {j}]: {cell_value}")
                if cell_value == 'System P/N':
                    header_row = i
                    config_col = j
                    logger.debug(f"找到精确匹配的System P/N: [{i}, {j}]")
                    break
            if header_row != -1:
                break
        
        # 如果没找到完整匹配，尝试模糊匹配
        if header_row == -1:
            for i in range(min(30, len(df))):
                row_values = df.iloc[i].astype(str)
                for j, value in enumerate(row_values):
                    if 'system' in value.lower() and 'p' in value.lower() and 'n' in value.lower():
                        header_row = i
                        config_col = j
                        logger.debug(f"找到模糊匹配的System P/N: [{i}, {j}]")
                        break
                if header_row != -1:
                    break
        
        if header_row == -1:
            logger.debug("未找到System P/N行")
            return -1, -1
            
        return header_row, config_col
        
    def analyze_all_sheets(self):
        """分析所有工作表"""
        self.sheet_configs = {}
        self.config_data = {}
        
        try:
            for sheet_name in self.excel_file.sheet_names:
                logger.debug(f"\n开始分析工作表: {sheet_name}")
                
                # 读取工作表，不使用任何转换
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
                
                # 分析工作表结构
                header_row, config_col = self.analyze_sheet_structure(df)
                
                if header_row != -1:
                    logger.debug(f"工作表 {sheet_name} 的标题行: {header_row}, 配置列: {config_col}")
                    
                    # 获取组件列表（第一列，从标题行后开始）
                    components_map = {}
                    row = header_row + 1
                    while row < len(df) and pd.notna(df.iloc[row, 0]):
                        component = str(df.iloc[row, 0]).strip()
                        if component:  # 只添加非空组件
                            # 尝试匹配组件名称
                            for keyword in self.component_keywords:
                                if keyword.lower() in component.lower():
                                    # 使用实际的组件名称作为键
                                    if keyword not in components_map:
                                        components_map[keyword] = []
                                    components_map[keyword].append({
                                        'name': component,
                                        'row': row
                                    })
                        row += 1
                    
                    logger.debug(f"找到组件映射: {components_map}")
                    
                    # 获取每个System P/N的配置
                    for col in range(config_col, df.shape[1]):
                        pn = df.iloc[header_row, col]
                        if pd.notna(pn) and str(pn).strip():
                            pn = str(pn).strip()
                            logger.debug(f"\n处理System P/N: {pn}")
                            
                            config = {}
                            # 按照component_keywords的顺序处理每个组件
                            for keyword in self.component_keywords:
                                if keyword in components_map:
                                    # 处理所有匹配的组件
                                    config[keyword] = []
                                    for comp in components_map[keyword]:
                                        row = comp['row']
                                        spec = df.iloc[row, col]
                                        pn_value = df.iloc[row, col + 1] if col + 1 < df.shape[1] else None
                                        
                                        if pd.notna(spec):
                                            spec_str = str(spec).strip()
                                            pn_str = str(pn_value).strip() if pd.notna(pn_value) else ''
                                            config[keyword].append({
                                                'name': comp['name'],
                                                'spec': spec_str,
                                                'pn': pn_str
                                            })
                                else:
                                    config[keyword] = []
                            
                            if pn not in self.config_data:
                                self.config_data[pn] = {
                                    'sheet': sheet_name,
                                    'config': config
                                }
                    
                    # 保存工作表配置信息
                    self.sheet_configs[sheet_name] = {
                        'header_row': header_row,
                        'config_col': config_col,
                        'components_map': components_map
                    }
                else:
                    logger.debug(f"工作表 {sheet_name} 未找到System P/N行")
            
            logger.debug(f"\n总共找到 {len(self.config_data)} 个System P/N配置")
            return True
            
        except Exception as e:
            error_msg = f"分析工作表失败: {str(e)}"
            logger.error(error_msg)
            return False
            
    def get_config_data(self):
        """获取配置数据"""
        return self.config_data
        
    def get_sheet_configs(self):
        """获取工作表配置"""
        return self.sheet_configs
        
    def get_pn_list(self, sheet_name):
        """获取指定工作表的系统P/N列表"""
        if not self.excel_file or sheet_name not in self.sheet_configs:
            # 如果工作表结构未分析，先分析
            if self.excel_file and sheet_name in self.excel_file.sheet_names:
                self.analyze_all_sheets()
                
            # 仍不存在则返回空列表
            if sheet_name not in self.sheet_configs:
                logger.warning(f"工作表 {sheet_name} 不存在或未找到系统P/N")
                return []
        
        pn_list = []
        # 从配置数据中筛选出属于该工作表的系统P/N
        for pn, data in self.config_data.items():
            if data['sheet'] == sheet_name:
                pn_list.append(pn)
        
        return pn_list
    
    def get_config_details(self, pn):
        """获取指定系统P/N的配置详情"""
        # 确保数据已加载
        if not self.config_data:
            logger.warning("配置数据未加载")
            return None
            
        logger.debug(f"获取系统P/N的配置详情: {pn}")
        logger.debug(f"配置数据包含的P/N: {list(self.config_data.keys())}")
        
        # 查找系统P/N的配置
        if pn in self.config_data:
            # 创建详情DataFrame
            details = []
            config = self.config_data[pn]['config']
            
            # 将嵌套的配置转换为扁平的列表以创建DataFrame
            for component_type, components in config.items():
                for component in components:
                    details.append({
                        'Component': component_type,
                        'Name': component.get('name', ''),
                        'Specification': component.get('spec', ''),
                        'P/N': component.get('pn', '')
                    })
            
            if details:
                logger.debug(f"找到系统P/N {pn} 的配置详情，共 {len(details)} 个组件")
                return pd.DataFrame(details)
            else:
                logger.warning(f"系统P/N {pn} 没有配置详情")
                return None
        else:
            logger.warning(f"系统P/N {pn} 不存在")
            return None 