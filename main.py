#!/usr/bin/env python3
"""MCP Document Converter - 主入口文件

启动多格式文档转换 MCP 服务器
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_document_converter.server import mcp

if __name__ == "__main__":
    # 启动MCP服务器
    mcp.run()