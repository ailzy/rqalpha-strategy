# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import pandas as pd
import numpy as np
import time
import datetime
import math
import itertools


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # 在context中保存全局变量
    context.tradings_stocks = ['300033.XSHE', '000025.XSHE']
    # 最长持有天数
    context.period = 10
    # 最小收益率
    context.limit_return = 0.05
    # 时间框
    context.time = pd.DataFrame()

    scheduler.run_monthly(rebalance, 1)
    scheduler.run_daily(stoploss)


# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    pass


# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass


# 记录持有股票的时间点
def record(context, bar_dict, stock):
    if stock not in context.time.columns:
        temp = pd.DataFrame({str(stock): [context.now.replace(tzinfo=None)]})
        logger.info(temp)
        cur_positions
        context.time = pd.concat([context.time, temp], axis=1, join='inner')


def stoploss(context, bar_dict):
    # 实现止损
    # print(context.time)
    # 获得现有的仓位
    cur_positions = context.portfolio.positions

    for stock in cur_positions:
        if stock in context.time.columns:
            # 获得股票的开始持有时间
            in_time = context.time[stock][0]
            cur_time = context.now.replace(tzinfo=None)

            # print('入仓时间='+str(in_time))
            # print('现在时间=' + str(cur_time))

            # 持仓累计盈亏
            total_returns = cur_positions[stock].pnl / cur_positions[stock].market_value
            # print(total_returns)

            # 计算已经持有的天数
            holdings_days = (cur_time - in_time).days

            # ----交易判断条件------
            if holdings_days > context.period and total_returns < context.limit_return:
                print(str(stock) + '已经持有大于' + str(context.period) + '天 且回报过小， 卖出')
            elif total_returns > context.limit_return:
                print(str(stock) + '回报为: ' + str(total_returns) + '大于预设值' + str(context.limit_return))
            else:
                print(str(stock) + '持仓未到' + str(context.period) + '天，所以继续持有')


# 每月第一个交易日进行交易，并且更新时间框。
def rebalance(context, bar_dict):
    if len(context.tradings_stocks) != 0:
        for stock in context.tradings_stocks:
            record(context, bar_dict, stock)
            order_target_percent(stock, 1 / len(context.tradings_stocks))
    # else:
    #     order_target_percent(stock,0)








