from rqalpha.api import *

import pandas as pd
import numpy as np
import time
import datetime
import math
import itertools

"""
买入策略： 
    一阳上穿10，20，30日线，量能是前一天3倍。

止损方式： 
    时间&收益率止损
    提前设定两个阈值（最长持有时间和最小收益率），如果某股票的持有天数超过天数阈值&&收益率小于收益率阈值，则清仓。其他情况下继续持有该股票。
    https://www.ricequant.com/community/topic/3828/

"""

def init(context):
    # 指数成分股
    context.stocks = ['300133.XSHE', '601098.XSHG', '600332.XSHG', '000623.XSHE', '600027.XSHG', '601179.XSHG', '600795.XSHG', '002399.XSHE', '300146.XSHE', '601009.XSHG', '601288.XSHG', '601800.XSHG', '600637.XSHG', '000983.XSHE', '600031.XSHG', '002236.XSHE', '603993.XSHG', '600739.XSHG', '600406.XSHG', '600256.XSHG', '600875.XSHG', '300027.XSHE', '000413.XSHE', '002739.XSHE', '600111.XSHG', '600015.XSHG', '600048.XSHG', '601933.XSHG', '002470.XSHE', '601628.XSHG', '600115.XSHG', '002153.XSHE', '000800.XSHE', '600649.XSHG', '000415.XSHE', '000009.XSHE', '600373.XSHG', '600999.XSHG', '601857.XSHG', '600837.XSHG', '601989.XSHG', '600570.XSHG', '600157.XSHG', '000917.XSHE', '600066.XSHG', '300003.XSHE', '601991.XSHG', '600863.XSHG', '002465.XSHE', '601021.XSHG', '600104.XSHG', '600109.XSHG', '000559.XSHE', '600271.XSHG', '601808.XSHG', '000333.XSHE', '601169.XSHG', '000629.XSHE', '600959.XSHG', '000060.XSHE', '601888.XSHG', '600177.XSHG', '000999.XSHE', '002353.XSHE', '601390.XSHG', '000423.XSHE', '600153.XSHG', '600016.XSHG', '600315.XSHG', '300017.XSHE', '600887.XSHG', '601333.XSHG', '600028.XSHG', '600867.XSHG', '601939.XSHG', '601238.XSHG', '600188.XSHG', '601318.XSHG', '600583.XSHG', '000156.XSHE', '600549.XSHG', '600535.XSHG', '600519.XSHG', '000858.XSHE', '002038.XSHE', '000503.XSHE', '000883.XSHE', '601872.XSHG', '600383.XSHG', '600196.XSHG', '002410.XSHE', '600873.XSHG', '600029.XSHG', '600021.XSHG', '000725.XSHE', '600023.XSHG', '601727.XSHG', '000750.XSHE', '600578.XSHG', '000625.XSHE', '002007.XSHE', '002294.XSHE', '000712.XSHE', '000069.XSHE', '600642.XSHG', '601898.XSHG', '002008.XSHE', '002241.XSHE', '000400.XSHE', '001979.XSHE', '600489.XSHG', '600415.XSHG', '601718.XSHG', '002456.XSHE', '300002.XSHE', '002450.XSHE', '600998.XSHG', '600350.XSHG', '601766.XSHG', '600010.XSHG', '601618.XSHG', '600089.XSHG', '600900.XSHG', '600895.XSHG', '600352.XSHG', '600005.XSHG', '601969.XSHG', '300070.XSHE', '600690.XSHG', '002594.XSHE', '000061.XSHE', '601336.XSHG', '600068.XSHG', '601018.XSHG', '601016.XSHG', '002081.XSHE', '601668.XSHG', '601788.XSHG', '000738.XSHE', '600221.XSHG', '002500.XSHE', '000778.XSHE', '601600.XSHG', '603000.XSHG', '600170.XSHG', '601118.XSHG', '601186.XSHG', '002252.XSHE', '600804.XSHG', '601928.XSHG', '600674.XSHG', '600118.XSHG', '600633.XSHG', '000425.XSHE', '601225.XSHG', '002292.XSHE', '600827.XSHG', '300015.XSHE', '601998.XSHG', '000100.XSHE', '600660.XSHG', '002304.XSHE', '601988.XSHG', '600030.XSHG', '601699.XSHG', '000402.XSHE', '600741.XSHG', '000630.XSHE', '600036.XSHG', '601818.XSHG', '600362.XSHG', '000793.XSHE', '002142.XSHE', '600008.XSHG', '600585.XSHG', '600688.XSHG', '000895.XSHE', '600893.XSHG', '600252.XSHG', '300024.XSHE', '000826.XSHE', '601633.XSHG', '600369.XSHG', '002422.XSHE', '601899.XSHG', '600060.XSHG', '300104.XSHE', '000876.XSHE', '601158.XSHG', '000776.XSHE', '600783.XSHG', '000686.XSHE', '601866.XSHG', '601117.XSHG', '600166.XSHG', '601211.XSHG', '600317.XSHG', '002202.XSHE', '600038.XSHG', '601006.XSHG', '600718.XSHG', '300315.XSHE', '600011.XSHG', '300124.XSHE', '002736.XSHE', '601398.XSHG', '601166.XSHG', '000166.XSHE', '600663.XSHG', '600019.XSHG', '000937.XSHE', '002129.XSHE', '601258.XSHG', '000063.XSHE', '600000.XSHG', '600372.XSHG', '000539.XSHE', '002024.XSHE', '002375.XSHE', '601377.XSHG', '601555.XSHG', '600886.XSHG', '600820.XSHG', '000039.XSHE', '300058.XSHE', '000792.XSHE', '000568.XSHE', '601198.XSHG', '600050.XSHG', '600208.XSHG', '600485.XSHG', '600009.XSHG', '601901.XSHG', '300251.XSHE', '000709.XSHE', '600705.XSHG', '000581.XSHE', '601607.XSHG', '600839.XSHG', '600703.XSHG', '000898.XSHE', '002146.XSHE', '002475.XSHE', '000046.XSHE', '300059.XSHE', '601106.XSHG', '601992.XSHG', '600340.XSHG', '600547.XSHG', '002230.XSHE', '002415.XSHE', '000001.XSHE', '600600.XSHG', '000825.XSHE', '600150.XSHG', '000338.XSHE', '600588.XSHG', '000728.XSHE', '000783.XSHE', '002673.XSHE', '601985.XSHG', '000027.XSHE', '601231.XSHG', '601919.XSHG', '601088.XSHG', '300144.XSHE', '000540.XSHE', '600648.XSHG', '600958.XSHG', '600309.XSHG', '601601.XSHG', '002385.XSHE', '601669.XSHG', '601958.XSHG', '600085.XSHG', '600018.XSHG', '600276.XSHG', '603885.XSHG', '002195.XSHE', '000651.XSHE', '601328.XSHG', '002065.XSHE', '000598.XSHE', '601111.XSHG', '600717.XSHG', '000157.XSHE', '603288.XSHG', '600518.XSHG', '600398.XSHG', '000002.XSHE', '600100.XSHG', '601216.XSHG', '601608.XSHG', '000768.XSHE', '601688.XSHG', '000963.XSHE', '601099.XSHG', '000538.XSHE', '000831.XSHE', '000729.XSHE']

    reg_indicator('signal', TARGET_SIGNAL, '1d', win_size=20)

    # 最长持有天数
    context.period = 10
    # 最小收益率
    context.limit_return = 0.05
    # 时间框
    context.time = pd.DataFrame()

    # scheduler.run_monthly(rebalance, 1)
    # scheduler.run_daily(stoploss)


def handle_bar(context, bar_dict):
    # 获得现有的仓位
    cur_positions = context.portfolio.positions
    for stock in cur_positions:
        if stock in context.time.columns:
            # 获得股票的开始持有时间
            in_time = context.time[stock][0]
            cur_time = context.now.replace(tzinfo=None)
            # 持仓累计盈亏
            total_returns = cur_positions[stock].pnl / cur_positions[stock].market_value
            # print(total_returns)
            # 计算已经持有的天数
            holdings_days = (cur_time - in_time).days
            # ----交易判断条件------
            if holdings_days > context.period and total_returns < context.limit_return:
                print(str(stock) + '已经持有大于' + str(context.period) + '天 且回报过小， 卖出')
                order_percent(stock, 0)

            elif total_returns > context.limit_return:
                order_percent(stock, 0)
                print(str(stock) + '回报为: ' + str(total_returns) + '大于预设值' + str(context.limit_return))
            else:
                print(str(stock) + '持仓未到' + str(context.period) + '天，所以继续持有')

    for stock in context.stocks:
        target = get_indicator(stock, 'signal')
        if target:
            order_percent(stock, 0.1)
            record(context, bar_dict, stock)


def record(context, bar_dict, stock):
    if stock not in context.time.columns:
        temp = pd.DataFrame({str(stock): [context.now.replace(tzinfo=None)]})
        logger.info(temp)
        context.time = pd.concat([context.time, temp], axis=1, join='inner')

def TARGET_SIGNAL():
    return CROSS(C, MA(C, 10)) & CROSS(C, MA(C, 20)) & CROSS(C, MA(C, 30)) & (V > REF(V, 1) * 3)



