#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl


__author__ = 'myh '
__date__ = '2023/3/10 '


# 放量上涨
# 1.当日比前一天上涨小于2%或收盘价小于开盘价
# 2.当日成交额不低于2亿
# 3.当日成交量/5日平均成交量>=2
def check_volume(code_name, data, date=None, threshold=60):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    p_change = data.iloc[-1]['p_change']
    if p_change < 2 or data.iloc[-1]['close'] < data.iloc[-1]['open']:
        return False

    data.loc[:, 'vol_ma5'] = tl.MA(data['volume'].values, timeperiod=5)
    data['vol_ma5'].values[np.isnan(data['vol_ma5'].values)] = 0.0

    data = data.tail(n=threshold + 1)
    if len(data) < threshold + 1:
        return False

    # 优先使用历史数据中的真实成交额，缺失时再退化为价格*成交量。
    last_amount = data.iloc[-1]['amount']
    if np.isnan(last_amount):
        last_amount = data.iloc[-1]['close'] * data.iloc[-1]['volume']
    last_vol = data.iloc[-1]['volume']

    # 成交额不低于2亿
    if last_amount < 200000000:
        return False

    data = data.head(n=threshold)

    mean_vol = data.iloc[-1]['vol_ma5']
    if mean_vol <= 0:
        return False

    vol_ratio = last_vol / mean_vol
    if vol_ratio >= 2:
        return True
    else:
        return False
