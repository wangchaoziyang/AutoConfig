#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="autoconfig",  # 项目名称
    version="0.1.0",    # 版本号
    description="一个用于查看和分析系统配置的图形界面工具",
    long_description="""
    AutoConfig是一个图形界面工具，可以：
    - 从Excel文件中读取系统配置信息
    - 分析和显示组件配置详情
    - 处理PHBOM文件
    """,
    author="Your Name",  # 请替换为你的名字
    author_email="your.email@example.com",  # 请替换为你的邮箱
    url="https://github.com/yourusername/autoconfig",  # 请替换为你的项目URL
    
    # 包含的Python包
    packages=find_packages(),
    
    # 项目依赖
    install_requires=[
        "PyQt6>=6.0.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",  # 用于读取Excel文件
    ],
    
    # 入口点，使得项目可以作为命令行工具运行
    entry_points={
        'console_scripts': [
            'autoconfig=main:main',
        ],
    },
    
    # 项目分类信息
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'Environment :: X11 Applications :: Qt',
        'Topic :: Office/Business',
    ],
    
    # 项目关键词
    keywords='system configuration viewer excel phbom',
    
    # Python版本要求
    python_requires='>=3.6',
    
    # 包含非Python文件
    include_package_data=True,
    
    # 许可证
    license='MIT',
) 