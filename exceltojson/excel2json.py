#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Created by malongge on 2016/6/20
#

"""Excel file to JSON file converter with modern Python features
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Iterator, Tuple

import xlrd
from xlrd.xldate import xldate_as_datetime
from xlrd import XL_CELL_DATE
from six import itervalues
from six.moves import range as _range
from six import PY2
from exceltojson.utils import get_sheets, get_sheet_names

import sys

if PY2:
    str = unicode
else:
    str = str

# for compatible python2 and python3 open function, then use open function like py3 style
if sys.version_info[0] > 2:
    #py3
    open = open
else:
    # py2
    import codecs
    import warnings

    def open(file, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None, closefd=True, opener=None):
        if newline is not None:
            warnings.warn('newline is not supported in py2')
        if not closefd:
            warnings.warn('closefd is not supported in py2')
        if opener is not None:
            warnings.warn('opener is not supported in py2')
        return codecs.open(filename=file, mode=mode, encoding=encoding, errors=errors, buffering=buffering)


@dataclass
class ExcelConfig:
    """Configuration for Excel processing"""
    merge_cell: bool = True
    show_row: bool = True
    max_row: int = 1000
    date_mode: int = 0


class ExcelProcessor:
    """Modern Excel to JSON converter"""
    
    MAX_SCAN_ROWS = 500
    MAX_SCAN_COLS = 1000

    def __init__(
        self,
        excel_path: Union[str, Path],
        save_path: Union[str, Path],
        config: Optional[ExcelConfig] = None
    ):
        self.excel_path = Path(excel_path)
        self.save_path = Path(save_path)
        self.config = config or ExcelConfig()
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f'Excel file not found: {excel_path}')
        if not self.save_path.exists():
            raise FileNotFoundError(f'Save directory not found: {save_path}')

    def process_cell(self, cell: Any) -> str:
        """Process a single cell value"""
        if cell.ctype is XL_CELL_DATE:
            return xldate_as_datetime(
                cell.value, 
                self.config.date_mode
            ).strftime('%Y/%m/%d')
        return str(cell.value).strip()

    def find_header_row(self, sheet: xlrd.sheet.Sheet) -> int:
        """Find the first non-empty row that can be used as header"""
        for row_idx in range(self.MAX_SCAN_ROWS):
            if any(cell.value.strip() for cell in sheet.row(row_idx)):
                return row_idx
        raise ValueError(f'No header found in first {self.MAX_SCAN_ROWS} rows')

    def get_headers(self, sheet: xlrd.sheet.Sheet, header_row: int) -> Tuple[int, List[str]]:
        """Get column headers and starting column index"""
        start_col = -1
        headers = []
        
        # 首先找到第一个非空列
        for col_idx in range(sheet.ncols):
            value = str(sheet.cell(header_row, col_idx).value).strip()
            if value and start_col == -1:
                start_col = col_idx
            if value:
                headers.append(value)
                
        if start_col == -1:
            raise ValueError('No headers found')
        if len(set(headers)) != len(headers):
            raise ValueError('Duplicate headers found')
            
        return start_col, headers

    def process_row(
        self, 
        sheet: xlrd.sheet.Sheet, 
        row_idx: int, 
        headers: List[str], 
        start_col: int,
        previous_row: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, str]]:
        """Process a single row of data"""
        row_data = {}
        
        for col_idx, header in enumerate(headers):
            cell = sheet.cell(row_idx, start_col + col_idx)
            value = self.process_cell(cell)
            
            if not value and self.config.merge_cell and previous_row:
                value = previous_row.get(header, '')
            row_data[header] = value
            
        return row_data if any(row_data.values()) else None

    def process_sheet(self, sheet: xlrd.sheet.Sheet) -> Iterator[Tuple[int, Dict[str, str]]]:
        """Process a single sheet"""
        header_row = self.find_header_row(sheet)
        start_col, headers = self.get_headers(sheet, header_row)
        
        previous_row = None
        for row_idx in range(header_row + 1, sheet.nrows):
            row_data = self.process_row(
                sheet, row_idx, headers, start_col, previous_row
            )
            if row_data:
                previous_row = row_data.copy()
                # 行号从1开始，header_row是0，所以实际行号是 row_idx - header_row
                yield row_idx - header_row, row_data

    def save_json(self, data: Union[Dict, List], filepath: Path) -> None:
        """Save data to JSON file"""
        with filepath.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def process_workbook(self) -> None:
        """Process the entire workbook"""
        workbook = xlrd.open_workbook(str(self.excel_path))
        
        for sheet_idx in range(workbook.nsheets):
            sheet = workbook.sheet_by_index(sheet_idx)
            output_path = self.save_path / f'sheet-{sheet_idx}.json'
            
            container = [] if not self.config.show_row else {}
            current_size = 0
            
            for row_num, row_data in self.process_sheet(sheet):
                if self.config.show_row:
                    container[row_num] = row_data
                else:
                    container.append(row_data)
                    
                current_size += 1
                if current_size >= self.config.max_row:
                    self.save_json(container, output_path)
                    output_path = output_path.with_name(
                        f'{output_path.stem}0{output_path.suffix}'
                    )
                    container = [] if not self.config.show_row else {}
                    current_size = 0
                    
            if container:
                self.save_json(container, output_path)


def excel_to_json(
    excel_path: Union[str, Path],
    save_path: Union[str, Path],
    config: Optional[ExcelConfig] = None
) -> None:
    """
    Convert Excel file to JSON file(s).
    
    Args:
        excel_path: Path to the Excel file
        save_path: Directory to save JSON files
        config: Optional configuration settings
    """
    processor = ExcelProcessor(excel_path, save_path, config)
    processor.process_workbook()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert Excel files to JSON')
    parser.add_argument('excel_path', help='Path to Excel file')
    parser.add_argument('save_path', help='Directory to save JSON files')
    parser.add_argument('--merge-cell', action='store_true', help='Merge empty cells with previous values')
    parser.add_argument('--show-row', action='store_true', help='Include row numbers in output')
    parser.add_argument('--max-row', type=int, default=1000, help='Maximum rows per JSON file')
    
    args = parser.parse_args()
    
    config = ExcelConfig(
        merge_cell=args.merge_cell,
        show_row=args.show_row,
        max_row=args.max_row
    )
    
    excel_to_json(args.excel_path, args.save_path, config)


class _RowProcess(object):
    """a row treat like an object, and empty row will
    """

    def __init__(self, sheet, keys, col_index):
        self.sheet = sheet

        # Each column corresponds to the key, it should be a list type
        self.keys = keys

        # The start column to use
        self.col = col_index

        self.date_mode = int(os.environ['date_mode']) or 0

    def __call__(self, row):
        """ give a row index return a dict value
        :param row: row index tell which row now process
        :return: dict value
        """

        row_dict = {}
        for index, key in enumerate(self.keys):
            cell = self.sheet.row(row)[self.col+index]
            if cell.ctype is XL_CELL_DATE:
                row_dict[key] = xldate_as_datetime(cell.value, self.date_mode).strftime('%Y/%m/%d')
            else:
                row_dict[key] = str(cell.value).strip()
        if self._check_state(row_dict):
            return
        return row_dict

    def _check_state(self, row_dict):
        """ check whether the row is empty
        :param row_dict:
        :return: empty row return true
        """
        for val in itervalues(row_dict):
            if val:
                return
        return True


class _ColProcess(object):
    """a col treat like an object, col should have a header
    """

    # scan to max column to find header
    MAX = 1000

    def __init__(self, sheet, alias, header_index):
        self.sheet = sheet
        # change the header if don't want header to be a json key
        self.alias = alias
        # row index which should be the header row
        self.header_index = header_index
        # find header column index
        self._header_start_col()

    def _header_start_col(self):
        """find the header row corresponding column index
        """
        self.start_col = self.MAX+1
        try:
            for i in _range(self.MAX):
                if self.sheet.row(self.header_index)[i].value.strip():
                    self.start_col = i
                    break
        except IndexError:
            raise ValueError('header_index: {} row is an empty row'.format(self.header_index))
        if self.start_col >= self.MAX + 1:
            raise ValueError('scan {} columns with row {}, but not found header'.format(self.MAX),
                             self.header_index)

    def __call__(self):
        """ get json keys
        :return: header start column, json keys
        """
        col_list = []
        row = self.sheet.row(self.header_index)
        row_length = len(row)
        for i in _range(self.start_col, row_length):
            key = row[i].value.strip()
            if key:
                alias_key = self.alias.pop(key, None) or key
                col_list.append(alias_key)
            else:
                raise ValueError('header should not have empty cell')
        if self.alias:
            raise ValueError('header alias {} not invalid'.format(self.alias))

        if len(set(col_list)) != row_length - self.start_col:
            raise ValueError('header duplicate')
        return self.start_col, col_list


class _SheetProcess(object):
    """all sheet rows should be transform to a dict value
    """

    # max scan rows to find the content header
    MAX = 500

    def __init__(self, sheet, alias=None, merge_cell=True):
        self.alias = alias or {}
        self.sheet = sheet
        self._fetch_start_row()
        # is a header list
        self.headers = self._fetch_header_and_start_col()
        self.merge_cell = merge_cell

    def _fetch_start_row(self):
        """find start row which should be a table header
        :return:
        """
        self.start_row = self.MAX+1
        try:
            for i in _range(self.MAX):
                row = self.sheet.row(i)
                for j in _range(len(row)):
                    if row[j].value.strip():
                        self.start_row = i
                        return
        except IndexError:
            raise ValueError('exist empty sheet, please check')
        if self.start_row >= self.MAX+1:
            raise ValueError('scan {} rows but not find the content header'.format(self.MAX))

    def _fetch_header_and_start_col(self):
        """
        :return: get header list to become a json keys
        """
        self.start_col, headers = _ColProcess(self.sheet, self.alias, self.start_row)()
        return headers

    def __call__(self):
        """ generator, each one should be a row index number and corresponding dict content, the dict keys
        which may be table headers or alias you give.
        """
        keys = self.headers
        sheet = self.sheet
        start_col = self.start_col
        content_bak = {}
        if self.merge_cell:
            for row_index in _range(self.start_row+1, sheet.nrows):
                content = _RowProcess(sheet, keys, start_col)(row_index)
                if not content:
                    continue

                # merge cell use the first cell value
                for key in keys:
                    if content[key]:
                        pass
                    else:
                        content[key] = content_bak.get(key, '')

                content_bak = content.copy()
                yield row_index+1, content
        else:
            for row_index in _range(self.start_row+1, sheet.nrows):
                content = _RowProcess(sheet, keys, start_col)(row_index)
                yield row_index+1, content


class ProcessExcel(object):
    """transform a excel file to a list json files
    """

    def __init__(self,
                 excel_path,
                 save_path,
                 index_sheets=None,
                 name_sheets=None,
                 merge_cell=True,
                 show_row=True,
                 patch_sheet_alias=True):
        """
        :param excel_path: excel source path
        :param save_path: save json file directory
        :param index_sheets: is a dict value, key is sheet index, value is header alias
               { 0: {'头部': 'header'}}
        :param name_sheets:  is a dict value, key is sheet name, value is header alias
               { 'sheet_name': {'头部': 'header'}}
        :param merge_cell: treat sheet white cell as a merge cell, use above cell value
        :param show_row: if it is true json file will use this as the key of each sheet row dict value
        :return:
        """

        merge_cell = True if merge_cell else False
        self.show_row = show_row
        self.patch_sheet = patch_sheet_alias
        self.sheets = []

        if not os.path.exists(save_path):
            raise ValueError('save path: {} not exist'.format(save_path))

        if not os.path.exists(excel_path):
            raise ValueError('Excel file: {} not found'.format(excel_path))

        self.save_path = save_path

        if index_sheets:
            self._get_sheets_by_index(excel_path, index_sheets, merge_cell)
        elif name_sheets:
            self._get_sheets_by_name(merge_cell, name_sheets, excel_path)
        else:
            self._get_all_sheets_with_no_alias(merge_cell, excel_path)

    def _get_all_sheets_with_no_alias(self, merge_cell, path):
        self.sheets = {index: _SheetProcess(sheet, merge_cell=merge_cell) for
                       index, sheet in enumerate(get_sheets(path))}

    def _get_sheets_by_name(self, merge_cell, name_sheets, path):
        sheets = get_sheet_names(path)
        name_set = set(sheets.keys())-set(name_sheets.keys())
        if set(name_sheets.keys()) <= set(sheets.keys()):
            pass
        else:
            raise ValueError('sheet names: {} not correct'.format(name_set))
        self.sheets = {name: _SheetProcess(sheets[name],
                                           name_sheets[name], merge_cell=merge_cell) for name in name_sheets}
        if self.patch_sheet:
            if name_set:
                self.sheets.update({name: _SheetProcess(sheets[name], merge_cell=merge_cell) for name in name_set})

    def _get_sheets_by_index(self, path, index_sheets, merge_cell):
        """ index sheets means only process index in index_sheets,
        :param path:
        :param index_sheets: it's a dict value, key is the sheet index, value is the header alias
        :param merge_cell:
        :return:
        """
        all_sheets = get_sheets(path)
        sheets = {}
        try:
            for index in index_sheets:
                sheets[int(index)] = index_sheets[index]
        except ValueError:
            raise ValueError('sheet index should be a int value')
        all_index_set = set([i for i in _range(0, len(all_sheets))])
        index_set = all_index_set - set(sheets.keys())
        if set(sheets.keys()) <= all_index_set:
            pass
        else:
            raise ValueError('sheet index: {} not exist'.format(index_set))
        self.sheets = {i: _SheetProcess(all_sheets[i], alias=sheets[i], merge_cell=merge_cell) for i in sheets}

        if self.patch_sheet:
            if index_set:
                self.sheets.update({i: _SheetProcess(all_sheets[i], merge_cell=merge_cell) for i in index_set})

    def __call__(self, max_row=1000):
        """ write excel data to json file
        :param max_row: sheet over max_row should split to another json file
        :return:
        """
        if int(max_row) > 1000000:
            raise ValueError('max row value should not large than 1000000 but you give {}'.format(max_row))
        for name in self.sheets:
            file_name = self._get_base_name(name)
            if self.show_row:
                self._write_json(max_row, name, file_name, _type=dict)
            else:
                self._write_json(max_row, name, file_name, _type=list)

    def _get_base_name(self, name):
        name_format = 'sheet-{}.json' if isinstance(name, int) else '{}.json'
        return os.path.join(self.save_path, name_format.format(name))

    def _write_json(self, max_row, name, file_name, _type=None):
        """
        :param max_row: large than this value will generate a new json file
                        this value only to limit the json file is to large
        :param name: is the sheet_name to get sheet object, also can be a index value
        :param file_name: save json file will use this as base file name, if a sheet
               more than max_row, the file_name will add a '0' between file name and
               file suffix.
        :param _type: dict or list
        :return:
        """
        container = _Container(_type)
        size = 0
        for row, data in self.sheets[name]():
            container.add_data(row, data)
            size += 1
            if size >= max_row:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(container.data, indent=2))
                header, sep, suffix = file_name.rpartition('.')
                file_name = ''.join([header+'0', sep, suffix])
                size = 0
                container.clear()
        if container.data:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(json.dumps(container.data))


class _Container(object):
    """solve the dict and list save data different
    """
    def __init__(self, _type):
        self.data = _type()
        self._type = _type
        if _type is dict:
            self.add_data = self.dict_add
        else:
            self.add_data = self.list_add

    def clear(self):
        self.data = self._type()

    def dict_add(self, *args):
        self.data[args[0]] = args[1]

    def list_add(self, *args):
        self.data.append(args[1])

