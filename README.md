# Excel to JSON Converter

[![Build Status](https://travis-ci.org/malongge/exceltojson.svg?branch=master)](https://travis-ci.org/malongge/exceltojson)

## 中文文档

### 命令行参数说明

- `-h | --help`: 显示帮助文档
- `-S | --notShowRow`: 默认表单中的行号将作为json文件中内容的关键字。使用此选项后，json文件中的内容将保存为包含表单中行内容的列表
- `-s | --sourcePath`: 要转换成json文件的excel文件所在的路径
- `-o | --outDir`: 生成的json文件所存放的目录
- `-P | --noPatchAlias`: 使用头部别名时(-a, --alias)，默认每个表单的头部都会作为每行的单元格的关键字，有别名的头部会以别名作为关键字。使用此选项后，没有别名的表单将被忽略，不会进行转换处理
- `-M | --noMergeCell`: 当表单中存在空的单元格时，默认按照合并单元格方式处理，使用前面行单元格的内容作为空单元格的内容。使用此选项后，空单元格不做特殊处理，将变成空字符串
- `-r | --rowMax`: 默认值为1000，用于限制json文件的大小。当表单包含大量行时，可以将其切割成多个小的json文件。默认每个json文件包含1000行内容。此参数最大取值为1000000
- `-i | --index`: 表单索引值列表，使用逗号分隔的整型数值字符串，例如：`-i 0,1,2`
- `-n | --names`: 表单名字列表，使用逗号分隔的字符串，例如：`-n name1,name2,name3`
- `-a | --alias`: 头部别名列表，使用分号分隔的字符串，每个分隔的值包含逗号分隔的字符串，逗号分隔的值包含冒号分隔的两部分，例如：`-a header1:alias1,header2:alias2;otherHeader:otherAlias`

> 注意：`-a, --alias` 必须与 `-i, --index` 或者 `-n, --names` 成对出现。例如：`-a header1:alias1,header2:alias2;otherHeader:otherAlias -i 0,1`。这是因为分号分隔的别名部分包含两个值，因此对于表单下标也应该为逗号分隔的两个值。

## English Documentation

### Command Line Arguments

- `-h | --help`: Get help document

## Installation

```bash
pip install excel2json
```

## Windows Example

```bash
excel2json -s "D:\exceltojson\data\test_excel_process.xlsx" -o "D:\output"
dir D:\output
```

Output:
```
d:\out 的目录
2016/06/27  16:52    <DIR>          .
2016/06/27  16:52    <DIR>          ..
2016/06/27  16:52                96 sheet-0.json
2016/06/27  16:52                91 sheet-1.json
2016/06/27  16:52               638 sheet-2.json
               3 个文件            825 字节
               2 个目录 370,679,599,104 可用字节
```

sheet-0.json:
```json
{"2": {"\u5934\u90e8": "\u5185\u5bb92", "header1": "\u5185\u5bb91", "header2": "\u5185\u5bb93"}}
```

Using alias:
```bash
excel2json -s "D:\exceltojson\data\test_excel_process.xlsx" -o "D:\out" -i 0 -a 头部:header4
```

sheet-0.json:
```json
{"2": {"header1": "\u5185\u5bb91", "header4": "\u5185\u5bb92", "header2": "\u5185\u5bb93"}}
``` 