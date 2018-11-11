from rqalpha.api import *
from rqalpha import run_func

import numpy as np
import pandas as pd
import talib



def init(context):
    """

    :param context:
    :return:
    """
    pass


def init(context):
    pass

def handle_bar(context, bar_dict):
    prices = history_bars('贵州茅台', 250, '1d', 'close')
    talib.MACD
    avg30 = talib.MA(prices, 30)
    avg60 = talib.MA(prices, 60)
    avg120 = talib.MA(prices, 120)

    macd, signal, hist = talib.MACD(prices, fastperiod=30, slowperiod=60, signalperiod=120)

    logger.info(macd)
    plot('price', prices[-1])
    plot('SMA30', avg30[-1])
    plot('SMA60', avg60[-1])
    plot('SMA120', avg120[-1])

    # plot("price", prices[-1])
    #plot('macd', macd[-1])
    #plot('macd', macd[-1])
    #plot('hist', hist[-1])


def handle_tick(context, tick):
    pass

def before_trading(context):
    pass

def after_trading(context):
    pass




config = {
  "base": {
    "start_date": "2017-01-01",
    "end_date": "2018-11-09",
    "benchmark": "000300.XSHG",
    "accounts": {
        "stock": 1000000
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