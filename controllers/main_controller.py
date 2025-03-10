#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主控制器模块

该模块包含应用程序的主控制器，负责协调模型和视图之间的交互。
"""

import os
import logging
import traceback
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
import pandas as pd

from models.config_model import ConfigModel
from models.phbom_model import PHBOMModel
from models.os_mod_model import OSModModel
from models.mod_model import MODModel
from models.keyparts_model import KeyPartsModel
from models.app_mod_model import AppModModel

from utils.event_bus import event_bus
from utils.event_constants import (
    CONFIG_FILE_SELECT_CLICKED,
    CONFIG_FILE_OK_CLICKED,
    CONFIG_FILE_SELECTED,
    CONFIG_FILE_LOADED,
    SHEET_SELECTED,
    SHEET_LIST_UPDATED,
    SHEET_CHANGED,
    PN_SELECTED,
    PN_LIST_UPDATED,
    PN_CHANGED,
    CONFIG_DETAILS_UPDATED,
    PHBOM_FILE_SELECTED,
    PHBOM_FILE_LOADED,
    PHBOM_DATA_UPDATED,
    OS_MOD_OPTIONS_UPDATED,
    OS_MOD_SELECTED,
    ERROR_OCCURRED,
    # UI事件
    LOAD_PHBOM_CLICKED,
    CLEAR_MOD_CLICKED,
    GENERATE_CLICKED,
    CHECK_CLICKED,
    # 系统事件
    STATUS_UPDATED,
    WHQL_CHANGED,
    MOD_LOAD_CLICKED,
    MOD_ADD_CLICKED,
    KEYPARTS_LOAD_CLICKED,
    KEYPARTS_SEARCH_CLICKED,
    KEYPARTS_ADD_CLICKED,
    KEYPARTS_CLEAR_CLICKED,
    APP_MOD_ADD_CLICKED,
    BYPASS_WHQL_CLICKED,
    OS_MOD_ADD_CLICKED
)

logger = logging.getLogger(__name__)

class MainController:
    """主控制器类，负责处理用户操作和更新视图"""
    
    def __init__(self, event_bus_instance=None):
        """初始化主控制器"""
        # 设置事件总线
        global event_bus
        if event_bus_instance:
            event_bus = event_bus_instance
        
        # 保存事件总线引用
        self.event_bus = event_bus
            
        # 初始化标志，防止事件循环
        self._is_updating_os_mod = False
        self._is_updating_pn = False  # 添加PN更新标志
        
        # 初始化模型
        self.config_model = ConfigModel(self.event_bus)
        self.os_mod_model = OSModModel(self.event_bus)
        self.phbom_model = PHBOMModel(self.event_bus)
        self.mod_model = MODModel(self.event_bus)
        self.keyparts_model = KeyPartsModel(self.event_bus)
        self.app_mod_model = AppModModel(self.event_bus)
        
        # 初始化主窗口引用
        self.main_window = None
        self.current_os_mod = None
        
        # 订阅事件
        self._subscribe_events()
        
    def initialize(self, main_window):
        """初始化控制器，设置主窗口并完成后续设置
        
        Args:
            main_window: 主窗口实例
        """
        # 设置主窗口引用
        self.main_window = main_window
        
        # 连接模型信号
        self._connect_model_signals()
        
        # 更新OS MOD选项
        logger.info("初始化时更新OS MOD选项")
        options = self.os_mod_model.get_options()
        self._on_os_mod_options_updated(options)
        logger.info(f"已更新OS MOD选项: {options}")
        
    def set_main_window(self, main_window):
        """设置主窗口引用
        
        Args:
            main_window: 主窗口实例
        """
        # 设置主窗口引用
        self.main_window = main_window
        
        # 连接模型信号
        self._connect_model_signals()
        
        # 如果已经有主窗口引用，则初始化
        if self.main_window:
            # 更新OS MOD选项
            logger.info("设置主窗口时更新OS MOD选项")
            options = self.os_mod_model.get_options()
            self._on_os_mod_options_updated(options)
            logger.info(f"已更新OS MOD选项: {options}")
    
    def _subscribe_events(self):
        """订阅事件总线事件"""
        # 导入事件常量
        from utils.event_constants import (
            CONFIG_FILE_SELECT_CLICKED, CONFIG_FILE_OK_CLICKED,
            SHEET_CHANGED, PN_CHANGED, OS_MOD_CHANGED,
            LOAD_PHBOM_CLICKED, CLEAR_MOD_CLICKED,
            GENERATE_CLICKED,
            CONFIG_FILE_LOADED, SHEET_LIST_UPDATED,
            PN_LIST_UPDATED, CONFIG_DETAILS_UPDATED,
            PHBOM_FILE_LOADED, ERROR_OCCURRED,
            OS_MOD_OPTIONS_UPDATED, OS_MOD_SELECTED,
            WHQL_CHANGED, MOD_LOAD_CLICKED, MOD_ADD_CLICKED,
            KEYPARTS_LOAD_CLICKED, KEYPARTS_SEARCH_CLICKED,
            KEYPARTS_ADD_CLICKED, KEYPARTS_CLEAR_CLICKED,
            APP_MOD_ADD_CLICKED, BYPASS_WHQL_CLICKED,
            OS_MOD_ADD_CLICKED
        )

        # UI事件
        self.event_bus.subscribe(CONFIG_FILE_SELECT_CLICKED, self._on_config_file_select_clicked)
        self.event_bus.subscribe(CONFIG_FILE_OK_CLICKED, self._on_config_file_ok_clicked)
        self.event_bus.subscribe(SHEET_CHANGED, self._on_sheet_changed)
        self.event_bus.subscribe(PN_CHANGED, self._on_pn_changed)
        self.event_bus.subscribe(OS_MOD_CHANGED, self.on_os_mod_changed)
        self.event_bus.subscribe(LOAD_PHBOM_CLICKED, self.load_phbom)
        self.event_bus.subscribe(CLEAR_MOD_CLICKED, self.clear_mod_file)
        self.event_bus.subscribe(GENERATE_CLICKED, self.generate_content)
        self.event_bus.subscribe(CHECK_CLICKED, self.check_number)
        self.event_bus.subscribe(OS_MOD_ADD_CLICKED, self.os_mod_add_to_file)

        # 模型事件
        self.event_bus.subscribe(CONFIG_FILE_LOADED, self._on_config_file_loaded)
        self.event_bus.subscribe(SHEET_LIST_UPDATED, self._on_sheet_list_updated)
        self.event_bus.subscribe(PN_LIST_UPDATED, self._on_pn_list_updated)
        self.event_bus.subscribe(CONFIG_DETAILS_UPDATED, self._on_config_details_updated)
        self.event_bus.subscribe(PHBOM_FILE_LOADED, self._on_phbom_file_loaded)
        self.event_bus.subscribe(ERROR_OCCURRED, self._on_error_occurred)
        self.event_bus.subscribe(OS_MOD_OPTIONS_UPDATED, self._on_os_mod_options_updated)
        self.event_bus.subscribe(OS_MOD_SELECTED, self._on_os_mod_selected)

        # 模块事件
        self.event_bus.subscribe(WHQL_CHANGED, self.on_whql_changed)
        self.event_bus.subscribe(MOD_LOAD_CLICKED, self.load_mod_data)
        self.event_bus.subscribe(MOD_ADD_CLICKED, self.add_mod_data)
        self.event_bus.subscribe(KEYPARTS_LOAD_CLICKED, self.keyparts_load_data)
        self.event_bus.subscribe(KEYPARTS_SEARCH_CLICKED, self.keyparts_search_data)
        self.event_bus.subscribe(KEYPARTS_ADD_CLICKED, self.keyparts_add_data)
        self.event_bus.subscribe(KEYPARTS_CLEAR_CLICKED, self.keyparts_clear_data)
        self.event_bus.subscribe(APP_MOD_ADD_CLICKED, self.app_mod_add_data)
        self.event_bus.subscribe(BYPASS_WHQL_CLICKED, self.on_bypass_whql_clicked)
    
    def _connect_model_signals(self):
        """连接模型信号"""
        # 配置模型信号
        self.config_model.file_loaded.connect(self._on_config_file_loaded)
        self.config_model.sheet_list_updated.connect(self._on_sheet_list_updated)
        self.config_model.pn_list_updated.connect(self._on_pn_list_updated)
        self.config_model.config_details_updated.connect(self._on_config_details_updated)
        
        # PHBOM模型信号连接已移除，完全使用事件总线
        
        # OS MOD模型信号
        self.os_mod_model.options_updated.connect(self._on_os_mod_options_updated)
    
    def select_config_file(self, file_path):
        """选择配置文件
        
        Args:
            file_path: 配置文件路径
        """
        try:
            logger.info(f"选择配置文件: {file_path}")
            # 只加载Excel文件并获取工作表列表，不进行数据提取
            if self.config_model.load_file(file_path, load_data=False):
                self.event_bus.publish(CONFIG_FILE_SELECTED, file_path)
                return True
            return False
        except Exception as e:
            error_msg = f"选择配置文件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False
    
    def select_sheet(self, sheet_name=None, analyze_data=True):
        """选择工作表并更新PN列表
        
        Args:
            sheet_name: 工作表名称，如果为None则使用当前选中的工作表
            analyze_data: 是否分析数据，默认为True
        """
        try:
            # 如果没有提供sheet_name，则获取当前选中的sheet
            if not sheet_name and self.main_window:
                index = self.main_window.control_panel.sheet_combo.currentIndex()
                if index >= 0:
                    sheet_name = self.main_window.control_panel.sheet_combo.itemText(index)
            
            if sheet_name:
                # 通过事件总线发布SHEET_SELECTED事件
                self.event_bus.publish(SHEET_SELECTED, sheet_name)
                logger.info(f"已选择工作表: {sheet_name}, 分析数据: {analyze_data}")
                return True
            return False
        except Exception as e:
            logger.error(f"选择工作表时出错: {str(e)}")
            return False
    
    def select_pn(self, pn=None, show_warning=True):
        """选择P/N并更新相关数据
        
        Args:
            pn: 要选择的P/N，如果为None则使用当前选中的P/N
            show_warning: 是否显示警告提示，默认为True
        
        Returns:
            bool: 是否成功选择P/N
        """
        try:
            # 如果没有提供pn参数，则尝试从下拉框获取
            if not pn and self.main_window:
                index = self.main_window.control_panel.pn_combo.currentIndex()
                if index >= 0:
                    pn = self.main_window.control_panel.pn_combo.itemText(index)
            
            if pn and pn != "System P/N":
                # 更新当前P/N
                if self.config_model:
                    self.config_model.current_pn = pn
                
                # 发布P/N选择事件
                self.event_bus.publish(PN_SELECTED, pn)
                logger.info(f"已选择P/N: {pn}")
                return True
            else:
                if show_warning:
                    logger.warning("未选择有效的P/N")
                return False
        except Exception as e:
            logger.error(f"选择P/N时出错: {str(e)}")
            return False
    
    def load_phbom(self, *args):
        """加载PHBOM文件"""
        try:
            # 先取消之前可能存在的订阅
            try:
                self.event_bus.unsubscribe(PHBOM_FILE_LOADED, self._temp_phbom_file_loaded_handler)
            except:
                pass

            # 定义一次性事件处理器
            def _temp_phbom_file_loaded_handler(file_path):
                logger.info(f"PHBOM文件已加载: {file_path}")
                # 显示提示信息
                # 使用QTimer.singleShot避免在事件处理过程中更新UI
                if self.main_window:
                    from PyQt6.QtCore import QTimer
                    # 使用500毫秒的延迟，确保提示框有足够的显示时间
                    QTimer.singleShot(500, lambda: QMessageBox.information(
                        self.main_window, 
                        'PHBOM处理成功', 
                        f'PHBOM文件已成功加载并处理\n文件路径: {file_path}'
                    ))
                # 完成后取消订阅，避免重复处理
                self.event_bus.unsubscribe(PHBOM_FILE_LOADED, _temp_phbom_file_loaded_handler)

            # 保存处理器引用，以便后续取消订阅
            self._temp_phbom_file_loaded_handler = _temp_phbom_file_loaded_handler

            # 订阅事件
            self.event_bus.subscribe(PHBOM_FILE_LOADED, self._temp_phbom_file_loaded_handler)

            # 使用文件对话框选择文件
            if self.main_window:
                from PyQt6.QtWidgets import QFileDialog, QProgressDialog
                from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
                
                # 创建文件加载线程
                class PHBOMLoadThread(QThread):
                    finished = pyqtSignal(bool, str)
                    progress = pyqtSignal(int)

                    def __init__(self, phbom_model, file_path):
                        super().__init__()
                        # 不要在线程中直接使用主线程的对象
                        # 而是保存必要的信息
                        self.file_path = file_path
                        # 将phbom_model移动到线程中
                        self.phbom_model = phbom_model
                        # 添加标志位，用于安全终止线程
                        self.is_running = True

                    def run(self):
                        try:
                            # 开始加载，更新进度
                            if not self.is_running:
                                return
                            self.progress.emit(5)
                            # 添加短暂延迟，确保进度条显示
                            QThread.msleep(200)

                            # 加载文件
                            if not self.is_running:
                                return
                            # 检查文件是否存在
                            if not os.path.exists(self.file_path):
                                self.finished.emit(False, f"文件不存在: {self.file_path}")
                                return
                            
                            self.progress.emit(10)
                            QThread.msleep(200)
                                
                            # 检查文件是否为CSV格式
                            try:
                                self.progress.emit(20)  # 更新进度
                                QThread.msleep(200)
                                with open(self.file_path, 'r', encoding='utf-8') as f:
                                    # 尝试读取前几行
                                    for _ in range(5):
                                        if not f.readline():
                                            break
                            except Exception as e:
                                self.finished.emit(False, f"文件读取失败: {str(e)}")
                                return
                                
                            if not self.is_running:
                                return
                            self.progress.emit(30)  # 更新进度
                            QThread.msleep(200)
                                
                            # 使用moveToThread确保对象在正确的线程中
                            # 但在这里我们直接在线程中处理文件，不使用QObject
                            from processors.phbom_processor import PHBOMProcessor
                            processor = PHBOMProcessor()
                            
                            self.progress.emit(40)  # 更新进度 - 开始处理文件
                            QThread.msleep(200)
                            
                            # 处理文件前先更新进度
                            self.progress.emit(50)
                            QThread.msleep(200)
                            
                            success, result = processor.process_file(self.file_path)
                            
                            # 完成加载，更新进度
                            if not self.is_running:
                                return
                            
                            # 逐步更新进度到100%
                            for i in range(60, 101, 10):
                                self.progress.emit(i)
                                QThread.msleep(100)  # 短暂延迟，使进度条动画更平滑

                            # 发送完成信号
                            if not self.is_running:
                                return
                            if success:
                                # 在主线程中更新模型
                                self.finished.emit(True, self.file_path)
                            else:
                                self.finished.emit(False, f"加载失败: {result}")
                        except Exception as e:
                            logger.error(f"加载PHBOM文件时发生错误: {str(e)}")
                            if self.is_running:
                                self.finished.emit(False, f"错误: {str(e)}")
                    
                    def terminate(self):
                        """安全终止线程"""
                        self.is_running = False
                        super().terminate()
                
                file_path, _ = QFileDialog.getOpenFileName(
                    self.main_window,
                    "选择PHBOM文件",
                    "",
                    "CSV文件 (*.csv);;所有文件 (*.*)"
                )
                
                if file_path:
                    try:
                        # 创建进度对话框
                        progress = QProgressDialog("正在加载PHBOM文件...", "取消", 0, 100, self.main_window)
                        progress.setWindowTitle("加载中")
                        progress.setWindowModality(Qt.WindowModality.WindowModal)
                        # 增加最小显示时间，确保用户能够看清楚
                        progress.setMinimumDuration(0)  # 设置为0，确保立即显示
                        # 设置进度条的最小宽度，使其更加明显
                        progress.setMinimumWidth(400)
                        # 设置标签文本的对齐方式
                        progress.setLabelText("正在加载和处理PHBOM文件...\n请稍候")
                        # 强制显示进度对话框
                        progress.show()
                        # 确保进度对话框立即更新
                        QApplication.processEvents()
                        # 保存进度对话框引用，以便在线程完成后关闭
                        self.progress_dialog = progress
                        
                        # 创建加载线程
                        self.load_thread = PHBOMLoadThread(self.phbom_model, file_path)

                        # 连接信号
                        self.load_thread.progress.connect(progress.setValue)
                        self.load_thread.finished.connect(self._on_phbom_load_finished)
                        # 确保在线程完成后不会立即关闭进度对话框
                        # 而是延迟一段时间后再关闭，以便用户能够看到100%的进度
                        self.load_thread.finished.connect(
                            lambda success, message: QTimer.singleShot(
                                1000,  # 延迟1秒关闭
                                lambda: progress.close() if progress else None
                            )
                        )

                        # 连接取消按钮
                        progress.canceled.connect(self.load_thread.terminate)
                        # 确保在取消时也能清理线程
                        progress.canceled.connect(lambda: self._cleanup_phbom_thread() if hasattr(self, 'load_thread') else None)

                        # 启动线程
                        self.load_thread.start()
                    except Exception as e:
                        logger.error(f"启动PHBOM加载线程时出错: {str(e)}")
                        QMessageBox.critical(self.main_window, "系统错误", f"启动PHBOM加载线程时出错:\n{str(e)}")
            else:
                logger.warning("主窗口不存在，无法选择文件")
        except Exception as e:
            logger.error(f"选择PHBOM文件时出错: {str(e)}")
            if self.main_window:
                QMessageBox.warning(self.main_window, "错误", f"选择PHBOM文件时出错: {str(e)}")
    
    def _on_phbom_load_finished(self, success, message):
        """PHBOM文件加载完成的回调"""
        try:
            # 确保线程对象被正确清理
            if hasattr(self, 'load_thread'):
                self.load_thread.disconnect()
                self.load_thread.wait()  # 等待线程完全结束
                self.load_thread.deleteLater()  # 安全删除线程对象
                self.load_thread = None
                
            if success:
                # 加载成功，在主线程中更新模型
                logger.info(f"PHBOM文件加载成功: {message}")
                
                # 在主线程中更新模型
                try:
                    # 直接更新模型
                    if hasattr(self, 'phbom_model') and self.phbom_model:
                        # 设置当前文件
                        self.phbom_model.current_file = message
                        # 发布事件
                        self.event_bus.publish(PHBOM_FILE_LOADED, message)
                except Exception as e:
                    logger.error(f"更新PHBOM模型时出错: {str(e)}")
                    self.event_bus.publish(ERROR_OCCURRED, f"更新PHBOM模型时出错: {str(e)}")
                    return
            else:
                logger.error(f"PHBOM加载失败: {message}")
                if self.main_window:
                    # 使用QTimer.singleShot避免在事件处理过程中更新UI
                    from PyQt6.QtCore import QTimer
                    # 使用500毫秒的延迟，确保错误提示框有足够的显示时间
                    QTimer.singleShot(500, lambda: QMessageBox.warning(
                        self.main_window, 
                        "PHBOM处理失败", 
                        f"PHBOM文件加载失败:\n{message}"
                    ))
        except Exception as e:
            logger.error(f"处理PHBOM加载完成事件时出错: {str(e)}")
            # 确保即使出错也能显示错误信息
            if self.main_window:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, lambda: QMessageBox.critical(
                    self.main_window,
                    "系统错误",
                    f"处理PHBOM加载完成事件时出错:\n{str(e)}"
                ))
    
    def clear_mod_file(self, *args):
        """清除MOD.TXT文件内容"""
        try:
            # 检查文件是否存在，如果不存在则创建
            if not os.path.exists('MOD.TXT'):
                reply = QMessageBox.question(
                    self.main_window,
                    '确认',
                    '文件MOD.TXT不存在，是否创建空文件？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No  # 默认选择No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # 用户选择Yes，创建空文件
                    open('MOD.TXT', 'w').close()
                    logger.info("已创建空的MOD.TXT文件")
                    # 显示成功提示
                    QMessageBox.information(
                        self.main_window,
                        '操作成功',
                        'MOD.TXT文件已成功创建！'
                    )
                else:
                    # 用户选择No，不执行操作
                    return
            else:
                # 文件存在，清空内容
                open('MOD.TXT', 'w').close()
                logger.info("MOD.TXT 文件内容已清空")
                # 显示成功提示
                QMessageBox.information(
                    self.main_window,
                    '操作成功',
                    'MOD.TXT文件内容已成功清除！'
                )

        except Exception as e:
            self._show_error(f"清除MOD.TXT文件时出错: {str(e)}")
    
    def generate_content(self):
        """生成内容 - 将MOD.TXT直接重命名为以当前P/N命名的文件"""
        try:
            # 检查是否已加载配置文件
            if not self.config_model.file_path:
                QMessageBox.warning(self.main_window, '提示', '请先加载配置文件')
                return

            # 检查是否已选择System P/N
            if not self.config_model.current_pn:
                QMessageBox.warning(self.main_window, '提示', '请先选择System P/N')
                return

            # 获取当前P/N
            current_pn = self.config_model.current_pn

            # 检查MOD.TXT文件是否存在
            if not os.path.exists('MOD.TXT'):
                QMessageBox.warning(self.main_window, '提示', '请先创建MOD.TXT文件')
                return

            # 生成目标文件名
            output_filename = f"{current_pn}.TXT"
            
            # 如果目标文件已存在，询问是否覆盖
            if os.path.exists(output_filename):
                reply = QMessageBox.question(
                    self.main_window,
                    '确认',
                    f'文件 {output_filename} 已存在，是否覆盖？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No  # 默认选择No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
                    
                # 如果用户选择覆盖，先删除已存在的文件
                try:
                    os.remove(output_filename)
                except Exception as e:
                    self._show_error(f"删除已存在的文件时出错: {str(e)}")
                    return

            # 直接重命名MOD.TXT文件
            os.rename('MOD.TXT', output_filename)
            
            # 显示成功提示
            self._show_success(f"MOD.TXT已成功重命名为 {output_filename}")

        except Exception as e:
            error_msg = f"生成内容时出错: {str(e)}"
            logger.error(error_msg)
            self._show_error(error_msg)
    
    def on_os_mod_changed(self, index):
        """处理OS MOD下拉框选择变更事件
        
        Args:
            index: 选择的选项索引
        """
        try:
            # 获取选择的选项文本
            if self.main_window and hasattr(self.main_window, 'module_panel'):
                panel = self.main_window.module_panel
                if panel and hasattr(panel, 'os_mod_combo'):
                    # 获取当前选择的选项文本
                    option = panel.os_mod_combo.itemText(index)
                    
                    # 如果选择了空选项，则清空显示框
                    if not option:
                        if panel and hasattr(panel, 'os_mod_text'):
                            panel.os_mod_text.setText("")
                        logger.info("已清空OS MOD选项")
                        return
                    
                    # 确保os_mod_model已初始化
                    if not hasattr(self, 'os_mod_model') or self.os_mod_model is None:
                        from models.os_mod_model import OSModModel
                        self.os_mod_model = OSModModel(self.event_bus)
                    
                    # 获取选项对应的参数文本
                    params_text = self.os_mod_model.get_params_text(option)
                    
                    # 更新显示框
                    if panel and hasattr(panel, 'os_mod_text'):
                        panel.os_mod_text.setText(params_text)
                    
                    # 发布选项选择事件
                    self.event_bus.publish(OS_MOD_SELECTED, option)
                    
                    logger.info(f"已选择OS MOD: {option}, 参数: {params_text}")
        except Exception as e:
            logger.error(f"处理OS MOD选择变更事件时出错: {str(e)}")
            # 打印详细的错误堆栈信息，便于调试
            import traceback
            logger.error(traceback.format_exc())
    
    def _on_os_mod_options_updated(self, options):
        """处理OS MOD选项更新事件"""
        if self._is_updating_os_mod:
            return
        
        try:
            self._is_updating_os_mod = True
            
            if not self.main_window or not hasattr(self.main_window, 'module_panel'):
                return
            
            panel = self.main_window.module_panel
            if not panel or not hasattr(panel, 'os_mod_combo'):
                return
            
            combo = panel.os_mod_combo
            
            # 更新OS MOD下拉框
            if isinstance(options, list):
                # 过滤掉空白选项
                valid_options = [opt for opt in options if opt and not opt.isspace()]
                if valid_options:
                    combo.blockSignals(True)  # 阻止信号触发事件
                    combo.clear()
                    combo.addItems(valid_options)
                    combo.blockSignals(False)  # 恢复信号
        except Exception as e:
            logger.error(f"更新OS MOD选项时出错: {str(e)}")
            self._show_error(f"更新OS MOD选项时出错: {str(e)}")
        finally:
            self._is_updating_os_mod = False
    
    def _on_os_mod_selected(self, option):
        """处理OS MOD选择事件"""
        if self.main_window:
            # 获取选项对应的参数
            params_text = self.os_mod_model.get_params_text(option)
            # 更新文本显示框
            self.main_window.module_panel.os_mod_text.setText(params_text)
            logger.info(f"已选择OS MOD: {option}, 参数: {params_text}")
    
    def on_whql_changed(self, checked=False, *args):
        """WHQL复选框变更处理"""
        status = "启用" if checked else "禁用"
        logger.info(f"Bypass WHQL 已{status}")
    
    def load_mod_data(self, *args):
        """加载MOD数据"""
        logger.info("加载MOD数据")
        # 实现加载MOD数据的逻辑
    
    def add_mod_data(self, *args):
        """添加MOD数据"""
        logger.info("添加MOD数据")
        # 实现添加MOD数据的逻辑
    
    def keyparts_load_data(self, *args):
        """加载关键部件数据"""
        logger.info("加载关键部件数据")
        # 实现加载关键部件数据的逻辑
    
    def keyparts_search_data(self, *args):
        """搜索关键部件数据"""
        logger.info("搜索关键部件数据")
        # 实现搜索关键部件数据的逻辑
        
    def keyparts_add_data(self, *args):
        """添加关键部件数据"""
        logger.info("添加关键部件数据")
        # 实现添加关键部件数据的逻辑
    
    def keyparts_clear_data(self, *args):
        """清除关键部件数据"""
        logger.info("清除关键部件数据")
        # 实现清除关键部件数据的逻辑
    
    def app_mod_add_data(self, *args):
        """添加APP MOD数据"""
        logger.info("添加APP MOD数据")
        # 实现添加APP MOD数据的逻辑
    
    def on_bypass_whql_clicked(self, is_active):
        """处理Bypass WHQL状态变化
        
        @param {bool} is_active - 是否激活Bypass WHQL
        """
        try:
            logger.info(f"Bypass WHQL状态变更为: {'激活' if is_active else '未激活'}")
            
            # 根据按钮状态处理MOD.TXT文件
            mod_file_path = os.path.join(os.getcwd(), "MOD.TXT")
            
            if is_active:
                # 按钮为绿色（激活状态），添加5P226到MOD.TXT
                self._add_5p226_to_mod_file(mod_file_path)
                status_message = "Bypass WHQL已激活，5P226已添加到MOD.TXT"
            else:
                # 按钮为红色（未激活状态），从MOD.TXT中删除5P226
                self._remove_5p226_from_mod_file(mod_file_path)
                status_message = "Bypass WHQL已禁用，5P226已从MOD.TXT中删除"
            
            # 更新状态信息
            self.event_bus.publish(STATUS_UPDATED, status_message)
            
        except Exception as e:
            error_msg = f"处理Bypass WHQL状态变化时出错: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
    
    def _add_5p226_to_mod_file(self, mod_file_path):
        """将5P226添加到MOD.TXT文件
        
        @param {str} mod_file_path - MOD.TXT文件路径
        """
        try:
            # 检查文件是否存在，不存在则创建
            if not os.path.exists(mod_file_path):
                with open(mod_file_path, 'w', encoding='utf-8') as f:
                    f.write("5P226\n")
                logger.info("已创建MOD.TXT文件并添加5P226")
                self._show_success("已创建MOD.TXT文件并添加5P226")
                return
            
            # 读取文件内容，检查是否已包含5P226
            with open(mod_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 检查是否已包含5P226
            if any(line.strip() == "5P226" for line in lines):
                logger.info("MOD.TXT文件已包含5P226，无需重复添加")
                return
            
            # 添加5P226到文件
            with open(mod_file_path, 'a', encoding='utf-8') as f:
                f.write("5P226\n")
            
            logger.info("已将5P226添加到MOD.TXT文件")
            self._show_success("已将5P226添加到MOD.TXT文件")
            
        except Exception as e:
            error_msg = f"添加5P226到MOD.TXT文件时出错: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            self._show_error(error_msg)
    
    def _remove_5p226_from_mod_file(self, mod_file_path):
        """从MOD.TXT文件中删除5P226
        
        @param {str} mod_file_path - MOD.TXT文件路径
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(mod_file_path):
                logger.info("MOD.TXT文件不存在，无需删除5P226")
                return
            
            # 读取文件内容
            with open(mod_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤掉5P226
            new_lines = [line for line in lines if line.strip() != "5P226"]
            
            # 如果没有变化，说明文件中不包含5P226
            if len(new_lines) == len(lines):
                logger.info("MOD.TXT文件中不包含5P226，无需删除")
                return
            
            # 写回文件
            with open(mod_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            logger.info("已从MOD.TXT文件中删除5P226")
            self._show_success("已从MOD.TXT文件中删除5P226")
            
        except Exception as e:
            error_msg = f"从MOD.TXT文件中删除5P226时出错: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            self._show_error(error_msg)
    
    def check_number(self, check_value):
        """处理Check按钮点击事件，从PHBOM.CSV文件中查找输入的Number并显示相关信息
        
        @param {str} check_value - 用户输入的检查值（Number）
        """
        try:
            logger.info(f"执行检查操作，检查值: {check_value}")
            
            if not check_value:
                self._show_error("请输入要查找的Number")
                return
            
            # 检查PHBOM.CSV文件是否存在
            phbom_file_path = os.path.join(os.getcwd(), "PHBOM.CSV")
            if not os.path.exists(phbom_file_path):
                self._show_error("PHBOM.CSV文件不存在，请先加载PHBOM文件")
                return
            
            # 读取PHBOM.CSV文件
            try:
                # 尝试使用UTF-8编码读取
                df = pd.read_csv(phbom_file_path, encoding='utf-8')
            except UnicodeDecodeError:
                # 如果失败，尝试使用GBK编码
                df = pd.read_csv(phbom_file_path, encoding='gbk')
            
            # 查找可能的Number列
            number_columns = ['Number', 'number', 'Part Number', 'PN', 'P/N', '料号', '零件号']
            number_col = None
            for col in number_columns:
                if col in df.columns:
                    number_col = col
                    break
            
            if number_col is None:
                self._show_error("PHBOM.CSV文件中未找到Number列")
                return
            
            # 查找匹配的行
            matched_rows = df[df[number_col].astype(str).str.contains(check_value, case=False, na=False)]
            
            if matched_rows.empty:
                self._show_error(f"未找到Number为 {check_value} 的记录")
                return
            
            # 构建显示信息
            info_text = f"找到 {len(matched_rows)} 条匹配记录：\n\n"
            
            # 获取所有列名
            columns = df.columns.tolist()
            
            # 对于每一行匹配的记录，显示所有列的信息
            for idx, row in matched_rows.iterrows():
                info_text += f"记录 #{idx+1}:\n"
                for col in columns:
                    info_text += f"{col}: {row[col]}\n"
                info_text += "\n"
            
            # 显示结果
            if self.main_window:
                QMessageBox.information(self.main_window, f"Number: {check_value} 查询结果", info_text)
            else:
                logger.info(info_text)
            
        except Exception as e:
            error_msg = f"执行检查操作时出错: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
    
    # 私有方法 - 处理模型信号
    def _on_config_file_loaded(self, file_path):
        """处理配置文件加载完成事件"""
        if self.main_window:
            # 启用OK按钮
            self.main_window.control_panel.enable_ok_button()
            logger.info(f"配置文件已加载: {file_path}")
    
    def _on_sheet_list_updated(self, sheets):
        """处理工作表列表更新事件"""
        if self.main_window:
            # 更新工作表下拉框
            self.main_window.control_panel.sheet_combo.clear()
            self.main_window.control_panel.sheet_combo.addItems(sheets)
            
            # 启用OK按钮，允许用户确认选择
            self.main_window.control_panel.enable_ok_button()
            
            logger.info(f"工作表列表已更新: {sheets}")
    
    def _on_pn_list_updated(self, pn_list):
        """处理P/N列表更新事件"""
        if self.main_window:
            # 过滤掉"System P/N"选项
            filtered_pn_list = [pn for pn in pn_list if pn != "System P/N"]
            
            # 更新P/N下拉框
            self.main_window.control_panel.pn_combo.clear()
            self.main_window.control_panel.pn_combo.addItems(filtered_pn_list)
            
            # 启用OK按钮，允许用户确认选择
            self.main_window.control_panel.enable_ok_button()
            
            logger.info(f"P/N列表已更新: {filtered_pn_list}")
    
    def _on_config_details_updated(self, config_data):
        """处理配置详情更新事件"""
        logger = logging.getLogger(__name__)
        try:
            # 检查配置数据是否有效
            if config_data is None:
                logger.warning("配置数据为None，无法更新配置详情")
                self._show_error("无法更新配置详情：数据为空")
                return
                
            # 如果是DataFrame，检查是否为空
            if isinstance(config_data, pd.DataFrame):
                if config_data.empty:
                    logger.warning("配置数据为空DataFrame，无法更新配置详情")
                    self._show_error("无法更新配置详情：数据为空")
                    return
            # 如果是其他类型（如字典），检查是否为空
            elif not config_data:
                logger.warning("配置数据为空，无法更新配置详情")
                self._show_error("无法更新配置详情：数据为空")
                return
                
            # 获取当前选中的P/N
            pn = self.config_model.get_current_pn()
            if not pn:
                logger.warning("未选择系统P/N，无法更新配置详情")
                self._show_error("请先选择系统P/N")
                return
                
            # 更新配置表格
            component_keywords = self.config_model.get_component_keywords()
            self.main_window.update_config_table(config_data, pn, component_keywords)
            
            # 更新显示框
            self.main_window.update_display_box(pn)
            
            logger.info(f"配置详情已更新: {pn}")
        except Exception as e:
            logger.error(f"更新配置详情时发生错误: {str(e)}")
            self._show_error(f"更新配置详情时发生错误: {str(e)}")
    
    def _on_phbom_file_loaded(self, file_path):
        """处理PHBOM文件加载完成信号"""
        logger.info(f"PHBOM文件已加载: {file_path}")
        
    def _on_error_occurred(self, error_msg):
        """处理错误事件"""
        self._show_error(error_msg)
    
    def _show_error(self, error_msg):
        """显示错误消息"""
        if self.main_window:
            QMessageBox.critical(self.main_window, '错误', error_msg)
            
    def _show_success(self, success_msg):
        """显示成功消息"""
        if self.main_window:
            QMessageBox.information(self.main_window, '成功', success_msg)

    def add_content(self, content):
        """添加内容到MOD.TXT文件"""
        try:
            # 确保内容不为空
            if not content:
                logger.warning("没有要添加的内容")
                return False
                
            # 添加内容到MOD.TXT文件
            with open('MOD.TXT', 'a', encoding='utf-8') as f:
                f.write(content + '\n')
                
            logger.info(f"成功添加内容到MOD.TXT: {content}")
            
            # 显示成功消息
            if self.main_window:
                QMessageBox.information(self.main_window, '成功', '内容已添加到MOD.TXT文件')
            return True
            
        except Exception as e:
            logger.error(f"添加内容时出错: {str(e)}")
            if self.main_window:
                QMessageBox.critical(self.main_window, '错误', f"添加内容时出错: {str(e)}")
            return False

    def _on_config_file_select_clicked(self, *args):
        """处理配置文件选择按钮点击事件"""
        try:
            if self.main_window:
                from PyQt6.QtWidgets import QFileDialog
                file_path, _ = QFileDialog.getOpenFileName(
                    self.main_window,
                    "选择配置文件",
                    "",
                    "Excel文件 (*.xlsx *.xlsm);;所有文件 (*.*)"
                )
                if file_path:
                    # 只加载Excel文件并获取工作表列表，不进行数据分析
                    self.load_config_file_sheets_only(file_path)
        except Exception as e:
            logger.error(f"选择配置文件时出错: {str(e)}")
            self._show_error(f"选择配置文件时出错: {str(e)}")
    
    def load_config_file_sheets_only(self, file_path):
        """加载配置文件并获取工作表列表，但不加载具体工作表数据
        
        Args:
            file_path: 配置文件路径
        """
        try:
            logger.info(f"正在加载配置文件工作表列表: {file_path}")
            
            # 创建进度对话框
            if self.main_window:
                from PyQt6.QtWidgets import QProgressDialog
                from PyQt6.QtCore import Qt, QTimer
                
                # 创建进度对话框
                progress = QProgressDialog("正在加载配置文件...", "取消", 0, 100, self.main_window)
                progress.setWindowTitle("加载中")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                # 设置最小显示时间
                progress.setMinimumDuration(0)  # 设置为0，确保立即显示
                # 设置进度条的最小宽度，使其更加明显
                progress.setMinimumWidth(400)
                # 设置标签文本
                progress.setLabelText("正在加载配置文件...\n请稍候")
                # 强制显示进度对话框
                progress.show()
                # 确保进度对话框立即更新
                QApplication.processEvents()
                
                # 更新进度
                progress.setValue(10)
                QTimer.singleShot(100, lambda: progress.setValue(20))

            # 检查文件是否存在
            if not os.path.exists(file_path):
                if progress:
                    progress.close()
                self._show_error(f"文件不存在: {file_path}")
                return False

            # 检查文件类型
            if not file_path.endswith(('.xlsx', '.xlsm')):
                if progress:
                    progress.close()
                self._show_error(f"不支持的文件类型: {file_path}")
                return False
                
            if progress:
                progress.setValue(40)
                QTimer.singleShot(100, lambda: progress.setValue(60))

            # 使用ConfigModel加载Excel文件并获取工作表列表
            result = self.config_model.load_file_sheets_only(file_path)
            
            if progress:
                progress.setValue(90)
                # 延迟关闭进度对话框，确保用户能看到进度
                QTimer.singleShot(500, lambda: progress.setValue(100))
                QTimer.singleShot(800, lambda: progress.close())
                
            if result:
                logger.info(f"成功加载配置文件工作表列表: {file_path}")
                return True

            return False
        except Exception as e:
            if 'progress' in locals() and progress:
                progress.close()
            error_msg = f"加载配置文件工作表列表时出错: {str(e)}"
            logger.error(error_msg)
            self._show_error(error_msg)
            return False
    
    def _on_config_file_ok_clicked(self, *args):
        """处理配置文件确定按钮点击事件"""
        try:
            # 检查配置模型是否存在
            if not self.config_model:
                self._show_error("配置模型未初始化")
                return
                
            file_path = self.config_model.get_current_file_path()
            if not file_path:
                self._show_error("配置文件未加载")
                return
                
            # 获取当前选择的表格
            if not self.main_window:
                self._show_error("主窗口未初始化")
                return
                
            index = self.main_window.control_panel.sheet_combo.currentIndex()
            if index < 0:
                self._show_error("请先选择工作表")
                return
                
            sheet_name = self.main_window.control_panel.sheet_combo.itemText(index)
            
            # 加载并分析表格数据，不检查P/N是否已选择
            self.load_and_analyze_sheet_data(file_path, sheet_name)
                
        except Exception as e:
            logger.error(f"处理配置文件确定按钮点击事件时出错: {str(e)}")
            self._show_error(f"处理配置文件确定按钮点击事件时出错: {str(e)}")
            
    def load_and_analyze_sheet_data(self, file_path, sheet_name):
        """加载并分析工作表数据
        Args:
            file_path: 配置文件路径
            sheet_name: 工作表名称
        """
        try:
            logger.info(f"正在加载并分析工作表数据: {sheet_name}")
            
            # 创建进度对话框
            if self.main_window:
                from PyQt6.QtWidgets import QProgressDialog
                from PyQt6.QtCore import Qt, QTimer
                
                # 创建进度对话框
                progress = QProgressDialog("正在加载工作表数据...", "取消", 0, 100, self.main_window)
                progress.setWindowTitle("加载中")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                # 设置最小显示时间
                progress.setMinimumDuration(0)  # 设置为0，确保立即显示
                # 设置进度条的最小宽度，使其更加明显
                progress.setMinimumWidth(400)
                # 设置标签文本
                progress.setLabelText(f"正在加载工作表 {sheet_name} 数据...\n请稍候")
                # 强制显示进度对话框
                progress.show()
                # 确保进度对话框立即更新
                QApplication.processEvents()
                
                # 更新进度
                progress.setValue(10)
                QTimer.singleShot(100, lambda: progress.setValue(20))

            # 使用ConfigProcessor加载工作表数据
            if progress:
                progress.setValue(30)
                
            result = self.config_model.processor.load_sheet_data(file_path, sheet_name)
            
            if progress:
                progress.setValue(50)
                
            if result:
                # 更新当前表
                self.config_model.current_sheet = sheet_name
                
                if progress:
                    progress.setValue(60)
                    QTimer.singleShot(100, lambda: progress.setValue(70))

                # 获取PN列表
                pn_list = self.config_model.processor.get_pn_list(sheet_name)
                
                if progress:
                    progress.setValue(80)
                    QTimer.singleShot(100, lambda: progress.setValue(90))

                # 发送PN列表更新事件
                self.config_model.pn_list_updated.emit(pn_list)
                self.event_bus.publish(PN_LIST_UPDATED, pn_list)
                
                if progress:
                    progress.setValue(100)
                    # 延迟关闭进度对话框，确保用户能看到进度
                    QTimer.singleShot(500, lambda: progress.close())

                logger.info(f"成功加载工作表数据: {sheet_name}, 包含 {len(pn_list)} 个P/N")
            else:
                if progress:
                    progress.close()
                logger.error(f"加载工作表数据失败: {sheet_name}")
                self._show_error(f"加载工作表数据失败: {sheet_name}")
                
        except Exception as e:
            if 'progress' in locals() and progress:
                progress.close()
            logger.error(f"加载并分析工作表数据时出错: {str(e)}")
            self._show_error(f"加载并分析工作表数据时出错: {str(e)}")
    
    def _on_sheet_changed(self, index):
        """处理工作表变更事件"""
        try:
            if index >= 0 and self.config_model:
                sheets = self.config_model.get_sheet_list()
                if 0 <= index < len(sheets):
                    sheet_name = sheets[index]
                    self.select_sheet(sheet_name)
        except Exception as e:
            logger.error(f"切换工作表时出错: {str(e)}")
            self._show_error(f"切换工作表时出错: {str(e)}")
        
    def _on_pn_changed(self, index):
        """处理PN下拉框选择变化事件"""
        try:
            if self._is_updating_pn:
                return
                
            self._is_updating_pn = True
            try:
                # 获取选中的P/N
                pn = self.main_window.control_panel.pn_combo.itemText(index)
                if not pn:
                    return
                    
                logger.info(f"P/N选择变更: {pn}")
                
                # 更新显示
                self.main_window.update_display_box(pn)
                
                # 显示配置详情
                self.main_window.show_config_details(pn)
                
                # 发布P/N变更事件
                event_bus.publish(PN_CHANGED, index)
                
                # 选择P/N并更新相关数据，显示警告提示
                self.select_pn(pn, show_warning=True)
            finally:
                self._is_updating_pn = False
        except Exception as e:
            logger.error(f"处理P/N选择变化事件时出错: {str(e)}")
            event_bus.publish(ERROR_OCCURRED, f"处理P/N选择变化事件时出错: {str(e)}")

    def _cleanup_phbom_thread(self):
        """清理PHBOM加载线程资源"""
        try:
            if hasattr(self, 'load_thread') and self.load_thread:
                # 断开所有信号连接
                try:
                    self.load_thread.disconnect()
                except:
                    pass
                
                # 等待线程结束
                if self.load_thread.isRunning():
                    self.load_thread.is_running = False  # 设置标志位，通知线程停止
                    self.load_thread.wait(1000)  # 最多等待1秒
                    
                # 安全删除线程对象
                self.load_thread.deleteLater()
                self.load_thread = None
                
            # 关闭进度对话框
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                try:
                    # 先将进度设置为100%，然后延迟关闭
                    self.progress_dialog.setValue(100)
                    QTimer.singleShot(500, self.progress_dialog.close)
                except:
                    try:
                        self.progress_dialog.close()
                    except:
                        pass
                self.progress_dialog = None
                
        except Exception as e:
            logger.error(f"清理PHBOM线程资源时出错: {str(e)}")

    def os_mod_add_to_file(self, *args):
        """处理OS MOD ADD按钮点击事件，将文本显示框中"="后的字符分行写入MOD.TXT文件
        
        将OS MOD文本框中的内容解析，提取每个参数"="后的值，并将这些值分行写入MOD.TXT文件
        """
        try:
            # 获取OS MOD文本框中的内容
            if self.main_window and hasattr(self.main_window, 'module_panel'):
                panel = self.main_window.module_panel
                if panel and hasattr(panel, 'os_mod_text'):
                    # 获取文本内容
                    text_content = panel.os_mod_text.text().strip()
                    
                    # 如果文本为空，则不处理
                    if not text_content:
                        logger.warning("OS MOD文本框为空，无法添加到MOD.TXT文件")
                        self._show_error("OS MOD文本框为空，请先选择一个OS MOD选项")
                        return
                    
                    # 解析文本内容，提取"="后的值
                    values = []
                    for item in text_content.split():
                        if "=" in item:
                            key, value = item.split("=", 1)
                            values.append(value)
                    
                    # 如果没有提取到值，则不处理
                    if not values:
                        logger.warning("未从OS MOD文本框中提取到有效值")
                        self._show_error("未从OS MOD文本框中提取到有效值，请确认格式是否正确")
                        return
                    
                    # 将值写入MOD.TXT文件
                    mod_file_path = os.path.join(os.getcwd(), "MOD.TXT")
                    with open(mod_file_path, "a", encoding="utf-8") as f:
                        for value in values:
                            f.write(f"{value}\n")
                    
                    # 显示成功消息
                    success_msg = f"已将OS MOD值添加到MOD.TXT文件：{', '.join(values)}"
                    logger.info(success_msg)
                    self._show_success(success_msg)
                else:
                    logger.error("无法获取OS MOD文本框")
                    self._show_error("无法获取OS MOD文本框")
            else:
                logger.error("无法获取主窗口或模块面板")
                self._show_error("无法获取主窗口或模块面板")
        except Exception as e:
            error_msg = f"将OS MOD值添加到MOD.TXT文件时出错: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            self._show_error(error_msg)