"""
APP MOD数据模型模块
"""
import os
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from utils.event_bus import event_bus
from utils.event_constants import ERROR_OCCURRED, APP_MOD_ADD_CLICKED

# 获取日志记录器
logger = logging.getLogger(__name__)

class AppModModel(QObject):
    """APP MOD数据模型类，用于管理APP MOD数据"""
    
    # 单例实例
    _instance = None
    
    # 信号定义
    app_mod_data_updated = pyqtSignal(dict)  # APP MOD数据更新信号
    
    def __new__(cls, event_bus_instance=None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(AppModModel, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, event_bus_instance=None):
        """初始化APP MOD模型"""
        if hasattr(self, '_initialized') and self._initialized:
            logger.debug("AppModModel已经初始化，跳过")
            return
            
        super().__init__()
        
        # 设置事件总线
        self.event_bus = event_bus_instance if event_bus_instance else event_bus
        
        # 初始化数据
        self.app_mod_data = {}
        self._is_updating = False
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 标记为已初始化
        self._initialized = True
        logger.info("AppModModel初始化完成")
        
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(APP_MOD_ADD_CLICKED, self._handle_app_mod_add)
        
    def _handle_app_mod_add(self, *args):
        """处理APP MOD添加事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            logger.info("处理APP MOD添加事件")
            # 这里实现APP MOD添加逻辑
        except Exception as e:
            error_msg = f"处理APP MOD添加事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        finally:
            self._is_updating = False
            
    def add_app_mod(self, app_mod_data):
        """添加APP MOD数据"""
        if not app_mod_data:
            error_msg = "APP MOD数据为空"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False
            
        try:
            # 这里实现APP MOD数据添加逻辑
            self.app_mod_data.update(app_mod_data)
            self.app_mod_data_updated.emit(self.app_mod_data)
            logger.info("成功添加APP MOD数据")
            return True
        except Exception as e:
            error_msg = f"添加APP MOD数据时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False 