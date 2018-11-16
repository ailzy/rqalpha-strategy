from rqalpha.api import *
from rqalpha import run_func

import talib

"""
RSI取值的大小

RSI的变动范围在0—100之间，强弱指标值一般分布在20—80。(如下图所示)
RSI值市场特征投资操作

80—100极强卖出
50—80强买入
20—50弱观望
0—20极弱买入

"""

def init(context):
    context.s1 = "000001.XSHE"
    context.s2 = "601988.XSHG"
    context.s3 = "000068.XSHE"
    context.stocks = [context.s1, context.s2, context.s3]

    context.TIME_PERIOD = 14
    context.HIGH_RSI = 60
    context.LOW_RSI = 30
    context.ORDER_PERCENT = 0.3


def handle_bar(context, bar_dict):

    for stock in context.stocks:
        prices = history_bars(stock, context.TIME_PERIOD+1, "1d", "close")

        # 用 talib 计算rsi值
        rsi_data = talib.RSI(prices, timeperiod=context.TIME_PERIOD)
        # logger.info(rsi_data)
        rsi_data = rsi_data[-1]
        plot("rsi", float(rsi_data))
        cur_position = context.portfolio.positions[stock].quantity  # 当前持股数
        # 使用当前现金的 30% 购买股票
        target_available_cash = context.portfolio.cash * context.ORDER_PERCENT

        # 当RSI大于设置的上限阀值，清仓该股票
        if rsi_data >= context.HIGH_RSI and cur_position > 0:
            order_target_value(stock, 0)
        if 20 <= rsi_data <= 30:
            logger.info("target available cash caled: " + str(target_available_cash))
            order_target_value(stock, target_available_cash)


config = {
  "base": {
    "start_date": "2018-01-01",
    "end_date": "2018-9-25",
    "benchmark": "000300.XSHG",
    "accounts": {
        "stock": 10000000
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
run_func(init=init, before_trading=None, handle_bar=handle_bar, config=config)
