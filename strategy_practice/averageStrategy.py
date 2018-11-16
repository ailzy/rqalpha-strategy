from rqalpha.api import *
from rqalpha import  run_func


def init(context):
    context.s1 = "000001.XSHE"
    update_universe([context.s1])

    context.slippage = 0.05
    #context.commission = 0.08  # 和默认数值相同，可以省略代码


def handle_bar(context, bar_dict):
    MA_short = bar_dict[context.s1].mavg(60, frequency='day')
    MA_long = bar_dict[context.s1].mavg(120, frequency='day')
    curPosition = context.portfolio.positions[context.s1].quantity
    shares = context.portfolio.cash / bar_dict[context.s1].close

    if MA_short > MA_long and curPosition == 0:
        order_shares(context.s1, shares)

    if MA_short < MA_long and curPosition != 0:
        order_shares(context.s1, 0)

    plot('close', bar_dict[context.s1].close)
    plot('short_avg',MA_short)
    plot('long_avg',MA_long)

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
run_func(init=init, before_trading=None, handle_bar=handle_bar, config=config)
