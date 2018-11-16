from rqalpha.api import *
from rqalpha import run_func


def init(context):
    context.stock = "万科A"
    # 实时打印日志
    logger.info("Interested at stock: " + str(context.stock))

    # 判断当日是否已经买过或卖出了
    context.fired = False

def before_trading(context, bar_dict):
    hist_series = history_bars('万科A',1, '1d', 'close')
    logger.info(str(hist_series))
    # 获取昨天的收盘价
    yesterday_close = hist_series[0]

    # 利用context来储存一个全局变量 - 买入或卖出信号，这个信号由下面的逻辑来决定. 每天开盘前初始化变成‘’
    context.signal = ''

    # 为了确保每天操作一次， 需要一个变量，重置为 False
    context.fired = False

    # 假设计算出来的一个神奇数字是7.5, 那么如果低于3%以上就买入，高于7.5这个价格就卖出。
    # 您可以任意修改这个数值或者通过一些复杂的公式来计算出来这个神奇数字
    magic_number = 7.5
    if yesterday_close <= magic_number * 0.97:
        context.signal = 'buy'
    elif yesterday_close > magic_number:
        context.signal = 'sell'

    # 保持良好的习惯继续打印吧：
    if context.signal != '':
        logger.info('获得调仓信号： ' + context.signal)


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 如果您的策略今天没有下过单 （便于和分钟回测进行兼容）。
    if not context.fired:
        if context.signal == 'buy':
            # 0.99 表示用现有资金 99% 全部买入，留一部分给手续费
            order_target_percent(context.stock, 0.99)

            # 今天已经调仓买入了，不再操作
            context.fired = True
        elif context.signal == 'sell':
            # 设置成0就是清仓全部卖出了
            order_target_percent(context.stock, 0)

            # 今天已经调仓卖出了，不再操作
            context.fired = True

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
run_func(init=init, before_trading=before_trading, handle_bar=handle_bar, config=config)
