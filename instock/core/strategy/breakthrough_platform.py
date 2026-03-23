#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import talib as tl
from instock.core.strategy import enter

__author__ = 'myh '
__date__ = '2023/3/10 '


# 平台突破策略
# 1.60日内某日收盘价>=60日均线>开盘价
# 2.且【1】放量上涨
# 3.且【1】间之前时间，任意一天收盘价与60日均线偏离在-5%~20%之间。
def check(code_name, data, date=None, threshold=60):
    origin_data = data
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    data.loc[:, 'ma60'] = tl.MA(data['close'].values, timeperiod=60)
    data['ma60'].values[np.isnan(data['ma60'].values)] = 0.0

    data = data.tail(n=threshold)

    for _close, _open, _date, _ma60 in zip(data['close'].values, data['open'].values, data['date'].values, data['ma60'].values):
        if _open < _ma60 <= _close:
            if enter.check_volume(code_name, origin_data, date=pd.Timestamp(_date).date(), threshold=threshold):
                data_front = data.loc[(data['date'] < _date) & (data['ma60'] > 0)]
                if data_front.empty:
                    continue

                is_platform = True
                for _front_close, _front_ma60 in zip(data_front['close'].values, data_front['ma60'].values):
                    deviation = (_front_close - _front_ma60) / _front_ma60
                    if not (-0.05 <= deviation <= 0.2):
                        is_platform = False
                        break
                if is_platform:
                    return True

    return False
