#!/usr/bin/env python3
"""
文档转换 MCP 服务器测试脚本
"""

import os
import sys
import tempfile
from pathlib import Path

# 测试内容
SAMPLE_MARKDOWN = """
# 测试文档

这是一个**测试文档**，用于验证文档转换功能。

## 功能特性

- 支持多种格式转换
- 自动格式检测
- 批量处理能力

> 这是一个引用块

```python
print("Hello, World!")
```
"""

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>测试文档</title>
</head>
<body>
    <h1>测试文档</h1>
    <p>这是一个<strong>HTML测试文档</strong>。</p>
    <ul>
        <li>项目 1</li>
        <li>项目 2</li>
    </ul>
</body>
</html>
"""

SAMPLE_TXT = """
测试文档

这是一个纯文本测试文档。
包含多行内容用于测试转换功能。

功能列表：
1. 文本处理
2. 格式转换
3. 文件操作
"""

class TestDocumentConverter:
    def __init__(self):
        self.test_dir = None
        self.test_files = {}
    
    def setup(self):
        """设置测试环境"""
        # 创建临时测试目录
        self.test_dir = Path(tempfile.mkdtemp())
        print(f"测试目录: {self.test_dir}")
        
        # 创建测试文件
        self.test_files = {
            'markdown': self.test_dir / 'test.md',
            'html': self.test_dir / 'test.html',
            'txt': self.test_dir / 'test.txt'
        }
        
        # 写入测试内容
        self.test_files['markdown'].write_text(SAMPLE_MARKDOWN, encoding='utf-8')
        self.test_files['html'].write_text(SAMPLE_HTML, encoding='utf-8')
        self.test_files['txt'].write_text(SAMPLE_TXT, encoding='utf-8')
        
        print("测试文件已创建:")
        for name, path in self.test_files.items():
            print(f"  {name}: {path}")
        print()
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir and self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
            print(f"测试目录已清理: {self.test_dir}")
    
    def test_imports(self):
        """测试依赖导入"""
        print("=== 测试依赖导入 ===")
        success = True
        
        # 测试 FastMCP
        try:
            from fastmcp import FastMCP
            print("✅ FastMCP 导入成功")
        except ImportError as e:
            print(f"❌ FastMCP 导入失败: {e}")
            success = False
        
        # 测试 MarkItDown
        try:
            from markitdown import MarkItDown
            print("✅ MarkItDown 导入成功")
        except ImportError as e:
            print(f"❌ MarkItDown 导入失败: {e}")
            success = False
        
        # 测试 pypandoc
        try:
            import pypandoc
            print("✅ pypandoc 导入成功")
            try:
                pypandoc.get_pandoc_version()
                print("  ✅ Pandoc 可用")
            except Exception as e:
                print(f"  ⚠️ Pandoc 不可用: {e}")
        except ImportError as e:
            print(f"❌ pypandoc 导入失败: {e}")
            success = False
        
        # 测试 python-docx
        try:
            from docx import Document
            print("✅ python-docx 导入成功")
        except ImportError as e:
            print(f"❌ python-docx 导入失败: {e}")
            success = False
        
        # 测试 pdfplumber
        try:
            import pdfplumber
            print("✅ pdfplumber 导入成功")
        except ImportError as e:
            print(f"❌ pdfplumber 导入失败: {e}")
            success = False
        
        return success
    
    def test_basic_functions(self):
        """测试基本功能"""
        print("=== 测试基本功能 ===")
        success = True
        
        try:
            # 导入服务器模块中的支持格式
            sys.path.insert(0, str(Path(__file__).parent))
            from document_converter_server import SUPPORTED_FORMATS, get_file_format, validate_file_path
            
            print("✅ 服务器模块导入成功")
            
            # 测试支持格式
            print(f"✅ 支持的格式: {list(SUPPORTED_FORMATS.keys())}")
            
            # 测试文件格式检测
            md_format = get_file_format(str(self.test_files['markdown']))
            print(f"✅ Markdown 文件格式检测: {md_format}")
            
            # 测试文件验证
            validate_file_path(str(self.test_files['markdown']))
            print("✅ 文件验证通过")
            
        except Exception as e:
            print(f"❌ 基本功能测试失败: {e}")
            success = False
        
        return success
    
    def test_conversion_logic(self):
        """测试转换逻辑"""
        print("=== 测试转换逻辑 ===")
        success = True
        
        try:
            # 测试 MarkItDown 转换
            from markitdown import MarkItDown
            md_converter = MarkItDown()
            
            # 测试 HTML 到 Markdown
            html_file = str(self.test_files['html'])
            result = md_converter.convert(html_file)
            if result and result.text_content:
                print("✅ HTML -> Markdown 转换成功")
            else:
                print("❌ HTML -> Markdown 转换失败")
                success = False
            
            # 测试 Markdown 处理
            import markdown
            md_content = self.test_files['markdown'].read_text(encoding='utf-8')
            html_output = markdown.markdown(md_content)
            if html_output and '<h1>' in html_output:
                print("✅ Markdown -> HTML 转换成功")
            else:
                print("❌ Markdown -> HTML 转换失败")
                success = False
                
        except Exception as e:
            print(f"❌ 转换逻辑测试失败: {e}")
            success = False
        
        return success
    
    def test_server_startup(self):
        """测试服务器启动"""
        print("=== 测试服务器启动 ===")
        success = True
        
        try:
            # 导入服务器模块
            from document_converter_server import mcp
            print("✅ MCP 服务器实例创建成功")
            
            # 检查工具注册
            if hasattr(mcp, '_tools') and mcp._tools:
                print(f"✅ 已注册 {len(mcp._tools)} 个工具")
                for tool_name in mcp._tools.keys():
                    print(f"  - {tool_name}")
            else:
                print("⚠️ 未找到注册的工具")
            
        except Exception as e:
            print(f"❌ 服务器启动测试失败: {e}")
            success = False
        
        return success
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始文档转换 MCP 服务器测试...")
        print("=" * 50)
        
        self.setup()
        
        try:
            tests = [
                ("依赖导入", self.test_imports),
                ("基本功能", self.test_basic_functions),
                ("转换逻辑", self.test_conversion_logic),
                ("服务器启动", self.test_server_startup)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                try:
                    if test_func():
                        passed += 1
                except Exception as e:
                    print(f"❌ {test_name}测试异常: {e}")
                print()
            
            print("=" * 50)
            print(f"测试完成: {passed}/{total} 通过")
            
            if passed == total:
                print("🎉 所有测试通过！")
            elif passed > 0:
                print("⚠️ 部分测试失败，请检查依赖安装和配置。")
            else:
                print("❌ 所有测试失败，请检查环境配置。")
                
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = TestDocumentConverter()
    tester.run_all_tests()