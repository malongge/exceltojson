# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json

from functools import partial

import pytest

from exceltojson.excel2json import (_RowProcess, _ColProcess, _SheetProcess, ProcessExcel)
from exceltojson.utils import (get_sheets, get_data_path, clear_json_files)
from exceltojson.excel2json import open


def test_row_process():
    col_headers = ['col1', 'col2', 'col3']
    start_col = 1
    sheet = get_sheets(get_data_path('test_row_process.xlsx'))[0]
    row_process = _RowProcess(sheet, col_headers, start_col)

    assert row_process(1) == {'col1': u"内容1", "col2": u"内容2", "col3": u"内容3"}
    assert row_process(2) is None
    assert row_process(3) == {'col1': "content1", "col2": "content2", "col3": "content3"}


def test_col_process():

    sheet = get_sheets(get_data_path('test_col_process.xlsx'))[0]
    alias = {u'头部': 'header3'}
    col_process = _ColProcess(sheet, alias, 15)
    ret = col_process()
    assert ret[0] == 3
    assert ret[1] == ['header1', 'header3', 'header2']

    # alias set invalid
    alias = {u'头': 'header3'}
    col_process = _ColProcess(sheet, alias, 15)
    with pytest.raises(ValueError):
        col_process()

    # header index not invalid
    with pytest.raises(ValueError):
        _ColProcess(sheet, alias, 16)()

    # header duplicate
    alias = {u'头部': 'header2'}
    with pytest.raises(ValueError):
        _ColProcess(sheet, alias, 15)()


def test_col_process_header_invalid():
    sheet = get_sheets(get_data_path('test_col_process_invalid_header.xlsx'))[0]
    with pytest.raises(ValueError):
        _ColProcess(sheet, {'头部': 'header3'}, 15)()


def test_sheet_process():
    sheet = get_sheets(get_data_path('test_sheet_process.xlsx'))[0]
    alias = {'头部': 'header3'}
    sheet_process = _SheetProcess(sheet, alias, merge_cell=True)

    data = [value for value in sheet_process()]

    assert data[0][0] == 10
    assert data[0][1] == {'header1': '内容1', 'header3': '内容2', 'header2': '内容3'}
    assert data[2][0] == 13
    assert data[2][1] == {'header1': 'test1', 'header3': 'conten2', 'header2': 'test3'}

def test_time_cell_process():
    sheet = get_sheets(get_data_path('test_time_cell_process.xlsx'))[0]
    sheet_process = _SheetProcess(sheet, merge_cell=True)

    data = [value for value in sheet_process()]

    assert data[0][0] == 10
    assert data[0][1] == {'time': '2016/11/16', 'header3': '内容2', 'header2': '内容3'}



class TestProcessExcel:

    @classmethod
    def setup_class(cls):
        """simple ProcessExcel instance
        :return:
        """
        cls.process_excel = partial(ProcessExcel, get_data_path('test_excel_process.xlsx'), get_data_path('.'))

    def setup_method(self, method):
        """
        every test should clear the json files
        """
        clear_json_files()

    @classmethod
    def teardown_class(cls):
        """
        after test clear the temporary test files
        """
        clear_json_files()

    def test_excel_process_with_show_row(self):
        excel = self.process_excel()
        # sheet small should not split
        excel(100)
        assert os.path.exists(get_data_path('sheet-20.json')) is False

        excel(max_row=5)
        # big excel file should be split
        assert os.path.exists(get_data_path('sheet-20.json'))
        assert os.path.exists(get_data_path('sheet-2.json'))
        # split file should be right json
        with open(get_data_path('sheet-20.json'), encoding='utf-8') as f:
            assert json.load(f) == {
                '9': {
                    'header1': u'内容6',
                    'header3': u'内容7',
                    'header2': u'内容8'
                },

                '10': {
                  'header1': u'内容7',
                  'header3': u'内容8',
                  'header2': u'内容9'
                }
            }
        # other sheet should be convert to json file
        assert os.path.exists(get_data_path('sheet-0.json'))
        assert os.path.exists(get_data_path('sheet-1.json'))
        with open(get_data_path('sheet-0.json'), encoding='utf-8') as f:
            assert json.load(f) == {
                '2': {
                    'header1': u'内容1',
                    u'头部': u'内容2',
                    'header2': u'内容3'
                }
            }

    def test_excel_process_with_no_show_row(self):
        excel = self.process_excel(show_row=False)
        excel(10)
        with open(get_data_path('sheet-0.json'), encoding='utf-8') as f:
            assert json.load(f) == [
                {
                    'header1': u'内容1',
                    u'头部': u'内容2',
                    'header2': u'内容3'
                }
            ]

    def test_excel_process_with_alias(self):
        excel = self.process_excel(show_row=False, index_sheets={'0': {
                u'头部': 'header3'
            }, 1: None}, patch_sheet_alias=False)
        excel(10)
        with open(get_data_path('sheet-0.json'), encoding='utf-8') as f:
            assert json.load(f) == [
                {
                    'header1': u'内容1',
                    'header3': u'内容2',
                    'header2': u'内容3'
                }
            ]
        # now sheet index 2 not exist
        assert os.path.exists(get_data_path('sheet-2.json')) is False

    def test_excel_process_patch_alias(self):
        excel = self.process_excel(show_row=False, index_sheets={0: {
                u'头部': 'header3'
            }}, patch_sheet_alias=True)
        excel(10)

        # now sheet index 2 should exist
        assert os.path.exists(get_data_path('sheet-2.json'))

    def test_excel_process_with_sheet_names(self):
        excel = self.process_excel(show_row=False, name_sheets={u'名字': {
                u'头部': 'header3'
            }}, patch_sheet_alias=True)
        excel(10)
        # json file name should be sheet name
        assert os.path.exists(get_data_path(u'名字.json'))
        assert os.path.exists(get_data_path('Sheet2.json'))
        assert os.path.exists(get_data_path('Sheet3.json'))

    def test_excel_process_not_patch_sheet_names(self):
        excel = self.process_excel(show_row=False, name_sheets={u'名字': {
                u'头部': 'header3'
            }}, patch_sheet_alias=False)
        excel(10)
        assert os.path.exists(get_data_path(u'名字.json'))
        assert os.path.exists(get_data_path('Sheet2.json')) is False

    def test_excel_process_sheet_index_not_invalid(self):
        # sheet index large not invalid
        with pytest.raises(ValueError):
            self.process_excel(show_row=False, index_sheets={5: {
                u'头部': 'header3'
            }}, patch_sheet_alias=True)

        # sheet index not int value or int str
        with pytest.raises(ValueError):
            self.process_excel(show_row=False, index_sheets={'a': {
                u'头部': 'header3'
            }}, patch_sheet_alias=True)

    def test_excel_process_sheet_name_not_invalid(self):
        # sheet index large not invalid
        with pytest.raises(ValueError):
            self.process_excel(show_row=False, name_sheets={'a': {
                u'头部': 'header3'
            }}, patch_sheet_alias=True)
