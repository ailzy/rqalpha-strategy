from rqalpha.api import *
from rqalpha import run_func


import numpy as np
import pandas as pd



"""
双均线策略：

ETF基金： 华夏上证50ETF，代码：510050.XSHG

短期均线： window_short = 20，相当于月均线
长期均线： window_long = 120，相当于半年线
偏离度阈值： SD = 5%，区间宽度，这个会在后面有详细解释

借助了numpy的内置移动平均函数：rolling_mean

参考： https://uqer.io/v3/community/share/554051bbf9f06c1c3d687fac

"""

def init(context):
    #context.s1 = '510050.XSHG'
    # context.s1 = '顺鑫农业'
    context.s1 = '510050.XSHG'
    context.window_short = 20
    context.window_long = 120
    context.SD = 0.05
    context.longest_history = context.window_long

def before_trading(context):
    pass

def handle_bar(context, bar_dict):
    price_history = history_bars(context.s1, context.longest_history, '1d', 'close')

    # 计算短均线
    short_mean = np.mean(price_history[-context.window_short:])

    long_mean = np.mean(price_history[-context.window_long:])

    plot("short_mean", short_mean)
    plot("long_mean", long_mean)

    # 计算买入卖出信号
    flag = True if (short_mean - long_mean) > context.SD * long_mean else False
    if flag:
        # 满仓入股
        order_target_percent(context.s1, 1)
    else:
        # 计算现在portfolio中股票的仓位
        curPosition = context.portfolio.positions[context.s1].quantity
        # 进行清仓
        if curPosition > 0:
            order_target_value(context.s1, 0)


config = {
  "base": {
    "start_date": "2018-01-01",
    "end_date": "2018-09-23",
    "benchmark": "000300.XSHG",
    "accounts": {
        "stock": 100000
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
run_func(init=init, before_trading=before_trading, handle_bar=handle_bar, config=config)
