#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
事件总线模块

这个模块提供了一个集中的事件总线，用于应用程序中的事件传递，
减少视图和控制器之间的直接依赖。
"""

from typing import Dict, List, Callable, Any
import logging

logger = logging.getLogger(__name__)

class EventType:
    """事件类型枚举"""
    pass

class EventBus:
    """事件总线类，用于处理事件的发布和订阅"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance
    
    def __init__(self):
        """初始化事件总线"""
        # 在__new__中已经初始化了_subscribers，这里不需要重复初始化
        pass
    
    def subscribe(self, event_type, handler):
        """订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        
    def unsubscribe(self, event_type, handler):
        """取消订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
            
    def publish(self, event_type, *args, **kwargs):
        """发布事件
        
        Args:
            event_type: 事件类型
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"处理事件 {event_type} 时出错: {str(e)}")
    
    def clear(self) -> None:
        """清除所有订阅"""
        self._subscribers.clear()
        logger.debug("已清除所有事件订阅")
    
    def get_event_names(self) -> List[str]:
        """获取所有已注册的事件名称"""
        return list(self._subscribers.keys())
    
    def get_subscriber_count(self, event_type: str) -> int:
        """获取特定事件的订阅者数量"""
        return len(self._subscribers.get(event_type, []))

# 创建全局事件总线实例
event_bus = EventBus() 