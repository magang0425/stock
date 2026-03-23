#!/usr/local/bin/python
# -*- coding: utf-8 -*-


__author__ = 'myh '
__date__ = '2023/3/10 '


# 低ATR成长
# 1.必须至少上市交易250日
# 2.最近10个交易日的最高收盘价必须比最近10个交易日的最低收盘价高1.1倍
def check_low_increase(code_name, data, date=None, ma_long=250, threshold=10):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    if len(data.index) < ma_long:
        return False

    data = data.tail(n=threshold)
    days_count = len(data.index)
    if days_count < threshold:
        return False

    lowest_close = data['close'].values.min()
    highest_close = data['close'].values.max()
    if lowest_close <= 0:
        return False

    ratio = highest_close / lowest_close
    if ratio > 1.1:
        return True

    return False
