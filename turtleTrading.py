from rqalpha.api import *
from rqalpha import run_func
#导入必须的模块
import numpy as np
import talib
import math

def get_extreme(array_high_price_result, array_low_price_result):
    #抛开最新价格的价格序列
    np_array_high_price_result = np.array(array_high_price_result[:-1])
    np_array_low_price_result = np.array(array_low_price_result[:-1])
    #序列最大值
    max_result = np_array_high_price_result.max()
    #最小值
    min_result = np_array_low_price_result.min()
    #返回一个两个元素的list
    return [max_result, min_result]

#拿到真实震幅与头寸
def get_atr_and_unit( atr_array_result,  atr_length_result, total_value_result):
    #atr为真实平均振幅的最新值
    atr =  atr_array_result[ atr_length_result-1]
    #头寸
    unit = math.floor(total_value_result * .01 / atr)
    return [atr, unit]

#得到止损价格
def get_stop_price(first_open_price_result, units_hold_result, atr_result):
    stop_price = first_open_price_result - 2 * atr_result \
                 + (units_hold_result - 1) * 0.5 * atr_result
    return stop_price


def init(context):
    context.trade_day_num = 0
    context.unit = 0
    context.atr = 0
    context.trading_signal = 'start'
    context.pre_trading_signal = ''
    context.units_hold_max = 4
    context.units_hold = 0
    context.quantity = 0
    context.max_add = 0
    context.first_open_price = 0
    context.s = '000300.XSHG'
    context.open_observe_time = 55
    context.close_observe_time = 20
    context.atr_time = 20


def handle_bar(context, bar_dict):
    #当前合约的价值
    total_value = context.portfolio.total_value
    #context.open_observe_time+1个bar的每日最高价
    high_price = history_bars(context.s,context.open_observe_time+1, '1d', 'high')
    low_price_for_atr = history_bars(context.s,context.open_observe_time+1, '1d', 'low')
    low_price_for_extreme = history_bars(context.s,context.close_observe_time+1, '1d', 'low')
    close_price = history_bars(context.s,context.open_observe_time+2, '1d', 'close')
    close_price_for_atr = close_price[:-1]
    #talib.ATR平均真实振幅
    atr_array = talib.ATR(high_price, low_price_for_atr, close_price_for_atr, timeperiod=context.atr_time)
    #得到max_result
    maxx = get_extreme(high_price, low_price_for_extreme)[0]
    #得到min_result
    minn = get_extreme(high_price, low_price_for_extreme)[1]
    #前两日的平均真实振幅
    atr = atr_array[-2]

    if context.trading_signal != 'start':
        if context.units_hold != 0:
            context.max_add += 0.5 * get_atr_and_unit(atr_array, atr_array.size, total_value)[0]
    else:
        context.max_add = bar_dict[context.s].last

    #当前context.s持仓股数
    cur_position = context.portfolio.positions[context.s].quantity
    #当前仓位的现金
    available_cash = context.portfolio.cash
    #当前仓位的市场价值
    market_value = context.portfolio.market_value

    #当前仓位大于0并且当前价格小于止损价，产生信号"stop"
    if (cur_position > 0 and
            bar_dict[context.s].last < get_stop_price(context.first_open_price, context.units_hold, atr)):
        context.trading_signal = 'stop'
    else:
        #仓位大于0，并且当前价格小于观察时期的low的最小值
        if cur_position > 0 and bar_dict[context.s].last < minn:
            context.trading_signal = 'exit'
        else:
            #仓位大于0但小于策略设计仓位，并且当前价格大于观察时期的high的最大值，产生追加持仓的信号
            if (bar_dict[context.s].last > context.max_add and context.units_hold != 0 and
                    context.units_hold < context.units_hold_max and
                    available_cash > bar_dict[context.s].last*context.unit):
                context.trading_signal = 'entry_add'
            else:
                #价格大于maxx并且持仓为0，产生信号"entry"
                if bar_dict[context.s].last > maxx and context.units_hold == 0:
                    context.max_add = bar_dict[context.s].last
                    context.trading_signal = 'entry'

    atr = get_atr_and_unit(atr_array, atr_array.size, total_value)[0]
    if context.trade_day_num % 5 == 0:
        #每5个bar计算一次context.unit寸头
        context.unit = get_atr_and_unit(atr_array, atr_array.size, total_value)[1]
    context.trade_day_num += 1
    context.quantity = context.unit

    #不同信号下的操作
    if (context.trading_signal != context.pre_trading_signal or
            (context.units_hold < context.units_hold_max and context.units_hold > 1) or
            context.trading_signal == 'stop'):
        if context.trading_signal == 'entry':
            context.quantity = context.unit
            if available_cash > bar_dict[context.s].last*context.quantity:
                order_shares(context.s, context.quantity)
                context.first_open_price = bar_dict[context.s].last
                context.units_hold = 1

        if context.trading_signal == 'entry_add':
            context.quantity = context.unit
            order_shares(context.s, context.quantity)
            context.units_hold += 1

        if context.trading_signal == 'stop':
            if context.units_hold > 0:
                order_shares(context.s, -context.quantity)
                context.units_hold -= 1

        if context.trading_signal == 'exit':
            if cur_position > 0:
                order_shares(context.s, -cur_position)
                context.units_hold = 0

    context.pre_trading_signal = context.trading_signal

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
