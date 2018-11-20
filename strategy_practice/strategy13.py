import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def init(context):
    context.buyList = []
    context.curPflInfo = {}
    context.holdSize = 10
    context.stpPftPrice = 0.04
    context.stpLosRate = -0.15
    context.orderList = []


def before_trading(context, bar_dict):
    q = query(
        fundamentals.eod_derivative_indicator.market_cap
    ).filter(
        fundamentals.eod_derivative_indicator.market_cap < 1e11
    ).order_by(
        fundamentals.eod_derivative_indicator.market_cap.asc()
    ).limit(300)
    df = get_fundamentals(q)
    context.allStocks = df.columns.values
    for stk in context.curPflInfo.keys():
        context.curPflInfo[stk]['holdDays'] += 1


def filterStAndPaused(stkList):
    stkList = [stk for stk in stkList if not is_st_stock(stk) and not is_st_stock(stk)]
    return stkList


def filterLimitStk(stk, bar_dict, context):
    yesterday = history(2, '1d', 'close')[stk].values[-1]
    his = history(2, '1d', 'close')[stk].values[-1]
    zt = round(1.10 * yesterday, 2)
    dt = round(0.97 * yesterday, 2)

    if dt < bar_dict[stk].last < zt:
        return True
    else:
        return False


def doSelect(context, bar_dict, stkList):
    buyList = []
    buyList = sanliandie(stkList, context)
    buyList = filterStAndPaused(buyList)
    buyList = [stk for stk in buyList if filterLimitStk(stk, bar_dict, context)]
    buyList = [stk for stk in buyList if bar_dict[stk].close < 140]
    buyList = getReturn(buyList, bar_dict, context)
    return buyList


def sanliandie(stkList, context):
    buyList = []
    for stk in stkList:
        if not is_st_stock(stk) and not is_suspended(stk):
            pan = history(10, '1d', 'close')["000001.XSHE"].values
            if pan[9] < pan[8] < pan[7]:
                buyList.append(stk)
    return buyList


def getReturn(stkList, bar_dict, context):
    buyList = []
    for stk in stkList:
        pan2 = current_snapshot("000001.XSHE").open
        pan5 = current_snapshot("000001.XSHE").last
        ret1 = (pan5 / pan2) - 1
        if (0 < ret1 < 0.004):
            buyList.append(stk)
    return buyList


def handle_bar(context, bar_dict):
    now = context.tody
    if not (now.hour == 14 and now.minute >= 59) and now.hour != 15:
        popList = []
        for stk in context.curPflInfo.keys():
            if bar_dict[stk].close / context.curPflInfo[stk]['avgCost'] - 1 >= context.stpPftPrice:
                order_target_value(stk, 0)
                print('止盈卖出 :', stk)
                popList.append(stk)
        for stk in popList:
            context.curPflInfo.pop(stk)

        popList = []
        for stk in context.curPflInfo.keys():
            if (context.curPflInfo[stk]['avgCost'] == 0):
                popList.append(stk)
                continue
            if bar_dict[stk].close / context.curPflInfo[stk]['avgCost'] - 1 <= context.stpLosRate:
                order_target_value(stk, 0)
                if now.hour == 14 and now.minute == 55:
                    print('止损卖出 :', stk)
                popList.append(stk)
        for stk in popList:
            context.curPflInfo.pop(stk)

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

    if now.hour == 14 and now.minute == 59:
        for stk in context.portfolio.positions.keys():
            stkInfo = {}
            stkInfo['avgCost'] = context.portfolio.positions[stk].average_cost
            stkInfo['holdDays'] = 1
            context.curPflInfo[stk] = stkInfo