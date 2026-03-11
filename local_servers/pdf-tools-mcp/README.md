# PDF Tools MCP Server

[English](#english) | [中文](#中文)

---

## 中文

一个基于 FastMCP 的 PDF 读取和操作工具服务器，支持从 PDF 文件的指定页面范围提取文本内容。

### 功能特性

- 📄 读取 PDF 文件指定页面范围的内容
- 🔢 支持起始和结束页面参数（包含范围）
- 🛡️ 自动处理无效页码（负数、超出范围等）
- 📊 获取 PDF 文件的基本信息
- 🔗 合并多个 PDF 文件
- ✂️ 提取 PDF 的特定页面
- 🔍 正则表达式搜索功能，支持分页查看结果
- 🌐 **URL 支持** - 支持直接从 URL 读取和操作 PDF 文件
- 💾 智能缓存机制，相同 URL 的 PDF 自动复用临时文件

### 安装

#### 从 PyPI 安装

```bash
uv add pdf-tools-mcp
```

如果 `uv add` 遇到依赖冲突，建议使用：

```bash
uvx tool install pdf-tools-mcp
```

#### 从源码安装

```bash
git clone https://github.com/yourusername/pdf-tools-mcp.git
cd pdf-tools-mcp
uv sync
```

### 使用方法

#### 与 Claude Desktop 集成

添加到你的 `~/.config/claude/claude_desktop_config.json` (Linux/Windows) 或 `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

**开发/未发布版本配置**

```json
{
  "mcpServers": {
    "pdf-tools-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<path/to/the/repo>/pdf-tools-mcp",
        "run",
        "pdf-tools-mcp",
        "--workspace_path",
        "</your/workspace/directory>",
        "--tempfile_dir",
        "</your/temp/directory>"
      ]
    }
  }
}
```

**已发布版本配置**

```json
{
  "mcpServers": {
    "pdf-tools-mcp": {
      "command": "uvx",
      "args": [
        "pdf-tools-mcp",
        "--workspace_path",
        "</your/workspace/directory>",
        "--tempfile_dir",
        "</your/temp/directory>"
      ]
    }
  }
}
```

**注意**: 出于安全考虑，此工具只能访问指定工作目录(`--workspace_path`)内的文件，无法访问工作目录之外的文件。

如果配置后无法正常工作或在UI中无法显示，请通过 `uv cache clean` 清除缓存。

#### 作为命令行工具

```bash
# 基本使用
pdf-tools-mcp

# 指定工作目录和临时文件目录
pdf-tools-mcp --workspace_path /path/to/workspace --tempfile_dir /path/to/temp
```

#### 作为 Python 包

```python
from pdf_tools_mcp import read_pdf_pages, get_pdf_info, merge_pdfs, extract_pdf_pages

# 读取 PDF 页面（支持 URL）
result = await read_pdf_pages("https://example.com/document.pdf", 1, 5)

# 获取 PDF 信息（支持 URL）
info = await get_pdf_info("document.pdf")

# 合并 PDF 文件（支持 URL 和本地文件混合）
result = await merge_pdfs(["file1.pdf", "https://example.com/file2.pdf"], "merged.pdf")

# 提取特定页面
result = await extract_pdf_pages("source.pdf", [1, 3, 5], "extracted.pdf")
```

### 主要工具函数

#### 1. read_pdf_pages
读取 PDF 文件指定页面范围的内容

**参数:**
- `pdf_file_path` (str): PDF 文件路径或 URL
- `start_page` (int, 默认 1): 起始页码
- `end_page` (int, 默认 1): 结束页码

**URL 支持:**
- 支持 `http://` 和 `https://` 协议的 URL
- 自动下载 PDF 文件到临时目录
- 相同 URL 会复用已下载的文件
- 支持 PDF 文件格式验证

**示例:**
```python
# 读取本地文件第 1-5 页
result = await read_pdf_pages("document.pdf", 1, 5)

# 读取 URL 中的 PDF 第 10 页
result = await read_pdf_pages("https://example.com/document.pdf", 10, 10)
```

#### 2. get_pdf_info
获取 PDF 文件的基本信息

**参数:**
- `pdf_file_path` (str): PDF 文件路径或 URL

**返回信息:**
- 总页数
- 标题
- 作者
- 创建者
- 创建日期

#### 3. merge_pdfs
合并多个 PDF 文件

**参数:**
- `pdf_paths` (List[str]): 要合并的 PDF 文件路径列表（支持 URL 和本地文件混合）
- `output_path` (str): 合并后的输出文件路径（必须是本地路径）

#### 4. extract_pdf_pages
从 PDF 中提取特定页面

**参数:**
- `source_path` (str): 源 PDF 文件路径或 URL
- `page_numbers` (List[int]): 要提取的页码列表（从 1 开始）
- `output_path` (str): 输出文件路径（必须是本地路径）

### 错误处理

工具自动处理以下情况：
- 负数页码：自动调整为第 1 页
- 超出 PDF 总页数的页码：自动调整为最后一页
- 起始页大于结束页：自动交换
- 文件未找到：返回相应错误信息
- 权限不足：返回相应错误信息

### 使用示例

```python
# 获取 PDF 信息
info = await get_pdf_info("sample.pdf")
print(info)

# 读取前 3 页
content = await read_pdf_pages("sample.pdf", 1, 3)
print(content)

# 读取最后一页（假设 PDF 有 10 页）
content = await read_pdf_pages("sample.pdf", 10, 10)
print(content)

# 使用 URL 读取 PDF
content = await read_pdf_pages("https://example.com/sample.pdf", 1, 3)
print(content)

# 合并多个 PDF（混合本地文件和 URL）
result = await merge_pdfs([
    "part1.pdf", 
    "https://example.com/part2.pdf", 
    "part3.pdf"
], "complete.pdf")
print(result)

# 从 URL 的 PDF 提取特定页面
result = await extract_pdf_pages("https://example.com/source.pdf", [1, 3, 5, 7], "selected.pdf")
print(result)
```

### 注意事项

- 页面范围使用包含区间，即起始页和结束页都包含在内
- 如果指定页面没有文本内容，将被跳过
- 返回结果会显示 PDF 总页数和实际提取的页面范围
- 支持各种语言的 PDF 文档
- 建议一次读取的页面数不超过 50 页，以避免性能问题
- **URL 支持说明**:
  - 支持 HTTP 和 HTTPS 协议的 URL
  - URL 中的 PDF 会被下载到临时目录（默认：`~/.pdf_tools_temp`）
  - 相同的 URL 会复用已下载的文件，避免重复下载
  - 下载的文件会进行 PDF 格式验证
  - 输出文件路径（如合并、提取功能）必须是本地路径，不能是 URL

### 开发

#### 构建

```bash
uv build
```

#### 发布到 PyPI

```bash
uv publish
```

#### 本地开发

```bash
# 安装开发依赖
uv sync

# 运行测试
uv run python -m pytest

# 运行服务器
uv run python -m pdf_tools_mcp.server
```

---

## English

A FastMCP-based PDF reading and manipulation tool server that supports extracting text content from specified page ranges of PDF files.

### Features

- 📄 Read content from specified page ranges of PDF files
- 🔢 Support for start and end page parameters (inclusive range)
- 🛡️ Automatic handling of invalid page numbers (negative numbers, out of range, etc.)
- 📊 Get basic information about PDF files
- 🔗 Merge multiple PDF files
- ✂️ Extract specific pages from PDFs
- 🔍 Regular expression search functionality with paginated results
- 🌐 **URL Support** - Direct support for reading and manipulating PDF files from URLs
- 💾 Smart caching mechanism to automatically reuse temporary files for the same URLs

### Installation

#### Install from PyPI

```bash
uv add pdf-tools-mcp
```

If `uv add` encounters dependency conflicts, use:

```bash
uvx tool install pdf-tools-mcp
```

#### Install from source

```bash
git clone https://github.com/yourusername/pdf-tools-mcp.git
cd pdf-tools-mcp
uv sync
```

### Usage

#### Usage with Claude Desktop

Add to your `~/.config/claude/claude_desktop_config.json` (Linux/Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

**Development/Unpublished Servers Configuration**

```json
{
  "mcpServers": {
    "pdf-tools-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<path/to/the/repo>/pdf-tools-mcp",
        "run",
        "pdf-tools-mcp",
        "--workspace_path",
        "</your/workspace/directory>",
        "--tempfile_dir",
        "</your/temp/directory>"
      ]
    }
  }
}
```

**Published Servers Configuration**

```json
{
  "mcpServers": {
    "pdf-tools-mcp": {
      "command": "uvx",
      "args": [
        "pdf-tools-mcp",
        "--workspace_path",
        "</your/workspace/directory>",
        "--tempfile_dir",
        "</your/temp/directory>"
      ]
    }
  }
}
```

**Note**: For security reasons, this tool can only access files within the specified workspace directory (`--workspace_path`) and cannot access files outside the workspace directory.

In case it's not working or showing in the UI, clear your cache via `uv cache clean`.

#### As a command line tool

```bash
# Basic usage
pdf-tools-mcp

# Specify workspace directory and temporary file directory
pdf-tools-mcp --workspace_path /path/to/workspace --tempfile_dir /path/to/temp
```

#### As a Python package

```python
from pdf_tools_mcp import read_pdf_pages, get_pdf_info, merge_pdfs, extract_pdf_pages

# Read PDF pages (URL support)
result = await read_pdf_pages("https://example.com/document.pdf", 1, 5)

# Get PDF info (URL support)
info = await get_pdf_info("document.pdf")

# Merge PDF files (mixed URLs and local files)
result = await merge_pdfs(["file1.pdf", "https://example.com/file2.pdf"], "merged.pdf")

# Extract specific pages
result = await extract_pdf_pages("source.pdf", [1, 3, 5], "extracted.pdf")
```

### Main Tool Functions

#### 1. read_pdf_pages
Read content from specified page ranges of a PDF file

**Parameters:**
- `pdf_file_path` (str): PDF file path or URL
- `start_page` (int, default 1): Starting page number
- `end_page` (int, default 1): Ending page number

**URL Support:**
- Supports `http://` and `https://` protocol URLs
- Automatically downloads PDF files to temporary directory
- Reuses downloaded files for the same URLs
- Includes PDF file format validation

**Example:**
```python
# Read pages 1-5 from local file
result = await read_pdf_pages("document.pdf", 1, 5)

# Read page 10 from URL
result = await read_pdf_pages("https://example.com/document.pdf", 10, 10)
```

#### 2. get_pdf_info
Get basic information about a PDF file

**Parameters:**
- `pdf_file_path` (str): PDF file path or URL

**Returns:**
- Total page count
- Title
- Author
- Creator
- Creation date

#### 3. merge_pdfs
Merge multiple PDF files

**Parameters:**
- `pdf_paths` (List[str]): List of PDF file paths to merge (supports mixed URLs and local files)
- `output_path` (str): Output file path for the merged PDF (must be local path)

#### 4. extract_pdf_pages
Extract specific pages from a PDF

**Parameters:**
- `source_path` (str): Source PDF file path or URL
- `page_numbers` (List[int]): List of page numbers to extract (1-based)
- `output_path` (str): Output file path (must be local path)

### Error Handling

The tool automatically handles the following situations:
- Negative page numbers: automatically adjusted to page 1
- Page numbers exceeding total PDF pages: automatically adjusted to the last page
- Start page greater than end page: automatically swapped
- File not found: returns appropriate error message
- Insufficient permissions: returns appropriate error message

### Usage Examples

```python
# Get PDF info
info = await get_pdf_info("sample.pdf")
print(info)

# Read first 3 pages
content = await read_pdf_pages("sample.pdf", 1, 3)
print(content)

# Read last page (assuming PDF has 10 pages)
content = await read_pdf_pages("sample.pdf", 10, 10)
print(content)

# Read PDF from URL
content = await read_pdf_pages("https://example.com/sample.pdf", 1, 3)
print(content)

# Merge multiple PDFs (mixed local files and URLs)
result = await merge_pdfs([
    "part1.pdf", 
    "https://example.com/part2.pdf", 
    "part3.pdf"
], "complete.pdf")
print(result)

# Extract specific pages from URL PDF
result = await extract_pdf_pages("https://example.com/source.pdf", [1, 3, 5, 7], "selected.pdf")
print(result)
```

### Notes

- Page ranges use inclusive intervals, meaning both start and end pages are included
- Pages without text content will be skipped
- Results show total PDF page count and actual extracted page range
- Supports PDF documents in various languages
- Recommended to read no more than 50 pages at a time to avoid performance issues
- **URL Support Notes**:
  - Supports HTTP and HTTPS protocol URLs
  - PDFs from URLs are downloaded to a temporary directory (default: `~/.pdf_tools_temp`)
  - Same URLs reuse downloaded files to avoid duplicate downloads
  - Downloaded files undergo PDF format validation
  - Output file paths (for merge, extract functions) must be local paths, not URLs

### Development

#### Build

```bash
uv build
```

#### Publish to PyPI

```bash
uv publish
```

#### Local Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run python -m pytest

# Run server
uv run python -m pdf_tools_mcp.server
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Changelog

### 0.1.4
- **🌐 URL Support**: Add support for reading PDF files directly from URLs
  - Support for HTTP and HTTPS protocols
  - Automatic PDF download to temporary directory with UUID naming
  - Smart caching mechanism to reuse downloaded files for same URLs
  - PDF format validation (magic bytes, PyPDF2 compatibility check)
  - URL to temporary file mapping management with JSON storage
- **⚙️ Configuration**: Add `--tempfile_dir` parameter for custom temporary directory
- **🔧 Enhanced Functions**: All main functions now support URLs:
  - `read_pdf_pages`: Read from URLs or local files
  - `get_pdf_info`: Get info from URLs or local files
  - `search_pdf_content`: Search in URLs or local files
  - `merge_pdfs`: Merge mixed URLs and local files
  - `extract_pdf_pages`: Extract from URLs to local files
- **📚 Documentation**: Updated README with URL usage examples and configuration

### 0.1.3
- Add regex search functionality for PDF content
- Add paginated search results with session management
- Add search navigation (next/prev/go to page)
- Add PDF content caching for improved performance
- Add search session cleanup and memory management

### 0.1.2
- Initial release
- Support for PDF text extraction
- Support for PDF info retrieval
- Support for PDF merging
- Support for page extraction
