#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主程序入口

这个模块是程序的入口点，负责初始化应用程序并启动主窗口
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication

# 导入控制器和视图
from controllers.main_controller import MainController
from ui.main_window import MainWindow
from utils.event_bus import EventBus

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函数"""
    logger.info("应用程序启动")
    
    app = QApplication(sys.argv)
    
    # 创建事件总线实例
    event_bus_instance = EventBus()
    
    # 创建控制器，传递事件总线实例
    controller = MainController(event_bus_instance)
    
    # 创建主窗口，传递控制器
    window = MainWindow(controller)
    
    # 初始化控制器，设置主窗口
    controller.initialize(window)
    
    # 记录事件总线状态
    event_names = controller.event_bus.get_event_names()
    logger.info(f"事件总线已注册事件: {event_names}")
    for event_name in event_names:
        count = controller.event_bus.get_subscriber_count(event_name)
        logger.info(f"事件 {event_name} 有 {count} 个订阅者")
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("程序发生未处理的异常: %s", str(e))