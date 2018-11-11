from rqalpha.api import *
from rqalpha import  run_func
import numpy as np
import pandas as pd



"""
策略多头排列
"""

def get_in_trends(available_stocks, context):
    """
    选出股票池中所有在过去的 TT 个交易日内，[N1,N2,N3,…,Nk][N1,N2,N3,…,Nk] 日均线组按照多头排列的股票，判定为多头趋势；
    :param available_stocks:
    :param context:
    :return:
    """
    to_remove = []
    for security in available_stocks:
        longest_ma = max(context.ma_lengths)
        date = context.now
        # all_past_prices = history(longest_ma + context.in_trend_days, '1d', 'close')[security]
        # 120 + 7
        all_past_prices = history_bars(security, longest_ma + context.in_trend_days, '1d', 'close')

        for day in range(context.in_trend_days):  # 7
            if day == 0:
                past_prices = all_past_prices
            else:
                past_prices = all_past_prices[:-day]

            mas = []

            for length in context.ma_lengths:  # [5, 10, 20, 60, 120]
                ma_data = past_prices[-length:]

                ma = sum(ma_data) / length

                mas.append(ma)

            sorted_mas = sorted(mas)
            sorted_mas.reverse()

            if mas != sorted_mas:
                to_remove.append(security)

                break

    for security in to_remove:
        available_stocks.remove(security)

    return available_stocks



