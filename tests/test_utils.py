# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from exceltojson.utils import get_sheet_names, get_data_path


def test_get_sheet_names():
    sheet_dict = get_sheet_names(get_data_path('test_get_sheet_names.xlsx'))
    from xlrd import sheet
    assert isinstance(sheet_dict[u'名字'], sheet.Sheet)
    assert set(sheet_dict.keys()) == {u'名字', 'Sheet2', 'Sheet3'}


