#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型包

该包包含所有数据模型类，负责处理应用程序的数据逻辑。
"""

from models.config_model import ConfigModel
from models.phbom_model import PHBOMModel

__all__ = ['ConfigModel', 'PHBOMModel'] 