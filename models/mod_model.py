"""
MOD数据模型模块
"""
import os
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from utils.event_bus import event_bus
from utils.event_constants import ERROR_OCCURRED, MOD_LOAD_CLICKED, MOD_ADD_CLICKED

# 获取日志记录器
logger = logging.getLogger(__name__)

class MODModel(QObject):
    """MOD数据模型类，用于管理MOD数据"""
    
    # 单例实例
    _instance = None
    
    # 信号定义
    mod_data_updated = pyqtSignal(dict)  # MOD数据更新信号
    
    def __new__(cls, event_bus_instance=None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(MODModel, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, event_bus_instance=None):
        """初始化MOD模型"""
        if self._initialized:
            logger.debug("MODModel已经初始化，跳过")
            return
            
        super().__init__()
        
        # 设置事件总线
        self.event_bus = event_bus_instance if event_bus_instance else event_bus
        
        # 初始化数据
        self.mod_data = {}
        self._is_updating = False
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 标记为已初始化
        self._initialized = True
        logger.info("MODModel初始化完成")
        
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(MOD_LOAD_CLICKED, self._handle_mod_load)
        self.event_bus.subscribe(MOD_ADD_CLICKED, self._handle_mod_add)
        
    def _handle_mod_load(self, *args):
        """处理MOD加载事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            logger.info("处理MOD加载事件")
            # 这里实现MOD加载逻辑
        except Exception as e:
            error_msg = f"处理MOD加载事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        finally:
            self._is_updating = False
            
    def _handle_mod_add(self, *args):
        """处理MOD添加事件"""
        if self._is_updating:
            return
            
        try:
            self._is_updating = True
            logger.info("处理MOD添加事件")
            # 这里实现MOD添加逻辑
        except Exception as e:
            error_msg = f"处理MOD添加事件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
        finally:
            self._is_updating = False
            
    def load_mod_file(self, file_path):
        """加载MOD文件"""
        if not os.path.exists(file_path):
            error_msg = f"MOD文件不存在: {file_path}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False
            
        try:
            # 这里实现MOD文件加载逻辑
            logger.info(f"成功加载MOD文件: {file_path}")
            return True
        except Exception as e:
            error_msg = f"加载MOD文件时出错: {str(e)}"
            logger.error(error_msg)
            self.event_bus.publish(ERROR_OCCURRED, error_msg)
            return False 