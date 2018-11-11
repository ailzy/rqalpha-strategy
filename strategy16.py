from rqalpha.api import *
from rqalpha import  run_func
import numpy as np

import pandas as pd
import talib
from datetime import datetime ,timedelta


""""
https://www.ricequant.com/community/topic/2216/?utm_source=codingpy

策略：追击涨停


"""

def init(context):

    context.buyList = []
    context.curPflInfo = {}
    context.holdSize = 10
    context.stpPftPrice = 0.04
    context.stpLosRate = -0.15
    context.orderList = []
def before_trading(context, bar_dict):
    q = query(
        fundamentals.eod_derivative_indicator.market_cap   # 总市值
    ).filter(
        fundamentals.eod_derivative_indicator.market_cap <1e11  # 小市值
    ).order_by(
        fundamentals.eod_derivative_indicator.market_cap.asc()
    ).limit(300)
    # 获取历史财务数据
    df = get_fundamentals(q)
    context.allStocks = df.columns.values
    for stk in context.curPflInfo.keys():
        context.curPflInfo[stk]['holdDays'] += 1

# 过滤ST 和停盘的股票
def filterStAndPaused(stkList):
    stkList = [stk for stk in stkList if not is_st_stock(stk) and  not is_st_stock(stk)]
    return stkList


# 判断股票是否涨停
def filterLimitStk(stk, bar_dict ,context):
    yesterday = history_bars(stk, 2, '1d', 'close')
    zt = round(1.10 * yesterday[-1], 2) # 返回浮点数x的四舍五入值
    dt = round(0.97 * yesterday[-1], 2)

    # last 最近的成交价表示
    if dt < bar_dict[stk].last < zt:
        return True
    else:
        return False


def doSelect(context, bar_dict, stkList):
    buyList = []
    # 选股
    buyList = sanliandie(stkList, context)
    # 过滤st
    buyList = filterStAndPaused(buyList)
    # 选择涨停的股票
    buyList = [stk for stk in buyList if filterLimitStk(stk, bar_dict, context)]
    buyList = [stk for stk in buyList if bar_dict[stk].close <140]
    # 开盘的判断
    buyList = getReturn(buyList, bar_dict, context)
    return buyList



# 过滤ST,停盘的股票，选择连续跌三天的股票。
def sanliandie (stkList, context):
    buyList = []
    for stk in stkList :
        if not is_st_stock(stk) and not is_suspended(stk):
            pan = history_bars("000001.XSHE", 10, '1d', 'close')
            if pan[9 ] <pan[8 ] <pan[7]:
                buyList.append(stk)
    return buyList

# 开盘可买状态
def getReturn(stkList, bar_dict, context):
    buyList = []
    for stk in stkList :
        # 获得当前市场快照数据。只能在日内交易阶段调用
        pan2 = current_snapshot("000001.XSHE").open  # 当日开盘价
        pan5 = current_snapshot("000001.XSHE").last  # 当前最新价
        ret1 = (pan5/pan2)-1
        if (0 < ret1< 0.004 ) :
            buyList.append(stk)
    return buyList


def handle_bar(context, bar_dict):
    now = context.now
    # 收盘前一小时处理
    if not (now.hour == 14 and now.minute >= 59) and now.hour != 15:
        popList = []
        for stk in context.curPflInfo.keys():
            # 大于 0.04
            if bar_dict[stk].close / context.curPflInfo[stk]['avgCost'] -1 >= context.stpPftPrice:
                order_target_value(stk, 0)
                logger.info('止盈卖出 :{}'.format(stk))
                popList.append(stk)
        for stk in popList:
            context.curPflInfo.pop(stk)

        popList = []
        for stk in context.curPflInfo.keys():
            if (context.curPflInfo[stk]['avgCost'] == 0):
                popList.append(stk)
                continue
            # 止损 15%
            if bar_dict[stk].close / context.curPflInfo[stk]['avgCost'] - 1 <= context.stpLosRate:
                order_target_value(stk, 0)
                # if now.hour == 14 and now.minute == 55:
                logger.info("止损卖出{}".format(stk))
                popList.append(stk)
        for stk in popList:
            context.curPflInfo.pop(stk)

    # 中午11点半前三分钟的
    if now.hour == 11 and (now.minute == 27 or now.minute == 28 or now.minute == 29):

        popList = []
        for stk in context.curPflInfo.keys():
            if context.curPflInfo[stk]['holdDays'] >= 50:
                order_target_value(stk, 0)
                print('超过持仓时间卖出：', stk)
                if context.portfolio.positions[stk].market_value == 0:
                    popList.append(stk)
        for stk in popList:
            context.curPflInfo.pop(stk)

        if len(context.curPflInfo.keys()) < context.holdSize:
            buyList = doSelect(context, bar_dict, context.allStocks)
            buyCount = context.holdSize - len(context.curPflInfo.keys())
            buyList = buyList[:buyCount]

            for stk in buyList:
                order_percent(stk, 0.2)
                print('建仓 :', stk)


# 每天收盘后数据处理
def after_trading(context):
    for stk in context.portfolio.positions.keys():
        stkInfo = {}
        stkInfo['avgCost'] = context.portfolio.positions[stk].avg_price  # 平均建仓成本
        stkInfo['holdDays'] = 1
        context.curPflInfo[stk] = stkInfo