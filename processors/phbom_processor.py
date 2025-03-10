#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PHBOM处理器模块

这个模块负责处理PHBOM文件，包括：
- 读取CSV文件
- 解析PHBOM信息
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

from utils.csv_reader import CSVReader

logger = logging.getLogger(__name__)

class PHBOMProcessor:
    """PHBOM文件处理器类"""
    
    def __init__(self):
        """初始化PHBOM处理器"""
        # 设置必需的列
        self.required_columns = ['Level', 'Number', '*Description', 'BOM Notes']
        
        # 可能的列名映射
        self.column_mappings = {
            'Level': ['Level', 'level', '层级', '级别'],
            'Number': ['Number', 'number', 'Part Number', 'PN', 'P/N', '料号', '零件号'],
            '*Description': ['*Description', 'Description', '描述', '说明'],
            'BOM Notes': ['BOM Notes', 'Notes', '备注', '注释']
        }
        
        self.output_filename = 'PHBOM.CSV'
        
    def validate_columns(self, df):
        """验证数据帧是否包含所需的列
        
        检查原始列名或可能的替代列名是否存在。
        
        Args:
            df: 数据帧
            
        Returns:
            bool: 是否包含所需的列
        """
        # 对于每个必需的列，检查是否存在至少一个可能的列名
        for required_col, possible_cols in self.column_mappings.items():
            if not any(col in df.columns for col in possible_cols):
                logger.warning(f"缺少必需的列 '{required_col}'，可能的列名: {possible_cols}")
                return False
        
        return True
        
    def read_csv_file(self, file_path):
        """读取CSV文件，自动处理编码"""
        try:
            # 首先尝试UTF-8编码
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # 如果失败，尝试GBK编码
            df = pd.read_csv(file_path, encoding='gbk')
        return df
        
    def extract_columns(self, df):
        """提取数据中需要的列
        
        如果原始列名不存在，尝试查找替代列名。
        
        Args:
            df: 数据帧
            
        Returns:
            包含提取列的新数据帧
        """
        try:
            # 检查所有的列名是否都存在
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            
            # 如果有缺失的列名，尝试查找替代的列名
            if missing_columns:
                logger.info(f"原始列名不完全匹配，尝试查找替代列名。缺失的列: {missing_columns}")
                
                # 创建一个新的数据帧，用于存储提取的列
                extracted_df = pd.DataFrame()
                
                # 对于每个必需的列，尝试从原始数据中找到匹配的列
                for required_col in self.required_columns:
                    if required_col in df.columns:
                        # 如果原始列名存在，直接使用
                        extracted_df[required_col] = df[required_col]
                    else:
                        # 尝试在原始数据中找到匹配的列名
                        found = False
                        for alt_col in self.column_mappings.get(required_col, []):
                            if alt_col in df.columns:
                                logger.info(f"找到替代列名: {alt_col} -> {required_col}")
                                extracted_df[required_col] = df[alt_col]
                                found = True
                                break
                        
                        if not found:
                            # 如果没有找到匹配的列名，添加一个空列
                            logger.warning(f"未找到列 '{required_col}' 的替代列，创建空列")
                            extracted_df[required_col] = None
                
                return extracted_df
            else:
                # 如果所有列都存在，直接返回这些列
                return df[self.required_columns].copy()
                
        except Exception as e:
            logger.error(f"提取列时出错: {str(e)}")
            # 返回一个带有所有必需列的空数据帧
            return pd.DataFrame(columns=self.required_columns)
        
    def save_to_csv(self, df):
        """保存数据到CSV文件"""
        df.to_csv(self.output_filename, index=False, encoding='utf-8')
        return self.output_filename
        
    def process_file(self, file_path):
        """处理PHBOM文件

        Args:
            file_path: CSV文件路径

        Returns:
            tuple: (成功标志, 结果信息)
                - 成功时返回(True, 输出文件路径)
                - 失败时返回(False, 错误信息)
        """
        try:
            # 读取文件
            logger.info(f"开始处理PHBOM文件: {file_path}")
            
            # 使用pandas高效读取
            df = self.read_csv_file(file_path)
            if df is None or df.empty:
                return False, "文件为空或格式不正确"
                
            logger.debug("成功读取CSV文件")
            
            # 列出可用的列
            logger.info(f"CSV文件包含以下列: {list(df.columns)}")

            # 检查是否至少有一列包含'Number'或'P/N'关键字
            has_number_column = any(col for col in df.columns if 'number' in col.lower() or 'p/n' in col.lower())
            if not has_number_column:
                logger.warning("CSV文件缺少Part Number列")
                return False, "CSV文件格式不正确，缺少Part Number列"

            # 验证列
            if not self.validate_columns(df):
                return False, "文件格式不正确，缺少必要的列"
                
            logger.debug("列验证通过")
            
            # 优化：只保留需要的列，减少内存使用
            needed_columns = [col for col in df.columns if any(
                keyword in col.lower() for keyword in ['level', 'number', 'p/n', 'description', 'notes']
            )]
            
            if needed_columns:
                df = df[needed_columns]
                logger.info(f"保留以下列进行处理: {needed_columns}")
            
            # 优化数据类型，减少内存使用
            for col in df.columns:
                if 'number' in col.lower() or 'p/n' in col.lower():
                    df[col] = df[col].astype(str)
            
            # 处理数据
            result_file = self._process_data(df, file_path)
            
            return True, result_file
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"处理PHBOM文件时出错: {str(e)}\n{error_details}")
            return False, f"处理PHBOM文件时出错: {str(e)}"

    def _process_data(self, df, file_path):
        # 提取数据
        extracted_df = self.extract_columns(df)
        logger.debug(f"成功提取指定列: {', '.join(self.required_columns)}")
        
        # 保存文件
        output_file = self.save_to_csv(extracted_df)
        logger.info(f"数据已保存到: {output_file}")
        
        return output_file 