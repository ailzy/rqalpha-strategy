from rqalpha.api import *
from rqalpha import run_func

'''
阶梯止损
止损描述 :  
    设置初始 止损比例 M ， 股价每上涨 X% ， 就将止损比例 提高 Y %
    本例中：初始止损比例为 -10%。 股价每上涨 10%， 就将止盈比例提高9% 

套用方法： 
0:  在 init 中设置你的 A X Y 
1： 复制‘scheduler.run_daily(stoploss)’ 至 init 
2:  复制 def stoploss ， def createdic 到策略内
3:  在 order  之后加入 createdic(context,bar_dict,stock)

'''

# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import pandas as pd
import numpy as np
import time
import math
import datetime


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.to_buy = ('300033.XSHE', '000025.XSHE')
    context.initSLM = 0.9  # 初始止损比例 M
    context.step = 0.10  # 间隔 X
    context.increment = 0.09  # 止损增量  Y
    # maxvalue是一个Dataframe包含两行数据，第一行记录股票的市值，第二行记录止损比例
    context.maxvalue = pd.DataFrame()
    logger.info("Interested at stock: " + str(context.to_buy))
    scheduler.run_monthly(position, 1)
    scheduler.run_daily(stoploss)


def stoploss(context, bar_dict):
    for stock in context.portfolio.positions:
        # 作此判断是避免仓位为0的股票
        if context.portfolio.positions[stock].quantity > 0:

            market_value = context.portfolio.positions[stock].market_value  # 该股市场价值 单位（RMB）
            # 成交价格
            bought_value = context.portfolio.positions[stock].avg_price * context.portfolio.positions[
                stock].quantity  # 该股初始价值 单位（RMB）
            # 记录最高的市值

            # --------对比某个股票的以往的最大市值和现在的市值，并且更新maxvalue--------

            stockdic = context.maxvalue[stock]
            maxvalue = stockdic[0]

            del context.maxvalue[stock]
            print(stock, '的最大市值是 = ', (maxvalue), ',买入价格是 = ', bought_value)

            # 计算现在的止损比例
            currSL = context.initSLM * (1 + context.increment) ** math.floor(
                (math.log(maxvalue / bought_value) / math.log(1 + context.step)))  # 阶梯止损算法

            temp = pd.DataFrame({str(stock): [max(maxvalue, market_value), currSL]})
            context.maxvalue = pd.concat([context.maxvalue, temp], axis=1, join='inner')  # 更新dataframe。

            # -------------------------------------------------------------------------

            print(str(stock) + '的成本为：' + str(bought_value) + ', 最高价值为：' + str(maxvalue) + '现价值为：' + str(market_value))
            print(str(stock) + '的现 止损价位为: ' + str(currSL))

            if market_value < bought_value * currSL:  # 现价初始止损价
                ors = order_target_percent(stock, 0)
                if not (ors.status is ORDER_STATUS.REJECTED):
                    del context.maxvalue[stock]
                else:
                    print(stock, '未交易成功...')
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑
    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合状态信息

    # 使用order_shares(id_or_ins, amount)方法进行落单

    # TODO: 开始编写你的算法吧！
    # position(context,bar_dict)
    # logger.info(type(context.now))
    pass


def createdic(context, bar_dict, stock):
    # 创建一个dataframe包含两行数据，第一行记录股票的市值，第二行记录止损比例
    if (stock not in context.maxvalue.columns) and (context.portfolio.positions[stock].quantity > 0):
        temp = pd.DataFrame({str(stock): [
            context.portfolio.positions[stock].quantity * context.portfolio.positions[stock].avg_price,
            context.initSLM]})
        context.maxvalue = pd.concat([context.maxvalue, temp], axis=1, join='outer')
    print(context.maxvalue)


def position(context, bar_dict):
    if len(context.to_buy) != 0:
        for stock in context.to_buy:
            order_target_percent(stock, 1 / len(context.to_buy))
            createdic(context, bar_dict, stock)

    # else:
    #     order_target_percent(stock,0)

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





