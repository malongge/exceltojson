# Excel to JSON 转换工具

一个简单的工具，用于将Excel文件转换为JSON格式。

## 功能特点

- 支持将Excel文件转换为JSON格式
- 支持合并空单元格（使用上一行的值）
- 支持在输出中包含行号
- 支持大文件分片处理
- 支持日期格式转换

## 安装

```bash
pip install .
```

## 使用方法

### 命令行使用

```bash
excel2json input.xlsx output_dir [选项]

选项:
  --merge-cell     合并空单元格（使用上一行的值）
  --show-row      在输出中包含行号
  --max-row N     每个JSON文件的最大行数（默认：1000）
  --date-mode N   日期格式模式（默认：0）
```

### Python代码中使用

```python
from exceltojson import excel_to_json, ExcelConfig

config = ExcelConfig(
    merge_cell=True,  # 合并空单元格
    show_row=True,    # 显示行号
    max_row=1000,     # 每个文件最大行数
    date_mode=0       # 日期格式模式
)

excel_to_json("input.xlsx", "output_dir", config)
```

## 输出格式

### 包含行号模式 (show_row=True)

```json
{
  "1": {
    "姓名": "张三",
    "年龄": "25",
    "日期": "2024/01/01"
  },
  "2": {
    "姓名": "李四",
    "年龄": "30",
    "日期": "2024/02/01"
  }
}
```

### 列表模式 (show_row=False)

```json
[
  {
    "姓名": "张三",
    "年龄": "25",
    "日期": "2024/01/01"
  },
  {
    "姓名": "李四",
    "年龄": "30",
    "日期": "2024/02/01"
  }
]
```

## 开发

1. 克隆仓库
2. 安装开发依赖：`pip install -r requirements-dev.txt`
3. 运行测试：`python -m pytest tests/` 