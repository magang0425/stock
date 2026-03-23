#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


# 持续上涨（MA30向上）
# 均线多头
# 1.30日前的30日均线<20日前的30日均线<10日前的30日均线<当日的30日均线
# 3.(当日的30日均线/30日前的30日均线)>1.2
def check(code_name, data, date=None, threshold=60):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    data.loc[:, 'ma30'] = tl.MA(data['close'].values, timeperiod=30)
    data['ma30'].values[np.isnan(data['ma30'].values)] = 0.0

    ma30_30 = data.iloc[-31]['ma30']
    ma30_20 = data.iloc[-21]['ma30']
    ma30_10 = data.iloc[-11]['ma30']
    ma30_now = data.iloc[-1]['ma30']

    if ma30_30 == 0:
        return False

    if ma30_30 < ma30_20 < ma30_10 < ma30_now and ma30_now > 1.2 * ma30_30:
        return True
    else:
        return False
