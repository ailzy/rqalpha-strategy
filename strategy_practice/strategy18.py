from rqalpha.api import *
from rqalpha import  run_func

"""
ETF轮动 策略

 https://www.ricequant.com/community/topic/1993/?utm_source=codingpy
 
 以中证500指数（399905.XSHE）为小盘股代表，
 以沪深300指数（399300.XSHE）为大盘股的代表，
 同时加入创业板指（399006.XSHE）代表创业板强弱。
 以22个交易日代表一月的情况,将昨日之前的22日周期的收益率作为参考值，将3个指数收益率参考值进行比较，孰高则代表孰强，
 
 则买入相应的基金，
    南方中证500etf（510500.XSHG)代表中证500，
    华泰柏瑞沪深300etf（510310.XSHG）代表沪深300，
    易方达创业板etf（159915.XSHE），
    
    如果收益率都为负则买入货币型基金。

"""

def init(context):
    pass

def before_trading(context):
    pass

def handle_bar(context, bar_dict):
    #获取前一交易日日期
    last_day=get_previous_trading_date(context.now)

    # 获取指数点位,以22个交易日作为一个月
    # 以中证500指数（399905.XSHE）为小盘股代表
    sz500_index = history_bars('399905.XSHE', 22, '1d', 'close')

    #权重  以沪深300指数（399300.XSHE）为大盘股的代表
    hs300_index = history_bars('399300.XSHE', 22, '1d', 'close')

    #创业板  同时加入创业板指（399006.XSHE）代表创业板强弱
    GEM_index = history_bars('399006.XSHE', 22, '1d', 'close')

    #计算三大指数的一月收益率
    S_return=((sz500_index[-1]-sz500_index[0])/sz500_index[0])
    B_return=((hs300_index[-1]-hs300_index[0])/hs300_index[0])
    GEM_return=((GEM_index[-1]-GEM_index[0])/GEM_index[0])
    #信号指标
    signal=max(S_return, B_return, GEM_return, 0)
    #当前持有的股票
    stocks = context.portfolio.positions
    #根据信号指标进行下单操作
    if signal == 0:
        for stock in stocks:
            order_target_percent(stock, 0)
    elif signal ==S_return :
        #当信号发出但没持有基金就先清空持有头寸再买入
        if "510500.XSHG" not in stocks:
            for stock in stocks:
                order_target_percent(stock, 0)
            # order_target_percent('510500.XSHG', 1)
            order_percent('510500.XSHG', 0.9)
    elif signal == B_return:
        if "510310.XSHG" not in stocks:
            for stock in stocks:
                order_target_percent(stock, 0)
            # order_target_percent("510310.XSHG", 1)
            order_percent('510310.XSHG', 0.9)

    elif signal == GEM_return:
        if "159915.XSHE" not in stocks:
            for stock in stocks:
                order_target_percent(stock, 0)
            # order_target_percent("159915.XSHE", 1)
            order_percent('159915.XSHE', 0.9)
    return


config = {
  "base": {
    "start_date": "2015-01-01",
    "end_date": "2018-11-07",
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
#run_func(init=init, before_trading=before_trading, handle_bar=handle_bar, config=config)
run_func(**globals())
