# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
from pathlib import Path
import pytest
from exceltojson import excel_to_json, ExcelConfig

def get_data_path(filename):
    """获取测试数据文件路径"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)

@pytest.fixture
def output_dir():
    """创建临时输出目录"""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    return temp_dir

def test_basic_conversion(output_dir):
    """测试基本的Excel到JSON转换"""
    excel_path = get_data_path('test_row_process.xlsx')
    config = ExcelConfig(merge_cell=False, show_row=True)
    excel_to_json(excel_path, output_dir, config)
    
    # 检查输出文件是否存在
    output_file = Path(output_dir) / 'sheet-0.json'
    assert output_file.exists()
    
    # 验证JSON内容
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 验证数据结构
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # 验证具体数据
    assert data['1']['col1'] == '内容1'
    assert data['1']['col2'] == '内容2'
    assert data['1']['col3'] == '内容3'

def test_merge_cells(output_dir):
    """测试合并单元格功能"""
    excel_path = get_data_path('test_sheet_process.xlsx')
    config = ExcelConfig(merge_cell=True, show_row=True)
    excel_to_json(excel_path, output_dir, config)
    
    output_file = Path(output_dir) / 'sheet-0.json'
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 验证空单元格是否被合并
    assert data['13']['header1'] == 'test1'
    assert data['13']['header3'] == 'conten2'
    assert data['13']['header2'] == 'test3'

def test_list_output(output_dir):
    """测试列表输出模式"""
    excel_path = get_data_path('test_row_process.xlsx')
    config = ExcelConfig(merge_cell=False, show_row=False)
    excel_to_json(excel_path, output_dir, config)
    
    output_file = Path(output_dir) / 'sheet-0.json'
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 验证输出是列表
    assert isinstance(data, list)
    assert len(data) > 0
    
    # 验证数据
    assert data[0]['col1'] == '内容1'
    assert data[0]['col2'] == '内容2'

def test_date_format(output_dir):
    """测试日期格式转换"""
    excel_path = get_data_path('test_time_cell_process.xlsx')
    config = ExcelConfig(merge_cell=True, show_row=True)
    excel_to_json(excel_path, output_dir, config)
    
    output_file = Path(output_dir) / 'sheet-0.json'
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 验证日期格式
    assert data['10']['time'] == '2016/11/16'

def test_multiple_sheets(output_dir):
    """测试多表格处理"""
    excel_path = get_data_path('test_excel_process.xlsx')
    config = ExcelConfig(merge_cell=False, show_row=True)
    excel_to_json(excel_path, output_dir, config)
    
    # 验证多个表格文件是否生成
    assert (Path(output_dir) / 'sheet-0.json').exists()
    assert (Path(output_dir) / 'sheet-1.json').exists()
    assert (Path(output_dir) / 'sheet-2.json').exists()

def test_header_validation(output_dir):
    """测试表头验证"""
    excel_path = get_data_path('test_col_process_invalid_header.xlsx')
    config = ExcelConfig(merge_cell=False, show_row=True)
    
    # 验证无效表头处理
    with pytest.raises(ValueError):
        excel_to_json(excel_path, output_dir, config)

def test_invalid_paths():
    """测试无效路径处理"""
    with pytest.raises(FileNotFoundError):
        excel_to_json('nonexistent.xlsx', 'output')
    
    with pytest.raises(FileNotFoundError):
        excel_to_json(get_data_path('test_row_process.xlsx'), 'nonexistent_dir')
