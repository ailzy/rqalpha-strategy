# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import talib
from rqalpha.api import *
from rqalpha import run_func

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.s1 = "000001.XSHE"

    # 使用MACD需要设置长短均线和macd平均线的参数
    context.SHORTPERIOD = 12
    context.LONGPERIOD = 26
    context.SMOOTHPERIOD = 9
    context.OBSERVATION = 100


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑
    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合状态信息
    # 使用order_shares(id_or_ins, amount)方法进行落单

    # 读取历史数据，使用sma方式计算均线准确度和数据长度无关，但是在使用ema方式计算均线时建议将历史数据窗口适当放大，结果会更加准确
    prices = history_bars(context.s1, context.OBSERVATION, '1d', 'close')

    # 用Talib计算MACD取值，得到三个时间序列数组，分别为macd, signal 和 hist
    macd, signal, hist = talib.MACD(prices, context.SHORTPERIOD,
                                    context.LONGPERIOD, context.SMOOTHPERIOD)

    plot("macd", macd[-1])
    plot("macd signal", signal[-1])

    # macd 是长短均线的差值，signal是macd的均线，使用macd策略有几种不同的方法，我们这里采用macd线突破signal线的判断方法

    # 如果macd从上往下跌破macd_signal

    if macd[-1] - signal[-1] < 0 and macd[-2] - signal[-2] > 0:
        # 计算现在portfolio中股票的仓位
        curPosition = context.portfolio.positions[context.s1].quantity
        #进行清仓
        if curPosition > 0:
            order_target_value(context.s1, 0)

    # 如果短均线从下往上突破长均线，为入场信号
    if macd[-1] - signal[-1] > 0 and macd[-2] - signal[-2] < 0:
        # 满仓入股
        order_target_percent(context.s1, 1)


config = {
  "base": {
    "start_date": "2013-06-01",
    "end_date": "2018-12-01",
    "frequency": "1d",
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
