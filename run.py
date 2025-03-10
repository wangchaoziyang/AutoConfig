#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动脚本
"""

import os
import sys

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 切换到项目根目录
    os.chdir(current_dir)
    
    # 将项目根目录添加到Python路径
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # 导入并运行主程序
    from main import main
    main()

if __name__ == '__main__':
    main() 