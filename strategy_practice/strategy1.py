from rqalpha.api import *
from rqalpha import run_func
import math
import pandas

"""
非常简单的思路，不同的ETF指数基金表现不同，行业分布和仓位分配都不一样。所以在不同的ETF轮动也能起到类似于板块轮动的作用。

调仓（选择ETF）时间频率是每月一次。

给每个ETF的打分模式：考虑2个月的回报率和每日回报的波动率两个指标。百分比可以自由分配。

我尝试了上证50，上证180，深证100，中小板，创业板，沪深300。有兴趣的同学也可以试下其他的板块ETF轮动。
"""

def init(context):
    context.stocks = ["510050.XSHG",
                      "510180.XSHG",
                      "159902.XSHE",
                      "159901.XSHE",
                      "159915.XSHE",
                      "159919.XSHE"]
    # The current stock being held
    context.currentStock = None
    # 观察2个月历史数据
    context.LOOKBACK = 40
    context.OBSERVATION = 100
    update_universe(context.stocks)

    # 每个月调仓
    scheduler.run_monthly(reselect, 2)


def reselect(context, bar_dict):
    historydata = history_bars(context.OBSERVATION, '1d', 'close')
    best = getBestSector(historydata, context.stocks, context.LOOKBACK)

    if best:
        if (context.currentStock is not None and context.currentStock == best):
            return
        else:
            if (context.currentStock is not None):
                order_target_percent(context.currentStock, 0)
            order_target_percent(best, 0.99)
            context.currentStock = best


def handle_data(context, data):
    pass


def getMinMax(arr):
    return min(arr.values()), max(arr.values())


def historicalVolatility(prices, period):
    dailyreturn = []
    for i in range(1, period + 1):
        dailyreturn.append(math.log(prices[i] / prices[i - 1]))

    returnMean = sum(dailyreturn) / period;

    diff = []
    for i in range(0, period):
        diff.append(math.pow((dailyreturn[i] - returnMean), 2))

    vol = math.sqrt(sum(diff) / (period - 1)) * math.sqrt(252 / period)

    return vol


def getStockPerformance(price, period):
    start = price[-period]  # start price
    end = price[-1]  # end price

    performance = (end - start) / start

    volatility = historicalVolatility(price[-period - 2:-1], period)

    return performance, volatility


def getBestSector(price, stocks, period):
    best = None

    performances = {}
    volatilities = {}

    for stock in stocks:
        performance, volatility = getStockPerformance(price[stock].values, period)
        performances[stock] = performance
        volatilities[stock] = volatility

    minP, maxP = getMinMax(performances)
    maxV, minV = getMinMax(volatilities)

    # 给历史回报率和volatility打分，based on a 80/20 weighting.

    for stock in stocks:
        scoreP = (performances[stock] - minP) / (maxP - minP)
        scoreV = (volatilities[stock] - minV) / (maxV - minV)
        rank = 0.9 * scoreP + 0.1 * scoreV

        if best is None or rank > best[1]:
            best = stock, rank

    logger.info("selected stock:")
    logger.info(best[0])
    return best[0]

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
run_func(init=init, before_trading=None, handle_bar=None, config=config)
