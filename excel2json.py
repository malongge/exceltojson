#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Excel to JSON converter command line tool
"""

from exceltojson import excel_to_json, ExcelConfig

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='将Excel文件转换为JSON格式')
    parser.add_argument('excel_path', help='Excel文件路径')
    parser.add_argument('save_path', help='JSON文件保存目录')
    parser.add_argument('--merge-cell', action='store_true', help='合并空单元格（使用上一行的值）')
    parser.add_argument('--show-row', action='store_true', help='在输出中包含行号')
    parser.add_argument('--max-row', type=int, default=1000, help='每个JSON文件的最大行数')
    parser.add_argument('--date-mode', type=int, default=0, help='日期格式模式')
    
    args = parser.parse_args()
    
    config = ExcelConfig(
        merge_cell=args.merge_cell,
        show_row=args.show_row,
        max_row=args.max_row,
        date_mode=args.date_mode
    )
    
    try:
        excel_to_json(args.excel_path, args.save_path, config)
        print(f'转换完成！输出目录: {args.save_path}')
    except Exception as e:
        print(f'错误: {str(e)}')
        exit(1)

if __name__ == '__main__':
    main() 