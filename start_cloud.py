#!/usr/bin/env python3
"""
云端MCP文档转换服务器启动脚本
适用于魔搭云端托管平台
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_cloud_environment():
    """设置云端环境配置"""
    # 从环境变量或配置文件读取设置
    config_file = project_root / "mcp_cloud.json"
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 设置环境变量
        cloud_env = config.get('cloud', {}).get('environment', {})
        for key, value in cloud_env.items():
            if key not in os.environ:
                os.environ[key] = str(value)
    
    # 确保必要的环境变量存在
    default_env = {
        'MCP_SERVER_NAME': 'DocumentConverter',
        'MCP_LOG_LEVEL': 'INFO',
        'MCP_MAX_FILE_SIZE': '50MB',
        'MCP_TEMP_DIR': '/tmp',
        'MCP_ENABLE_PANDOC': 'true'
    }
    
    for key, value in default_env.items():
        if key not in os.environ:
            os.environ[key] = value

def setup_logging():
    """设置日志配置"""
    log_level = os.environ.get('MCP_LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """主启动函数"""
    try:
        # 设置云端环境
        setup_cloud_environment()
        
        # 设置日志
        setup_logging()
        
        logger = logging.getLogger(__name__)
        logger.info("启动云端MCP文档转换服务器...")
        
        # 导入并启动MCP服务器
        from document_converter_mcp import main as mcp_main
        
        logger.info("MCP服务器配置完成，开始运行...")
        mcp_main()
        
    except Exception as e:
        logging.error(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()