from rqalpha.api import *
from rqalpha import  run_func
import numpy as np

import pandas as pd
import talib



"""
陶博士月线反转 择股 策略

选股条件 , 选出刚刚站上年线小于30天，大于3天的 ：
    1. RPS50大于87 , RPS120 > 90 , RPS250 > 120
        
    2. 一月内曾创50日新高
        NH:=IF(H<HHV(H,50),0,1);
        COUNT(NH,30);{一月内曾创50日新高}
        
    3. 站上年线
        C/MA(C,250)>1
          
    4. 收盘价距离120日内的最高价不到10%
        CLOSE/HHV(HIGH,120)>0.9;{
   
    5. 选出刚刚站上年线小于30天，大于3天的
        NN:=IF(C>MA(C,250),1,0);
        AA:=COUNT(NN,30);   
        AA>3 AND AA<30
"""



def init(context):
    # 这里选了000001.SZ作为参考基准，大家可以根据自己的不同需要进行修改；
    context.set_benchmark("000001.SZ")

    # 制定了一个买股的集合单子；存放在buyList里面的就是我们选出来后的要买的股
    context.buyList = []

    # curPflInfo 的key为当前持仓股票，value为股票信息
    # 如 context.curPflInfo = {'000001.XSHE':{'time':1,'avgCost':9.5}}
    context.curPflInfo = {}

    # avgCost是平均成本
    context.avgCost = 0

    # 持仓数
    context.holdSize = 10

    # 新买个股的初始仓位 每天开盘前初始化
    context.weight = 0

    # 止盈，可以是值，也可以是百分比制；
    context.stpPftPrice = 0.05

    # 止损，和止盈同样的道理
    context.stpLosRate = -0.05

    # 下单集合
    context.orderList = []

    # 股票池
    context.stocks = []

    # 可用股票池
    context.avail_stocks = []

    context.window_50 = 50
    context.window_120 = 120
    context.window_250 = 250

    # 月线反转信号 注册
    reg_indicator('MR', MONTH_INVERSION, freq='1d', win_size=250+1)






def handle_bar(context, bar_dict):
    # 获取指标 get_indicator(order_book_id, name)

    rps_120 = calRPS(context.stocks, context.window_120)
    rps_250 = calRPS(context.stocks, context.window_250)
    rps_50  = calRPS(context.stocks, context.window_50)

    # 列过滤
    rps_50 = rps_50[rps_50['rpsValue'] > 87]
    rps_120 = rps_120[rps_120['rpsValue'] >= 90]
    rps_250 = rps_250[rps_250['rpsValue'] >= 90]

    # 修改列名
    rps_50.columns = ['code', 'RPS50']
    rps_120.columns = ['code', 'RPS120']
    rps_250.columns = ['code', 'RPS250']

    # 交集
    res1 = pd.merge(rps_50, rps_120, on='code')
    res = pd.merge(res1, rps_250, on='code')

    logger.info(res)

    # stocks = []
    # RPS250 = []
    # RPS120 = []
    #
    # for i in range(rps_250.shape[0]):
    #     if rps_250.rpsValue[i] >= 90:
    #         for index, stock in enumerate(list(rps_120.code)):
    #             if rps_250.code[i] == stock and rps_120.rpsValue[index] >= 90:
    #                 stocks.append(instruments(stock).symbol)
    #                 RPS120.append(rps_120.rpsValue[index])
    #                 RPS250.append(rps_250.rpsValue[i])
    # rpsStocks = {'stock': stocks, 'RPS250': RPS250, 'RPS120': RPS120}
    # rpsStocks = pd.DataFrame(rpsStocks)
    # rpsStocks = rpsStocks.sort_values('RPS120', ascending=False)
    # return rpsStocks






def handle_tick(context, tick):
    pass



def before_trading(context):
    """
    q = query(
        fundamentals.equity_valuation_indicator.market_cap
    ).filter(
        fundamentals.equity_valuation_indicator.market_cap<1e11
    ).order_by(
        fundamentals.equity_valuation_indicator.market_cap.asc()
    ).limit(2500)
    df = get_fundamentals(q)
    context.allStocks = df.columns.values

    for stk in context.curPflInfo.keys():
        context.curPflInfo[stk]['holdDays'] += 1
    上面这个很基础的，通过市值来选取股，帮助文档里面能找到相关说明，这里就不多废话了,asc是从小到大取，
    如果选得多，成交机制也是从小到大进行成交;limit()为限制数量;
    接下来是过滤st和停牌，涨跌停股，目前不设置也不会买
    """
    # 获取沪深A股所有股票
    stocks = list(all_instruments("CS").order_book_id)
    # 获取的股票数
    logger.info(len(stocks))
    available_stocks = []
    for stock in stocks:
        # 过滤出上市时间大于一年的股票
        if not is_suspended(stock) and (not str(is_suspended(stock)) == 'None') and moreThanOneYear(stock):
            available_stocks.append(stock)
    context.stocks = available_stocks


def MONTH_INVERSION():
    """
     2. 一月内曾创50日新高
        NH:=IF(H<HHV(H,50),0,1);
        B:=COUNT(NH,30);{一月内曾创50日新高}

    3. 站上年线
        A:=C/MA(C,250)>1;{站上年线}

    4. 收盘价距离120日内的最高价不到10%
        AB:=CLOSE/HHV(HIGH,120)>0.9;{收盘价距离120日内的最高价不到10%}
        AB =

    5. 选出刚刚站上年线小于30天，大于3天的
        NN:=IF(C>MA(C,250),1,0);
        AA:=COUNT(NN,30);
        AA>3 AND AA<30
    :return:
    """
    # 1. 一月内曾创50日新高
    # HHV(H, 50), 过去50个交易周期内，最高价的最大值
    NH = IF(H > HHV(H, 50), 1, 0)
    B = COUNT(NH, 30)

    # 站上年线
    A = IF( C/MA(C, 250) > 1, 1, 0)

    # 收盘价距离120日内的最高价不到10%
    AB = CLOSE/HHV(H, 120) > 0.9

    # 选出刚刚站上年线小于30天，大于3天的
    NN = IF(C>MA(C,250), 1, 0)
    AA = COUNT(NN, 30)

    return (B & A & AB  & AA>3 & AA<30)







# 上市时间大于一年
def moreThanOneYear(stock):
    # 获取合约已上市天数
    days = instruments(stock).days_from_listed()
    return True if days > 250 else False


# 计算相对强弱RPS值
def calRPS(stocks, n):
    numStocks = len(stocks)

    rankValue = []

    # 计算涨跌幅
    for stock in stocks:
        price = history_bars(stock, n, '1d', 'close')
        firstClosePrice = price[0]
        lastClosePrice = price[-1]
        # 计算涨跌幅
        errCloseOpen = [lastClosePrice - firstClosePrice]
        rankValue += errCloseOpen

    # 计算排名
    rpsStocks = {'code': stocks, 'rankValue': rankValue}
    rpsStocks = pd.DataFrame(rpsStocks)
    rpsStocks = rpsStocks.sort_values('rankValue', ascending=False)
    stocks = list(rpsStocks['code'])

    # 计算RPS值
    rpsValue = [round(99 - (100 * i / numStocks)) for i in range(numStocks)]
    rpsStocks = {'code': stocks, 'rpsValue': rpsValue}
    rpsStocks = pd.DataFrame(rpsStocks)

    return rpsStocks