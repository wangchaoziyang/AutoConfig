#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置表格组件模块

这个模块提供了用于显示配置详情的表格组件
"""

import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
                          QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
import logging
import pandas as pd

class ConfigTable(QWidget):
    """配置详情表格组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.table = QTableWidget()
        self._setup_table()
        layout.addWidget(self.table)
        
    def _setup_table(self):
        """设置表格基本属性"""
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['组件', '规格', 'P/N', '组件', '规格', 'P/N'])
        
        # 隐藏行序号
        self.table.verticalHeader().setVisible(False)
        
        # 设置水平表头
        header = self.table.horizontalHeader()
        header_font = QFont()
        header_font.setBold(True)
        header.setFont(header_font)
        
        # 设置列宽
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(3, 150)
        
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(2, 160)
        self.table.setColumnWidth(5, 160)
        
    def update_content(self, config_data, pn, component_keywords):
        """更新表格内容"""
        logger = logging.getLogger(__name__)

        # 检查参数
        if not pn:
            logger.warning("未提供系统P/N")
            return

        # 正确检查DataFrame是否为空
        if isinstance(config_data, pd.DataFrame):
            if config_data.empty:
                logger.warning("配置数据为空DataFrame")
                return
        elif config_data is None:
            logger.warning("配置数据为None")
            return
        elif not config_data:  # 如果是字典或其他容器类型
            logger.warning("配置数据为空")
            return

        # 如果是DataFrame格式，需要转换成字典格式
        if isinstance(config_data, pd.DataFrame):
            logger.info(f"收到DataFrame格式的配置数据，行数: {len(config_data)}")
            logger.debug(f"DataFrame列: {config_data.columns.tolist()}")

            # 打印所有组件类型，帮助调试
            if 'Component' in config_data.columns:
                component_types = config_data['Component'].unique()
                logger.info(f"配置数据中包含的组件类型: {component_types.tolist()}")

            # 转换DataFrame为ConfigTable需要的格式
            # 首先将数据按Component分组
            grouped_data = {}
            try:
                for component_type, group in config_data.groupby('Component'):
                    components = []
                    for _, row in group.iterrows():
                        # 确保所有字段都存在并且是字符串类型
                        name = str(row.get('Name', '')) if not pd.isna(row.get('Name')) else ''
                        spec = str(row.get('Specification', '')) if not pd.isna(row.get('Specification')) else ''
                        pn_value = str(row.get('P/N', '')) if not pd.isna(row.get('P/N')) else ''

                        components.append({
                            'name': name,
                            'spec': spec,
                            'pn': pn_value
                        })
                    
                    # 将组件类型转换为小写以便于比较
                    component_type_lower = component_type.lower() if isinstance(component_type, str) else ''
                    grouped_data[component_type_lower] = components
                    logger.debug(f"添加组件类型 {component_type} 的组件: {len(components)} 个")
            except Exception as e:
                logger.error(f"处理配置数据时出错: {str(e)}")
                return

            # 记录可用的组件类型
            logger.info(f"配置中可用的组件类型: {list(grouped_data.keys())}")
            
            # 收集匹配的组件
            components = self._collect_components(grouped_data, component_keywords)
            
            # 准备表格并填充数据
            if components:
                # 计算左右两侧的组件数量
                total_components = len(components)
                left_count = (total_components + 1) // 2  # 左侧显示一半（如果是奇数，左侧多显示一个）
                
                # 设置表格行数
                self._prepare_table(left_count)
                
                # 计算可见字符数
                visible_chars = self._get_spec_limits()
                
                # 填充左侧和右侧
                self._fill_left_side(components, left_count, visible_chars)
                self._fill_right_side(components, left_count, visible_chars)
                
                logger.info(f"表格已更新，显示 {len(components)} 个组件，左侧 {left_count} 个，右侧 {total_components - left_count} 个")
            else:
                logger.warning("未找到匹配的组件")
                # 清空表格
                self.table.setRowCount(0)
        else:
            logger.warning(f"不支持的配置数据类型: {type(config_data)}")
        
    def _collect_components(self, config, keywords):
        """收集并过滤组件数据，按照关键字顺序排序，只显示以关键字开头的组件"""
        logger = logging.getLogger(__name__)
        
        # 记录所有可用的组件类型
        logger.info(f"配置中可用的组件类型: {list(config.keys())}")
        
        # 定义关键字的别名映射，以处理可能的拼写变体
        keyword_aliases = {
            "CPU": ["cpu", "processor", "central"],
            "GPU": ["gpu", "graphics", "vga"],
            "Memory": ["memory", "ram", "dimm", "ddr"],
            "LCD": ["lcd", "display", "screen", "monitor", "panel"],
            "WLAN": ["wlan", "wifi", "wireless"],
            "WWAN": ["wwan", "cellular", "mobile"],
            "SSD": ["ssd", "solid", "nvme"],
            "Battery": ["battery", "batt", "accu"],
            "Adaptor": ["adaptor", "adapter", "power adapter", "ac adapter", "charger", "ac power"],
            "KeyBoard": ["keyboard", "kb"],
            "USH": ["ush"],
            "Finger Print": ["finger print", "fingerprint", "finger"],
            "Smart Card": ["smart card", "smartcard", "smart"],
            "RFID": ["rfid", "nfc", "near field", "contactless", "rfid/nfc"],
            "FIPS": ["fips"]
        }
        
        # 显示所有定义的别名，帮助调试
        logger.debug(f"关键字别名定义: {keyword_aliases}")
        
        # 结果列表，按关键字顺序收集组件
        ordered_components = []
        collected_comps = set()  # 用于跟踪已收集的组件，避免重复
        
        # 遍历关键字（按指定顺序）
        for keyword in keywords:
            keyword_components = []
            # 对于多词关键字，需要特殊处理
            keyword_variants = [keyword.lower()]
            
            # 处理空格、斜杠和连字符
            keyword_no_space = keyword.lower().replace(" ", "").replace("/", "").replace("-", "")
            if keyword_no_space != keyword.lower():
                keyword_variants.append(keyword_no_space)
            
            # 处理有空格的关键字，如"Finger Print"
            if " " in keyword:
                keyword_variants.append(keyword.split()[0].lower())
            
            aliases = keyword_aliases.get(keyword, [])
            
            logger.info(f"正在查找以关键字 {keyword} 开头的组件，变体: {keyword_variants}")
            
            # 搜索所有组件类型
            for component_type, components in config.items():
                
                # 检查每个组件
                for comp in components:
                    # 跳过已收集的组件
                    comp_id = f"{comp.get('name')}-{comp.get('pn')}"
                    if comp_id in collected_comps:
                        continue
                        
                    name = str(comp.get('name', '')).lower() if comp.get('name') is not None else ''
                    
                    # 显示正在检查的组件，帮助调试
                    logger.debug(f"检查组件: {name}")
                    
                    # 严格检查组件名称是否以关键字或其别名开头
                    is_match = False
                    
                    # 检查是否以关键字变体开头
                    for variant in keyword_variants:
                        if name.startswith(variant):
                            is_match = True
                            logger.debug(f"组件 {name} 以关键字变体 {variant} 开头")
                            break
                    
                    # 如果没有匹配关键字变体，检查别名
                    if not is_match:
                        for alias in aliases:
                            if name.startswith(alias.lower()):
                                is_match = True
                                logger.debug(f"组件 {name} 以别名 {alias} 开头")
                                break
                    
                    # 如果组件名称与当前关键字匹配
                    if is_match:
                        logger.info(f"找到匹配组件: {comp.get('name')} (关键字: {keyword})")
                        keyword_components.append(comp)
                        collected_comps.add(comp_id)
            
            # 将此关键字下的所有组件添加到结果列表
            if keyword_components:
                logger.info(f"关键字 {keyword} 找到 {len(keyword_components)} 个组件")
                ordered_components.extend(keyword_components)
            else:
                logger.warning(f"未找到以关键字 {keyword} 开头的组件")
        
        logger.info(f"总共收集到 {len(ordered_components)} 个组件，按指定顺序排列")
        
        return ordered_components
        
    def _prepare_table(self, total_rows):
        """准备表格显示"""
        # 设置表格行数
        self.table.setRowCount(total_rows)
        
        # 清空表格
        for row in range(total_rows):
            for col in range(6):
                self.table.setItem(row, col, QTableWidgetItem(""))
        
        # 设置表格属性
        self.table.setWordWrap(False)
        for row in range(total_rows):
            self.table.setRowHeight(row, 30)  # 恢复行高到30
            
    def _get_spec_limits(self):
        """获取规格列的限制"""
        # 获取列宽
        left_width = self.table.columnWidth(1)
        right_width = self.table.columnWidth(4)
        
        # 计算可见字符数
        font_metrics = self.table.fontMetrics()
        avg_char_width = font_metrics.horizontalAdvance('x') * 0.7
        
        return {
            'left': max(80, int(left_width / avg_char_width) - 3),
            'right': max(80, int(right_width / avg_char_width) - 3)
        }
        
    def _fill_left_side(self, components, count, visible_chars):
        """填充左侧数据"""
        bg_color = QColor(230, 240, 250)
        
        # 如果visible_chars是字典，获取左侧的值
        if isinstance(visible_chars, dict):
            visible_chars_value = visible_chars.get('left', 80)
        else:
            visible_chars_value = visible_chars
            
        for i in range(count):
            if i < len(components):
                comp = components[i]
                self._set_component_row(i, 0, comp, bg_color, visible_chars_value)
                
    def _fill_right_side(self, components, start, visible_chars):
        """填充右侧数据"""
        bg_color = QColor(230, 240, 250)
        
        # 如果visible_chars是字典，获取右侧的值
        if isinstance(visible_chars, dict):
            visible_chars_value = visible_chars.get('right', 80)
        else:
            visible_chars_value = visible_chars
            
        for i in range(start, len(components)):
            row = i - start
            comp = components[i]
            self._set_component_row(row, 3, comp, bg_color, visible_chars_value)
            
    def _set_component_row(self, row, start_col, comp_data, bg_color, visible_chars):
        """设置组件行数据"""
        # 组件名称
        name_item = QTableWidgetItem(str(comp_data['name']))
        name_item.setBackground(QBrush(bg_color))
        self.table.setItem(row, start_col, name_item)
        
        # 规格说明
        spec_text = self._process_spec_text(comp_data['spec'])
        if len(spec_text) > visible_chars:
            spec_text = self._smart_truncate(spec_text, visible_chars, comp_data['name'])
        
        spec_item = QTableWidgetItem(spec_text)
        spec_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        spec_item.setToolTip(self._process_spec_text(comp_data['spec']))
        self.table.setItem(row, start_col + 1, spec_item)
        
        # 零件编号
        pn_item = QTableWidgetItem(comp_data['pn'])
        self.table.setItem(row, start_col + 2, pn_item)
        
    @staticmethod
    def _process_spec_text(text):
        """处理规格文本"""
        text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        return re.sub(r'\s+', ' ', text).strip()
        
    @staticmethod
    def _smart_truncate(text, max_length, component_name):
        """智能截断文本"""
        text = ConfigTable._process_spec_text(text)
        
        if len(text) <= max_length:
            return text
            
        # 特殊组件处理
        special_components = ["WLAN", "CPU", "GPU", "SSD", "Memory"]
        if any(comp.lower() in component_name.lower() for comp in special_components):
            return ConfigTable._handle_special_component(text, max_length)
            
        return ConfigTable._handle_normal_component(text, max_length)
        
    @staticmethod
    def _handle_special_component(text, max_length):
        """处理特殊组件的文本"""
        model_patterns = [
            r'([A-Z0-9]+-[A-Z0-9]+)',
            r'([A-Z]{1,4}[0-9]{3,6}[A-Z0-9]*)',
            r'([0-9]{3,4}[A-Z]{1,2})',
        ]
        
        for pattern in model_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                model = match.group(1)
                brand_text = text[max(0, match.start()-30):match.start()].strip()
                priority_info = f"{brand_text} {model}"
                
                if len(priority_info) > max_length - 3:
                    return priority_info[:max_length-3] + "..."
                    
                remaining = max_length - len(priority_info) - 3
                if remaining > 10:
                    spec_info = text[match.end():match.end()+remaining].strip()
                    return f"{priority_info} {spec_info}..."
                    
                return priority_info + "..."
                
        return text[:max_length - 3] + "..."
        
    @staticmethod
    def _handle_normal_component(text, max_length):
        """处理普通组件的文本"""
        delimiters = [',', ';', '/', '-', '+', '(', ')', '[', ']']
        positions = []
        
        for delimiter in delimiters:
            positions.extend([pos for pos, char in enumerate(text) if char == delimiter])
            
        positions.sort()
        
        suitable_position = -1
        for pos in positions:
            if pos < max_length - 3:
                suitable_position = pos
            else:
                break
                
        if suitable_position > max_length // 2:
            return text[:suitable_position + 1] + "..."
            
        return text[:max_length - 3] + "..." 