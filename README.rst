.. image:: https://travis-ci.org/malongge/exceltojson.svg?branch=master
    :target: https://travis-ci.org/malongge/exceltojson


中文帮助文档
=======================

-h | --help： 帮助文档

-S | --notShowRow:  默认表单中的行号将作为json文件中内容的关键字，
如果使用了这个选项，那么json文件中的内容将保存的是包含表单中行内容一个列表

-s | --sourcePath: 要转换成json文件的excel文件所在的路径

-o | --outDir: 生成的json文件所存放的目录

-P | --noPatchAlias: 使用了头部别名的话(-a, --alias)，默认每个表单的头部都会作为每行的单元格的关键字，
有别名的头部会以别名作为关键字，如果使用了这个选项没有别名的表单会被忽悠，将不会转换处理

-M | --noMergeCell: 当表单中存在空的单元格时，默认是按照变得的合并单元格方式处理，以前面行单元格的内容作
为空单元格的内容，如果使用了这个选项，空单元格不做特殊处理，将会变成一个空的字符串

-r | --rowMax: 这个选项的默认值是1000，它是一个整形数值，它主要的作用是限制json文件的大小，例如有一个包含上百万的行的表单，当转换成一个json文件时，这个json文件将会非常大，使用这个参数可以将这个表单，切割成一些小的json文件，如果你使用默认值的话，每个json文件将包含1000行的内容, 这个参数最大取值为1000000，因此你不能取比这个更大的值.

-i | --index: 表单索引值列表，它应该是一个包含逗号分隔符的字符串，每个分割的值都应该是一个整型数值，例如(-i 0,1,2)

-n | --names: 表单名字列表，它应该是一个包含逗号分隔符的字符串，例如(-n name1,name2,name3)

-a | --alias: 头部别名列表，它应该是一个包含分号分隔符的字符串，每个分隔的值应该是包含逗号分隔符的字符串，
逗号分隔符分隔的值应该是包含冒号分隔符的两部分，
例如(-a header1:alias1,header2:alias2;otherHeader:otherAlias)

注: (-a, --alias) 必须与 (-i, --index) 或者 (-n, --names) 成对出现, 例如 (-a header1:alias1,header2:alias2;otherHeader:otherAlias -i 0,1) 原因如下, 分号分隔的别名部分包含两个值("header1:alias1,header2:alias2"   "header2:alias2;otherHeader:otherAlias")
)，因此对于表单下标也应该为逗号分隔的两个值("0" "1")


english help
====================

-h | --help: get help document


install
=============
pip install excel2json


windows example (例子)
======================

>excel2json -s "D:\exceltojson\data\test_exc el_process.xlsx" -o "D:\output"
>dir D:\output
::

    d:\out 的目录
    2016/06/27  16:52    <DIR>          .
    2016/06/27  16:52    <DIR>          ..
    2016/06/27  16:52                96 sheet-0.json
    2016/06/27  16:52                91 sheet-1.json
    2016/06/27  16:52               638 sheet-2.json
                   3 个文件            825 字节
                   2 个目录 370,679,599,104 可用字节
                   
   
sheet-0.json:
::

    {"2": {"\u5934\u90e8": "\u5185\u5bb92", "header1": "\u5185\u5bb91", "header2": "\u5185\u5bb93"}}
   

>excel2json -s "D:\exceltojson\data\test_excel_process.xlsx" -o "D:\out" -i 0 -a 头部:header4

sheet-0.json:
::

    {"2": {"header1": "\u5185\u5bb91", "header4": "\u5185\u5bb92", "header2": "\u5185\u5bb93"}}