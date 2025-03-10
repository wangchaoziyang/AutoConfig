"""
关键部件数据模型模块
"""
import os
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from utils.event_bus import event_bus
from utils.event_constants import (
    ERROR_OCCURRED, 
    KEYPARTS_LOAD_CLICKED, 
    KEYPARTS_SEARCH_CLICKED,
    KEYPARTS_ADD_CLICKED,
    KEYPARTS_CLEAR_CLICKED
)

# 获取日志记录器
logger = logging.getLogger(__name__)

class KeyPartsModel(QObject):
    """关键部件数据模型类，用于管理关键部件数据"""
    
    # 单例实例
    _instance = None
    
    # 信号定义
    keyparts_data_updated = pyqtSignal(dict)  # 关键部件数据更新信号
    
    def __new__(cls, event_bus_instance=None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(KeyPartsModel, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, event_bus_instance=None):
        """初始化关键部件模型"""
        if hasattr(self, '_initialized') and self._initialized:
            logger.debug("KeyPartsModel已经初始化，跳过")
            return
            
        super().__init__()
        
        # 设置事件总线
        self.event_bus = event_bus_instance if event_bus_instance else event_bus
        
        # 初始化数据
        self.keyparts_data = {}
        self._is_updating = False
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 标记为已初始化
        self._initialized = True
        logger.info("KeyPartsModel初始化完成")
        
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(KEYPARTS_LOAD_CLICKED, self._handle_keyparts_load)
        self.event_bus.subscribe(KEYPARTS_SEARCH_CLICKED, self._handle_keyparts_search)
        self.event_bus.subscribe(KEYPARTS_ADD_CLICKED, self._handle_keyparts_add)
        self.event_bus.subscribe(KEYPARTS_CLEAR_CLICKED, self._handle_keyparts_clear)
        
    def _handle_keyparts_load(self, *args):
        """处理关键部件加载事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            logger.info("处理关键部件加载事件")
            # 这里实现关键部件加载逻辑
        except Exception as e:
            error_msg = f"处理关键部件加载事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        finally:
            self._is_updating = False
            
    def _handle_keyparts_search(self, *args):
        """处理关键部件搜索事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            logger.info("处理关键部件搜索事件")
            # 这里实现关键部件搜索逻辑
        except Exception as e:
            error_msg = f"处理关键部件搜索事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        finally:
            self._is_updating = False
            
    def _handle_keyparts_add(self, *args):
        """处理关键部件添加事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            logger.info("处理关键部件添加事件")
            # 这里实现关键部件添加逻辑
        except Exception as e:
            error_msg = f"处理关键部件添加事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        finally:
            self._is_updating = False
            
    def _handle_keyparts_clear(self, *args):
        """处理关键部件清除事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            logger.info("处理关键部件清除事件")
            # 这里实现关键部件清除逻辑
            self.keyparts_data = {}
            self.keyparts_data_updated.emit({})
        except Exception as e:
            error_msg = f"处理关键部件清除事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        finally:
            self._is_updating = False 