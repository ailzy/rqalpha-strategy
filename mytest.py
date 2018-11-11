
from rqalpha.api import *
import pandas as pd
import numpy as np
import time
import math
import itertools
from rqalpha import run_func

def init(context):
    """

    :param context:
    :return:
    """
    pass


def init(context):
    pass

def handle_bar(context, bar_dict):
  logger.info("--------")
  logger.info(history_bars('300174.XSHE', 5, '1d', 'close'))

def handle_tick(context, tick):
    pass

def before_trading(context):
    pass

def after_trading(context):
    pass



config = {
  "base": {
    "data_bundle_path": "/Users/cuijl/.rqalpha/bundle",
    "start_date": "2017-01-01",
    "end_date": "2017-5-01",
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
