from rqalpha.api import *
from rqalpha import  run_func
import numpy as np
import pandas as pd

"""
多头趋势回踩策略

交易策略
仅仅运用多头趋势回撤的思路，我们构建策略如下：

一、选定一股票池，并且选定一系列系数：
二、一组均线天数 [N1,N2,N3,…,Nk][N1,N2,N3,…,Nk]：总数量 kk 限制，按照从小到大 N1≤N2≤⋯≤NkN1≤N2≤⋯≤Nk 排列。当相应天数的移动均线是从大到小排列时，是多头排列的格局；
三、趋势天数 TT： 当上面指定的移动均线在 TT 天内都处于多头排列时，我们才判断价格处于多头趋势；
四、回撤均线 MM：当前一天的最收盘价低于 MM 日均线时时判断为回撤；
五、持有股票上限 num_stocks：同时最多持仓 num_stocks 支股票。
六、止损比例 dd 和止盈比例 uu：当股票价格搞出买入价的 uu 倍，或低于买入价的 dd 倍时，卖出股票。

每日执行以下操作
产生信号：
一、选出股票池中所有在过去的 TT 个交易日内，[N1,N2,N3,…,Nk][N1,N2,N3,…,Nk] 日均线组按照多头排列的股票，判定为多头趋势；
二、在处于多头趋势的股票中选出前一日收盘价低于 MM 日均线的股票，判定为发生回撤点；
三、在所有出现多头趋势回撤点的股票中，去掉已持仓的股票，其余的发出买入信号。
调换仓位：
一、全仓卖出所有达到止盈或止损线的股票；
二、在有现金的情况下，买入所有发出信号的股票，每支股票的买入总值为总资产净值除以 num_stocks。

"""

import talib


def init(context):
    # context.components = index_components('000300.XSHG')

    context.components = ['300133.XSHE', '601098.XSHG', '600332.XSHG', '000623.XSHE', '600027.XSHG', '601179.XSHG', '600795.XSHG', '002399.XSHE', '300146.XSHE', '601009.XSHG', '601288.XSHG', '601800.XSHG', '600637.XSHG', '000983.XSHE', '600031.XSHG', '002236.XSHE', '603993.XSHG', '600739.XSHG', '600406.XSHG', '600256.XSHG', '600875.XSHG', '300027.XSHE', '000413.XSHE', '002739.XSHE', '600111.XSHG', '600015.XSHG', '600048.XSHG', '601933.XSHG', '002470.XSHE', '601628.XSHG', '600115.XSHG', '002153.XSHE', '000800.XSHE', '600649.XSHG', '000415.XSHE', '000009.XSHE', '600373.XSHG', '600999.XSHG', '601857.XSHG', '600837.XSHG', '601989.XSHG', '600570.XSHG', '600157.XSHG', '000917.XSHE', '600066.XSHG', '300003.XSHE', '601991.XSHG', '600863.XSHG', '002465.XSHE', '601021.XSHG', '600104.XSHG', '600109.XSHG', '000559.XSHE', '600271.XSHG', '601808.XSHG', '000333.XSHE', '601169.XSHG', '000629.XSHE', '600959.XSHG', '000060.XSHE', '601888.XSHG', '600177.XSHG', '000999.XSHE', '002353.XSHE', '601390.XSHG', '000423.XSHE', '600153.XSHG', '600016.XSHG', '600315.XSHG', '300017.XSHE', '600887.XSHG', '601333.XSHG', '600028.XSHG', '600867.XSHG', '601939.XSHG', '601238.XSHG', '600188.XSHG', '601318.XSHG', '600583.XSHG', '000156.XSHE', '600549.XSHG', '600535.XSHG', '600519.XSHG', '000858.XSHE', '002038.XSHE', '000503.XSHE', '000883.XSHE', '601872.XSHG', '600383.XSHG', '600196.XSHG', '002410.XSHE', '600873.XSHG', '600029.XSHG', '600021.XSHG', '000725.XSHE', '600023.XSHG', '601727.XSHG', '000750.XSHE', '600578.XSHG', '000625.XSHE', '002007.XSHE', '002294.XSHE', '000712.XSHE', '000069.XSHE', '600642.XSHG', '601898.XSHG', '002008.XSHE', '002241.XSHE', '000400.XSHE', '001979.XSHE', '600489.XSHG', '600415.XSHG', '601718.XSHG', '002456.XSHE', '300002.XSHE', '002450.XSHE', '600998.XSHG', '600350.XSHG', '601766.XSHG', '600010.XSHG', '601618.XSHG', '600089.XSHG', '600900.XSHG', '600895.XSHG', '600352.XSHG', '600005.XSHG', '601969.XSHG', '300070.XSHE', '600690.XSHG', '002594.XSHE', '000061.XSHE', '601336.XSHG', '600068.XSHG', '601018.XSHG', '601016.XSHG', '002081.XSHE', '601668.XSHG', '601788.XSHG', '000738.XSHE', '600221.XSHG', '002500.XSHE', '000778.XSHE', '601600.XSHG', '603000.XSHG', '600170.XSHG', '601118.XSHG', '601186.XSHG', '002252.XSHE', '600804.XSHG', '601928.XSHG', '600674.XSHG', '600118.XSHG', '600633.XSHG', '000425.XSHE', '601225.XSHG', '002292.XSHE', '600827.XSHG', '300015.XSHE', '601998.XSHG', '000100.XSHE', '600660.XSHG', '002304.XSHE', '601988.XSHG', '600030.XSHG', '601699.XSHG', '000402.XSHE', '600741.XSHG', '000630.XSHE', '600036.XSHG', '601818.XSHG', '600362.XSHG', '000793.XSHE', '002142.XSHE', '600008.XSHG', '600585.XSHG', '600688.XSHG', '000895.XSHE', '600893.XSHG', '600252.XSHG', '300024.XSHE', '000826.XSHE', '601633.XSHG', '600369.XSHG', '002422.XSHE', '601899.XSHG', '600060.XSHG', '300104.XSHE', '000876.XSHE', '601158.XSHG', '000776.XSHE', '600783.XSHG', '000686.XSHE', '601866.XSHG', '601117.XSHG', '600166.XSHG', '601211.XSHG', '600317.XSHG', '002202.XSHE', '600038.XSHG', '601006.XSHG', '600718.XSHG', '300315.XSHE', '600011.XSHG', '300124.XSHE', '002736.XSHE', '601398.XSHG', '601166.XSHG', '000166.XSHE', '600663.XSHG', '600019.XSHG', '000937.XSHE', '002129.XSHE', '601258.XSHG', '000063.XSHE', '600000.XSHG', '600372.XSHG', '000539.XSHE', '002024.XSHE', '002375.XSHE', '601377.XSHG', '601555.XSHG', '600886.XSHG', '600820.XSHG', '000039.XSHE', '300058.XSHE', '000792.XSHE', '000568.XSHE', '601198.XSHG', '600050.XSHG', '600208.XSHG', '600485.XSHG', '600009.XSHG', '601901.XSHG', '300251.XSHE', '000709.XSHE', '600705.XSHG', '000581.XSHE', '601607.XSHG', '600839.XSHG', '600703.XSHG', '000898.XSHE', '002146.XSHE', '002475.XSHE', '000046.XSHE', '300059.XSHE', '601106.XSHG', '601992.XSHG', '600340.XSHG', '600547.XSHG', '002230.XSHE', '002415.XSHE', '000001.XSHE', '600600.XSHG', '000825.XSHE', '600150.XSHG', '000338.XSHE', '600588.XSHG', '000728.XSHE', '000783.XSHE', '002673.XSHE', '601985.XSHG', '000027.XSHE', '601231.XSHG', '601919.XSHG', '601088.XSHG', '300144.XSHE', '000540.XSHE', '600648.XSHG', '600958.XSHG', '600309.XSHG', '601601.XSHG', '002385.XSHE', '601669.XSHG', '601958.XSHG', '600085.XSHG', '600018.XSHG', '600276.XSHG', '603885.XSHG', '002195.XSHE', '000651.XSHE', '601328.XSHG', '002065.XSHE', '000598.XSHE', '601111.XSHG', '600717.XSHG', '000157.XSHE', '603288.XSHG', '600518.XSHG', '600398.XSHG', '000002.XSHE', '600100.XSHG', '601216.XSHG', '601608.XSHG', '000768.XSHE', '601688.XSHG', '000963.XSHE', '601099.XSHG', '000538.XSHE', '000831.XSHE', '000729.XSHE']

    context.avgLen = 40
    context.atrLen = 40

    # 测试多头趋势的均线长度
    context.ma_lengths = [5, 10, 20, 60, 120]

    # 测试买入回踩的均线长度
    context.test_ma_length = 10

    # 买入时回踩但必须站住的均线
    context.stand_ma_length = 10

    context.num_stocks = 15
    context.in_trend_days = 7
    context.cut_gain_percentage = 0.05
    context.cut_loss_percentage = 0.05
    context.available_stocks = []


def before_trading(context):
    context.available_stocks = get_available_stocks(context)

def handle_bar(context, bar_dict):
    # in_trend_stocks = get_in_trends(context.available_stocks, context)
    # logger.info(context.now.isoformat(' ') + "多头排列:"  + str(in_trend_stocks))


    to_sell = sell_signal(context)
    sell_stocks(to_sell)

    to_buy = buy_signal(context.available_stocks, context)
    buy_stocks(to_buy, context)


def get_available_stocks(context):
    longest_ma = max(context.ma_lengths)
    available_stocks = []
    components = context.components
    for stock in components:  # 去除停牌、ST股
        if not is_suspended(stock) and (not str(is_suspended(stock)) == 'None') and (not is_st_stock(stock)):
            available_stocks.append(stock)
    return available_stocks



def sell_signal(context):
    to_sell = []
    for security in context.portfolio.positions:
        # 按分钟获取当前价格
        # current_price = history(1, '1m', 'close')[security].iloc[0]

        price = history_bars(security, 1, '1d', 'close')
        current_price = price[-1]

        # 平均建仓成本
        avg_price = context.portfolio.positions[security].avg_price
        high = avg_price * (1 + context.cut_gain_percentage)  # 1+0.05
        low = avg_price * (1 - context.cut_loss_percentage)
        # 全仓卖出所有达到止盈或止损线的股票
        if current_price <= low or current_price >= high:
            to_sell.append(security)

    return to_sell


def sell_stocks(to_sell):
    for security in to_sell:
        order_target_percent(security, 0)


def buy_signal(available_stocks, context):
    # 获取多头排列股票池
    in_trend_stocks = get_in_trends(available_stocks, context)
    signal = []

    for security in in_trend_stocks:
        # 获取10天交易数据
        past_prices = history_bars(security, context.test_ma_length, '1d', 'close')
        # 获取10天交易均价
        test_ma = sum(past_prices) / context.test_ma_length

        #
        past_prices2 = history_bars(security, context.stand_ma_length, '1d', 'close')
        stand_ma = sum(past_prices2) / context.stand_ma_length
        # current_price = history(1, '1d', 'close')[security].iloc[0]
        current_price = history_bars(security, 1, '1d', 'close')

        # previous_low = history(1, '1d', 'low')[security].iloc[0]
        if current_price <= test_ma and security not in context.portfolio.positions:
            signal.append(security)
    # 最多只取15个股票
    return (signal[0: context.num_stocks])


def buy_stocks(signal, context):
    """
    在有现金的情况下，买入所有发出信号的股票，每支股票的买入总值为总资产净值除以 num_stocks。
    """
    cash_per_stock = context.portfolio.portfolio_value / context.num_stocks
    for security in signal:
        order_value(security, cash_per_stock)


# 选择多头排列的股票
def get_in_trends(available_stocks, context):
    """
    选出股票池中所有在过去的 TT 个交易日内，[N1,N2,N3,…,Nk][N1,N2,N3,…,Nk] 日均线组按照多头排列的股票，判定为多头趋势
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

            sorted_mas = sorted(mas)  # 递增排序
            sorted_mas.reverse()  # 反向

            if mas != sorted_mas:
                # 判断是否为多头排列，如果不是，则退出
                # 判断依据是判断 5，10，20，60，120日是否按顺序排列。
                to_remove.append(security)
                break

    for security in to_remove:
        available_stocks.remove(security)

    return available_stocks


config = {
  "base": {
    "start_date": "2018-01-01",
    "end_date": "2018-11-07",
    "benchmark": "000300.XSHG",
    "accounts": {
        "stock": 1000000
    }
  },
  "extra": {
    "log_level": "verbose",
    "locale": "zh_Hans_CN"
  },
  "mod": {
    "sys_analyser": {
      "enabled": True,
      "plot": True
    }
  }
}

# 您可以指定您要传递的参数
#run_func(init=init, before_trading=before_trading, handle_bar=handle_bar, config=config)
run_func(**globals())

