# MCP 文档转换服务器

基于 FastMCP 框架的多格式文档转换 MCP 服务器，支持 PDF、Word、Markdown、HTML 等格式之间的相互转换。

[![魔搭MCP广场](https://img.shields.io/badge/魔搭-MCP广场-blue)](https://modelscope.cn/mcp)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11+-orange)](https://gofastmcp.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🚀 特性

- **多格式支持**: PDF ↔ DOCX ↔ Markdown ↔ HTML ↔ TXT
- **批量转换**: 支持目录批量转换
- **智能转换**: 多种转换策略自动选择最佳方案
- **文件验证**: 自动验证文件格式和大小
- **MCP 标准**: 完全兼容 Model Context Protocol
- **易于集成**: 可与 Claude Desktop、Cursor 等 AI 工具集成

## 📋 支持的格式

| 格式 | 扩展名 | 读取 | 写入 |
|------|--------|------|------|
| PDF | `.pdf` | ✅ | ✅ |
| Word | `.docx`, `.doc` | ✅ | ✅ |
| Markdown | `.md`, `.markdown` | ✅ | ✅ |
| HTML | `.html`, `.htm` | ✅ | ✅ |
| 纯文本 | `.txt`, `.text` | ✅ | ✅ |

## 快速开始

### 方式一：从魔搭MCP广场安装（推荐）

1. 访问 [魔搭MCP广场](https://modelscope.cn/mcp)
2. 搜索 "mcp-document-converter"
3. 点击安装并配置到您的AI助手中

### 方式二：本地安装

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/mcp-document-converter.git
cd mcp-document-converter
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 方式三：使用pip安装

```bash
pip install mcp-document-converter
mcp-document-converter
```

## 🛠️ 安装

### 3. 安装 Pandoc（推荐）

Pandoc 是一个强大的文档转换工具，建议安装以获得最佳转换效果：

**Windows:**
```bash
# 使用 Chocolatey
choco install pandoc

# 或下载安装包
# 访问 https://pandoc.org/installing.html
```

**macOS:**
```bash
brew install pandoc
```

**Linux:**
```bash
sudo apt-get install pandoc
```

## 🚀 使用方法

### 启动服务器

```bash
python document_converter_server.py
```

## AI助手集成

### Claude Desktop 集成

在 Claude Desktop 的配置文件中添加以下配置：

#### Windows

编辑文件：`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "document-converter": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "E:\\DocumentConversion",
      "env": {}
    }
  }
}
```

#### 使用pip安装版本

```json
{
  "mcpServers": {
    "document-converter": {
      "command": "mcp-document-converter",
      "args": [],
      "env": {}
    }
  }
}
```

#### macOS/Linux

编辑文件：`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "document-converter": {
      "command": "python3",
      "args": ["main.py"],
      "cwd": "/path/to/mcp-document-converter",
      "env": {}
    }
  }
}
```

重启 Claude Desktop

### 与 Cursor 集成

1. 创建或编辑 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "document-converter": {
      "command": "python",
      "args": ["path/to/DocumentConversion/document_converter_server.py"],
      "cwd": "path/to/DocumentConversion"
    }
  }
}
```

2. 重启 Cursor

## 🔧 可用工具

### 1. convert_document
转换单个文档格式

**参数:**
- `input_file`: 输入文件路径
- `output_format`: 目标格式 (pdf, docx, markdown, html, txt)
- `output_file`: 输出文件路径（可选）

**示例:**
```
转换 report.pdf 为 Markdown 格式
```

### 2. batch_convert
批量转换目录中的文档

**参数:**
- `input_directory`: 输入目录路径
- `output_format`: 目标格式
- `output_directory`: 输出目录路径（可选）

**示例:**
```
将 documents 文件夹中的所有文档转换为 PDF 格式
```

### 3. list_supported_formats
列出所有支持的文档格式

### 4. get_file_info
获取文件信息（格式、大小等）

**参数:**
- `file_path`: 文件路径

## 💡 使用示例

### 在 Claude Desktop 中使用

1. **单文件转换:**
   ```
   请帮我将 C:\Documents\report.pdf 转换为 Markdown 格式
   ```

2. **批量转换:**
   ```
   将 C:\Documents\presentations 文件夹中的所有文档转换为 HTML 格式
   ```

3. **查看支持格式:**
   ```
   显示所有支持的文档格式
   ```

4. **文件信息:**
   ```
   查看 C:\Documents\manual.docx 的文件信息
   ```

## 🔄 转换策略

服务器使用多层转换策略确保最佳转换效果：

1. **MarkItDown**: 优先用于提取各种格式到 Markdown
2. **Pandoc**: 通用文档转换，支持最多格式
3. **自定义逻辑**: 针对特定格式组合的优化转换

## ⚙️ 配置

### 文件大小限制
默认最大文件大小为 10MB，可在代码中修改 `MAX_FILE_SIZE` 变量。

### 日志级别
可通过修改 `logging.basicConfig(level=logging.INFO)` 调整日志级别。

## 🐛 故障排除

### 常见问题

1. **Pandoc 未找到**
   ```
   错误: pandoc not found
   解决: 安装 Pandoc 并确保在 PATH 中
   ```

2. **文件过大**
   ```
   错误: 文件过大 (>10.0MB)
   解决: 减小文件大小或修改 MAX_FILE_SIZE
   ```

3. **不支持的格式**
   ```
   错误: 不支持的文件格式
   解决: 检查文件扩展名是否在支持列表中
   ```

### 调试模式

启动时添加详细日志：

```bash
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" document_converter_server.py
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd DocumentConversion

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-asyncio

# 运行测试
pytest
```

## 📄 许可证

MIT License

## 🔗 相关链接

- [FastMCP 文档](https://gofastmcp.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Pandoc 官网](https://pandoc.org/)
- [MarkItDown](https://github.com/microsoft/markitdown)