from rqalpha.api import *
from rqalpha import run_func

'''
止损描述 : 
    回撤止损是根据回撤进行止损，如果此时回撤大于某个固定的阈值，
    就将此股票卖出，回撤是一个在某一段时期内产品净值从最高点开始回落到最低点的幅度的指标，在一定程度上可以评估策略极端风险管理能力。
    回撤超过 X%  之后 止损。 

套用方法： 
0:  在 init 中设置你的 回撤 X  context.drawdown = 0.1 % 回撤限度 10%
1： 复制‘scheduler.run_daily(stoploss)’ 至 init 
2:  复制 def stoploss ， def createdic 到策略内
3:  在 order  之前加入 createdic(context,bar_dict,stock)

'''

# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import pandas as pd
import numpy as np
import time
import math
import datetime


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.to_buy = ['300033.XSHE', '000025.XSHE', '601390.XSHG']
    context.drawdown = 0.1  # 回撤限度 10%
    # 记录最大的市值（市值框）
    context.maxvalue = pd.DataFrame()
    # 实时打印日志
    # scheduler.run_daily(stoploss)
    logger.info("Interested at stock: " + str(context.to_buy))
    # 每月1号进行
    scheduler.run_monthly(position, 1)
    scheduler.run_daily(stoploss)


def stoploss(context, bar_dict):
    # print(context.portfolio.positions)

    for stock in context.portfolio.positions:

        # print(context.maxvalue)

        # 获得股票的现在市值
        market_value = context.portfolio.positions[stock].market_value
        # 获得 购买时的市值（平均价 * 购买量）
        bought_value = context.portfolio.positions[stock].avg_price * context.portfolio.positions[stock].quantity

        # -----------以下的代码实际上是对市值框的数据进行更新。-------

        # 获得过去记录市值中的最大市值（maxvalue）
        #if not context.maxvalue.columns.contains(stock):
        #    continue
        stockdic = context.maxvalue[stock]
        maxvalue = stockdic[0]
        # 将市值框对应目前所选股票的那一列数据删除
        del context.maxvalue[stock]

        # 对比过去最大市值和现在市值的大小
        temp = pd.DataFrame({str(stock): [max(maxvalue, market_value)]})

        context.maxvalue = pd.concat([context.maxvalue, temp], axis=1, join='outer')  # 更新其盘中最高价值和先阶段比例。

        # -------------------------------------------------------------

        # 计算当前股票的回撤，若市值创新高，回撤=0
        drawdown = 1 - market_value / max(maxvalue, market_value)

        print(str(stock) + '的成本为：' + str(bought_value) + ', 最高价值为：' + str(maxvalue) + '现价值为：' + str(market_value))
        print(str(stock) + '的现回撤为: ' + str(drawdown * 100) + '%')

        # 回撤大于阈值，将股票卖出
        if drawdown > context.drawdown:  # 现价低于原价一定比例
            ors = order_target_percent(stock, 0)
            if not (ors.status is ORDER_STATUS.REJECTED):
                # 已经卖出去了，可以将数据框中的数据删除，positions里面没有此股票了
                print(str(stock) + '的回撤= ' + str(drawdown) + '这个回撤大于阈值 = ' + str(
                    context.drawdown * 100) + '%' + '  触发止损,并且交下单成功')
                del context.maxvalue[stock]
            else:
                # 没有卖出去，留着另寻机会
                pass

    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    pass


# 创建一个dic
def createdic(context, bar_dict, stock):
    # 将在市值框中没有数据的股票，记录其交易额
    if stock not in context.maxvalue.columns:
        # 计算购买股票的市值， 平均价 * 数量
        temp = pd.DataFrame(
            {str(stock): [context.portfolio.positions[stock].avg_price * context.portfolio.positions[stock].quantity]})
        logger.info("temp: " + str(temp))
        # 横向拼接
        concat_result = pd.concat([context.maxvalue, temp], axis=1, join='outer')
        logger.info("concat_result: " + str(concat_result))
        context.maxvalue = concat_result
        # context.maxvalue = pd.concat([context.maxvalue, temp], axis=1, join='inner')
    # 这样得到市值框是包含所有股票数据的
    # print(context.maxvalue)
    logger.info("context.maxvalue: " + str(context.maxvalue))


def position(context, bar_dict):
    if len(context.to_buy) != 0:
        for stock in context.to_buy:
            order_target_percent(stock, 1 / len(context.to_buy))
            createdic(context, bar_dict, stock)
            # 在position里面调用creatdic函数，意味着每次进行买入之后，市值框是满的。
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


