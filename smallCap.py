from rqalpha.api import *
from rqalpha import run_func

import pandas as pd
import numpy as np


def init(context):
    context.s1 = '000001.XSHG'
    context.max_num_stocks = 40
    context.days = 0
    context.period_days = 1
    context.relative_strength_6m = {}


def period_passed(context):
    return context.days % context.period_days == 0


def before_trading(context):
    context.days += 1
    if not period_passed(context):
        return

    dofilter(context)
    update_universe(context.fundamental_df.columns.values)


def dofilter(context):
    fundamental_df = get_fundamentals(
        query(fundamentals.eod_derivative_indicator.market_cap)
            .order_by(fundamentals.eod_derivative_indicator.market_cap.asc())
            .limit(context.max_num_stocks)
    )

    # Update context
    if '300372.XSH' in fundamental_df.columns:
        del fundamental_df['300372.XSHE']

    if '600656.XSHG' in fundamental_df.columns:
        del fundamental_df['600656.XSHG']

    context.stocks = [stock for stock in fundamental_df]

    context.fundamental_df = fundamental_df


def rebalance(context, bar_dict):
    for stock in context.portfolio.positions:
        if stock not in context.fundamental_df:
            order_target_percent(stock, 0)

    context.stocks = [stock for stock in context.stocks
                      if
                      stock in bar_dict and bar_dict[stock].is_trading and context.relative_strength_6m[stock] < -0.5]

    if len(context.stocks) == 0:
        return

    weight = 1.0 / len(context.stocks)

    for stock in context.stocks:
        order_target_percent(stock, weight)


def handle_bar(context, bar_dict):
    his = history_bars(10, '1d', 'close')['000001.XSHG']

    if period_passed(context):
        if his[9] / his[8] < 0.97:
            if len(context.portfolio.positions) > 0:
                for stock in context.portfolio.positions.keys():
                    order_target_percent(stock, 0)
            return

    if not period_passed(context):
        return

    compute_relative_strength(context, bar_dict)
    rebalance(context, bar_dict)


def compute_relative_strength(context, bar_dict):
    prices = history_bars(150, '1d', 'close')
    # prices = history(150, '1d', 'close')

    # 过去六个月的价格变化率
    pct_change = (prices.ix[149] - prices.ix[19]) / prices.ix[19]
    # print(prices.ix[19])
    # print(pct_change)
    priceofbase = history_bars(150, '1d', 'close')[context.s1]
    pct_changeforbase = (priceofbase.ix[149] - priceofbase.ix[19]) / priceofbase.ix[19]
    pct_change = pct_change - pct_changeforbase
    print(pct_change.index)
    print(bar_dict)
    if pct_changeforbase != 0:
        pct_change = pct_change / abs(pct_changeforbase)
    context.relative_strength_6m = pct_change


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
