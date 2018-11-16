from rqalpha.api import *
from rqalpha import run_func


# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import numpy as np
import pandas as pd
import math
import datetime
import collections
import talib


"""
均线通道策略

https://www.ricequant.com/community/topic/4654/%E5%9D%87%E7%BA%BF%E9%80%9A%E9%81%93%E7%AD%96%E7%95%A5/3
"""

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # 在context中保存全局变量
    # context.s1 = "000001.XSHE"
    # 实时打印日志
    logger.info("RunInfo: {}".format(context.run_info))

    # 指数成分股
    context.stocks = ['300133.XSHE', '601098.XSHG', '600332.XSHG', '000623.XSHE', '600027.XSHG', '601179.XSHG', '600795.XSHG', '002399.XSHE', '300146.XSHE', '601009.XSHG', '601288.XSHG', '601800.XSHG', '600637.XSHG', '000983.XSHE', '600031.XSHG', '002236.XSHE', '603993.XSHG', '600739.XSHG', '600406.XSHG', '600256.XSHG', '600875.XSHG', '300027.XSHE', '000413.XSHE', '002739.XSHE', '600111.XSHG', '600015.XSHG', '600048.XSHG', '601933.XSHG', '002470.XSHE', '601628.XSHG', '600115.XSHG', '002153.XSHE', '000800.XSHE', '600649.XSHG', '000415.XSHE', '000009.XSHE', '600373.XSHG', '600999.XSHG', '601857.XSHG', '600837.XSHG', '601989.XSHG', '600570.XSHG', '600157.XSHG', '000917.XSHE', '600066.XSHG', '300003.XSHE', '601991.XSHG', '600863.XSHG', '002465.XSHE', '601021.XSHG', '600104.XSHG', '600109.XSHG', '000559.XSHE', '600271.XSHG', '601808.XSHG', '000333.XSHE', '601169.XSHG', '000629.XSHE', '600959.XSHG', '000060.XSHE', '601888.XSHG', '600177.XSHG', '000999.XSHE', '002353.XSHE', '601390.XSHG', '000423.XSHE', '600153.XSHG', '600016.XSHG', '600315.XSHG', '300017.XSHE', '600887.XSHG', '601333.XSHG', '600028.XSHG', '600867.XSHG', '601939.XSHG', '601238.XSHG', '600188.XSHG', '601318.XSHG', '600583.XSHG', '000156.XSHE', '600549.XSHG', '600535.XSHG', '600519.XSHG', '000858.XSHE', '002038.XSHE', '000503.XSHE', '000883.XSHE', '601872.XSHG', '600383.XSHG', '600196.XSHG', '002410.XSHE', '600873.XSHG', '600029.XSHG', '600021.XSHG', '000725.XSHE', '600023.XSHG', '601727.XSHG', '000750.XSHE', '600578.XSHG', '000625.XSHE', '002007.XSHE', '002294.XSHE', '000712.XSHE', '000069.XSHE', '600642.XSHG', '601898.XSHG', '002008.XSHE', '002241.XSHE', '000400.XSHE', '001979.XSHE', '600489.XSHG', '600415.XSHG', '601718.XSHG', '002456.XSHE', '300002.XSHE', '002450.XSHE', '600998.XSHG', '600350.XSHG', '601766.XSHG', '600010.XSHG', '601618.XSHG', '600089.XSHG', '600900.XSHG', '600895.XSHG', '600352.XSHG', '600005.XSHG', '601969.XSHG', '300070.XSHE', '600690.XSHG', '002594.XSHE', '000061.XSHE', '601336.XSHG', '600068.XSHG', '601018.XSHG', '601016.XSHG', '002081.XSHE', '601668.XSHG', '601788.XSHG', '000738.XSHE', '600221.XSHG', '002500.XSHE', '000778.XSHE', '601600.XSHG', '603000.XSHG', '600170.XSHG', '601118.XSHG', '601186.XSHG', '002252.XSHE', '600804.XSHG', '601928.XSHG', '600674.XSHG', '600118.XSHG', '600633.XSHG', '000425.XSHE', '601225.XSHG', '002292.XSHE', '600827.XSHG', '300015.XSHE', '601998.XSHG', '000100.XSHE', '600660.XSHG', '002304.XSHE', '601988.XSHG', '600030.XSHG', '601699.XSHG', '000402.XSHE', '600741.XSHG', '000630.XSHE', '600036.XSHG', '601818.XSHG', '600362.XSHG', '000793.XSHE', '002142.XSHE', '600008.XSHG', '600585.XSHG', '600688.XSHG', '000895.XSHE', '600893.XSHG', '600252.XSHG', '300024.XSHE', '000826.XSHE', '601633.XSHG', '600369.XSHG', '002422.XSHE', '601899.XSHG', '600060.XSHG', '300104.XSHE', '000876.XSHE', '601158.XSHG', '000776.XSHE', '600783.XSHG', '000686.XSHE', '601866.XSHG', '601117.XSHG', '600166.XSHG', '601211.XSHG', '600317.XSHG', '002202.XSHE', '600038.XSHG', '601006.XSHG', '600718.XSHG', '300315.XSHE', '600011.XSHG', '300124.XSHE', '002736.XSHE', '601398.XSHG', '601166.XSHG', '000166.XSHE', '600663.XSHG', '600019.XSHG', '000937.XSHE', '002129.XSHE', '601258.XSHG', '000063.XSHE', '600000.XSHG', '600372.XSHG', '000539.XSHE', '002024.XSHE', '002375.XSHE', '601377.XSHG', '601555.XSHG', '600886.XSHG', '600820.XSHG', '000039.XSHE', '300058.XSHE', '000792.XSHE', '000568.XSHE', '601198.XSHG', '600050.XSHG', '600208.XSHG', '600485.XSHG', '600009.XSHG', '601901.XSHG', '300251.XSHE', '000709.XSHE', '600705.XSHG', '000581.XSHE', '601607.XSHG', '600839.XSHG', '600703.XSHG', '000898.XSHE', '002146.XSHE', '002475.XSHE', '000046.XSHE', '300059.XSHE', '601106.XSHG', '601992.XSHG', '600340.XSHG', '600547.XSHG', '002230.XSHE', '002415.XSHE', '000001.XSHE', '600600.XSHG', '000825.XSHE', '600150.XSHG', '000338.XSHE', '600588.XSHG', '000728.XSHE', '000783.XSHE', '002673.XSHE', '601985.XSHG', '000027.XSHE', '601231.XSHG', '601919.XSHG', '601088.XSHG', '300144.XSHE', '000540.XSHE', '600648.XSHG', '600958.XSHG', '600309.XSHG', '601601.XSHG', '002385.XSHE', '601669.XSHG', '601958.XSHG', '600085.XSHG', '600018.XSHG', '600276.XSHG', '603885.XSHG', '002195.XSHE', '000651.XSHE', '601328.XSHG', '002065.XSHE', '000598.XSHE', '601111.XSHG', '600717.XSHG', '000157.XSHE', '603288.XSHG', '600518.XSHG', '600398.XSHG', '000002.XSHE', '600100.XSHG', '601216.XSHG', '601608.XSHG', '000768.XSHE', '601688.XSHG', '000963.XSHE', '601099.XSHG', '000538.XSHE', '000831.XSHE', '000729.XSHE']

    context.deque = {}
    context.stocks_yield = {}
    context.holding = []
    context.high = {}


def get_fun(stocks, context):
    # print('获取股票信息')
    # stocks_yield={}
    stocks_yield1 = []
    # MA={}
    MA1 = []
    # SGM={}
    SGM1 = []
    # s=1

    # 遍历沪深300股票（不含停牌股票）
    for i in stocks:
        # print('循环开始',s)
        # s=s+1
        price = history_bars(i, 20, '1d', 'close')
        # 期初价格
        start_price = price[0]
        # 期末价格
        end_price = price[-1]
        # 计算收益率
        stock_yield = (end_price - start_price) / start_price
        # stocks_yield[i]=stock_yield
        stocks_yield1.append(stock_yield)
        # 计算20日均值
        stock_ma = sum(price) / 20
        # print(i,'20日均值',stock_ma)
        # MA[i]=stock_ma
        MA1.append(stock_ma)
        # 计算股价波动率
        stock_var = talib.VAR(price, 20, 1)
        stock_sgm = stock_var ** 0.5
        # print(i,'波动率',stock_sgm[-1])
        # SGM[i]=stock_sgm[-1]
        SGM1.append(stock_sgm[-1])
        try:
            if context.deque[i][0] > -3:
                pass
        except:
            context.deque[i] = collections.deque(maxlen=2)
            context.deque[i].append(-2)
            context.deque[i].append(-2)

    # print('跳出循环')
    column = list(range(1, len(stocks) + 1))
    stock_pool = pd.DataFrame([stocks_yield1, MA1, SGM1], index=['stocks_yield', 'stocks_ma', 'stocks_sgm'],
                              columns=stocks)
    """
    300133.XSHE  601098.XSHG    000623.XSHE 
    tocks_yield     0.044090     -0.034892     
    stocks_ma       10.697500    13.961000   
    stocks_sgm       0.197683    0.341305
    """
    logger.info(str(stock_pool))
    return stock_pool


# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    # print('盘前')
    stocks = [stock for stock in context.stocks if is_suspended(stock) != 1]
    # 获取股票的收益率，20日均值、波动率
    stocks_pool = get_fun(stocks, context)
    # print(stocks_pool)

    stocks_pool_300 = stocks_pool.sort_values(by='stocks_yield', axis=1, ascending=False)
    # print(stocks_pool)
    # 获取市场上表现最好的前60只股票
    stocks_pool_60 = stocks_pool.iloc[:, 0:60]

    context.stocks_pool_300 = stocks_pool_300
    context.stocks_pool_60 = stocks_pool_60

    context.stocks_pool_list_60 = stocks_pool_60.columns.tolist()
    context.stocks_pool_list_300 = stocks_pool_300.columns.tolist()

    context.stocks_pool_list_60_2 = context.stocks_pool_list_60
    context.stocks_pool_list_300_2 = context.stocks_pool_list_300


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑

    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合信息

    # 使用order_shares(id_or_ins, amount)方法进行落单

    # TODO: 开始编写你的算法吧！
    stocks_pool_list_60 = context.stocks_pool_list_60
    stocks_pool_list_300 = context.stocks_pool_list_300
    stocks_pool_list_60_2 = context.stocks_pool_list_60_2
    stocks_pool_list_300_2 = context.stocks_pool_list_300_2

    for i in stocks_pool_list_60:
        try:
            if bar_dict[i].close > context.high[i]:
                context.high[i] = bar_dict[i].close
        except:
            pass

        if bar_dict[i].close < (
                context.stocks_pool_60.ix['stocks_ma', i] - 2 * context.stocks_pool_60.ix['stocks_sgm', i]):
            context.deque[i].append(-1)

            if context.portfolio.positions[i].quantity != 0:
                # print('卖出',i)
                order_target_percent(i, 0)

                if context.portfolio.positions[i].quantity == 0:
                    context.stocks_pool_list_60.remove(i)
                    context.holding.remove(i)

        elif bar_dict[i].close > (
                context.stocks_pool_60.ix['stocks_ma', i] + 2 * context.stocks_pool_60.ix['stocks_sgm', i]) and \
                context.deque[i][0] == 0:

            context.deque[i].append(1)

            if i in stocks_pool_list_60 and context.portfolio.positions[i].quantity == 0:
                # print('买入',i)
                order_target_value(i, 200000)

                if context.portfolio.positions[i].quantity != 0:
                    context.high[i] = bar_dict[i].close
                    context.stocks_pool_list_60.remove(i)
                    context.holding.append(i)
        else:
            context.deque[i].append(0)

    holding_list = context.holding

    for i in holding_list:

        if i not in stocks_pool_list_60_2:
            if bar_dict[i].close > context.high[i]:
                context.high[i] = bar_dict[i].close
            elif bar_dict[i].close < 0.95 * context.high[i]:
                order_target_percent(i, 0)
                if context.portfolio.positions[i].quantity == 0:
                    context.high.pop(i)
                    context.holding.remove(i)
            else:
                pass
        else:
            pass

    # order_shares(context.s1, 1000)


# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass



config = {
  "base": {
    "start_date": "2018-01-04",
    "end_date": "2018-09-26",
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
