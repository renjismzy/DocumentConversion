#!/usr/bin/env python3
"""
文档转换 MCP 服务器
基于 FastMCP 构建，支持多种文档格式之间的转换

支持的转换格式：
- PDF ↔ Markdown, HTML, DOCX, TXT
- DOCX ↔ Markdown, HTML, PDF, TXT
- Markdown ↔ PDF, HTML, DOCX, TXT
- HTML ↔ PDF, Markdown, DOCX, TXT
- TXT ↔ PDF, Markdown, HTML, DOCX
"""

import os
import tempfile
import logging
import time
from pathlib import Path
from typing import Optional, Union
import asyncio
import traceback
from functools import wraps

import json

try:
    from fastmcp import FastMCP
except ImportError:
    print("请安装 fastmcp: pip install fastmcp")
    exit(1)

# 依赖可用性检查
markitdown_available = True
try:
    from markitdown import MarkItDown
except ImportError:
    print("请安装 markitdown: pip install markitdown[all]")
    markitdown_available = False
    exit(1)

pypandoc_available = True
try:
    import pypandoc
except ImportError:
    print("请安装 pypandoc: pip install pypandoc")
    pypandoc_available = False
    exit(1)

docx_available = True
try:
    from docx import Document as DocxDocument
    from docx.shared import Inches
except ImportError:
    print("请安装 python-docx: pip install python-docx")
    docx_available = False
    exit(1)

pdfplumber_available = True
try:
    import pdfplumber
except ImportError:
    print("请安装 pdfplumber: pip install pdfplumber")
    pdfplumber_available = False
    exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_document_converter.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 性能监控装饰器
def performance_monitor(func):
    """监控函数执行时间和错误"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 执行成功，耗时: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {execution_time:.2f}秒，错误: {str(e)}")
            logger.debug(f"详细错误信息: {traceback.format_exc()}")
            raise
    return wrapper

# 配置管理
class ServerConfig:
    """服务器配置管理"""
    def __init__(self):
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB
        self.temp_dir = os.getenv('TEMP_DIR', tempfile.gettempdir())
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.enable_pandoc = os.getenv('ENABLE_PANDOC', 'true').lower() == 'true'
        
    def validate_file_size(self, file_path: str) -> bool:
        """验证文件大小"""
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= self.max_file_size
        except OSError:
            return False
            
    def get_temp_file(self, suffix: str = '') -> str:
        """获取临时文件路径"""
        return tempfile.mktemp(suffix=suffix, dir=self.temp_dir)

# 全局配置实例
config = ServerConfig()

# 创建 FastMCP 服务器实例
mcp = FastMCP("DocumentConverter")

# 初始化 MarkItDown
md_converter = MarkItDown()

# 支持的文件格式
SUPPORTED_FORMATS = {
    'pdf': ['.pdf'],
    'docx': ['.docx', '.doc'],
    'markdown': ['.md', '.markdown'],
    'html': ['.html', '.htm'],
    'txt': ['.txt', '.text']
}

# 文件大小限制 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_file_path(file_path: str) -> bool:
    """验证文件路径是否存在且可读"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    if not path.is_file():
        raise ValueError(f"路径不是文件: {file_path}")
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"文件过大 (>{MAX_FILE_SIZE/1024/1024:.1f}MB): {file_path}")
    return True

def get_file_format(file_path: str) -> str:
    """根据文件扩展名确定文件格式"""
    ext = Path(file_path).suffix.lower()
    for format_name, extensions in SUPPORTED_FORMATS.items():
        if ext in extensions:
            return format_name
    raise ValueError(f"不支持的文件格式: {ext}")

def create_temp_file(content: str, suffix: str) -> str:
    """创建临时文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name

@mcp.tool()
@performance_monitor
def convert_document(input_file: str, output_format: str, output_file: Optional[str] = None) -> str:
    """
    转换文档格式
    
    Args:
        input_file: 输入文件路径
        output_format: 目标格式 (pdf, docx, markdown, html, txt)
        output_file: 输出文件路径（可选，如果不提供则自动生成）
    
    Returns:
        转换结果信息和输出文件路径
    """
    try:
        # 验证输入文件
        validate_file_path(input_file)
        
        # 验证文件大小
        if not config.validate_file_size(input_file):
            max_size_mb = config.max_file_size / (1024 * 1024)
            return f"错误：文件大小超过限制 ({max_size_mb:.1f}MB)"
        
        input_format = get_file_format(input_file)
        
        # 验证输出格式
        if output_format not in SUPPORTED_FORMATS:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        # 生成输出文件路径
        if not output_file:
            input_path = Path(input_file)
            output_ext = SUPPORTED_FORMATS[output_format][0]
            output_file = str(input_path.with_suffix(output_ext))
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"开始转换: {input_file} ({input_format}) -> {output_file} ({output_format})")
        
        # 执行转换
        if input_format == output_format:
            # 相同格式，直接复制
            import shutil
            shutil.copy2(input_file, output_file)
            return f"文件已复制到: {output_file}"
        
        # 使用不同的转换策略
        success = False
        
        # 策略1: 使用 MarkItDown (适合从各种格式转为 Markdown)
        if output_format == 'markdown':
            try:
                result = md_converter.convert(input_file)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.text_content)
                success = True
                logger.info(f"使用 MarkItDown 成功转换")
            except Exception as e:
                logger.warning(f"MarkItDown 转换失败: {e}")
        
        # 策略2: 使用 Pandoc (通用转换)
        if not success:
            try:
                # 确定 pandoc 格式名称
                pandoc_formats = {
                    'markdown': 'markdown',
                    'html': 'html',
                    'docx': 'docx',
                    'txt': 'plain',
                    'pdf': 'pdf'
                }
                
                input_pandoc_format = pandoc_formats.get(input_format)
                output_pandoc_format = pandoc_formats.get(output_format)
                
                if input_pandoc_format and output_pandoc_format:
                    pypandoc.convert_file(
                        input_file,
                        output_pandoc_format,
                        format=input_pandoc_format,
                        outputfile=output_file
                    )
                    success = True
                    logger.info(f"使用 Pandoc 成功转换")
            except Exception as e:
                logger.warning(f"Pandoc 转换失败: {e}")
        
        # 策略3: 自定义转换逻辑
        if not success:
            success = _custom_convert(input_file, input_format, output_file, output_format)
        
        if success:
            return f"转换成功！输出文件: {output_file}"
        else:
            raise Exception("所有转换策略都失败了")
            
    except Exception as e:
        error_msg = f"转换失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

def _custom_convert(input_file: str, input_format: str, output_file: str, output_format: str) -> bool:
    """自定义转换逻辑"""
    try:
        # PDF 到文本的转换
        if input_format == 'pdf' and output_format == 'txt':
            text_content = ""
            with pdfplumber.open(input_file) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() or ""
                    text_content += "\n\n"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return True
        
        # 文本到 DOCX 的转换
        if input_format == 'txt' and output_format == 'docx':
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc = DocxDocument()
            doc.add_paragraph(content)
            doc.save(output_file)
            return True
        
        # Markdown 到 HTML 的转换
        if input_format == 'markdown' and output_format == 'html':
            try:
                import markdown
                with open(input_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                html_content = markdown.markdown(md_content)
                html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>转换的文档</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
                """
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_template)
                return True
            except ImportError:
                logger.warning("markdown 库未安装，跳过自定义 Markdown 转换")
        
        return False
        
    except Exception as e:
        logger.error(f"自定义转换失败: {e}")
        return False

@mcp.tool()
def list_supported_formats() -> str:
    """
    列出所有支持的文档格式
    
    Returns:
        支持的格式列表
    """
    formats_info = []
    for format_name, extensions in SUPPORTED_FORMATS.items():
        formats_info.append(f"{format_name}: {', '.join(extensions)}")
    
    return "支持的文档格式:\n" + "\n".join(formats_info)

@mcp.tool()
@performance_monitor
def health_check() -> str:
    """
    服务器健康检查
    
    Returns:
        健康状态信息
    """
    try:
        health_info = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "dependencies": {
                "fastmcp": "available",
                "markitdown": "available" if markitdown_available else "unavailable",
                "pypandoc": "available" if pypandoc_available else "unavailable",
                "python_docx": "available" if docx_available else "unavailable",
                "pdfplumber": "available" if pdfplumber_available else "unavailable"
            },
            "config": {
                "max_file_size": f"{config.max_file_size / (1024*1024):.1f}MB",
                "temp_dir": config.temp_dir,
                "pandoc_enabled": config.enable_pandoc
            },
            "supported_formats": list(SUPPORTED_FORMATS.keys())
        }
        return json.dumps(health_info, ensure_ascii=False, indent=2)
    except Exception as e:
        error_info = {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }
        return json.dumps(error_info, ensure_ascii=False, indent=2)

@mcp.tool()
@performance_monitor
def get_file_info(file_path: str) -> str:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件信息（格式、大小等）
    """
    try:
        validate_file_path(file_path)
        path = Path(file_path)
        file_format = get_file_format(file_path)
        file_size = path.stat().st_size
        
        info = f"""
文件信息:
- 路径: {file_path}
- 格式: {file_format}
- 大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)
- 扩展名: {path.suffix}
        """.strip()
        
        return info
        
    except Exception as e:
        return f"获取文件信息失败: {str(e)}"

@mcp.tool()
@performance_monitor
def batch_convert(input_directory: str, output_format: str, output_directory: Optional[str] = None) -> str:
    """
    批量转换目录中的文档
    
    Args:
        input_directory: 输入目录路径
        output_format: 目标格式
        output_directory: 输出目录路径（可选）
    
    Returns:
        批量转换结果
    """
    try:
        input_dir = Path(input_directory)
        if not input_dir.exists() or not input_dir.is_dir():
            raise ValueError(f"输入目录不存在或不是目录: {input_directory}")
        
        if not output_directory:
            output_directory = str(input_dir / f"converted_{output_format}")
        
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)
        
        # 查找所有支持的文件
        supported_files = []
        for format_name, extensions in SUPPORTED_FORMATS.items():
            for ext in extensions:
                supported_files.extend(input_dir.glob(f"*{ext}"))
        
        if not supported_files:
            return f"在目录 {input_directory} 中未找到支持的文档文件"
        
        results = []
        success_count = 0
        
        for file_path in supported_files:
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    results.append(f"跳过 {file_path.name} (文件过大)")
                    continue
                
                output_ext = SUPPORTED_FORMATS[output_format][0]
                output_file = output_dir / f"{file_path.stem}{output_ext}"
                
                result = convert_document(str(file_path), output_format, str(output_file))
                if "成功" in result:
                    success_count += 1
                    results.append(f"✓ {file_path.name} -> {output_file.name}")
                else:
                    results.append(f"✗ {file_path.name}: {result}")
                    
            except Exception as e:
                results.append(f"✗ {file_path.name}: {str(e)}")
        
        summary = f"批量转换完成: {success_count}/{len(supported_files)} 个文件成功转换\n"
        summary += f"输出目录: {output_directory}\n\n"
        summary += "详细结果:\n" + "\n".join(results)
        
        return summary
        
    except Exception as e:
        return f"批量转换失败: {str(e)}"

def main():
    """主入口函数"""
    logger.info("启动文档转换 MCP 服务器...")
    logger.info(f"支持的格式: {list(SUPPORTED_FORMATS.keys())}")
    mcp.run()

if __name__ == "__main__":
    main()